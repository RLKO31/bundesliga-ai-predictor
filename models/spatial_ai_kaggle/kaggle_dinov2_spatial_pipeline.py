"""
===============================================================================
KAGGLE NOTEBOOK: Spatial AI + Tabular Hybrid Predictor (Smart Path Resolution)
===============================================================================
Hardware Accelerator: GPU (NVIDIA T4 / P100 recommended)
Environment: Kaggle PyTorch 2.x
Runtime: ~2 to 3 minutes
===============================================================================
"""

import os
import json
import time
import math
import glob
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, log_loss
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim

# ===============================================================================
# 1. GPU ENVIRONMENT SETUP
# ===============================================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"--- 1. Kaggle Compute Device: {device} ---")
if torch.cuda.is_available():
    print(f"GPU Name: {torch.cuda.get_device_name(0)}")

# ===============================================================================
# 2. MULTI-CHANNEL GAUSSIAN KDE RASTERIZER (224x224x4 TENSORS)
# ===============================================================================
def rasterize_heatmap_tensor(x_coords, y_coords, grid_size=224, pitch_x=105.0, pitch_y=68.0):
    x_coords, y_coords = np.array(x_coords), np.array(y_coords)
    xi, yi = np.mgrid[0:pitch_x:complex(0, grid_size), 0:pitch_y:complex(0, grid_size)]
    
    if len(x_coords) > 3:
        try:
            positions = np.vstack([x_coords, y_coords])
            kernel = gaussian_kde(positions, bw_method=0.25)
            positions_grid = np.vstack([xi.ravel(), yi.ravel()])
            zi = kernel(positions_grid).reshape(xi.shape)
            zi = (zi - zi.min()) / (zi.max() - zi.min() + 1e-8)
        except Exception:
            zi = np.zeros((grid_size, grid_size))
    else:
        zi = np.zeros((grid_size, grid_size))
        
    ch0 = zi
    ch1 = ch0 * (xi > 70.0).astype(float)
    ch2 = ch0 * (xi <= 52.5).astype(float)
    ch3 = np.gradient(ch0)[0]
    ch3 = (ch3 - ch3.min()) / (ch3.max() - ch3.min() + 1e-8)
    return np.stack([ch0, ch1, ch2, ch3], axis=0).astype(np.float32)

# ===============================================================================
# 3. SPATIAL EXTRACTOR BACKBONE (DINOv2 WITH OFFLINE FALLBACK)
# ===============================================================================
class DINOv2SpatialExtractor(nn.Module):
    def __init__(self, in_channels=4, out_dim=384):
        super().__init__()
        print("Attempting to load DINOv2 model ('dinov2_vits14') from PyTorch Hub...")
        self.is_hub_model = False
        try:
            self.backbone = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')
            self.input_proj = nn.Conv2d(in_channels, 3, kernel_size=1)
            self.is_hub_model = True
            for p in self.backbone.parameters():
                p.requires_grad = False
            print("SUCCESS: Pre-trained DINOv2 model loaded successfully!")
        except Exception as e:
            print(f"\n[NOTE] Internet Off or Download error ({e}). Using Self-Contained Offline Spatial CNN Encoder...")
            self.backbone = nn.Sequential(
                nn.Conv2d(in_channels, 64, kernel_size=7, stride=2, padding=3),
                nn.BatchNorm2d(64),
                nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
                nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
                nn.BatchNorm2d(128),
                nn.ReLU(inplace=True),
                nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
                nn.BatchNorm2d(256),
                nn.ReLU(inplace=True),
                nn.Conv2d(256, out_dim, kernel_size=3, stride=2, padding=1),
                nn.BatchNorm2d(out_dim),
                nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool2d((1, 1)),
                nn.Flatten()
            )
            
    def forward(self, x):
        if self.is_hub_model:
            x3 = self.input_proj(x)
            with torch.no_grad():
                feat = self.backbone(x3)
        else:
            feat = self.backbone(x)
        return feat

# ===============================================================================
# 4. HYBRID SPATIAL + TABULAR MATCHUP PREDICTOR
# ===============================================================================
class HybridSpatialMatchupPredictor(nn.Module):
    def __init__(self, in_dim=384, tab_dim=8, hidden_dim=256, num_classes=3):
        super().__init__()
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=in_dim, nhead=4, batch_first=True)
        self.temporal_transformer = nn.TransformerEncoder(encoder_layer, num_layers=2)
        self.cross_attn = nn.MultiheadAttention(embed_dim=in_dim, num_heads=4, batch_first=True)
        
        self.tabular_encoder = nn.Sequential(
            nn.Linear(tab_dim, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Dropout(0.2)
        )
        
        fused_in_dim = in_dim * 3 + 64
        self.fc = nn.Sequential(
            nn.Linear(fused_in_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes)
        )
        
    def forward(self, seq_home, seq_away, tab_feats):
        h_home = self.temporal_transformer(seq_home)
        h_away = self.temporal_transformer(seq_away)
        
        u_home = torch.mean(h_home, dim=1)
        u_away = torch.mean(h_away, dim=1)
        
        attn_out, _ = self.cross_attn(query=h_home, key=h_away, value=h_away)
        u_matchup = torch.mean(attn_out, dim=1)
        
        tab_emb = self.tabular_encoder(tab_feats)
        fused = torch.cat([u_home, u_away, u_matchup, tab_emb], dim=1)
        logits = self.fc(fused)
        return logits

# ===============================================================================
# SMART DATASET RESOLVER (PREVENTS IsADirectoryError)
# ===============================================================================
def resolve_csv_filepath(path_input):
    if os.path.isfile(path_input) and path_input.endswith('.csv'):
        return path_input
        
    if os.path.isdir(path_input):
        for root, dirs, files in os.walk(path_input):
            for file in files:
                if file.endswith('.csv'):
                    resolved = os.path.join(root, file)
                    print(f"[AUTO-DETECT] Detected CSV file in directory: '{resolved}'")
                    return resolved
                    
    # Scan /kaggle/input/ for any csv file
    if os.path.exists("/kaggle/input"):
        for root, dirs, files in os.walk("/kaggle/input"):
            for file in files:
                if file.endswith('.csv') and 'spatial' in file.lower():
                    resolved = os.path.join(root, file)
                    print(f"[AUTO-DETECT] Detected CSV file in /kaggle/input: '{resolved}'")
                    return resolved
                    
    if os.path.exists("kaggle_spatial_match_dataset.csv"):
        return "kaggle_spatial_match_dataset.csv"
        
    return path_input

# ===============================================================================
# 5. KAGGLE EXECUTION & 5-FOLD CROSS-VALIDATION LOOP
# ===============================================================================
def run_kaggle_pipeline(dataset_path="/kaggle/input/datasets/ralfo31/kaggle-spatial-match-dataset"):
    print("\n--- 2. Resolving Dataset File Path ---")
    final_path = resolve_csv_filepath(dataset_path)
    
    if not os.path.isfile(final_path):
        print(f"Error: Could not locate a valid .csv file from '{dataset_path}'.")
        return
        
    df = pd.read_csv(final_path)
    print(f"Loaded {len(df)} match records from '{final_path}'.")
    
    extractor = DINOv2SpatialExtractor().to(device)
    extractor.eval()
    
    print("\n--- 3. Extracting Spatial & Tabular Embeddings ---")
    match_embeddings = []
    start_time = time.time()
    
    tabular_cols = [
        'elo_diff', 'rest_diff', 'home_goals_roll15', 'away_goals_roll15',
        'home_xg_roll15', 'away_xg_roll15', 'finishing_eff_diff', 'value_rank_diff'
    ]
    
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing Heatmaps"):
        h_x = json.loads(row['home_x_coords'])
        h_y = json.loads(row['home_y_coords'])
        a_x = json.loads(row['away_x_coords'])
        a_y = json.loads(row['away_y_coords'])
        
        t_home = rasterize_heatmap_tensor(h_x, h_y)
        t_away = rasterize_heatmap_tensor(a_x, a_y)
        
        tensor_batch = torch.tensor(np.stack([t_home, t_away]), dtype=torch.float32).to(device)
        with torch.no_grad():
            feats = extractor(tensor_batch)
            
        tab_vector = row[tabular_cols].values.astype(np.float32)
        
        match_embeddings.append({
            'home_team': row['home_team'],
            'away_team': row['away_team'],
            'outcome': int(row['outcome']),
            'h_feat': feats[0].cpu().numpy(),
            'a_feat': feats[1].cpu().numpy(),
            'tab_feat': tab_vector
        })
        
    print(f"Extracted spatial & tabular features for {len(match_embeddings)} matches in {round(time.time() - start_time, 2)} seconds!")
    
    print("\n--- 4. Constructing 5-Match Trajectory Sequences ---")
    X_home_seq = []
    X_away_seq = []
    X_tabular = []
    y_labels = []
    
    in_dim = match_embeddings[0]['h_feat'].shape[0]
    
    for i in range(5, len(match_embeddings)):
        h_seq = [match_embeddings[j]['h_feat'] for j in range(i-5, i)]
        a_seq = [match_embeddings[j]['a_feat'] for j in range(i-5, i)]
        
        X_home_seq.append(h_seq)
        X_away_seq.append(a_seq)
        X_tabular.append(match_embeddings[i]['tab_feat'])
        y_labels.append(match_embeddings[i]['outcome'])
        
    X_home = np.array(X_home_seq, dtype=np.float32)
    X_away = np.array(X_away_seq, dtype=np.float32)
    X_tab = np.array(X_tabular, dtype=np.float32)
    y = np.array(y_labels, dtype=np.int64)
    
    print(f"Created {len(y)} hybrid sequence-tabular training pairs.")
    
    print("\n--- 5. Training HybridSpatialMatchupPredictor with 5-Fold Cross-Validation ---")
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    fold_accuracies = []
    fold_log_losses = []
    
    for fold, (train_idx, val_idx) in enumerate(kf.split(X_home)):
        scaler = StandardScaler()
        X_tab_tr = scaler.fit_transform(X_tab[train_idx])
        X_tab_va = scaler.transform(X_tab[val_idx])
        
        h_tr, h_va = torch.tensor(X_home[train_idx]).to(device), torch.tensor(X_home[val_idx]).to(device)
        a_tr, a_va = torch.tensor(X_away[train_idx]).to(device), torch.tensor(X_away[val_idx]).to(device)
        t_tr, t_va = torch.tensor(X_tab_tr, dtype=torch.float32).to(device), torch.tensor(X_tab_va, dtype=torch.float32).to(device)
        y_tr, y_va = torch.tensor(y[train_idx]).to(device), torch.tensor(y[val_idx]).to(device)
        
        model = HybridSpatialMatchupPredictor(in_dim=in_dim, tab_dim=8, hidden_dim=256, num_classes=3).to(device)
        optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
        criterion = nn.CrossEntropyLoss()
        
        model.train()
        for epoch in range(35):
            optimizer.zero_grad()
            logits = model(h_tr, a_tr, t_tr)
            loss = criterion(logits, y_tr)
            loss.backward()
            optimizer.step()
            
        model.eval()
        with torch.no_grad():
            val_logits = model(h_va, a_va, t_va)
            probs = torch.softmax(val_logits, dim=1).cpu().numpy()
            preds = np.argmax(probs, axis=1)
            y_true = y[val_idx]
            
            acc = accuracy_score(y_true, preds)
            loss_val = log_loss(y_true, probs, labels=[0, 1, 2])
            
            fold_accuracies.append(acc)
            fold_log_losses.append(loss_val)
            print(f"  Fold {fold+1} Validation Accuracy: {acc*100:.2f}% | Log Loss: {loss_val:.4f}")
            
    print("\n==================== HYBRID OPTIMIZATION 1 RESULTS ====================")
    print(f"Mean 5-Fold Cross-Validation Accuracy: {np.mean(fold_accuracies)*100:.2f}% (± {np.std(fold_accuracies)*100:.2f}%)")
    print(f"Mean 5-Fold Cross-Validation Log Loss: {np.mean(fold_log_losses):.4f}")
    print("=======================================================================")

if __name__ == "__main__":
    run_kaggle_pipeline("/kaggle/input/datasets/ralfo31/kaggle-spatial-match-dataset")
