import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
import numpy as np
import copy
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, log_loss

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)

# Set random seed for reproducibility
torch.manual_seed(42)
np.random.seed(42)

class MatchDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
        
    def __len__(self):
        return len(self.y)
        
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]

class FeatureTokenizer(nn.Module):
    """
    Tokenizer for numerical features.
    Maps each scalar feature to a d_model vector.
    """
    def __init__(self, num_features, d_model):
        super().__init__()
        # Creating a linear layer (or embedding weight/bias) for each feature
        self.weights = nn.Parameter(torch.randn(num_features, d_model))
        self.biases = nn.Parameter(torch.randn(num_features, d_model))
        
    def forward(self, x):
        # x shape: (batch_size, num_features)
        # We want to output: (batch_size, num_features, d_model)
        # x[:, :, None] has shape (batch_size, num_features, 1)
        # self.weights[None, :, :] has shape (1, num_features, d_model)
        # We multiply elementwise and add bias
        return x[:, :, None] * self.weights[None, :, :] + self.biases[None, :, :]

class TabularTransformer(nn.Module):
    def __init__(self, num_features, d_model=32, nhead=4, num_layers=2, dim_feedforward=64, dropout=0.1, num_classes=3):
        super().__init__()
        self.d_model = d_model
        
        # Tokenizer
        self.tokenizer = FeatureTokenizer(num_features, d_model)
        
        # CLS Token
        self.cls_token = nn.Parameter(torch.randn(1, 1, d_model))
        
        # Transformer Encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # MLP Head
        self.mlp = nn.Sequential(
            nn.LayerNorm(d_model),
            nn.Linear(d_model, dim_feedforward),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(dim_feedforward, num_classes)
        )
        
    def forward(self, x):
        # x shape: (batch_size, num_features)
        
        # Tokenize features
        x_tok = self.tokenizer(x) # (batch_size, num_features, d_model)
        
        # Append CLS token to the beginning
        batch_size = x.shape[0]
        cls_tokens = self.cls_token.expand(batch_size, -1, -1) # (batch_size, 1, d_model)
        x_tok = torch.cat([cls_tokens, x_tok], dim=1) # (batch_size, num_features + 1, d_model)
        
        # Transformer
        x_trans = self.transformer(x_tok) # (batch_size, num_features + 1, d_model)
        
        # Pull representation of CLS token (index 0)
        cls_rep = x_trans[:, 0, :] # (batch_size, d_model)
        
        # Predict logits
        logits = self.mlp(cls_rep) # (batch_size, num_classes)
        return logits

def load_and_preprocess_data():
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
    
    # Chronological Split
    train_seasons = ["2021-2022", "2022-2023", "2023-2024"]
    val_seasons = ["2024-2025"]
    test_seasons = ["2025-2026"]
    
    train_mask = df_bl['season'].isin(train_seasons)
    val_mask = df_bl['season'].isin(val_seasons)
    test_mask = df_bl['season'].isin(test_seasons)
    
    X_train_raw = df_bl.loc[train_mask, features].values
    y_train = df_bl.loc[train_mask, 'target'].values
    
    X_val_raw = df_bl.loc[val_mask, features].values
    y_val = df_bl.loc[val_mask, 'target'].values
    
    X_test_raw = df_bl.loc[test_mask, features].values
    y_test = df_bl.loc[test_mask, 'target'].values
    
    # Scale features (fitting on train only!)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train_raw)
    X_val = scaler.transform(X_val_raw)
    X_test = scaler.transform(X_test_raw)
    
    return X_train, y_train, X_val, y_val, X_test, y_test, scaler, features

def train_model(X_train, y_train, X_val, y_val, num_features):
    train_dataset = MatchDataset(X_train, y_train)
    val_dataset = MatchDataset(X_val, y_val)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=64, shuffle=False)
    
    # Instantiate Model
    model = TabularTransformer(
        num_features=num_features,
        d_model=32,
        nhead=4,
        num_layers=2,
        dim_feedforward=64,
        dropout=0.2
    ).to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=5)
    
    best_val_loss = float('inf')
    best_model_weights = None
    patience = 15
    patience_counter = 0
    
    epochs = 100
    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        for batch_X, batch_y in train_loader:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device)
            
            optimizer.zero_grad()
            logits = model(batch_X)
            loss = criterion(logits, batch_y)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * batch_X.size(0)
            
        train_loss /= len(train_loader.dataset)
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_preds = []
        val_targets = []
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device)
                logits = model(batch_X)
                loss = criterion(logits, batch_y)
                val_loss += loss.item() * batch_X.size(0)
                
                preds = torch.argmax(logits, dim=1).cpu().numpy()
                val_preds.extend(preds)
                val_targets.extend(batch_y.cpu().numpy())
                
        val_loss /= len(val_loader.dataset)
        val_acc = accuracy_score(val_targets, val_preds)
        
        scheduler.step(val_loss)
        
        # Early Stopping check
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_weights = copy.deepcopy(model.state_dict())
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                # Early stop
                break
                
    # Load best model weights
    if best_model_weights is not None:
        model.load_state_dict(best_model_weights)
        
    return model

def evaluate_model(model, X, y):
    model.eval()
    dataset = MatchDataset(X, y)
    loader = DataLoader(dataset, batch_size=64, shuffle=False)
    
    all_probs = []
    all_preds = []
    with torch.no_grad():
        for batch_X, _ in loader:
            batch_X = batch_X.to(device)
            logits = model(batch_X)
            probs = torch.softmax(logits, dim=1).cpu().numpy()
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            
            all_probs.append(probs)
            all_preds.append(preds)
            
    all_probs = np.concatenate(all_probs, axis=0)
    all_preds = np.concatenate(all_preds, axis=0)
    
    acc = accuracy_score(y, all_preds)
    loss = log_loss(y, all_probs)
    return acc, loss, all_probs

if __name__ == "__main__":
    X_train, y_train, X_val, y_val, X_test, y_test, scaler, features = load_and_preprocess_data()
    print("Training Tabular Transformer...")
    model = train_model(X_train, y_train, X_val, y_val, len(features))
    
    # Save model and scaler
    torch.save(model.state_dict(), "tabular_transformer.pt")
    import joblib
    joblib.dump(scaler, "scaler.joblib")
    print("Model and scaler saved successfully!")
    
    # Evaluate
    val_acc, val_loss, _ = evaluate_model(model, X_val, y_val)
    test_acc, test_loss, _ = evaluate_model(model, X_test, y_test)
    
    print(f"\n--- Transformer Evaluation ---")
    print(f"Val Accuracy:  {val_acc:.4f} | Log Loss: {val_loss:.4f}")
    print(f"Test Accuracy: {test_acc:.4f} | Log Loss: {test_loss:.4f}")
