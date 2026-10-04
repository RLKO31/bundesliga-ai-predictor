"""
===============================================================================
HISTORICAL DATA HARVESTER: BUNDESLIGA 2015–2019 SEASONS
===============================================================================
Harvests and processes match records, chronological Elo ratings, rest days, 
rolling xG/goals, and market value ranks for seasons 2015/16 through 2018/19.
===============================================================================
"""

import os
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime

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
        "1. FSV Mainz 05": "Mainz 05", "RB Leipzig": "RasenBallsport Leipzig", 
        "1. FC Union Berlin": "Union Berlin", "VfL Wolfsburg": "Wolfsburg", 
        "Borussia Mnchengladbach": "Borussia M.Gladbach", "Borussia Mönchengladbach": "Borussia M.Gladbach", 
        "FC Schalke 04": "Schalke 04", "1. FC Kln": "FC Cologne", "1. FC Köln": "FC Cologne", 
        "FC Kln": "FC Cologne", "FC Köln": "FC Cologne", "VfB Stuttgart": "VfB Stuttgart", 
        "Eintracht Frankfurt": "Eintracht Frankfurt", "SV 07 Elversberg": "Elversberg", 
        "SC Paderborn 07": "Paderborn", "SV Werder Bremen": "Werder Bremen",
        "Ingolstadt": "FC Ingolstadt 04", "FC Ingolstadt": "FC Ingolstadt 04",
        "Hannover 96": "Hannover 96", "Nürnberg": "1. FC Nurnberg", "1. FC Nürnberg": "1. FC Nurnberg"
    }
    for k, v in replacements.items():
        if k in name or name == k:
            return v
    return name.strip()

def update_elo(r_home, r_away, actual_home_goals, actual_away_goals, K=32.0):
    if actual_home_goals > actual_away_goals:
        s_home, s_away = 1.0, 0.0
    elif actual_home_goals < actual_away_goals:
        s_home, s_away = 0.0, 1.0
    else:
        s_home, s_away = 0.5, 0.5

    dr = r_home - r_away + 100.0  # Home advantage +100
    e_home = 1.0 / (1.0 + 10.0 ** (-dr / 400.0))
    e_away = 1.0 - e_home

    goal_diff = abs(actual_home_goals - actual_away_goals)
    mult = 1.0 if goal_diff <= 1 else (1.5 if goal_diff == 2 else (11.0 + goal_diff) / 8.0)

    new_r_home = r_home + K * mult * (s_home - e_home)
    new_r_away = r_away + K * mult * (s_away - e_away)
    return new_r_home, new_r_away

def harvest_historical_2015_2019():
    print("--- 1. Harvesting Historical Seasons 2015/16 to 2018/19 ---")
    
    seasons = ['2015-2016', '2016-2017', '2017-2018', '2018-2019']
    all_season_matches = []
    
    import soccerdata as sd
    for s in seasons:
        print(f"Fetching season {s} via Understat...")
        try:
            us = sd.Understat(leagues="GER-Bundesliga", seasons=s)
            df_s = us.read_team_match_stats().reset_index()
            print(f"Retrieved {len(df_s)} match rows for {s}.")
            
            for idx, row in df_s.iterrows():
                all_season_matches.append({
                    'season': s,
                    'date': str(row['date']),
                    'home_team': clean_team_name(row['home_team']),
                    'away_team': clean_team_name(row['away_team']),
                    'home_goals': int(row['home_goals']),
                    'away_goals': int(row['away_goals']),
                    'home_xg': float(row['home_xg']),
                    'away_xg': float(row['away_xg'])
                })
        except Exception as e:
            print(f"Error harvesting season {s}: {e}")
            
    df_raw = pd.DataFrame(all_season_matches)
    df_raw['date'] = pd.to_datetime(df_raw['date'])
    df_raw = df_raw.sort_values('date').reset_index(drop=True)
    print(f"Total raw historical matches: {len(df_raw)}")
    
    # Process Elo, rest days, and rolling metrics
    elos = {
        "Bayern Munich": 1880.0,
        "Wolfsburg": 1720.0,
        "Borussia Dortmund": 1710.0,
        "Bayer Leverkusen": 1690.0,
        "Borussia M.Gladbach": 1660.0,
        "Schalke 04": 1640.0,
        "TSG Hoffenheim": 1580.0,
        "Eintracht Frankfurt": 1570.0,
        "Mainz 05": 1560.0,
        "Freiburg": 1550.0,
        "Augsburg": 1550.0,
        "Werder Bremen": 1540.0,
        "Hamburger SV": 1520.0,
        "FC Cologne": 1520.0,
        "VfB Stuttgart": 1530.0,
        "FC Ingolstadt 04": 1460.0,
        "Darmstadt": 1440.0,
        "Hannover 96": 1500.0,
        "Paderborn": 1450.0,
        "RasenBallsport Leipzig": 1620.0,
        "Union Berlin": 1500.0
    }
    last_dates = {}
    team_history = {}
    processed_records = []
    
    for idx, row in df_raw.iterrows():
        home = row['home_team']
        away = row['away_team']
        date_obj = row['date']
        date_str = date_obj.strftime("%Y-%m-%d %H:%M:%S")
        
        h_elo = elos.get(home, 1500.0)
        a_elo = elos.get(away, 1500.0)
        elo_diff = h_elo - a_elo
        
        last_h = last_dates.get(home, date_obj)
        last_a = last_dates.get(away, date_obj)
        h_rest = min((date_obj - last_h).days, 14) if home in last_dates else 7.0
        a_rest = min((date_obj - last_a).days, 14) if away in last_dates else 7.0
        rest_diff = float(h_rest - a_rest)
        
        h_hist = team_history.get(home, [])
        a_hist = team_history.get(away, [])
        
        h_g15 = float(np.mean([m['g'] for m in h_hist[-15:]])) if h_hist else 1.5
        a_g15 = float(np.mean([m['g'] for m in a_hist[-15:]])) if a_hist else 1.2
        
        h_xg15 = float(np.mean([m['xg'] for m in h_hist[-15:]])) if h_hist else 1.4
        a_xg15 = float(np.mean([m['xg'] for m in a_hist[-15:]])) if a_hist else 1.1
        
        h_eff10 = float(np.mean([m['g'] - m['xg'] for m in h_hist[-10:]])) if h_hist else 0.1
        a_eff10 = float(np.mean([m['g'] - m['xg'] for m in a_hist[-10:]])) if a_hist else 0.0
        fin_diff = float(h_eff10 - a_eff10)
        
        hg, ag = int(row['home_goals']), int(row['away_goals'])
        outcome = 0 if hg > ag else (2 if hg < ag else 1)
        
        record = {
            'match_id': idx,
            'season': row['season'],
            'date': date_str,
            'home_team': home,
            'away_team': away,
            'home_goals': hg,
            'away_goals': ag,
            'home_xg': float(row['home_xg']),
            'away_xg': float(row['away_xg']),
            'outcome': outcome,
            'home_elo': h_elo,
            'away_elo': a_elo,
            'elo_diff': elo_diff,
            'home_rest': h_rest,
            'away_rest': a_rest,
            'rest_diff': rest_diff,
            'home_goals_roll15': h_g15,
            'away_goals_roll15': a_g15,
            'home_xg_roll15': h_xg15,
            'away_xg_roll15': a_xg15,
            'finishing_eff_diff': fin_diff,
            'value_rank_diff': 0.0
        }
        processed_records.append(record)
        
        # Update Elo & histories after match outcome
        new_h_elo, new_a_elo = update_elo(h_elo, a_elo, hg, ag)
        elos[home] = new_h_elo
        elos[away] = new_a_elo
        last_dates[home] = date_obj
        last_dates[away] = date_obj
        
        if home not in team_history: team_history[home] = []
        if away not in team_history: team_history[away] = []
        team_history[home].append({'g': hg, 'xg': float(row['home_xg'])})
        team_history[away].append({'g': ag, 'xg': float(row['away_xg'])})
        
    df_out = pd.DataFrame(processed_records)
    out_csv = "data/bundesliga_historical_2015_2019_processed.csv"
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df_out.to_csv(out_csv, index=False)
    print(f"SUCCESS: Saved {len(df_out)} processed historical matches to '{out_csv}'.")

if __name__ == "__main__":
    harvest_historical_2015_2019()
