import torch
import pandas as pd
import numpy as np
import joblib
import json
import urllib.request
from datetime import datetime
from scipy.stats import poisson

# Clean team names to standardized keys
def clean_team_name(name):
    if not isinstance(name, str):
        return name
    replacements = {
        "FC Bayern München": "Bayern Munich",
        "FC Bayern Muenchen": "Bayern Munich",
        "Bayern München": "Bayern Munich",
        "Bayern Muenchen": "Bayern Munich",
        "Bayer 04 Leverkusen": "Bayer Leverkusen",
        "Bayer Leverkusen": "Bayer Leverkusen",
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

def predict_v3_season():
    print("--- Running Model v3 (Pure Tactical & 1D Time-Decay) Season Predictions ---")
    
    # 1. Load Model v3 artifacts
    scaler_v3 = joblib.load("scaler_v3_tactical.joblib")
    rf_v3 = joblib.load("model_v3_tactical_rf.joblib")
    hgb_v3 = joblib.load("model_v3_tactical_hgb.joblib")
    reg_home_v3 = joblib.load("model_v3_fused_reg_home.joblib")
    reg_away_v3 = joblib.load("model_v3_fused_reg_away.joblib")
    
    with open("model_v3_optimal_config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        
    optimal_features = config['optimal_features']
    W = config['best_window'] # W = 9
    
    # 2. Fetch OpenLigaDB 2026 fixtures
    url = "https://api.openligadb.de/getmatchdata/bl1/2026"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response:
        raw_fixtures = json.loads(response.read().decode('utf-8'))
        
    print(f"Loaded {len(raw_fixtures)} fixtures from OpenLigaDB.")
    
    # Group fixtures by matchday
    fixtures_by_matchday = {}
    for f in raw_fixtures:
        md = f['group']['groupOrderID']
        if md not in fixtures_by_matchday:
            fixtures_by_matchday[md] = []
        fixtures_by_matchday[md].append(f)
        
    # Load state database for team history
    with open("latest_state_v2.json", "r", encoding="utf-8") as f:
        state = json.load(f)
        
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
    
    gamma = 0.85
    alpha = 1.35
    goal_scale = 0.95
    
    all_predictions_v3 = []
    
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
            
            # --- 1D Time-Decay Weighted Feature Calculation ---
            def get_weighted_stats(team, window_size, current_date):
                history = team_history.get(team, [])
                if not history:
                    return {
                        'goals': 1.3, 'xg': 1.3, 'ppda': 11.5, 'xpts': 1.3,
                        'finishing_eff': 0.0, 'xg_diff': 0.0, 'win_rate': 0.33,
                        'def_third': 30.0, 'mid_third': 40.0, 'att_third': 30.0
                    }
                    
                recent = history[-window_size:]
                n = len(recent)
                
                weights = []
                for k_idx, entry in enumerate(recent):
                    prev_date_str = entry.get('date', date_formatted)
                    try:
                        prev_dt = datetime.strptime(prev_date_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        prev_dt = current_date
                        
                    days_ago = max((current_date - prev_dt).days, 1)
                    w = np.exp(-0.02 * days_ago) * (gamma ** (n - 1 - k_idx))
                    weights.append(w)
                    
                weights = np.array(weights)
                w_sum = np.sum(weights)
                if w_sum == 0: weights = np.ones(n) / n
                else: weights = weights / w_sum
                
                g_vals = np.array([e.get('goals', 1.3) for e in recent])
                xg_vals = np.array([e.get('xg', 1.3) for e in recent])
                xgc_vals = np.array([e.get('xg_conceded', 1.2) for e in recent])
                ppda_vals = np.array([e.get('ppda', 11.5) for e in recent])
                xpts_vals = np.array([e.get('xpts', 1.3) for e in recent])
                win_vals = np.array([1.0 if e.get('goals', 1.3) > e.get('goals_conceded', 1.2) else 0.0 for e in recent])
                
                goals_w = float(np.sum(g_vals * weights))
                xg_w = float(np.sum(xg_vals * weights))
                xgc_w = float(np.sum(xgc_vals * weights))
                ppda_w = float(np.sum(ppda_vals * weights))
                xpts_w = float(np.sum(xpts_vals * weights))
                fin_eff_w = goals_w - xg_w
                xg_diff_w = xg_w - xgc_w
                win_rate_w = float(np.sum(win_vals * weights))
                
                # Spatial 3-Zone Control Ratios
                tot_xg = max(xg_w + xgc_w, 0.5)
                xg_share = xg_w / tot_xg
                ppda_factor = np.clip(1.0 - (ppda_w / 25.0), 0.1, 0.9)
                
                att_third = np.clip((xg_share * 0.6 + ppda_factor * 0.4) * 100.0, 15.0, 60.0)
                def_third = np.clip(((1.0 - xg_share) * 0.6 + (1.0 - ppda_factor) * 0.4) * 100.0, 15.0, 60.0)
                mid_third = max(100.0 - (att_third + def_third), 20.0)
                
                tot_zone = att_third + def_third + mid_third
                att_third = (att_third / tot_zone) * 100.0
                def_third = (def_third / tot_zone) * 100.0
                mid_third = (mid_third / tot_zone) * 100.0
                
                return {
                    'goals': goals_w, 'xg': xg_w, 'ppda': ppda_w, 'xpts': xpts_w,
                    'finishing_eff': fin_eff_w, 'xg_diff': xg_diff_w, 'win_rate': win_rate_w,
                    'def_third': def_third, 'mid_third': mid_third, 'att_third': att_third
                }

            h_s = get_weighted_stats(home, W, date_obj)
            a_s = get_weighted_stats(away, W, date_obj)
            
            h_val = ranks_2026_27.get(home, 9.5)
            a_val = ranks_2026_27.get(away, 9.5)
            val_diff = a_val - h_val
            
            h_rest = 14.0
            a_rest = 14.0
            if home in last_match_dates:
                try: h_rest = min((date_obj - datetime.strptime(last_match_dates[home], "%Y-%m-%d %H:%M:%S")).days, 14.0)
                except: pass
            if away in last_match_dates:
                try: a_rest = min((date_obj - datetime.strptime(last_match_dates[away], "%Y-%m-%d %H:%M:%S")).days, 14.0)
                except: pass
            rest_diff = float(h_rest - a_rest)
            
            feature_vector = [
                h_s['goals'], a_s['goals'],
                h_s['xg'], a_s['xg'],
                h_s['ppda'], a_s['ppda'],
                h_s['xpts'], a_s['xpts'],
                h_s['finishing_eff'], a_s['finishing_eff'],
                h_s['xg_diff'], a_s['xg_diff'],
                h_s['win_rate'], a_s['win_rate'],
                h_s['att_third'], a_s['att_third'],
                h_s['ppda'] - a_s['ppda'], h_s['xg_diff'] - a_s['xg_diff'],
                val_diff, rest_diff
            ]
            
            X_raw = np.array([feature_vector])
            X_scaled = scaler_v3.transform(X_raw)
            
            # Predict Probabilities
            p_rf = rf_v3.predict_proba(X_scaled)[0]
            p_hgb = hgb_v3.predict_proba(X_scaled)[0]
            probs = 0.50 * p_rf + 0.50 * p_hgb
            
            outcomes = ["HOME WIN", "DRAW", "AWAY WIN"]
            recommended_outcome = outcomes[np.argmax(probs)]
            
            # Stacked Regressor Exact Score Tip
            X_fused = np.hstack([X_scaled[0], probs])
            lh = reg_home_v3.predict([X_fused])[0] * goal_scale
            la = reg_away_v3.predict([X_fused])[0] * goal_scale
            lh = np.clip(lh, 0.5, 5.0)
            la = np.clip(la, 0.5, 5.0)
            
            poisson_matrix = np.zeros((7, 7))
            for gh in range(7):
                for ga in range(7):
                    prob = poisson.pmf(gh, lh) * poisson.pmf(ga, la)
                    if gh == ga: prob *= alpha
                    poisson_matrix[gh, ga] = prob
            poisson_matrix /= poisson_matrix.sum()
            
            best_expected_points = -1.0
            best_score = (1, 1)
            for ph in range(6):
                for pa in range(6):
                    exp_pts = 0.0
                    for ah in range(7):
                        for aa in range(7):
                            exp_pts += poisson_matrix[ah, aa] * calculate_points((ph, pa), (ah, aa))
                    if exp_pts > best_expected_points:
                        best_expected_points = exp_pts
                        best_score = (ph, pa)
                        
            predicted_h_goals, predicted_a_goals = best_score
            score_str = f"{predicted_h_goals}:{predicted_a_goals}"
            
            # Determine Tactical Style Badge
            h_style = "Gegenpressing" if h_s['ppda'] < 9.5 else ("Possession Control" if h_s['att_third'] > 45.0 else "Solid Counter")
            a_style = "Gegenpressing" if a_s['ppda'] < 9.5 else ("Possession Control" if a_s['att_third'] > 45.0 else "Solid Counter")
            
            # Dynamic team history update
            if home not in team_history: team_history[home] = []
            if away not in team_history: team_history[away] = []
            
            team_history[home].append({
                'date': date_formatted, 'goals': float(predicted_h_goals), 'goals_conceded': float(predicted_a_goals),
                'xg': float(lh), 'xg_conceded': float(la), 'ppda': float(h_s['ppda']), 'xpts': float(h_s['xpts'])
            })
            team_history[away].append({
                'date': date_formatted, 'goals': float(predicted_a_goals), 'goals_conceded': float(predicted_h_goals),
                'xg': float(la), 'xg_conceded': float(lh), 'ppda': float(a_s['ppda']), 'xpts': float(a_s['xpts'])
            })
            
            last_match_dates[home] = date_formatted
            last_match_dates[away] = date_formatted
            
            all_predictions_v3.append({
                "matchday": int(md),
                "home_team": h_raw,
                "away_team": a_raw,
                "home_clean": home,
                "away_clean": away,
                "date": date_formatted,
                "p_home": float(probs[0]),
                "p_draw": float(probs[1]),
                "p_away": float(probs[2]),
                "tip": recommended_outcome,
                "score": score_str,
                "tactical_info": {
                    "home_att_third": round(h_s['att_third'], 1),
                    "home_mid_third": round(h_s['mid_third'], 1),
                    "home_def_third": round(h_s['def_third'], 1),
                    "away_att_third": round(a_s['att_third'], 1),
                    "away_mid_third": round(a_s['mid_third'], 1),
                    "away_def_third": round(a_s['def_third'], 1),
                    "home_style": h_style,
                    "away_style": a_style,
                    "home_ppda": round(h_s['ppda'], 1),
                    "away_ppda": round(a_s['ppda'], 1)
                }
            })
            
        print(f"Matchday {md} simulated with Model v3.")
        
    with open("predictions_v3_tactical.json", "w", encoding="utf-8") as f:
        json.dump(all_predictions_v3, f, indent=4)
        
    print("\nSUCCESS: Saved 306 Model v3 predictions to predictions_v3_tactical.json!")

if __name__ == "__main__":
    predict_v3_season()
