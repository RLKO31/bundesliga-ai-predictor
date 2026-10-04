import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib
from scipy.stats import poisson

def train_score_predictor():
    # 1. Load data
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
    
    X_train_pool = df_bl.loc[train_pool_mask, features].values
    y_train_home = df_bl.loc[train_pool_mask, 'home_goals'].values
    y_train_away = df_bl.loc[train_pool_mask, 'away_goals'].values
    
    X_test_raw = df_bl.loc[test_mask, features].values
    y_test_home = df_bl.loc[test_mask, 'home_goals'].values
    y_test_away = df_bl.loc[test_mask, 'away_goals'].values
    
    # Scale features
    scaler = joblib.load("scaler_v2.joblib")
    X_train_pool_scaled = scaler.transform(X_train_pool)
    X_test_scaled = scaler.transform(X_test_raw)
    
    # 2. Train Regressors for Home and Away Goals
    print("Training Home Goals Regressor...")
    reg_home = RandomForestRegressor(n_estimators=150, max_depth=5, random_state=42)
    reg_home.fit(X_train_pool_scaled, y_train_home)
    
    print("Training Away Goals Regressor...")
    reg_away = RandomForestRegressor(n_estimators=150, max_depth=5, random_state=42)
    reg_away.fit(X_train_pool_scaled, y_train_away)
    
    # Predict lambdas on test set
    lambda_home = reg_home.predict(X_test_scaled)
    lambda_away = reg_away.predict(X_test_scaled)
    
    # Clip lambdas to avoid negative or extremely small goal expectations
    lambda_home = np.clip(lambda_home, 0.5, 5.0)
    lambda_away = np.clip(lambda_away, 0.5, 5.0)
    
    print(f"\nTest set stats:")
    print(f"  - Average Predicted Home Goals (Lambda H): {np.mean(lambda_home):.3f} (Actual: {np.mean(y_test_home):.3f})")
    print(f"  - Average Predicted Away Goals (Lambda A): {np.mean(lambda_away):.3f} (Actual: {np.mean(y_test_away):.3f})")
    print(f"  - Home Goals MAE: {mean_absolute_error(y_test_home, lambda_home):.3f}")
    print(f"  - Away Goals MAE: {mean_absolute_error(y_test_away, lambda_away):.3f}")
    
    # 3. Poisson Bivariate Exact Score Calculation
    correct_scores = 0
    correct_outcomes = 0 # win, draw, loss check via exact score prediction
    
    predicted_scores = []
    actual_scores = []
    
    for i in range(len(X_test_scaled)):
        l_h = lambda_home[i]
        l_a = lambda_away[i]
        
        # Grid search for score with highest combined probability from 0-0 to 5-5
        best_prob = -1.0
        best_score = (0, 0)
        
        for hg in range(6):
            for ag in range(6):
                # Poisson probability P(X=hg) * P(Y=ag)
                p_h = poisson.pmf(hg, l_h)
                p_a = poisson.pmf(ag, l_a)
                p_score = p_h * p_a
                
                if p_score > best_prob:
                    best_prob = p_score
                    best_score = (hg, ag)
                    
        predicted_scores.append(best_score)
        act_h = int(y_test_home[i])
        act_a = int(y_test_away[i])
        actual_scores.append((act_h, act_a))
        
        # Evaluate exact score prediction
        if best_score == (act_h, act_a):
            correct_scores += 1
            
        # Check if predicted outcome (W/D/L) matches actual
        pred_outcome = 0 if best_score[0] > best_score[1] else (2 if best_score[0] < best_score[1] else 1)
        act_outcome = 0 if act_h > act_a else (2 if act_h < act_a else 1)
        if pred_outcome == act_outcome:
            correct_outcomes += 1
            
    score_accuracy = correct_scores / len(X_test_scaled) * 100
    outcome_accuracy = correct_outcomes / len(X_test_scaled) * 100
    
    print(f"\nExact Score Prediction Results:")
    print(f"  - Correct Exact Scores: {correct_scores} / {len(X_test_scaled)} ({score_accuracy:.2f}%)")
    print(f"  - Derived Outcome Accuracy: {correct_outcomes} / {len(X_test_scaled)} ({outcome_accuracy:.2f}%)")
    
    # Print sample predictions vs actual
    print("\nSample Exact Score Predictions:")
    for i in range(15):
        print(f"  - Game {i+1}: Pred: {predicted_scores[i][0]}:{predicted_scores[i][1]} (Lambda: {lambda_home[i]:.2f}:{lambda_away[i]:.2f}) | Actual: {actual_scores[i][0]}:{actual_scores[i][1]}")
        
    # Save regressors
    joblib.dump(reg_home, "regressor_home_goals.joblib")
    joblib.dump(reg_away, "regressor_away_goals.joblib")
    print("\nSaved regressor_home_goals.joblib and regressor_away_goals.joblib.")

if __name__ == "__main__":
    train_score_predictor()
