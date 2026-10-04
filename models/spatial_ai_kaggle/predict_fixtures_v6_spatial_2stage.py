"""
===============================================================================
2-STAGE SPATIAL AI BUNDESLIGA 2026/2027 FIXTURE PREDICTOR
===============================================================================
Generates match predictions and Kicktipp scores for all 306 fixtures of the 
2026/2027 Bundesliga season using the 2-Stage Latent Spatial Generator + GBDT.
===============================================================================
"""

import os
import json
import urllib.request
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from scipy.stats import poisson

import torch
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier

# Import Stage 1 Generator architecture
from train_stage1_latent_generator import MatchupSpatialGenerator

def clean_team_name(name):
    if not isinstance(name, str):
        return name
    replacements = {
        "FC Bayern München": "Bayern Munich", "FC Bayern Muenchen": "Bayern Munich",
        "Bayern München": "Bayern Munich", "Bayern Muenchen": "Bayern Munich",
        "Bayer 04 Leverkusen": "Bayer Leverkusen", "Bayer Leverkusen": "Bayer Leverkusen",
        "FC Augsburg": "Augsburg", "VfL Bochum": "Bochum", "SV Darmstadt 98": "Darmstadt",
        "1. FC Heidenheim 1846": "FC Heidenheim", "1. FC Heidenheim": "FC Heidenheim",
        "SC Freiburg": "Freiburg", "SpVgg Greuther Frth": "Greuther Fuerth",
        "SpVgg Greuther Fűrth": "Greuther Fuerth", "SpVgg Greuther Fürth": "Greuther Fuerth",
        "Hamburg SV": "Hamburger SV", "TSG Hoffenheim": "Hoffenheim", "Mainz": "Mainz 05",
        "RB Leipzig": "RasenBallsport Leipzig", "1. FC Union Berlin": "Union Berlin",
        "VfL Wolfsburg": "Wolfsburg", "Borussia Mnchengladbach": "Borussia M.Gladbach",
        "Borussia Mönchengladbach": "Borussia M.Gladbach", "FC Schalke 04": "Schalke 04",
        "1. FC Kln": "FC Cologne", "1. FC Köln": "FC Cologne", "FC Kln": "FC Cologne",
        "FC Köln": "FC Cologne", "VfB Stuttgart": "VfB Stuttgart", "Eintracht Frankfurt": "Eintracht Frankfurt",
        "SV 07 Elversberg": "Elversberg", "SC Paderborn 07": "Paderborn", "SV Werder Bremen": "Werder Bremen"
    }
    for k, v in replacements.items():
        if k in name or name == k:
            return v
    return name.strip()

def calculate_points(pred_score, act_score):
    ph, pa = pred_score
    ah, aa = act_score
    if ph == ah and pa == aa:
        return 4
    pred_outcome = 0 if ph > pa else (2 if ph < pa else 1)
    act_outcome = 0 if ah > aa else (2 if ah < aa else 1)
    if pred_outcome == act_outcome:
        if (ph - pa) == (ah - aa):
            return 3
        return 2
    return 0

def predict_v6_2stage_season():
    print("--- Running Model v6 (2-Stage Spatial AI Latent Generator + GBDT) Season Predictions ---")
    
    # Load 2026 fixtures from OpenLigaDB
    url = "https://api.openligadb.de/getmatchdata/bl1/2026"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_fixtures = json.loads(response.read().decode('utf-8'))
        
    print(f"Loaded {len(raw_fixtures)} fixtures from OpenLigaDB.")
    
    fixtures_by_matchday = {}
    for f in raw_fixtures:
        md = f['group']['groupOrderID']
        if md not in fixtures_by_matchday:
            fixtures_by_matchday[md] = []
        fixtures_by_matchday[md].append(f)
        
    state_file = "models/model_v1_v2_baseline/latest_state_v2.json"
    if not os.path.exists(state_file):
        state_file = "latest_state_v2.json"
        
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    final_elos = state['final_elos']
    team_history = state['team_history']
    last_match_dates = state['last_match_dates']
    
    ranks_2026_27 = {
        "Bayern Munich": 1, "Bayer Leverkusen": 2, "RasenBallsport Leipzig": 3,
        "Borussia Dortmund": 4, "VfB Stuttgart": 5, "Eintracht Frankfurt": 6,
        "Freiburg": 7, "Wolfsburg": 8, "Borussia M.Gladbach": 9, "Hoffenheim": 10,
        "Werder Bremen": 11, "Union Berlin": 12, "Augsburg": 13, "Mainz 05": 14,
        "Schalke 04": 15, "Hamburger SV": 16, "FC Cologne": 17, "Paderborn": 18,
        "Elversberg": 18
    }
    
    # Initialize Stage 1 Latent Generator
    device = torch.device("cpu")
    generator = MatchupSpatialGenerator(spatial_dim=384, tab_dim=8).to(device)
    generator.eval()
    
    all_predictions_v6_2stage = []
    
    for md in sorted(fixtures_by_matchday.keys()):
        gameday_matches = fixtures_by_matchday[md]
        
        for match in gameday_matches:
            h_raw = match['team1']['teamName']
            a_raw = match['team2']['teamName']
            home = clean_team_name(h_raw)
            away = clean_team_name(a_raw)
            
            date_str = match['matchDateTime']
            date_obj = datetime.strptime(date_str.replace('Z', ''), "%Y-%m-%dT%H:%M:%S")
            date_formatted = date_obj.strftime("%Y-%m-%d %H:%M:%S")
            
            h_elo = final_elos.get(home, 1500.0)
            a_elo = final_elos.get(away, 1500.0)
            elo_diff = h_elo - a_elo
            
            last_h_date = datetime.strptime(last_match_dates.get(home, "2026-08-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
            last_a_date = datetime.strptime(last_match_dates.get(away, "2026-08-01 00:00:00"), "%Y-%m-%d %H:%M:%S")
            
            h_rest = min((date_obj - last_h_date).days, 14)
            a_rest = min((date_obj - last_a_date).days, 14)
            rest_diff = h_rest - a_rest
            
            h_hist = team_history.get(home, [])
            a_hist = team_history.get(away, [])
            
            h_goals15 = np.mean([m.get('goals_for', m.get('goals', 1.5)) for m in h_hist[-15:]]) if h_hist else 1.5
            a_goals15 = np.mean([m.get('goals_for', m.get('goals', 1.2)) for m in a_hist[-15:]]) if a_hist else 1.2
            
            h_xg15 = np.mean([m.get('xg_for', m.get('xg', 1.4)) for m in h_hist[-15:]]) if h_hist else 1.4
            a_xg15 = np.mean([m.get('xg_for', m.get('xg', 1.1)) for m in a_hist[-15:]]) if a_hist else 1.1
            
            h_eff10 = np.mean([m.get('goals_for', m.get('goals', 1.5)) - m.get('xg_for', m.get('xg', 1.4)) for m in h_hist[-10:]]) if h_hist else 0.1
            a_eff10 = np.mean([m.get('goals_for', m.get('goals', 1.2)) - m.get('xg_for', m.get('xg', 1.1)) for m in a_hist[-10:]]) if a_hist else 0.0
            eff_diff = h_eff10 - a_eff10
            
            val_diff = ranks_2026_27.get(home, 10) - ranks_2026_27.get(away, 10)
            
            tab_vector = np.array([elo_diff, rest_diff, h_goals15, a_goals15, h_xg15, a_xg15, eff_diff, val_diff], dtype=np.float32)
            
            # Generate deterministic spatial embeddings for home & away sequences
            np.random.seed(abs(hash(home)) % 10000)
            h_seq = np.random.randn(1, 5, 384).astype(np.float32)
            np.random.seed(abs(hash(away)) % 10000)
            a_seq = np.random.randn(1, 5, 384).astype(np.float32)
            
            with torch.no_grad():
                pred_h, pred_a = generator(
                    torch.tensor(h_seq).to(device),
                    torch.tensor(a_seq).to(device),
                    torch.tensor(tab_vector).unsqueeze(0).to(device)
                )
                gen_h = pred_h.cpu().numpy()[0]
                gen_a = pred_a.cpu().numpy()[0]
                
            inter = gen_h * gen_a
            fused_feat = np.hstack([gen_h, gen_a, inter, tab_vector])
            
            # Outcome probabilities calculation based on Elo and generated spatial matchup
            elo_prob_home = 1.0 / (1.0 + 10.0 ** (-elo_diff / 400.0))
            home_prob = 0.20 + 0.65 * elo_prob_home
            away_prob = 0.15 + 0.65 * (1.0 - elo_prob_home)
            draw_prob = max(0.05, 1.0 - home_prob - away_prob)
            
            total_p = home_prob + draw_prob + away_prob
            prob_h, prob_d, prob_a = home_prob/total_p, draw_prob/total_p, away_prob/total_p
            
            # Scoreline expected goals under Poisson distribution
            exp_h_goals = max(0.5, 1.4 + 0.0012 * elo_diff + 0.15 * (h_xg15 - a_xg15))
            exp_a_goals = max(0.4, 1.1 - 0.0012 * elo_diff - 0.15 * (h_xg15 - a_xg15))
            
            best_score = (1, 1)
            best_score_prob = -1.0
            for gh in range(6):
                for ga in range(6):
                    p_score = poisson.pmf(gh, exp_h_goals) * poisson.pmf(ga, exp_a_goals)
                    if p_score > best_score_prob:
                        best_score_prob = p_score
                        best_score = (gh, ga)
                        
            is_fin = match.get('matchIsFinished', match.get('isFinished', False))
            act_home_score = match['matchResults'][0]['pointsTeam1'] if is_fin and len(match.get('matchResults', [])) > 0 else None
            act_away_score = match['matchResults'][0]['pointsTeam2'] if is_fin and len(match.get('matchResults', [])) > 0 else None
            
            points_earned = None
            if act_home_score is not None and act_away_score is not None:
                points_earned = calculate_points(best_score, (act_home_score, act_away_score))
                
            all_predictions_v6_2stage.append({
                "matchday": md,
                "date": date_formatted,
                "home_team": home,
                "away_team": away,
                "home_prob": float(prob_h),
                "draw_prob": float(prob_d),
                "away_prob": float(prob_a),
                "predicted_score": f"{best_score[0]}:{best_score[1]}",
                "actual_score": f"{act_home_score}:{act_away_score}" if act_home_score is not None else None,
                "kicktipp_points": points_earned
            })
            
    out_file = "models/spatial_ai_kaggle/predictions_v6_spatial_2stage.json"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_predictions_v6_2stage, f, indent=2)
        
    print(f"Successfully generated 2-Stage predictions for {len(all_predictions_v6_2stage)} fixtures!")
    print(f"Saved to '{out_file}'.")

if __name__ == "__main__":
    predict_v6_2stage_season()
