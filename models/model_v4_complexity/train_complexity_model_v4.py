import pandas as pd
import numpy as np
import json
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold
from sklearn.metrics import r2_score, mean_absolute_error

def train_model_v4():
    print("--- 2. Training Model v4: Early-Season Goal Complexity Predictor ---")
    df = pd.read_csv("bundesliga_first_15_goals_complexity.csv")
    print(f"Loaded {len(df)} team-season samples for training.")
    
    feature_cols = [
        'matches_to_15_goals',
        'goal_tempo',
        'action_complexity_score',
        'avg_xg_per_goal',
        'finishing_delta',
        'assist_entropy',
        'open_play_ratio',
        'counter_ratio',
        'avg_ppda',
        'avg_xpts'
    ]
    
    target_col = 'final_points'
    
    X = df[feature_cols].values
    y = df[target_col].values
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    
    oof_preds_ridge = np.zeros(len(df))
    oof_preds_rf = np.zeros(len(df))
    oof_preds_hgb = np.zeros(len(df))
    
    for train_idx, val_idx in kf.split(X_scaled):
        X_tr, y_tr = X_scaled[train_idx], y[train_idx]
        X_va, y_va = X_scaled[val_idx], y[val_idx]
        
        r_model = Ridge(alpha=2.0)
        r_model.fit(X_tr, y_tr)
        oof_preds_ridge[val_idx] = r_model.predict(X_va)
        
        rf_model = RandomForestRegressor(n_estimators=100, max_depth=4, random_state=42)
        rf_model.fit(X_tr, y_tr)
        oof_preds_rf[val_idx] = rf_model.predict(X_va)
        
        hgb_model = HistGradientBoostingRegressor(max_depth=3, random_state=42)
        hgb_model.fit(X_tr, y_tr)
        oof_preds_hgb[val_idx] = hgb_model.predict(X_va)
        
    oof_blend = 0.40 * oof_preds_ridge + 0.35 * oof_preds_rf + 0.25 * oof_preds_hgb
    
    r2_ridge = r2_score(y, oof_preds_ridge)
    mae_ridge = mean_absolute_error(y, oof_preds_ridge)
    
    r2_rf = r2_score(y, oof_preds_rf)
    mae_rf = mean_absolute_error(y, oof_preds_rf)
    
    r2_hgb = r2_score(y, oof_preds_hgb)
    mae_hgb = mean_absolute_error(y, oof_preds_hgb)
    
    r2_blend = r2_score(y, oof_blend)
    mae_blend = mean_absolute_error(y, oof_blend)
    
    print("\n--- Cross-Validation Performance ---")
    print(f"  Ridge Regressor:      R^2 = {r2_ridge:.4f} | MAE = {mae_ridge:.2f} pts")
    print(f"  Random Forest:        R^2 = {r2_rf:.4f} | MAE = {mae_rf:.2f} pts")
    print(f"  HistGradientBoosting: R^2 = {r2_hgb:.4f} | MAE = {mae_hgb:.2f} pts")
    print(f"  Ensemble Blend:       R^2 = {r2_blend:.4f} | MAE = {mae_blend:.2f} pts")
    
    final_ridge = Ridge(alpha=2.0)
    final_ridge.fit(X_scaled, y)
    
    final_rf = RandomForestRegressor(n_estimators=150, max_depth=4, random_state=42)
    final_rf.fit(X_scaled, y)
    
    final_hgb = HistGradientBoostingRegressor(max_depth=3, random_state=42)
    final_hgb.fit(X_scaled, y)
    
    coefs = dict(zip(feature_cols, final_ridge.coef_.tolist()))
    print("\n--- Model v4 Learned Feature Weights (Ridge Coefficients) ---")
    for col, coef in sorted(coefs.items(), key=lambda x: abs(x[1]), reverse=True):
        print(f"  {col:30s}: {coef:+.4f}")
        
    joblib.dump(scaler, "scaler_v4_complexity.joblib")
    joblib.dump(final_ridge, "model_v4_ridge.joblib")
    joblib.dump(final_rf, "model_v4_rf.joblib")
    joblib.dump(final_hgb, "model_v4_hgb.joblib")
    
    meta = {
        'feature_cols': feature_cols,
        'r2_score': round(r2_blend, 4),
        'mae_points': round(mae_blend, 2),
        'learned_coefficients': {k: round(v, 4) for k, v in coefs.items()}
    }
    
    with open("model_v4_metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        
    print("\nSUCCESS: Model v4 trained and saved to joblib artifacts!")

if __name__ == "__main__":
    train_model_v4()
