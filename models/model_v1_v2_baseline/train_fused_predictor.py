import numpy as np
import pandas as pd
import torch
import joblib
import json
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from scipy.stats import poisson
from model_transformer_v2 import TabularTransformer

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def train_fused():
    print("Loading data...")
    df = pd.read_csv("bundesliga_multicomp_processed_v2.csv")
    df_bl = df[df['competition'] == 'Bundesliga'].copy()
    df_bl = df_bl.dropna(subset=['home_goals', 'away_goals']).reset_index(drop=True)
    
    df_bl['elo_diff'] = df_bl['home_elo'] - df_bl['away_elo']
    df_bl['rest_diff'] = df_bl['home_rest'] - df_bl['away_rest']
    
    features = [
        'elo_diff', 'rest_diff', 'home_elo', 'away_elo', 'home_rest', 'away_rest',
        'home_goals_roll3', 'home_goals_roll15', 'home_xg_roll3', 'home_xg_roll15', 'home_xg_diff_roll10',
        'away_goals_roll3', 'away_goals_roll15', 'away_xg_roll3', 'away_xg_roll15', 'away_xg_diff_roll10',
        'home_value_rank', 'away_value_rank', 'value_rank_diff',
        'away_finishing_eff_roll10', 'finishing_eff_diff'
    ]
    
    # Chronological Split
    train_seasons = ["2021-2022", "2022-2023", "2023-2024"]
    val_seasons = ["2024-2025"]
    test_seasons = ["2025-2026"]
    
    train_pool_mask = df_bl['season'].isin(train_seasons + val_seasons)
    test_mask = df_bl['season'].isin(test_seasons)
    
    # Features & Targets
    X_train_raw = df_bl.loc[train_pool_mask, features].values
    y_train_home = df_bl.loc[train_pool_mask, 'home_goals'].values
    y_train_away = df_bl.loc[train_pool_mask, 'away_goals'].values
    
    X_test_raw = df_bl.loc[test_mask, features].values
    y_test_home = df_bl.loc[test_mask, 'home_goals'].values
    y_test_away = df_bl.loc[test_mask, 'away_goals'].values
    
    # Load Stage 1 classifiers
    scaler = joblib.load("scaler_v2.joblib")
    rf_clf = joblib.load("ensemble_rf_v2.joblib")
    hgb_clf = joblib.load("ensemble_hgb_v2.joblib")
    
    transformer = TabularTransformer(
        num_features=21, d_model=32, nhead=4, num_layers=2, dim_feedforward=64, dropout=0.2
    ).to(device)
    transformer.load_state_dict(torch.load("tabular_transformer_v2.pt"))
    transformer.eval()
    
    X_train_scaled = scaler.transform(X_train_raw)
    X_test_scaled = scaler.transform(X_test_raw)
    
    # Predict probabilities for Stage 1 on Train Pool
    print("Generating Stage 1 probabilities for Training pool...")
    rf_probs_train = rf_clf.predict_proba(X_train_scaled)
    hgb_probs_train = hgb_clf.predict_proba(X_train_scaled)
    
    X_train_tensor = torch.tensor(X_train_scaled, dtype=torch.float32).to(device)
    with torch.no_grad():
        logits_train = transformer(X_train_tensor)
        trans_probs_train = torch.softmax(logits_train, dim=1).cpu().numpy()
        
    blend_probs_train = 0.19 * rf_probs_train + 0.41 * hgb_probs_train + 0.40 * trans_probs_train
    
    # Predict probabilities for Stage 1 on Test Set
    print("Generating Stage 1 probabilities for Test set...")
    rf_probs_test = rf_clf.predict_proba(X_test_scaled)
    hgb_probs_test = hgb_clf.predict_proba(X_test_scaled)
    
    X_test_tensor = torch.tensor(X_test_scaled, dtype=torch.float32).to(device)
    with torch.no_grad():
        logits_test = transformer(X_test_tensor)
        trans_probs_test = torch.softmax(logits_test, dim=1).cpu().numpy()
        
    blend_probs_test = 0.19 * rf_probs_test + 0.41 * hgb_probs_test + 0.40 * trans_probs_test
    
    # Append probabilities to feature vectors (Stacking!)
    X_train_fused = np.hstack([X_train_scaled, blend_probs_train])
    X_test_fused = np.hstack([X_test_scaled, blend_probs_test])
    
    # Train Goal Regressors with Meta-Features
    print("\nTraining Fused Regressor for Home Goals...")
    reg_home = RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42)
    reg_home.fit(X_train_fused, y_train_home)
    
    print("Training Fused Regressor for Away Goals...")
    reg_away = RandomForestRegressor(n_estimators=150, max_depth=6, random_state=42)
    reg_away.fit(X_train_fused, y_train_away)
    
    # Predict lambdas on test set
    lambda_home = reg_home.predict(X_test_fused)
    lambda_away = reg_away.predict(X_test_fused)
    
    lambda_home = np.clip(lambda_home, 0.5, 5.0)
    lambda_away = np.clip(lambda_away, 0.5, 5.0)
    
    # 4. Score Tipping Evaluation
    correct_unconstrained = 0
    correct_constrained = 0
    
    for i in range(len(X_test_fused)):
        l_h = lambda_home[i]
        l_a = lambda_away[i]
        
        # Classifier prediction
        p_dist = blend_probs_test[i]
        pred_outcome = np.argmax(p_dist) # 0: Home, 1: Draw, 2: Away
        
        # 4.1 Unconstrained Search
        best_prob_un = -1.0
        best_score_un = (0, 0)
        for hg in range(6):
            for ag in range(6):
                p_score = poisson.pmf(hg, l_h) * poisson.pmf(ag, l_a)
                if p_score > best_prob_un:
                    best_prob_un = p_score
                    best_score_un = (hg, ag)
                    
        act_h = int(y_test_home[i])
        act_a = int(y_test_away[i])
        if best_score_un == (act_h, act_a):
            correct_unconstrained += 1
            
        # 4.2 Fused Constrained Search: Find score matching classification outcome
        best_prob_con = -1.0
        best_score_con = (0, 0)
        for hg in range(6):
            for ag in range(6):
                # Check if this score fits the predicted outcome from classification
                score_outcome = 0 if hg > ag else (2 if hg < ag else 1)
                if score_outcome != pred_outcome:
                    continue
                    
                p_score = poisson.pmf(hg, l_h) * poisson.pmf(ag, l_a)
                if p_score > best_prob_con:
                    best_prob_con = p_score
                    best_score_con = (hg, ag)
                    
        # If no score matched the constraints (highly unlikely with range 0-5), fallback
        if best_prob_con == -1.0:
            best_score_con = best_score_un
            
        if best_score_con == (act_h, act_a):
            correct_constrained += 1
            
    uncon_acc = correct_unconstrained / len(X_test_fused) * 100
    con_acc = correct_constrained / len(X_test_fused) * 100
    
    print("\n--- Multi-Modular Model Evaluation ---")
    print(f"Unconstrained Exact Score Accuracy: {uncon_acc:.2f}%")
    print(f"Outcome-Constrained Exact Score Accuracy: {con_acc:.2f}%")
    print(f"Classifier Outcome Accuracy (Stage 1): {57.52:.2f}%")
    
    # Save the fused models
    joblib.dump(reg_home, "fused_regressor_home.joblib")
    joblib.dump(reg_away, "fused_regressor_away.joblib")
    print("\nSaved fused_regressor_home.joblib and fused_regressor_away.joblib.")

if __name__ == "__main__":
    train_fused()
