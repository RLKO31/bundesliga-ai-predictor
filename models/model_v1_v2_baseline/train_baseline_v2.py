import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, log_loss, classification_report
from sklearn.inspection import permutation_importance

def train_and_evaluate():
    # 1. Load data
    df = pd.read_csv("bundesliga_multicomp_processed_v2.csv")
    
    # Filter for Bundesliga only
    df_bl = df[df['competition'] == 'Bundesliga'].copy()
    
    # Drop rows that are missing goals (unplayed games, though there shouldn't be any in completed seasons)
    df_bl = df_bl.dropna(subset=['home_goals', 'away_goals']).reset_index(drop=True)
    
    # 2. Define target
    # 0 = Home Win, 1 = Draw, 2 = Away Win
    def get_outcome(row):
        hg = row['home_goals']
        ag = row['away_goals']
        if hg > ag:
            return 0
        elif hg < ag:
            return 2
        else:
            return 1
            
    df_bl['target'] = df_bl.apply(get_outcome, axis=1)
    
    # 3. Engineer target-specific difference features
    df_bl['elo_diff'] = df_bl['home_elo'] - df_bl['away_elo']
    df_bl['rest_diff'] = df_bl['home_rest'] - df_bl['away_rest']
    
    # List of features to use
    features = [
        'elo_diff',
        'rest_diff',
        'home_elo',
        'away_elo',
        'home_rest',
        'away_rest',
        'home_goals_roll3',
        'home_goals_roll15',
        'home_xg_roll3',
        'home_xg_roll15',
        'home_xg_diff_roll10',
        'away_goals_roll3',
        'away_goals_roll15',
        'away_xg_roll3',
        'away_xg_roll15',
        'away_xg_diff_roll10',
        'home_value_rank',
        'away_value_rank',
        'value_rank_diff',
        'away_finishing_eff_roll10',
        'finishing_eff_diff'
    ]
    
    # 4. Chronological split
    # Train: 21-22, 22-23, 23-24
    # Val: 24-25
    # Test: 25-26
    train_seasons = ["2021-2022", "2022-2023", "2023-2024"]
    val_seasons = ["2024-2025"]
    test_seasons = ["2025-2026"]
    
    train_mask = df_bl['season'].isin(train_seasons)
    val_mask = df_bl['season'].isin(val_seasons)
    test_mask = df_bl['season'].isin(test_seasons)
    
    X_train = df_bl.loc[train_mask, features]
    y_train = df_bl.loc[train_mask, 'target']
    
    X_val = df_bl.loc[val_mask, features]
    y_val = df_bl.loc[val_mask, 'target']
    
    X_test = df_bl.loc[test_mask, features]
    y_test = df_bl.loc[test_mask, 'target']
    
    print(f"Train set shape: {X_train.shape}")
    print(f"Val set shape: {X_val.shape}")
    print(f"Test set shape: {X_test.shape}")
    
    # Check class balance in training set
    print("\nTraining set outcome distribution:")
    print(y_train.value_counts(normalize=True))
    
    # 5. Train Random Forest Baseline
    print("\n--- Training Random Forest Baseline ---")
    rf = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
    rf.fit(X_train, y_train)
    
    # Validate
    val_preds_rf = rf.predict(X_val)
    val_probs_rf = rf.predict_proba(X_val)
    val_acc_rf = accuracy_score(y_val, val_preds_rf)
    val_loss_rf = log_loss(y_val, val_probs_rf)
    
    # Test
    test_preds_rf = rf.predict(X_test)
    test_probs_rf = rf.predict_proba(X_test)
    test_acc_rf = accuracy_score(y_test, test_preds_rf)
    test_loss_rf = log_loss(y_test, test_probs_rf)
    
    print(f"RF Validation Accuracy: {val_acc_rf:.4f} | Log Loss: {val_loss_rf:.4f}")
    print(f"RF Test Accuracy:       {test_acc_rf:.4f} | Log Loss: {test_loss_rf:.4f}")
    
    # 6. Train HistGradientBoosting Baseline
    print("\n--- Training HistGradientBoosting Baseline ---")
    hgb = HistGradientBoostingClassifier(max_iter=100, max_depth=4, learning_rate=0.05, random_state=42)
    hgb.fit(X_train, y_train)
    
    # Validate
    val_preds_hgb = hgb.predict(X_val)
    val_probs_hgb = hgb.predict_proba(X_val)
    val_acc_hgb = accuracy_score(y_val, val_preds_hgb)
    val_loss_hgb = log_loss(y_val, val_probs_hgb)
    
    # Test
    test_preds_hgb = hgb.predict(X_test)
    test_probs_hgb = hgb.predict_proba(X_test)
    test_acc_hgb = accuracy_score(y_test, test_preds_hgb)
    test_loss_hgb = log_loss(y_test, test_probs_hgb)
    
    print(f"HGB Validation Accuracy: {val_acc_hgb:.4f} | Log Loss: {val_loss_hgb:.4f}")
    print(f"HGB Test Accuracy:       {test_acc_hgb:.4f} | Log Loss: {test_loss_hgb:.4f}")
    
    # Print classification report for the best model on test set
    best_model_name = "HistGradientBoosting" if test_acc_hgb > test_acc_rf else "Random Forest"
    best_preds = test_preds_hgb if test_acc_hgb > test_acc_rf else test_preds_rf
    print(f"\nClassification Report for Best Model ({best_model_name}) on Test Set:")
    print(classification_report(y_test, best_preds, target_names=["Home Win", "Draw", "Away Win"]))
    
    # 7. Permutation Importances on Test Set
    print("\nCalculating Permutation Importances (Test Set)...")
    best_model = hgb if test_acc_hgb > test_acc_rf else rf
    result = permutation_importance(best_model, X_test, y_test, n_repeats=10, random_state=42)
    
    importances = pd.DataFrame({
        'Feature': features,
        'Importance_Mean': result.importances_mean,
        'Importance_Std': result.importances_std
    }).sort_values(by='Importance_Mean', ascending=False)
    
    print("\nPermutation Importances:")
    print(importances.to_string(index=False))
    
    # Save the models
    import joblib
    joblib.dump(rf, "ensemble_rf_v2.joblib")
    joblib.dump(hgb, "ensemble_hgb_v2.joblib")
    print("Saved ensemble_rf_v2.joblib and ensemble_hgb_v2.joblib.")

if __name__ == "__main__":
    train_and_evaluate()
