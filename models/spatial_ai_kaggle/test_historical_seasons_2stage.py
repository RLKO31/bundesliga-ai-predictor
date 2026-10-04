"""
===============================================================================
FAST ZERO-SHOT OUT-OF-SAMPLE STRESS TEST: BUNDESLIGA 2015–2019 SEASONS
===============================================================================
Evaluates our existing 2-Stage Spatial AI Model (Stage 1 Latent Generator + 
Stage 2 HistGBDT) on completely unseen historical Bundesliga seasons 
(2015/16, 2016/17, 2017/18, 2018/19 — 1,224 matches) WITHOUT retraining.
===============================================================================
"""

import os
import json
import time
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss

import torch
import torch.nn as nn
import torch.optim as optim

# Import Stage 1 Generator module
from train_stage1_latent_generator import MatchupSpatialGenerator, CosineMSELoss
from kaggle_2stage_spatial_pipeline import rasterize_heatmap_tensor

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Fast Spatial CNN Encoder for ultra-fast local CPU execution
class FastSpatialEncoder(nn.Module):
    def __init__(self, in_channels=4, out_dim=384):
        super().__init__()
        self.backbone = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=5, stride=2, padding=2),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Conv2d(32, 64, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, out_dim, kernel_size=3, stride=2, padding=1),
            nn.BatchNorm2d(out_dim),
            nn.ReLU(inplace=True),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten()
        )
    def forward(self, x):
        return self.backbone(x)

def extract_dataset_embeddings_batched(df, extractor, tabular_cols, batch_size=128):
    embeddings = []
    num_samples = len(df)
    
    for start_idx in range(0, num_samples, batch_size):
        end_idx = min(start_idx + batch_size, num_samples)
        batch_df = df.iloc[start_idx:end_idx]
        
        tensors_h, tensors_a, tab_vectors, outcomes, seasons, elo_diffs = [], [], [], [], [], []
        
        for idx, row in batch_df.iterrows():
            h_x, h_y = json.loads(row['home_x_coords']), json.loads(row['home_y_coords'])
            a_x, a_y = json.loads(row['away_x_coords']), json.loads(row['away_y_coords'])
            
            t_home = rasterize_heatmap_tensor(h_x, h_y)
            t_away = rasterize_heatmap_tensor(a_x, a_y)
            
            tensors_h.append(t_home)
            tensors_a.append(t_away)
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
            embeddings.append({
                'season': seasons[i],
                'h_feat': feats_h[i],
                'a_feat': feats_a[i],
                'tab_feat': tab_vectors[i],
                'outcome': outcomes[i],
                'elo_diff': elo_diffs[i]
            })
            
    return embeddings

def run_out_of_sample_historical_test():
    print("\n=======================================================================")
    print("      OUT-OF-SAMPLE STRESS TEST: BUNDESLIGA 2015–2019 (1,224 MATCHES)   ")
    print("=======================================================================")
    
    train_csv = "models/spatial_ai_kaggle/kaggle_spatial_match_dataset.csv"
    if not os.path.exists(train_csv):
        train_csv = "data/kaggle_spatial_match_dataset.csv"
        
    print(f"--- 1. Training Baseline 2-Stage Model on Primary Training Data ({train_csv}) ---")
    df_train = pd.read_csv(train_csv)
    print(f"Loaded {len(df_train)} primary training match samples.")
    
    extractor = FastSpatialEncoder().to(device)
    extractor.eval()
    
    tabular_cols = [
        'elo_diff', 'rest_diff', 'home_goals_roll15', 'away_goals_roll15',
        'home_xg_roll15', 'away_xg_roll15', 'finishing_eff_diff', 'value_rank_diff'
    ]
    
    start_time = time.time()
    train_embeddings = extract_dataset_embeddings_batched(df_train, extractor, tabular_cols, batch_size=128)
    print(f"Extracted train features for {len(df_train)} matches in {round(time.time() - start_time, 2)}s.")
    
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
    print("Training Stage 1 Latent Generator on primary data...")
    generator = MatchupSpatialGenerator(spatial_dim=384, tab_dim=8).to(device)
    optimizer = optim.AdamW(generator.parameters(), lr=1e-3, weight_decay=1e-4)
    
    h_tr_t = torch.tensor(X_tr_h).to(device)
    a_tr_t = torch.tensor(X_tr_a).to(device)
    t_tr_t = torch.tensor(X_tr_tb).to(device)
    yh_tr_t = torch.tensor(Y_tr_tgt_h).to(device)
    ya_tr_t = torch.tensor(Y_tr_tgt_a).to(device)
    
    generator.train()
    for epoch in range(25):
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
    
    clf = HistGradientBoostingClassifier(
        max_iter=150,
        learning_rate=0.05,
        max_leaf_nodes=31,
        min_samples_leaf=20,
        l2_regularization=1.0,
        random_state=42
    )
    clf.fit(X_stage2_train_scaled, y_train)
    print("SUCCESS: 2-Stage Model trained and ready for Out-of-Sample testing!")
    
    # 2. Load completely UNSEEN 2015-2019 Historical Test Dataset
    test_csv = "data/historical_spatial_2015_2019.csv"
    print(f"\n--- 2. Loading Unseen 2015-2019 Historical Test Dataset ({test_csv}) ---")
    df_test = pd.read_csv(test_csv)
    print(f"Loaded {len(df_test)} unseen historical matches across 4 seasons (2015–2019).")
    
    start_time = time.time()
    test_embeddings = extract_dataset_embeddings_batched(df_test, extractor, tabular_cols, batch_size=128)
    print(f"Extracted test features for {len(df_test)} matches in {round(time.time() - start_time, 2)}s.")
    
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
    print("\n--- 3. Running Zero-Shot Inference on 2015-2019 Historical Data ---")
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
    run_out_of_sample_historical_test()
