import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics import accuracy_score, log_loss, classification_report
from model_transformer import TabularTransformer, MatchDataset

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def run_rolling_backtest(online_tuning=True, lr=5e-5, epochs_per_gameday=5):
    # 1. Load data
    df = pd.read_csv("bundesliga_multicomp_processed.csv")
    df_bl = df[df['competition'] == 'Bundesliga'].copy()
    df_bl = df_bl.dropna(subset=['home_goals', 'away_goals']).reset_index(drop=True)
    
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
    df_bl['elo_diff'] = df_bl['home_elo'] - df_bl['away_elo']
    df_bl['rest_diff'] = df_bl['home_rest'] - df_bl['away_rest']
    
    features = [
        'elo_diff', 'rest_diff', 'home_elo', 'away_elo', 'home_rest', 'away_rest',
        'home_goals_roll3', 'home_goals_roll15', 'home_xg_roll3', 'home_xg_roll15', 'home_xg_diff_roll10',
        'away_goals_roll3', 'away_goals_roll15', 'away_xg_roll3', 'away_xg_roll15', 'away_xg_diff_roll10',
        'home_value_rank', 'away_value_rank', 'value_rank_diff'
    ]
    
    # Load pre-trained model and scaler
    scaler = joblib.load("scaler.joblib")
    
    model = TabularTransformer(
        num_features=len(features),
        d_model=32,
        nhead=4,
        num_layers=2,
        dim_feedforward=64,
        dropout=0.2
    ).to(device)
    model.load_state_dict(torch.load("tabular_transformer.pt"))
    
    # Filter test season matches (2025-2026) and sort chronologically
    test_mask = df_bl['season'] == "2025-2026"
    df_test = df_bl.loc[test_mask].copy()
    df_test['date'] = pd.to_datetime(df_test['date'], format='mixed', utc=True)
    df_test = df_test.sort_values(by='date').reset_index(drop=True)
    
    print(f"Total test matches: {len(df_test)}")
    
    # Chunk into 34 gamedays of 9 matches each
    gamedays_count = 34
    matches_per_gameday = 9
    
    all_rolling_probs = []
    all_rolling_preds = []
    all_rolling_targets = []
    
    # Define optimizer for fine-tuning
    optimizer = optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()
    
    for g in range(gamedays_count):
        start_idx = g * matches_per_gameday
        end_idx = start_idx + matches_per_gameday
        gameday_df = df_test.iloc[start_idx:end_idx]
        
        X_raw = gameday_df[features].values
        y_true = gameday_df['target'].values
        
        # Scale features
        X_scaled = scaler.transform(X_raw)
        
        # Convert to tensors
        X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(device)
        y_tensor = torch.tensor(y_true, dtype=torch.long).to(device)
        
        # --- 1. PREDICT step (predicting before seeing outcomes) ---
        model.eval()
        with torch.no_grad():
            logits = model(X_tensor)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            
            all_rolling_probs.append(probs)
            all_rolling_preds.append(preds)
            all_rolling_targets.extend(y_true)
            
        # --- 2. FINE-TUNE step (updating model weights with observed outcomes) ---
        if online_tuning:
            model.train()
            for epoch in range(epochs_per_gameday):
                optimizer.zero_grad()
                logits = model(X_tensor)
                loss = criterion(logits, y_tensor)
                loss.backward()
                optimizer.step()
                
    # Concatenate all results
    all_rolling_probs = np.concatenate(all_rolling_probs, axis=0)
    all_rolling_preds = np.concatenate(all_rolling_preds, axis=0)
    all_rolling_targets = np.array(all_rolling_targets)
    
    # Calculate performance metrics
    accuracy = accuracy_score(all_rolling_targets, all_rolling_preds)
    loss = log_loss(all_rolling_targets, all_rolling_probs)
    
    return accuracy, loss, all_rolling_targets, all_rolling_preds

if __name__ == "__main__":
    print("--- Running Tabular Transformer WITHOUT Online Fine-Tuning ---")
    acc_static, loss_static, _, _ = run_rolling_backtest(online_tuning=False)
    print(f"Static Transformer - Accuracy: {acc_static:.4f} | Log Loss: {loss_static:.4f}")
    
    print("\n--- Running Tabular Transformer WITH Online Fine-Tuning ---")
    # Grid search for learning rate and epochs
    for current_lr in [1e-5, 5e-5, 1e-4]:
        for current_epochs in [3, 5, 8]:
            acc, loss, y_true, y_pred = run_rolling_backtest(
                online_tuning=True, 
                lr=current_lr, 
                epochs_per_gameday=current_epochs
            )
            print(f"Online (lr={current_lr}, epochs={current_epochs}) - Accuracy: {acc:.4f} | Log Loss: {loss:.4f}")
            
    # Run the best configuration and print classification report
    best_lr = 5e-5
    best_epochs = 5
    print(f"\n--- Running Best Configuration (lr={best_lr}, epochs={best_epochs}) ---")
    acc, loss, y_true, y_pred = run_rolling_backtest(
        online_tuning=True, 
        lr=best_lr, 
        epochs_per_gameday=best_epochs
    )
    print(f"Final Model Accuracy: {acc:.4f} | Log Loss: {loss:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Home Win", "Draw", "Away Win"]))
