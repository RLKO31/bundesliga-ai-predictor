import pandas as pd
import numpy as np
import json

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
        "Borussia Mönchengladbach": "Borussia M.Gladbach", "Borussia M. Gladbach": "Borussia M.Gladbach",
        "FC Schalke 04": "Schalke 04", "Arminia Bielefeld": "Arminia Bielefeld",
        "Fortuna Dsseldorf": "Fortuna Dusseldorf", "Fortuna Düsseldorf": "Fortuna Dusseldorf",
        "1. FC Kln": "FC Cologne", "1. FC Köln": "FC Cologne", "FC Kln": "FC Cologne",
        "FC Köln": "FC Cologne", "Hrtha BSC": "Hertha Berlin", "Hertha BSC": "Hertha Berlin",
        "Werder Bremen": "Werder Bremen", "St. Pauli": "St. Pauli", "VfB Stuttgart": "VfB Stuttgart",
        "Eintracht Frankfurt": "Eintracht Frankfurt", "Holstein Kiel": "Holstein Kiel"
    }
    for k, v in replacements.items():
        if k in name or name == k:
            return v
    name = name.replace("\ufffd", "u").replace("\u00fd", "u").replace("ö", "o").replace("ä", "a").replace("ü", "u")
    return name.strip()

def calculate_elo_rest_fatigue(df):
    df['date'] = pd.to_datetime(df['date'], format='mixed', utc=True)
    df = df.sort_values(by='date').reset_index(drop=True)
    
    elos = {}
    last_match_dates = {}
    last_match_comps = {}
    
    home_elo_before = []
    away_elo_before = []
    home_rest_days = []
    away_rest_days = []
    home_midweek_europe = []
    away_midweek_europe = []
    
    K = 32
    H = 80 # Home advantage
    
    for idx, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        date = row['date']
        comp = row['competition']
        
        # 1. Elos
        h_elo = elos.get(home, 1500.0)
        a_elo = elos.get(away, 1500.0)
        home_elo_before.append(h_elo)
        away_elo_before.append(a_elo)
        
        # 2. Rest Days
        h_rest = (date - last_match_dates[home]).days if home in last_match_dates else 14.0
        a_rest = (date - last_match_dates[away]).days if away in last_match_dates else 14.0
        home_rest_days.append(min(h_rest, 14.0))
        away_rest_days.append(min(a_rest, 14.0))
        
        # 3. European Fatigue Coefficient (previous match was European Cup in last 5 days)
        def check_europe_midweek(team, rest, match_date):
            if team in last_match_dates and team in last_match_comps:
                prev_comp = last_match_comps[team]
                is_euro = any(x in str(prev_comp) for x in ['Champions League', 'Europa League', 'Conference League', 'UEFA'])
                if rest <= 5 and is_euro:
                    return 1.0
            return 0.0
            
        home_midweek_europe.append(check_europe_midweek(home, h_rest, date))
        away_midweek_europe.append(check_europe_midweek(away, a_rest, date))
        
        # Update trackers
        last_match_dates[home] = date
        last_match_dates[away] = date
        last_match_comps[home] = comp
        last_match_comps[away] = comp
        
        # 4. Update Elos
        hg = row['home_goals']
        ag = row['away_goals']
        E_h = 1.0 / (1.0 + 10.0 ** ((a_elo - (h_elo + H)) / 400.0))
        E_a = 1.0 - E_h
        S_h, S_a = (1.0, 0.0) if hg > ag else ((0.0, 1.0) if hg < ag else (0.5, 0.5))
        
        gd = abs(hg - ag)
        mult = 1.5 if gd == 2 else (1.75 + (gd - 3) / 8.0 if gd >= 3 else 1.0)
        
        elos[home] = h_elo + K * mult * (S_h - E_h)
        elos[away] = a_elo + K * mult * (S_a - E_a)
        
    df['home_elo'] = home_elo_before
    df['away_elo'] = away_elo_before
    df['home_rest'] = home_rest_days
    df['away_rest'] = away_rest_days
    df['home_midweek_europe'] = home_midweek_europe
    df['away_midweek_europe'] = away_midweek_europe
    df['europe_fatigue_diff'] = df['home_midweek_europe'] - df['away_midweek_europe']
    
    return df, elos, last_match_dates, last_match_comps

def calculate_rolling_and_motivation_features(df):
    df = df.sort_values(by='date').reset_index(drop=True)
    
    team_history = {} # team -> stats history
    table_stats = {} # (season, team) -> points, gd, goals_scored, matches_played
    
    # Track features
    h_roll_g3, h_roll_g15, h_roll_xg3, h_roll_xg15, h_roll_xgdiff10 = [], [], [], [], []
    a_roll_g3, a_roll_g15, a_roll_xg3, a_roll_xg15, a_roll_xgdiff10 = [], [], [], [], []
    
    # Finishing efficiency features
    h_fin_eff_roll10, a_fin_eff_roll10 = [], []
    
    # Motivation features
    h_motivation, a_motivation = [], []
    
    for idx, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        season = row['season']
        comp = row['competition']
        
        h_hist = team_history.get(home, [])
        a_hist = team_history.get(away, [])
        
        # 1. Rolling Average helper
        def get_rolling_avg(history, key, window, default_val=1.2):
            vals = [h[key] for h in history if h[key] is not None and not pd.isna(h[key])]
            if not vals:
                return default_val
            return np.mean(vals[-window:])
            
        def get_rolling_xg_diff(history, window, default_val=0.0):
            diffs = []
            for h in history:
                if (h['xg'] is not None and h['xg_conceded'] is not None and 
                    not pd.isna(h['xg']) and not pd.isna(h['xg_conceded'])):
                    diffs.append(h['xg'] - h['xg_conceded'])
            if not diffs:
                return default_val
            return np.mean(diffs[-window:])
            
        # Append standard rolling
        h_roll_g3.append(get_rolling_avg(h_hist, 'goals', 3, 1.3))
        h_roll_g15.append(get_rolling_avg(h_hist, 'goals', 15, 1.3))
        h_roll_xg3.append(get_rolling_avg(h_hist, 'xg', 3, 1.3))
        h_roll_xg15.append(get_rolling_avg(h_hist, 'xg', 15, 1.3))
        h_roll_xgdiff10.append(get_rolling_xg_diff(h_hist, 10, 0.0))
        
        a_roll_g3.append(get_rolling_avg(a_hist, 'goals', 3, 1.2))
        a_roll_g15.append(get_rolling_avg(a_hist, 'goals', 15, 1.2))
        a_roll_xg3.append(get_rolling_avg(a_hist, 'xg', 3, 1.2))
        a_roll_xg15.append(get_rolling_avg(a_hist, 'xg', 15, 1.2))
        a_roll_xgdiff10.append(get_rolling_xg_diff(a_hist, 10, 0.0))
        
        # Finishing Efficiency: rolling goals - xg over last 10 games
        h_g10 = get_rolling_avg(h_hist, 'goals', 10, 1.3)
        h_xg10 = get_rolling_avg(h_hist, 'xg', 10, 1.3)
        h_fin_eff_roll10.append(h_g10 - h_xg10)
        
        a_g10 = get_rolling_avg(a_hist, 'goals', 10, 1.2)
        a_xg10 = get_rolling_avg(a_hist, 'xg', 10, 1.2)
        a_fin_eff_roll10.append(a_g10 - a_xg10)
        
        # 2. Dynamic League Table and Motivation Calculation
        # Initialize stats for teams in this season if not present
        if comp == 'Bundesliga':
            for t in [home, away]:
                if (season, t) not in table_stats:
                    table_stats[(season, t)] = {
                        "points": 0, "goals_scored": 0, "goals_conceded": 0, "matches_played": 0
                    }
            
            # Sort teams in this season to find positions
            season_teams = [t for (s, t) in table_stats.keys() if s == season]
            
            def get_rank(t):
                stats = table_stats[(season, t)]
                gd = stats["goals_scored"] - stats["goals_conceded"]
                return (stats["points"], gd, stats["goals_scored"])
                
            sorted_teams = sorted(season_teams, key=get_rank, reverse=True)
            
            home_pos = sorted_teams.index(home) + 1 if home in sorted_teams else 9.5
            away_pos = sorted_teams.index(away) + 1 if away in sorted_teams else 9.5
            
            h_played = table_stats[(season, home)]["matches_played"]
            a_played = table_stats[(season, away)]["matches_played"]
            
            # Motivation is active on matchdays 29 to 34 (matches_played >= 28)
            # High motivation if fighting for Europe (1-6) or survival (15-18)
            h_mot = 1.0 if h_played >= 28 and (home_pos <= 6 or home_pos >= 15) else 0.0
            a_mot = 1.0 if a_played >= 28 and (away_pos <= 6 or away_pos >= 15) else 0.0
            
            h_motivation.append(h_mot)
            a_motivation.append(a_mot)
            
            # Update dynamic table stats AFTER calculations
            hg = row['home_goals']
            ag = row['away_goals']
            
            table_stats[(season, home)]["matches_played"] += 1
            table_stats[(season, away)]["matches_played"] += 1
            table_stats[(season, home)]["goals_scored"] += hg
            table_stats[(season, home)]["goals_conceded"] += ag
            table_stats[(season, away)]["goals_scored"] += ag
            table_stats[(season, away)]["goals_conceded"] += hg
            
            if hg > ag:
                table_stats[(season, home)]["points"] += 3
            elif hg < ag:
                table_stats[(season, away)]["points"] += 3
            else:
                table_stats[(season, home)]["points"] += 1
                table_stats[(season, away)]["points"] += 1
        else:
            h_motivation.append(0.0)
            a_motivation.append(0.0)
            
        # 3. Save to history
        h_hist.append({
            'goals': row['home_goals'],
            'xg': row['home_xg'],
            'xg_conceded': row['away_xg'],
            'goals_conceded': row['away_goals']
        })
        a_hist.append({
            'goals': row['away_goals'],
            'xg': row['away_xg'],
            'xg_conceded': row['home_xg'],
            'goals_conceded': row['home_goals']
        })
        team_history[home] = h_hist
        team_history[away] = a_hist
        
    df['home_goals_roll3'] = h_roll_g3
    df['home_goals_roll15'] = h_roll_g15
    df['home_xg_roll3'] = h_roll_xg3
    df['home_xg_roll15'] = h_roll_xg15
    df['home_xg_diff_roll10'] = h_roll_xgdiff10
    
    df['away_goals_roll3'] = a_roll_g3
    df['away_goals_roll15'] = a_roll_g15
    df['away_xg_roll3'] = a_roll_xg3
    df['away_xg_roll15'] = a_roll_xg15
    df['away_xg_diff_roll10'] = a_roll_xgdiff10
    
    df['home_finishing_eff_roll10'] = h_fin_eff_roll10
    df['away_finishing_eff_roll10'] = a_fin_eff_roll10
    df['finishing_eff_diff'] = df['home_finishing_eff_roll10'] - df['away_finishing_eff_roll10']
    
    df['home_motivation'] = h_motivation
    df['away_motivation'] = a_motivation
    df['motivation_diff'] = df['home_motivation'] - df['away_motivation']
    
    return df, team_history

if __name__ == "__main__":
    df = pd.read_csv("bundesliga_multicomp_raw.csv")
    print("Standardizing team names (v2)...")
    df['home_team'] = df['home_team'].apply(clean_team_name)
    df['away_team'] = df['away_team'].apply(clean_team_name)
    
    print("Calculating Elo, Rest, and Midweek Fatigue (v2)...")
    df, final_elos, last_match_dates, last_match_comps = calculate_elo_rest_fatigue(df)
    
    print("Calculating Rolling, Finishing Efficiency, and Motivation Features (v2)...")
    df, team_history = calculate_rolling_and_motivation_features(df)
    
    # Add squad ranks
    print("Adding squad market value ranks (v2)...")
    ranks = {
        "2021-2022": {
            "Bayern Munich": 1, "Borussia Dortmund": 2, "RasenBallsport Leipzig": 3,
            "Bayer Leverkusen": 4, "Wolfsburg": 5, "Borussia M.Gladbach": 6,
            "Eintracht Frankfurt": 7, "Hoffenheim": 8, "VfB Stuttgart": 9,
            "Freiburg": 10, "Hertha Berlin": 11, "Mainz 05": 12, "Union Berlin": 13,
            "FC Cologne": 14, "Augsburg": 15, "Arminia Bielefeld": 16, "Bochum": 17,
            "Greuther Fuerth": 18
        },
        "2022-2023": {
            "Bayern Munich": 1, "Borussia Dortmund": 2, "RasenBallsport Leipzig": 3,
            "Bayer Leverkusen": 4, "Eintracht Frankfurt": 5, "Wolfsburg": 6,
            "Borussia M.Gladbach": 7, "Hoffenheim": 8, "VfB Stuttgart": 9,
            "Freiburg": 10, "Union Berlin": 11, "Mainz 05": 12, "Hertha Berlin": 13,
            "FC Cologne": 14, "Augsburg": 15, "Werder Bremen": 16, "Schalke 04": 17,
            "Bochum": 18
        },
        "2023-2024": {
            "Bayern Munich": 1, "Bayer Leverkusen": 2, "RasenBallsport Leipzig": 3,
            "Borussia Dortmund": 4, "Eintracht Frankfurt": 5, "Wolfsburg": 6,
            "Borussia M.Gladbach": 7, "Hoffenheim": 8, "Freiburg": 9,
            "VfB Stuttgart": 10, "Union Berlin": 11, "Mainz 05": 12, "Augsburg": 13,
            "FC Cologne": 14, "Werder Bremen": 15, "Bochum": 16, "FC Heidenheim": 17,
            "Darmstadt": 18
        },
        "2024-2025": {
            "Bayern Munich": 1, "Bayer Leverkusen": 2, "RasenBallsport Leipzig": 3,
            "Borussia Dortmund": 4, "VfB Stuttgart": 5, "Eintracht Frankfurt": 6,
            "Wolfsburg": 7, "Freiburg": 8, "Borussia M.Gladbach": 9, "Hoffenheim": 10,
            "Werder Bremen": 11, "Union Berlin": 12, "Augsburg": 13, "Mainz 05": 14,
            "FC Heidenheim": 15, "St. Pauli": 16, "Bochum": 17, "Holstein Kiel": 18
        },
        "2025-2026": {
            "Bayern Munich": 1, "Bayer Leverkusen": 2, "RasenBallsport Leipzig": 3,
            "Borussia Dortmund": 4, "VfB Stuttgart": 5, "Eintracht Frankfurt": 6,
            "Freiburg": 7, "Wolfsburg": 8, "Borussia M.Gladbach": 9, "Hoffenheim": 10,
            "Werder Bremen": 11, "Union Berlin": 12, "Augsburg": 13, "Mainz 05": 14,
            "FC Heidenheim": 15, "St. Pauli": 16, "Bochum": 17, "Holstein Kiel": 18
        }
    }
    
    home_ranks = []
    away_ranks = []
    for idx, row in df.iterrows():
        comp = row['competition']
        season = row['season']
        home = row['home_team']
        away = row['away_team']
        h_rank = 9.5
        a_rank = 9.5
        if comp == 'Bundesliga' and season in ranks:
            season_ranks = ranks[season]
            h_rank = season_ranks.get(home, 9.5)
            a_rank = season_ranks.get(away, 9.5)
        home_ranks.append(h_rank)
        away_ranks.append(a_rank)
        
    df['home_value_rank'] = home_ranks
    df['away_value_rank'] = away_ranks
    df['value_rank_diff'] = df['away_value_rank'] - df['home_value_rank']
    
    df.to_csv("bundesliga_multicomp_processed_v2.csv", index=False)
    print("Updated bundesliga_multicomp_processed_v2.csv with all advanced features!")
    
    # Save latest state to JSON for production predictions
    serialized_dates = {team: dt.strftime("%Y-%m-%d %H:%M:%S") for team, dt in last_match_dates.items()}
    state = {
        'final_elos': final_elos,
        'last_match_dates': serialized_dates,
        'last_match_comps': last_match_comps,
        'team_history': team_history
    }
    with open("latest_state_v2.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
    print("Saved latest ratings and form history to 'latest_state_v2.json'")
