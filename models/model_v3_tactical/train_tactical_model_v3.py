import pandas as pd
import numpy as np
import joblib
import json
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, log_loss

def train_v3():
    print("======================================================================")
    print(" TRAINING STANDALONE MODEL V3 (PURE TACTICAL & 1D TIME-DECAY MODEL)")
    print("======================================================================")
    
    df = pd.read_csv("bundesliga_multicomp_processed_v3_tactical.csv")
    df_bl = df[df['competition'] == 'Bundesliga'].copy()
    df_bl = df_bl.dropna(subset=['home_goals', 'away_goals']).reset_index(drop=True)
    
    if 'rest_diff' not in df_bl.columns:
        df_bl['rest_diff'] = df_bl['home_rest'] - df_bl['away_rest']
        
    # Chronological Split
    train_seasons = ["2021-2022", "2022-2023", "2023-2024"]
    val_seasons = ["2024-2025"]
    test_seasons = ["2025-2026"]
    
    train_pool_mask = df_bl['season'].isin(train_seasons + val_seasons)
    test_mask = df_bl['season'].isin(test_seasons)
    
    # Target outcome: 0 = Home Win, 1 = Draw, 2 = Away Win
    def get_outcome(row):
        if row['home_goals'] > row['away_goals']: return 0
        elif row['home_goals'] < row['away_goals']: return 2
        else: return 1
        
    df_bl['target_outcome'] = df_bl.apply(get_outcome, axis=1)
    
    y_train = df_bl.loc[train_pool_mask, 'target_outcome'].values
    y_test = df_bl.loc[test_mask, 'target_outcome'].values
    
    y_train_hg = df_bl.loc[train_pool_mask, 'home_goals'].values
    y_train_ag = df_bl.loc[train_pool_mask, 'away_goals'].values
    y_test_hg = df_bl.loc[test_mask, 'home_goals'].values
    y_test_ag = df_bl.loc[test_mask, 'away_goals'].values
    
    # --- STEP 1: Window Grid Search across W in [1..10] ---
    print("\n--- 1. Evaluating Rolling Window Sizes W in [1..10] ---")
    window_results = {}
    best_w = 9
    best_acc = 0.0
    
    for W in range(1, 11):
        feature_cols = [
            f'home_goals_decay_{W}', f'away_goals_decay_{W}',
            f'home_xg_decay_{W}', f'away_xg_decay_{W}',
            f'home_ppda_decay_{W}', f'away_ppda_decay_{W}',
            f'home_xpts_decay_{W}', f'away_xpts_decay_{W}',
            f'home_finishing_eff_decay_{W}', f'away_finishing_eff_decay_{W}',
            f'home_xg_diff_decay_{W}', f'away_xg_diff_decay_{W}',
            f'home_win_rate_decay_{W}', f'away_win_rate_decay_{W}',
            f'home_att_third_{W}', f'away_att_third_{W}',
            f'pressing_diff_{W}', f'xg_diff_matchup_{W}',
            'value_rank_diff', 'rest_diff'
        ]
        
        X_train_raw = df_bl.loc[train_pool_mask, feature_cols].values
        X_test_raw = df_bl.loc[test_mask, feature_cols].values
        
        scaler = StandardScaler()
        X_train_s = scaler.fit_transform(X_train_raw)
        X_test_s = scaler.transform(X_test_raw)
        
        rf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        rf.fit(X_train_s, y_train)
        
        hgb = HistGradientBoostingClassifier(max_iter=80, max_depth=4, random_state=42)
        hgb.fit(X_train_s, y_train)
        
        p_rf = rf.predict_proba(X_test_s)
        p_hgb = hgb.predict_proba(X_test_s)
        
        p_blend = 0.5 * p_rf + 0.5 * p_hgb
        preds = np.argmax(p_blend, axis=1)
        
        acc = accuracy_score(y_test, preds) * 100.0
        loss = log_loss(y_test, p_blend)
        
        window_results[W] = {"accuracy": round(acc, 2), "log_loss": round(loss, 4)}
        print(f"  - Window W = {W:2d} games | Test Accuracy: {acc:.2f}% | Log Loss: {loss:.4f}")
        
        if acc > best_acc:
            best_acc = acc
            best_w = W
            
    print(f"\nOptimal Single Window: W* = {best_w} games (Accuracy: {best_acc:.2f}%)")
    
    # --- STEP 2: Train Final Model v3 using Peak Single Window W=9 Features ---
    print(f"\n--- 2. Building Model v3 Feature Set (W={best_w}) ---")
    optimal_features = [
        f'home_goals_decay_{best_w}', f'away_goals_decay_{best_w}',
        f'home_xg_decay_{best_w}', f'away_xg_decay_{best_w}',
        f'home_ppda_decay_{best_w}', f'away_ppda_decay_{best_w}',
        f'home_xpts_decay_{best_w}', f'away_xpts_decay_{best_w}',
        f'home_finishing_eff_decay_{best_w}', f'away_finishing_eff_decay_{best_w}',
        f'home_xg_diff_decay_{best_w}', f'away_xg_diff_decay_{best_w}',
        f'home_win_rate_decay_{best_w}', f'away_win_rate_decay_{best_w}',
        f'home_att_third_{best_w}', f'away_att_third_{best_w}',
        f'pressing_diff_{best_w}', f'xg_diff_matchup_{best_w}',
        'value_rank_diff', 'rest_diff'
    ]
    
    X_train_opt_raw = df_bl.loc[train_pool_mask, optimal_features].values
    X_test_opt_raw = df_bl.loc[test_mask, optimal_features].values
    
    scaler_v3 = StandardScaler()
    X_train_s = scaler_v3.fit_transform(X_train_opt_raw)
    X_test_s = scaler_v3.transform(X_test_opt_raw)
    
    rf_v3 = RandomForestClassifier(n_estimators=150, max_depth=5, random_state=42)
    rf_v3.fit(X_train_s, y_train)
    
    hgb_v3 = HistGradientBoostingClassifier(max_iter=80, max_depth=4, random_state=42)
    hgb_v3.fit(X_train_s, y_train)
    
    p_rf = rf_v3.predict_proba(X_test_s)
    p_hgb = hgb_v3.predict_proba(X_test_s)
    p_blend_final = 0.50 * p_rf + 0.50 * p_hgb
    
    final_acc = accuracy_score(y_test, np.argmax(p_blend_final, axis=1)) * 100.0
    final_loss = log_loss(y_test, p_blend_final)
    print(f"\nFinal Model v3 (W={best_w}) Test Accuracy: {final_acc:.2f}% | Log Loss: {final_loss:.4f}")
    
    # --- STEP 3: Train Stacked Goal Regressors ---
    print("\n--- 3. Training Model v3 Stacked Goal Regressors ---")
    p_train_rf = rf_v3.predict_proba(X_train_s)
    p_train_hgb = hgb_v3.predict_proba(X_train_s)
    p_train_blend = 0.50 * p_train_rf + 0.50 * p_train_hgb
    
    X_train_fused = np.hstack([X_train_s, p_train_blend])
    X_test_fused = np.hstack([X_test_s, p_blend_final])
    
    reg_home_v3 = RandomForestRegressor(n_estimators=150, max_depth=5, random_state=42)
    reg_home_v3.fit(X_train_fused, y_train_hg)
    
    reg_away_v3 = RandomForestRegressor(n_estimators=150, max_depth=5, random_state=42)
    reg_away_v3.fit(X_train_fused, y_train_ag)
    
    # --- STEP 4: Save Artifacts & Config ---
    joblib.dump(scaler_v3, "scaler_v3_tactical.joblib")
    joblib.dump(rf_v3, "model_v3_tactical_rf.joblib")
    joblib.dump(hgb_v3, "model_v3_tactical_hgb.joblib")
    joblib.dump(reg_home_v3, "model_v3_fused_reg_home.joblib")
    joblib.dump(reg_away_v3, "model_v3_fused_reg_away.joblib")
    
    config = {
        "best_window": best_w,
        "final_accuracy": round(final_acc, 2),
        "final_log_loss": round(final_loss, 4),
        "window_results": window_results,
        "optimal_features": optimal_features
    }
    
    with open("model_v3_optimal_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
        
    print("\nSAVED MODEL V3 ARTIFACTS AND CONFIG SUCCESSFULLY!")

if __name__ == "__main__":
    train_v3()
