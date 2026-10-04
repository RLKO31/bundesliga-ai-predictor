"""
===============================================================================
KAGGLE / LOCAL NOTEBOOK: 2-Stage Spatial AI (Generative Latent + HistGBDT)
===============================================================================
Stage 1: 1D Temporal Attention Latent Generator predicts upcoming match DINOv2 
         spatial vectors (z_home, z_away) from 5-match historical sequences.
Stage 2: HistGradientBoostingClassifier evaluates the generated spatial 
         vectors + tabular Elo metrics to forecast match outcomes.
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
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim

# ===============================================================================
# STAGE 1: 1D TEMPORAL ATTENTION LATENT GENERATOR ARCHITECTURE
# ===============================================================================
class TemporalRecencyAttention(nn.Module):
    def __init__(self, embed_dim=384, num_heads=4, seq_len=5):
        super().__init__()
        self.seq_len = seq_len
        self.multihead_attn = nn.MultiheadAttention(embed_dim=embed_dim, num_heads=num_heads, batch_first=True)
        self.norm = nn.LayerNorm(embed_dim)
        decay_weights = np.exp(np.linspace(-0.8, 0.0, seq_len)).astype(np.float32)
        decay_weights = decay_weights / decay_weights.sum()
        self.register_buffer("recency_bias", torch.tensor(decay_weights).unsqueeze(0).unsqueeze(-1))

    def forward(self, x):
        attn_out, attn_weights = self.multihead_attn(x, x, x)
        x_attn = self.norm(x + attn_out)
        weighted_x = x_attn * self.recency_bias
        pooled_representation = torch.sum(weighted_x, dim=1)
        return pooled_representation, attn_weights

class MatchupSpatialGenerator(nn.Module):
    def __init__(self, spatial_dim=384, tab_dim=8, hidden_dim=512):
        super().__init__()
        self.home_temporal_attn = TemporalRecencyAttention(embed_dim=spatial_dim, num_heads=4, seq_len=5)
        self.away_temporal_attn = TemporalRecencyAttention(embed_dim=spatial_dim, num_heads=4, seq_len=5)
        self.tab_encoder = nn.Sequential(
            nn.Linear(tab_dim, 64),
            nn.SiLU(),
            nn.LayerNorm(64)
        )
        in_dim = spatial_dim * 2 + 64
        self.generator_trunk = nn.Sequential(
            nn.Linear(in_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Dropout(0.2)
        )
        self.home_head = nn.Sequential(
            nn.Linear(hidden_dim, spatial_dim),
            nn.LayerNorm(spatial_dim)
        )
        self.away_head = nn.Sequential(
            nn.Linear(hidden_dim, spatial_dim),
            nn.LayerNorm(spatial_dim)
        )

    def forward(self, home_seq, away_seq, tab_context):
        h_spatial_emb, _ = self.home_temporal_attn(home_seq)
        a_spatial_emb, _ = self.away_temporal_attn(away_seq)
        tab_emb = self.tab_encoder(tab_context)
        fused_input = torch.cat([h_spatial_emb, a_spatial_emb, tab_emb], dim=1)
        trunk_out = self.generator_trunk(fused_input)
        pred_h_spatial = h_spatial_emb + self.home_head(trunk_out)
        pred_a_spatial = a_spatial_emb + self.away_head(trunk_out)
        return pred_h_spatial, pred_a_spatial

def CosineMSELoss(pred, target, alpha=0.7):
    mse_loss = nn.MSELoss()(pred, target)
    cos_sim = nn.CosineSimilarity(dim=1)(pred, target)
    cos_loss = 1.0 - torch.mean(cos_sim)
    return alpha * cos_loss + (1.0 - alpha) * mse_loss

# ===============================================================================
# 1. COMPUTE DEVICE SETUP
# ===============================================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

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
# 3. DINOv2 SPATIAL BACKBONE (WITH OFFLINE FALLBACK)
# ===============================================================================
class DINOv2SpatialExtractor(nn.Module):
    def __init__(self, in_channels=4, out_dim=384):
        super().__init__()
        self.is_hub_model = False
        try:
            self.backbone = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')
            self.input_proj = nn.Conv2d(in_channels, 3, kernel_size=1)
            self.is_hub_model = True
            for p in self.backbone.parameters():
                p.requires_grad = False
            print("Loaded pre-trained DINOv2 backbone ('dinov2_vits14')!")
        except Exception as e:
            print(f"[OFFLINE FALLBACK] Using Spatial CNN Encoder ({e})...")
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
# SMART DATASET RESOLVER
# ===============================================================================
def resolve_csv_filepath(path_input):
    if os.path.isfile(path_input) and path_input.endswith('.csv'):
        return path_input
    if os.path.isdir(path_input):
        for root, dirs, files in os.walk(path_input):
            for file in files:
                if file.endswith('.csv'):
                    return os.path.join(root, file)
    if os.path.exists("data/kaggle_spatial_match_dataset.csv"):
        return "data/kaggle_spatial_match_dataset.csv"
    if os.path.exists("kaggle_spatial_match_dataset.csv"):
        return "kaggle_spatial_match_dataset.csv"
    return path_input

# ===============================================================================
# 4. 2-STAGE PIPELINE EXECUTION & 5-FOLD CROSS-VALIDATION
# ===============================================================================
def run_2stage_pipeline(dataset_path="data/kaggle_spatial_match_dataset.csv"):
    print("\n=======================================================================")
    print("      RUNNING 2-STAGE SPATIAL AI PIPELINE (GENERATIVE + HistGBDT)      ")
    print("=======================================================================")
    
    final_path = resolve_csv_filepath(dataset_path)
    if not os.path.isfile(final_path):
        print(f"Error: Could not locate CSV dataset file from '{dataset_path}'.")
        return
        
    df = pd.read_csv(final_path)
    print(f"Loaded {len(df)} match records from '{final_path}'.")
    
    extractor = DINOv2SpatialExtractor().to(device)
    extractor.eval()
    
    tabular_cols = [
        'elo_diff', 'rest_diff', 'home_goals_roll15', 'away_goals_roll15',
        'home_xg_roll15', 'away_xg_roll15', 'finishing_eff_diff', 'value_rank_diff'
    ]
    
    match_embeddings = []
    print("\n--- Step 1: Extracting Spatial & Tabular Embeddings ---")
    start_time = time.time()
    
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
        
        match_id_val = row['match_id'] if 'match_id' in row and not pd.isna(row['match_id']) else idx
        match_embeddings.append({
            'match_id': match_id_val,
            'home_team': row['home_team'],
            'away_team': row['away_team'],
            'outcome': int(row['outcome']),
            'h_feat': feats[0].cpu().numpy(),
            'a_feat': feats[1].cpu().numpy(),
            'tab_feat': tab_vector
        })
        
    print(f"Extracted features for {len(match_embeddings)} matches in {round(time.time() - start_time, 2)}s.")
    
    print("\n--- Step 2: Constructing 5-Match Trajectory Sequences ---")
    X_home_seq, X_away_seq, X_tabular = [], [], []
    y_target_h_spatial, y_target_a_spatial = [], []
    y_outcomes, match_groups = [], []
    
    for i in range(5, len(match_embeddings)):
        h_seq = [match_embeddings[j]['h_feat'] for j in range(i-5, i)]
        a_seq = [match_embeddings[j]['a_feat'] for j in range(i-5, i)]
        
        X_home_seq.append(h_seq)
        X_away_seq.append(a_seq)
        X_tabular.append(match_embeddings[i]['tab_feat'])
        
        y_target_h_spatial.append(match_embeddings[i]['h_feat'])
        y_target_a_spatial.append(match_embeddings[i]['a_feat'])
        y_outcomes.append(match_embeddings[i]['outcome'])
        match_groups.append(match_embeddings[i]['match_id'])
        
    X_home = np.array(X_home_seq, dtype=np.float32)
    X_away = np.array(X_away_seq, dtype=np.float32)
    X_tab = np.array(X_tabular, dtype=np.float32)
    Y_tgt_h = np.array(y_target_h_spatial, dtype=np.float32)
    Y_tgt_a = np.array(y_target_a_spatial, dtype=np.float32)
    y = np.array(y_outcomes, dtype=np.int64)
    groups = np.array(match_groups)
    
    print(f"Constructed {len(y)} sequence-matchup samples across {len(set(groups))} unique match IDs.")
    
    print("\n--- Step 3: Training 2-Stage Pipeline with Strict GroupKFold Cross-Validation ---")
    from sklearn.model_selection import GroupKFold
    gkf = GroupKFold(n_splits=5)
    
    fold_accuracies = []
    fold_log_losses = []
    
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X_home, y, groups=groups)):
        # Train Stage 1 Latent Generator on training fold
        generator = MatchupSpatialGenerator(spatial_dim=384, tab_dim=8).to(device)
        optimizer = optim.AdamW(generator.parameters(), lr=1e-3, weight_decay=1e-4)
        
        h_tr = torch.tensor(X_home[train_idx]).to(device)
        a_tr = torch.tensor(X_away[train_idx]).to(device)
        t_tr = torch.tensor(X_tab[train_idx]).to(device)
        yh_tr = torch.tensor(Y_tgt_h[train_idx]).to(device)
        ya_tr = torch.tensor(Y_tgt_a[train_idx]).to(device)
        
        generator.train()
        for epoch in range(25):
            optimizer.zero_grad()
            pred_h, pred_a = generator(h_tr, a_tr, t_tr)
            loss = CosineMSELoss(pred_h, yh_tr) + CosineMSELoss(pred_a, ya_tr)
            loss.backward()
            optimizer.step()
            
        # Generate predicted spatial latent vectors for train and val sets
        generator.eval()
        with torch.no_grad():
            h_va = torch.tensor(X_home[val_idx]).to(device)
            a_va = torch.tensor(X_away[val_idx]).to(device)
            t_va = torch.tensor(X_tab[val_idx]).to(device)
            
            gen_h_tr, gen_a_tr = generator(h_tr, a_tr, t_tr)
            gen_h_va, gen_a_va = generator(h_va, a_va, t_va)
            
            gen_h_tr, gen_a_tr = gen_h_tr.cpu().numpy(), gen_a_tr.cpu().numpy()
            gen_h_va, gen_a_va = gen_h_va.cpu().numpy(), gen_a_va.cpu().numpy()
            
        # Construct fused 1,160-dim vectors for Stage 2 HistGBDT
        # [generated_h (384), generated_a (384), interaction (384), tabular (8)]
        inter_tr = gen_h_tr * gen_a_tr
        inter_va = gen_h_va * gen_a_va
        
        X_stage2_tr = np.hstack([gen_h_tr, gen_a_tr, inter_tr, X_tab[train_idx]])
        X_stage2_va = np.hstack([gen_h_va, gen_a_va, inter_va, X_tab[val_idx]])
        
        scaler = StandardScaler()
        X_stage2_tr = scaler.fit_transform(X_stage2_tr)
        X_stage2_va = scaler.transform(X_stage2_va)
        
        clf = HistGradientBoostingClassifier(
            max_iter=150,
            learning_rate=0.05,
            max_leaf_nodes=31,
            min_samples_leaf=20,
            l2_regularization=1.0,
            random_state=42
        )
        clf.fit(X_stage2_tr, y[train_idx])
        
        probs = clf.predict_proba(X_stage2_va)
        preds = np.argmax(probs, axis=1)
        
        acc = accuracy_score(y[val_idx], preds)
        loss_val = log_loss(y[val_idx], probs, labels=[0, 1, 2])
        
        fold_accuracies.append(acc)
        fold_log_losses.append(loss_val)
        print(f"  Fold {fold+1} Validation Accuracy: {acc*100:.2f}% | Log Loss: {loss_val:.4f}")
        
    print("\n==================== MODEL V6 (2-STAGE SPATIAL AI) RESULTS ====================")
    print(f"Mean 5-Fold Cross-Validation Accuracy: {np.mean(fold_accuracies)*100:.2f}% (± {np.std(fold_accuracies)*100:.2f}%)")
    print(f"Mean 5-Fold Cross-Validation Log Loss: {np.mean(fold_log_losses):.4f}")
    print("===============================================================================")

if __name__ == "__main__":
    run_2stage_pipeline("data/kaggle_spatial_match_dataset.csv")
