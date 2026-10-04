import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime
from model_transformer import TabularTransformer

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def clean_team_name(name):
    if not isinstance(name, str):
        return name
    replacements = {
        "FC Augsburg": "Augsburg", "VfL Bochum": "Bochum", "SV Darmstadt 98": "Darmstadt",
        "1. FC Heidenheim 1846": "FC Heidenheim", "1. FC Heidenheim": "FC Heidenheim",
        "SC Freiburg": "Freiburg", "SpVgg Greuther Frth": "Greuther Fuerth",
        "SpVgg Greuther Fűrth": "Greuther Fuerth", "SpVgg Greuther Fürth": "Greuther Fuerth",
        "Hamburg SV": "Hamburger SV", "TSG Hoffenheim": "Hoffenheim", "Mainz": "Mainz 05",
        "RB Leipzig": "RasenBallsport Leipzig", "1. FC Union Berlin": "Union Berlin",
        "VfL Wolfsburg": "Wolfsburg", "Borussia Mnchengladbach": "Borussia M.Gladbach",
        "Borussia Mönchengladbach": "Borussia M.Gladbach", "FC Schalke 04": "Schalke 04",
        "Arminia Bielefeld": "Arminia Bielefeld", "Fortuna Dsseldorf": "Fortuna Dusseldorf",
        "Fortuna Düsseldorf": "Fortuna Dusseldorf", "1. FC Kln": "FC Cologne",
        "1. FC Köln": "FC Cologne", "FC Kln": "FC Cologne", "FC Köln": "FC Cologne",
        "Hertha BSC": "Hertha Berlin", "St. Pauli": "St. Pauli", "VfB Stuttgart": "VfB Stuttgart",
        "Eintracht Frankfurt": "Eintracht Frankfurt", "Holstein Kiel": "Holstein Kiel"
    }
    for k, v in replacements.items():
        if k in name or name == k:
            return v
    return name.strip()

def predict_matches(fixtures):
    """
    fixtures: list of dicts, e.g. [{"home_team": "Bayern Munich", "away_team": "Borussia Dortmund", "date": "2026-08-22 18:30:00"}]
    """
    # 1. Load state database
    with open("latest_state_v2.json", "r", encoding="utf-8") as f:
        state = json.load(f)
        
    final_elos = state['final_elos']
    last_match_dates = state['last_match_dates']
    team_history = state['team_history']
    
    # 2. Load scaler and models
    scaler = joblib.load("scaler_v2.joblib")
    rf = joblib.load("ensemble_rf_v2.joblib")
    hgb = joblib.load("ensemble_hgb_v2.joblib")
    
    features_count = 21
    from model_transformer_v2 import TabularTransformer
    transformer = TabularTransformer(
        num_features=features_count,
        d_model=32,
        nhead=4,
        num_layers=2,
        dim_feedforward=64,
        dropout=0.2
    ).to(device)
    transformer.load_state_dict(torch.load("tabular_transformer_v2.pt"))
    transformer.eval()
    
    # Define ranks for upcoming season (based on 2025-26 squad quality)
    ranks_2025_26 = {
        "Bayern Munich": 1, "Bayer Leverkusen": 2, "RasenBallsport Leipzig": 3,
        "Borussia Dortmund": 4, "VfB Stuttgart": 5, "Eintracht Frankfurt": 6,
        "Freiburg": 7, "Wolfsburg": 8, "Borussia M.Gladbach": 9, "Hoffenheim": 10,
        "Werder Bremen": 11, "Union Berlin": 12, "Augsburg": 13, "Mainz 05": 14,
        "FC Heidenheim": 15, "St. Pauli": 16, "Bochum": 17, "Holstein Kiel": 18
    }
    
    # Process each fixture into a feature vector
    rows = []
    for f in fixtures:
        home = clean_team_name(f['home_team'])
        away = clean_team_name(f['away_team'])
        date_str = f['date']
        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        
        # 1. Elos
        h_elo = final_elos.get(home, 1500.0)
        a_elo = final_elos.get(away, 1500.0)
        elo_diff = h_elo - a_elo
        
        # 2. Rest Days
        def get_rest_days(team, match_date):
            if team in last_match_dates:
                prev_date = datetime.strptime(last_match_dates[team], "%Y-%m-%d %H:%M:%S")
                return min((match_date - prev_date).days, 14.0)
            return 14.0
            
        h_rest = get_rest_days(home, date_obj)
        a_rest = get_rest_days(away, date_obj)
        rest_diff = h_rest - a_rest
        
        # 3. Rolling Form
        def get_rolling_avg(team, key, window, default_val):
            history = team_history.get(team, [])
            vals = [h[key] for h in history if h[key] is not None and not pd.isna(h[key])]
            if not vals:
                return default_val
            return np.mean(vals[-window:])
            
        def get_rolling_xg_diff(team, window, default_val=0.0):
            history = team_history.get(team, [])
            diffs = []
            for h in history:
                if (h['xg'] is not None and h['xg_conceded'] is not None and 
                    not pd.isna(h['xg']) and not pd.isna(h['xg_conceded'])):
                    diffs.append(h['xg'] - h['xg_conceded'])
            if not diffs:
                return default_val
            return np.mean(diffs[-window:])
            
        h_goals_roll3 = get_rolling_avg(home, 'goals', 3, 1.3)
        h_goals_roll15 = get_rolling_avg(home, 'goals', 15, 1.3)
        h_xg_roll3 = get_rolling_avg(home, 'xg', 3, 1.3)
        h_xg_roll15 = get_rolling_avg(home, 'xg', 15, 1.3)
        h_xg_diff_roll10 = get_rolling_xg_diff(home, 10, 0.0)
        
        a_goals_roll3 = get_rolling_avg(away, 'goals', 3, 1.2)
        a_goals_roll15 = get_rolling_avg(away, 'goals', 15, 1.2)
        a_xg_roll3 = get_rolling_avg(away, 'xg', 3, 1.2)
        a_xg_roll15 = get_rolling_avg(away, 'xg', 15, 1.2)
        a_xg_diff_roll10 = get_rolling_xg_diff(away, 10, 0.0)
        
        # 4. Market Values
        h_value = ranks_2025_26.get(home, 9.5)
        a_value = ranks_2025_26.get(away, 9.5)
        value_diff = a_value - h_value # positive if home team is more valuable
        
        # 5. Finishing Efficiency (refined v2 features)
        h_g10 = get_rolling_avg(home, 'goals', 10, 1.3)
        h_xg10 = get_rolling_avg(home, 'xg', 10, 1.3)
        h_fin_eff = h_g10 - h_xg10
        
        a_g10 = get_rolling_avg(away, 'goals', 10, 1.2)
        a_xg10 = get_rolling_avg(away, 'xg', 10, 1.2)
        a_fin_eff = a_g10 - a_xg10
        
        finishing_eff_diff = h_fin_eff - a_fin_eff
        
        feature_vector = [
            elo_diff, rest_diff, h_elo, a_elo, h_rest, a_rest,
            h_goals_roll3, h_goals_roll15, h_xg_roll3, h_xg_roll15, h_xg_diff_roll10,
            a_goals_roll3, a_goals_roll15, a_xg_roll3, a_xg_roll15, a_xg_diff_roll10,
            h_value, a_value, value_diff,
            a_fin_eff, finishing_eff_diff
        ]
        rows.append(feature_vector)
        
    X_raw = np.array(rows)
    X_scaled = scaler.transform(X_raw)
    
    # 3. Model Predictions
    # RF
    probs_rf = rf.predict_proba(X_scaled)
    # HGB
    probs_hgb = hgb.predict_proba(X_scaled)
    # Transformer
    X_tensor = torch.tensor(X_scaled, dtype=torch.float32).to(device)
    with torch.no_grad():
        logits = transformer(X_tensor)
        probs_trans = torch.softmax(logits, dim=1).cpu().numpy()
        
    # 4. Ensemble Blend
    # Weights: 19% RF, 41% HGB, 40% Transformer
    probs_blend = 0.19 * probs_rf + 0.41 * probs_hgb + 0.40 * probs_trans
    
    # Print results
    print("\n" + "="*70)
    print(" BUNDESLIGA MATCHDAY PREDICTIONS (ENSEMBLE BLEND)")
    print("="*70)
    for idx, f in enumerate(fixtures):
        home = f['home_team']
        away = f['away_team']
        p = probs_blend[idx]
        
        p_home = p[0] * 100
        p_draw = p[1] * 100
        p_away = p[2] * 100
        
        # Decide tipped outcome
        outcomes = ["HOME WIN", "DRAW", "AWAY WIN"]
        tip = outcomes[np.argmax(p)]
        
        print(f"\n{home} vs {away} ({f['date']})")
        print(f"  - Home Win: {p_home:.1f}%")
        print(f"  - Draw:     {p_draw:.1f}%")
        print(f"  - Away Win: {p_away:.1f}%")
        print(f"  * Recommended Tip: {tip}")
    print("="*70)

if __name__ == "__main__":
    # Test with a sample opening matchday fixtures list
    sample_fixtures = [
        {"home_team": "Bayern Munich", "away_team": "Borussia Dortmund", "date": "2026-08-21 20:30:00"},
        {"home_team": "Bayer Leverkusen", "away_team": "VfB Stuttgart", "date": "2026-08-22 15:30:00"},
        {"home_team": "RasenBallsport Leipzig", "away_team": "FC Cologne", "date": "2026-08-22 15:30:00"},
        {"home_team": "Werder Bremen", "away_team": "Mainz 05", "date": "2026-08-22 15:30:00"},
        {"home_team": "FC Augsburg", "away_team": "Bochum", "date": "2026-08-22 15:30:00"}
    ]
    predict_matches(sample_fixtures)
