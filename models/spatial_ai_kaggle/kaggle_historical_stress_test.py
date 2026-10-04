"""
===============================================================================
KAGGLE NOTEBOOK: Out-of-Sample Historical Stress Test (Bundesliga 2015–2019)
===============================================================================
Trains 2-Stage Spatial AI Model on Primary Data and evaluates ZERO-SHOT 
(0 retraining) on completely unseen historical seasons (2015/16 through 2018/19).
===============================================================================
Hardware Accelerator: GPU (NVIDIA T4 / P100 recommended)
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

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Kaggle Compute Device: {device}")

# ===============================================================================
# 1. MULTI-CHANNEL GAUSSIAN KDE RASTERIZER (224x224x4 TENSORS)
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
# 2. DINOv2 SPATIAL BACKBONE
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
                nn.BatchNorm2d(64), nn.ReLU(inplace=True),
                nn.MaxPool2d(kernel_size=3, stride=2, padding=1),
                nn.Conv2d(64, 128, kernel_size=3, stride=2, padding=1),
                nn.BatchNorm2d(128), nn.ReLU(inplace=True),
                nn.Conv2d(128, 256, kernel_size=3, stride=2, padding=1),
                nn.BatchNorm2d(256), nn.ReLU(inplace=True),
                nn.Conv2d(256, out_dim, kernel_size=3, stride=2, padding=1),
                nn.BatchNorm2d(out_dim), nn.ReLU(inplace=True),
                nn.AdaptiveAvgPool2d((1, 1)), nn.Flatten()
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
# 3. STAGE 1: 1D TEMPORAL ATTENTION LATENT GENERATOR ARCHITECTURE
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
# SMART DATASET RESOLVER
# ===============================================================================
def find_csv_file(keyword):
    if os.path.exists("/kaggle/input"):
        for root, dirs, files in os.walk("/kaggle/input"):
            for file in files:
                if file.endswith('.csv') and keyword.lower() in file.lower():
                    return os.path.join(root, file)
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith('.csv') and keyword.lower() in file.lower():
                return os.path.join(root, file)
    return None

def extract_dataset_embeddings_batched(df, extractor, tabular_cols, batch_size=64, desc="Processing"):
    embeddings = []
    num_samples = len(df)
    
    for start_idx in range(0, num_samples, batch_size):
        end_idx = min(start_idx + batch_size, num_samples)
        batch_df = df.iloc[start_idx:end_idx]
        
        tensors_h, tensors_a, tab_vectors, outcomes, seasons, elo_diffs = [], [], [], [], [], []
        
        for idx, row in batch_df.iterrows():
            h_x, h_y = json.loads(row['home_x_coords']), json.loads(row['home_y_coords'])
            a_x, a_y = json.loads(row['away_x_coords']), json.loads(row['away_y_coords'])
            tensors_h.append(rasterize_heatmap_tensor(h_x, h_y))
            tensors_a.append(rasterize_heatmap_tensor(a_x, a_y))
            tab_vectors.append(row[tabular_cols].values.astype(np.float32))
            outcomes.append(int(row['outcome']))
            seasons.append(row.get('season', 'Unknown'))
            elo_diffs.append(row.get('elo_diff', 0.0))
            
        tensors_h_stack = torch.tensor(np.stack(tensors_h), dtype=torch.float32).to(device)
        tensors_a_stack = torch.tensor(np.stack(tensors_a), dtype=torch.float32).to(device)
        with torch.no_grad():
            feats_h = extractor(tensors_h_stack).cpu().numpy()
            feats_a = extractor(tensors_a_stack).cpu().numpy()
            
        for i in range(len(batch_df)):
            m_id = batch_df.iloc[i].get('match_id', start_idx + i)
            embeddings.append({
                'match_id': m_id,
                'season': seasons[i], 'h_feat': feats_h[i], 'a_feat': feats_a[i],
                'tab_feat': tab_vectors[i], 'outcome': outcomes[i], 'elo_diff': elo_diffs[i]
            })
    return embeddings

# ===============================================================================
# 4. KAGGLE OUT-OF-SAMPLE HISTORICAL STRESS TEST (2015–2019)
# ===============================================================================
def run_kaggle_historical_test():
    print("\n=======================================================================")
    print("  KAGGLE OUT-OF-SAMPLE STRESS TEST: BUNDESLIGA 2015–2019 (1,224 MATCHES)  ")
    print("=======================================================================")
    
    train_csv = find_csv_file("spatial_match_dataset") or find_csv_file("kaggle_spatial")
    test_csv = find_csv_file("2015_2019") or find_csv_file("historical_spatial")
    
    if not train_csv:
        print("Error: Could not locate primary training CSV file.")
        return
    if not test_csv:
        print("Error: Could not locate historical test CSV file (2015-2019).")
        return
        
    print(f"Loaded Primary Training CSV: '{train_csv}'")
    print(f"Loaded Historical Test CSV:     '{test_csv}'")
    
    df_train = pd.read_csv(train_csv)
    df_test = pd.read_csv(test_csv)
    
    extractor = DINOv2SpatialExtractor().to(device)
    extractor.eval()
    
    tabular_cols = [
        'elo_diff', 'rest_diff', 'home_goals_roll15', 'away_goals_roll15',
        'home_xg_roll15', 'away_xg_roll15', 'finishing_eff_diff', 'value_rank_diff'
    ]
    
    print("\n--- Step 1: Extracting Spatial Embeddings for Primary Training Data ---")
    start_time = time.time()
    train_embeddings = extract_dataset_embeddings_batched(df_train, extractor, tabular_cols, batch_size=64, desc="Train Embeddings")
    print(f"Extracted train features for {len(train_embeddings)} matches in {round(time.time() - start_time, 2)}s.")
    
    X_tr_h_seq, X_tr_a_seq, X_tr_tab = [], [], []
    y_tr_tgt_h, y_tr_tgt_a, y_tr_outcomes = [], [], []
    
    for i in range(5, len(train_embeddings)):
        X_tr_h_seq.append([train_embeddings[j]['h_feat'] for j in range(i-5, i)])
        X_tr_a_seq.append([train_embeddings[j]['a_feat'] for j in range(i-5, i)])
        X_tr_tab.append(train_embeddings[i]['tab_feat'])
        y_tr_tgt_h.append(train_embeddings[i]['h_feat'])
        y_tr_tgt_a.append(train_embeddings[i]['a_feat'])
        y_tr_outcomes.append(train_embeddings[i]['outcome'])
        
    X_tr_h = np.array(X_tr_h_seq, dtype=np.float32)
    X_tr_a = np.array(X_tr_a_seq, dtype=np.float32)
    X_tr_tb = np.array(X_tr_tab, dtype=np.float32)
    Y_tr_tgt_h = np.array(y_tr_tgt_h, dtype=np.float32)
    Y_tr_tgt_a = np.array(y_tr_tgt_a, dtype=np.float32)
    y_train = np.array(y_tr_outcomes, dtype=np.int64)
    
    # Train Stage 1 Latent Generator on Primary Data
    print("\n--- Step 2: Training Stage 1 Latent Generator on Primary Data ---")
    generator = MatchupSpatialGenerator(spatial_dim=384, tab_dim=8).to(device)
    optimizer = optim.AdamW(generator.parameters(), lr=1e-3, weight_decay=1e-4)
    
    h_tr_t = torch.tensor(X_tr_h).to(device)
    a_tr_t = torch.tensor(X_tr_a).to(device)
    t_tr_t = torch.tensor(X_tr_tb).to(device)
    yh_tr_t = torch.tensor(Y_tr_tgt_h).to(device)
    ya_tr_t = torch.tensor(Y_tr_tgt_a).to(device)
    
    generator.train()
    for epoch in range(30):
        optimizer.zero_grad()
        pred_h, pred_a = generator(h_tr_t, a_tr_t, t_tr_t)
        loss = CosineMSELoss(pred_h, yh_tr_t) + CosineMSELoss(pred_a, ya_tr_t)
        loss.backward()
        optimizer.step()
        
    generator.eval()
    with torch.no_grad():
        gen_h_tr, gen_a_tr = generator(h_tr_t, a_tr_t, t_tr_t)
        gen_h_tr, gen_a_tr = gen_h_tr.cpu().numpy(), gen_a_tr.cpu().numpy()
        
    inter_tr = gen_h_tr * gen_a_tr
    X_stage2_train = np.hstack([gen_h_tr, gen_a_tr, inter_tr, X_tr_tb])
    
    scaler = StandardScaler()
    X_stage2_train_scaled = scaler.fit_transform(X_stage2_train)
    
    print("--- Step 3: Training Stage 2 HistGradientBoostingClassifier ---")
    clf = HistGradientBoostingClassifier(
        max_iter=150,
        learning_rate=0.05,
        max_leaf_nodes=31,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=42
    )
    clf.fit(X_stage2_train_scaled, y_train)
    print("SUCCESS: 2-Stage Model trained and ready for Zero-Shot testing!")
    
    # 2. Process completely UNSEEN 2015-2019 Historical Test Dataset
    print("\n--- Step 4: Extracting Spatial Embeddings for Unseen 2015-2019 Test Data ---")
    start_time = time.time()
    test_embeddings = extract_dataset_embeddings_batched(df_test, extractor, tabular_cols, batch_size=64, desc="Test Embeddings")
    print(f"Extracted test features for {len(test_embeddings)} matches in {round(time.time() - start_time, 2)}s.")
    
    X_te_h_seq, X_te_a_seq, X_te_tab = [], [], []
    test_seasons, test_outcomes, test_elo_diffs = [], [], []
    
    for i in range(5, len(test_embeddings)):
        X_te_h_seq.append([test_embeddings[j]['h_feat'] for j in range(i-5, i)])
        X_te_a_seq.append([test_embeddings[j]['a_feat'] for j in range(i-5, i)])
        X_te_tab.append(test_embeddings[i]['tab_feat'])
        test_seasons.append(test_embeddings[i]['season'])
        test_outcomes.append(test_embeddings[i]['outcome'])
        test_elo_diffs.append(test_embeddings[i]['elo_diff'])
        
    X_te_h = np.array(X_te_h_seq, dtype=np.float32)
    X_te_a = np.array(X_te_a_seq, dtype=np.float32)
    X_te_tb = np.array(X_te_tab, dtype=np.float32)
    y_test = np.array(test_outcomes, dtype=np.int64)
    test_seasons = np.array(test_seasons)
    
    # 3. ZERO-SHOT INFERENCE ON UNSEEN DATA
    print("\n--- Step 5: Running Zero-Shot Inference on 2015-2019 Historical Data ---")
    h_te_t = torch.tensor(X_te_h).to(device)
    a_te_t = torch.tensor(X_te_a).to(device)
    t_te_t = torch.tensor(X_te_tb).to(device)
    
    with torch.no_grad():
        gen_h_te, gen_a_te = generator(h_te_t, a_te_t, t_te_t)
        gen_h_te, gen_a_te = gen_h_te.cpu().numpy(), gen_a_te.cpu().numpy()
        
    inter_te = gen_h_te * gen_a_te
    X_stage2_test = np.hstack([gen_h_te, gen_a_te, inter_te, X_te_tb])
    X_stage2_test_scaled = scaler.transform(X_stage2_test)
    
    probs_test = clf.predict_proba(X_stage2_test_scaled)
    preds_test = np.argmax(probs_test, axis=1)
    
    overall_acc = accuracy_score(y_test, preds_test)
    overall_loss = log_loss(y_test, probs_test, labels=[0, 1, 2])
    
    # Baseline Elo-only prediction comparison
    elo_preds = []
    for ed in test_elo_diffs:
        p_h = 1.0 / (1.0 + 10.0 ** (-(ed + 100.0) / 400.0))
        p_a = 1.0 / (1.0 + 10.0 ** ((ed - 100.0) / 400.0))
        p_d = max(0.05, 1.0 - p_h - p_a)
        elo_preds.append(np.argmax([p_h, p_d, p_a]))
        
    elo_acc = accuracy_score(y_test, elo_preds)
    
    print("\n=======================================================================")
    print("    OUT-OF-SAMPLE STRESS TEST RESULTS (UNSEEN BUNDESLIGA 2015–2019)    ")
    print("=======================================================================")
    print(f"Overall 2-Stage Model Accuracy:  {overall_acc*100:.2f}%")
    print(f"Overall 2-Stage Model Log Loss:  {overall_loss:.4f}")
    print(f"Baseline Elo-Only Accuracy:      {elo_acc*100:.2f}%")
    print(f"Net Accuracy Gain over Elo:     +{overall_acc*100 - elo_acc*100:.2f}%")
    print("-----------------------------------------------------------------------")
    print("\n--- Season-by-Season Out-of-Sample Performance Breakdown ---")
    
    unique_seasons = sorted(list(set(test_seasons)))
    for s in unique_seasons:
        mask = (test_seasons == s)
        s_y = y_test[mask]
        s_pred = preds_test[mask]
        s_prob = probs_test[mask]
        s_acc = accuracy_score(s_y, s_pred)
        s_loss = log_loss(s_y, s_prob, labels=[0, 1, 2])
        print(f"  Season {s}: Accuracy = {s_acc*100:.2f}% | Log Loss = {s_loss:.4f} (Matches: {len(s_y)})")
        
    print("=======================================================================\n")

if __name__ == "__main__":
    run_kaggle_historical_test()
