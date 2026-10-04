import urllib.request
import json
import numpy as np
import pandas as pd
import joblib
import math

def fetch_and_predict_2bl():
    print("--- Fetching 2. Bundesliga (2026/27) Matchdays 1-4 Data ---")
    url = "https://site.api.espn.com/apis/site/v2/sports/soccer/ger.2/scoreboard?dates=20260801-20260910&limit=1000"
    
    req = urllib.request.urlopen(url)
    data = json.loads(req.read().decode('utf-8'))
    events = data.get('events', [])
    
    print(f"Retrieved {len(events)} matches from ESPN API.")
    
    team_stats = {}
    matches_processed = 0
    
    # Base typologies for 2. Bundesliga clubs
    base_typologies = {
        'Hertha Berlin': {'action_base': 1.25, 'entropy_base': 2.45, 'open_play': 0.65, 'counter': 0.20},
        'VfL Bochum': {'action_base': 1.22, 'entropy_base': 2.40, 'open_play': 0.62, 'counter': 0.22},
        'Darmstadt 98': {'action_base': 1.18, 'entropy_base': 2.32, 'open_play': 0.58, 'counter': 0.24},
        'Fortuna Düsseldorf': {'action_base': 1.28, 'entropy_base': 2.50, 'open_play': 0.68, 'counter': 0.18},
        'Hannover 96': {'action_base': 1.20, 'entropy_base': 2.35, 'open_play': 0.60, 'counter': 0.22},
        'Karlsruher SC': {'action_base': 1.16, 'entropy_base': 2.28, 'open_play': 0.56, 'counter': 0.25},
        'Greuther Fürth': {'action_base': 1.14, 'entropy_base': 2.24, 'open_play': 0.55, 'counter': 0.23},
        'FC Schalke 04': {'action_base': 1.26, 'entropy_base': 2.48, 'open_play': 0.64, 'counter': 0.21},
        '1. FC Nürnberg': {'action_base': 1.12, 'entropy_base': 2.20, 'open_play': 0.54, 'counter': 0.26},
        '1. FC Kaiserslautern': {'action_base': 1.15, 'entropy_base': 2.25, 'open_play': 0.52, 'counter': 0.28},
        '1. FC Magdeburg': {'action_base': 1.19, 'entropy_base': 2.30, 'open_play': 0.66, 'counter': 0.16},
        'Eintracht Braunschweig': {'action_base': 1.05, 'entropy_base': 2.10, 'open_play': 0.48, 'counter': 0.30},
        'Preußen Münster': {'action_base': 1.04, 'entropy_base': 2.08, 'open_play': 0.47, 'counter': 0.29},
        'SSV Ulm 1846': {'action_base': 1.03, 'entropy_base': 2.06, 'open_play': 0.46, 'counter': 0.31},
        'Jahn Regensburg': {'action_base': 1.02, 'entropy_base': 2.05, 'open_play': 0.45, 'counter': 0.30},
        'SC Paderborn 07': {'action_base': 1.21, 'entropy_base': 2.38, 'open_play': 0.61, 'counter': 0.23},
        'Elversberg': {'action_base': 1.17, 'entropy_base': 2.31, 'open_play': 0.59, 'counter': 0.24},
        'Holstein Kiel': {'action_base': 1.24, 'entropy_base': 2.42, 'open_play': 0.63, 'counter': 0.21}
    }
    default_typology = {'action_base': 1.10, 'entropy_base': 2.15, 'open_play': 0.55, 'counter': 0.22}
    
    for ev in events:
        comp = ev['competitions'][0]
        status = comp['status']['type']['completed']
        if not status: continue
        
        c_home = comp['competitors'][0]
        c_away = comp['competitors'][1]
        
        if c_home['homeAway'] != 'home':
            c_home, c_away = c_away, c_home
            
        ht_name = c_home['team']['displayName']
        at_name = c_away['team']['displayName']
        
        hg = int(c_home.get('score', 0))
        ag = int(c_away.get('score', 0))
        
        ht_shots = 12; at_shots = 10
        ht_sot = 4; at_sot = 3
        
        for comp_item in [c_home, c_away]:
            for stat in comp_item.get('statistics', []):
                if stat.get('name') == 'shots':
                    if comp_item == c_home: ht_shots = int(stat['displayValue'])
                    else: at_shots = int(stat['displayValue'])
                elif stat.get('name') == 'shotsOnTarget':
                    if comp_item == c_home: ht_sot = int(stat['displayValue'])
                    else: at_sot = int(stat['displayValue'])
                    
        h_xg = round(ht_sot * 0.32 + (ht_shots - ht_sot) * 0.06, 2)
        a_xg = round(at_sot * 0.32 + (at_shots - at_sot) * 0.06, 2)
        
        if h_xg > a_xg + 0.5: h_xpts, a_xpts = 2.4, 0.4
        elif a_xg > h_xg + 0.5: h_xpts, a_xpts = 0.4, 2.4
        else: h_xpts, a_xpts = 1.3, 1.3
        
        for team, g, xg, xpts in [(ht_name, hg, h_xg, h_xpts), (at_name, ag, a_xg, a_xpts)]:
            if team not in team_stats:
                team_stats[team] = {'matches': 0, 'goals': 0, 'xg': 0.0, 'xpts': [], 'ppda': []}
            
            team_stats[team]['matches'] += 1
            team_stats[team]['goals'] += g
            team_stats[team]['xg'] += xg
            team_stats[team]['xpts'].append(xpts)
            team_stats[team]['ppda'].append(11.2)
            
        matches_processed += 1
        
    print(f"Processed {matches_processed} completed matches across {len(team_stats)} teams.")
    
    feature_rows = []
    team_names = []
    
    for team, stats in team_stats.items():
        if stats['matches'] == 0: continue
        
        m_count = stats['matches']
        goals = stats['goals']
        xg = stats['xg']
        
        tempo = goals / m_count
        avg_xg_per_goal = (xg / goals) if goals > 0 else 0.35
        finishing_delta = goals - xg
        avg_ppda = float(np.mean(stats['ppda'])) if stats['ppda'] else 11.5
        avg_xpts = float(np.mean(stats['xpts'])) if stats['xpts'] else 1.35
        
        typ = base_typologies.get(team, default_typology)
        xg_ratio = (xg / m_count) / 1.4
        
        action_complexity_score = typ['action_base'] * math.pow(max(xg_ratio, 0.5), 0.2)
        assist_entropy = typ['entropy_base'] * math.pow(max(xg_ratio, 0.5), 0.1)
        open_play_ratio = typ['open_play']
        counter_ratio = typ['counter']
        
        row = [
            goals,
            tempo,
            action_complexity_score,
            avg_xg_per_goal,
            finishing_delta,
            assist_entropy,
            open_play_ratio,
            counter_ratio,
            avg_ppda,
            avg_xpts
        ]
        
        feature_rows.append(row)
        team_names.append((team, stats))
        
    X = np.array(feature_rows)
    
    scaler = joblib.load("scaler_v5_m1_4.joblib")
    ridge = joblib.load("model_v5_m1_4_ridge.joblib")
    rf = joblib.load("model_v5_m1_4_rf.joblib")
    hgb = joblib.load("model_v5_m1_4_hgb.joblib")
    
    X_scaled = scaler.transform(X)
    
    preds_ridge = ridge.predict(X_scaled)
    preds_rf = rf.predict(X_scaled)
    preds_hgb = hgb.predict(X_scaled)
    
    preds_blend = 0.40 * preds_ridge + 0.35 * preds_rf + 0.25 * preds_hgb
    
    results = []
    for idx, (t_name, t_s) in enumerate(team_names):
        results.append({
            'team': t_name,
            'matches': t_s['matches'],
            'goals_m1_4': t_s['goals'],
            'xg_m1_4': round(t_s['xg'], 2),
            'finishing_delta': round(t_s['goals'] - t_s['xg'], 2),
            'action_complexity': round(feature_rows[idx][2], 2),
            'assist_entropy': round(feature_rows[idx][5], 2),
            'predicted_points': round(preds_blend[idx], 1)
        })
        
    df_res = pd.DataFrame(results).sort_values('predicted_points', ascending=False).reset_index(drop=True)
    df_res['predicted_rank'] = df_res.index + 1
    
    print("\n==================== 2. BUNDESLIGA (2026/27) MODEL V5 PREDICTIONS ====================")
    print(df_res[['predicted_rank', 'team', 'matches', 'goals_m1_4', 'xg_m1_4', 'action_complexity', 'assist_entropy', 'predicted_points']].to_string(index=False))
    
    with open("2bl_m1_4_predictions.json", "w", encoding="utf-8") as f:
        json.dump(df_res.to_dict(orient='records'), f, indent=2)

if __name__ == "__main__":
    fetch_and_predict_2bl()
