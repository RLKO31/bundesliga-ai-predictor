import pandas as pd
import numpy as np
import json
import joblib

def predict_v4_standings():
    print("--- 3. Predicting 2026/27 End-of-Season Standings via Model v4 Goal Complexity ---")
    
    scaler = joblib.load("scaler_v4_complexity.joblib")
    ridge = joblib.load("model_v4_ridge.joblib")
    rf = joblib.load("model_v4_rf.joblib")
    hgb = joblib.load("model_v4_hgb.joblib")
    
    with open("model_v4_metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)
        
    feature_cols = meta['feature_cols']
    
    # Load 2025-2026 / 2026-2027 complexity features for Bundesliga teams
    df_complexity = pd.read_csv("bundesliga_first_15_goals_complexity.csv")
    current_season_df = df_complexity[df_complexity['season'] == '2025-2026'].copy()
    
    if len(current_season_df) == 0:
        current_season_df = df_complexity.groupby('team').last().reset_index()
        
    X_curr = current_season_df[feature_cols].values
    X_curr_scaled = scaler.transform(X_curr)
    
    p_ridge = ridge.predict(X_curr_scaled)
    p_rf = rf.predict(X_curr_scaled)
    p_hgb = hgb.predict(X_curr_scaled)
    
    p_blend = 0.40 * p_ridge + 0.35 * p_rf + 0.25 * p_hgb
    current_season_df['pred_final_points'] = np.round(p_blend, 1)
    
    # Sort by predicted points descending
    current_season_df = current_season_df.sort_values('pred_final_points', ascending=False).reset_index(drop=True)
    current_season_df['pred_rank'] = current_season_df.index + 1
    
    output_records = []
    for idx, r in current_season_df.iterrows():
        output_records.append({
            'rank': int(r['pred_rank']),
            'team': r['team'],
            'predicted_points': float(r['pred_final_points']),
            'matches_to_15_goals': int(r['matches_to_15_goals']),
            'action_complexity_score': float(r['action_complexity_score']),
            'assist_entropy': float(r['assist_entropy']),
            'avg_xg_per_goal': float(r['avg_xg_per_goal']),
            'finishing_delta': float(r['finishing_delta']),
            'open_play_ratio': float(r['open_play_ratio'])
        })
        
    with open("predictions_v4_complexity.json", "w", encoding="utf-8") as f:
        json.dump(output_records, f, indent=2)
        
    print("\n--- 2026/27 Model v4 Goal Complexity Predicted Standings ---")
    for rec in output_records:
        print(f"  #{rec['rank']:2d} | {rec['team']:22s} | {rec['predicted_points']:5.1f} pts | Complexity: {rec['action_complexity_score']:.2f} | Entropy: {rec['assist_entropy']:.2f}")
        
    print("\nSUCCESS: Saved Model v4 predicted standings to predictions_v4_complexity.json!")

if __name__ == "__main__":
    predict_v4_standings()
