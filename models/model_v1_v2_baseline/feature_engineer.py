import pandas as pd
import numpy as np

def clean_team_name(name):
    if not isinstance(name, str):
        return name
    
    # Common replacements for standardizing to Understat naming convention
    replacements = {
        "FC Augsburg": "Augsburg",
        "VfL Bochum": "Bochum",
        "SV Darmstadt 98": "Darmstadt",
        "1. FC Heidenheim 1846": "FC Heidenheim",
        "1. FC Heidenheim": "FC Heidenheim",
        "SC Freiburg": "Freiburg",
        "SpVgg Greuther Frth": "Greuther Fuerth",
        "SpVgg Greuther Fűrth": "Greuther Fuerth",
        "SpVgg Greuther Fürth": "Greuther Fuerth",
        "Hamburg SV": "Hamburger SV",
        "TSG Hoffenheim": "Hoffenheim",
        "Mainz": "Mainz 05",
        "RB Leipzig": "RasenBallsport Leipzig",
        "1. FC Union Berlin": "Union Berlin",
        "VfL Wolfsburg": "Wolfsburg",
        "Borussia Mnchengladbach": "Borussia M.Gladbach",
        "Borussia Mönchengladbach": "Borussia M.Gladbach",
        "Borussia M. Gladbach": "Borussia M.Gladbach",
        "FC Schalke 04": "Schalke 04",
        "Arminia Bielefeld": "Arminia Bielefeld",
        "Fortuna Dsseldorf": "Fortuna Dusseldorf",
        "Fortuna Düsseldorf": "Fortuna Dusseldorf",
        "1. FC Kln": "FC Cologne",
        "1. FC Köln": "FC Cologne",
        "FC Kln": "FC Cologne",
        "FC Köln": "FC Cologne",
        "Hrtha BSC": "Hertha Berlin",
        "Hertha BSC": "Hertha Berlin",
        "Werder Bremen": "Werder Bremen",
        "St. Pauli": "St. Pauli",
        "VfB Stuttgart": "VfB Stuttgart",
        "Eintracht Frankfurt": "Eintracht Frankfurt",
        "Holstein Kiel": "Holstein Kiel"
    }
    
    # Check if there is a match in our replacements dictionary
    for k, v in replacements.items():
        if k in name or name == k:
            return v
            
    # Replace common encoding bugs for general teams
    name = name.replace("\ufffd", "u").replace("\u00fd", "u").replace("ö", "o").replace("ä", "a").replace("ü", "u")
    name = name.strip()
    return name

def calculate_elo_and_rest(df):
    # Sort chronologically by date
    df['date'] = pd.to_datetime(df['date'], format='mixed', utc=True)
    df = df.sort_values(by='date').reset_index(drop=True)
    
    # Initialize Elos and last match dates
    elos = {}
    last_match_dates = {}
    
    home_elo_before = []
    away_elo_before = []
    home_rest_days = []
    away_rest_days = []
    
    # Elo parameters
    K = 32
    H = 80 # Home advantage
    
    for idx, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        date = row['date']
        
        # 1. Elo Ratings before the match
        h_elo = elos.get(home, 1500.0)
        a_elo = elos.get(away, 1500.0)
        
        home_elo_before.append(h_elo)
        away_elo_before.append(a_elo)
        
        # 2. Rest Days
        if home in last_match_dates:
            h_rest = (date - last_match_dates[home]).days
        else:
            h_rest = 14.0 # default
            
        if away in last_match_dates:
            a_rest = (date - last_match_dates[away]).days
        else:
            a_rest = 14.0 # default
            
        # Cap rest days at 14 to avoid outlier distortion from long breaks
        home_rest_days.append(min(h_rest, 14.0))
        away_rest_days.append(min(a_rest, 14.0))
        
        # Update last match dates
        last_match_dates[home] = date
        last_match_dates[away] = date
        
        # 3. Update Elo Ratings based on match result
        hg = row['home_goals']
        ag = row['away_goals']
        
        # Expected scores
        E_h = 1.0 / (1.0 + 10.0 ** ((a_elo - (h_elo + H)) / 400.0))
        E_a = 1.0 - E_h
        
        # Actual outcome
        if hg > ag:
            S_h, S_a = 1.0, 0.0
        elif hg < ag:
            S_h, S_a = 0.0, 1.0
        else:
            S_h, S_a = 0.5, 0.5
            
        # Goal difference margin multiplier
        gd = abs(hg - ag)
        mult = 1.0
        if gd == 2:
            mult = 1.5
        elif gd >= 3:
            mult = 1.75 + (gd - 3) / 8.0
            
        # Update Elos
        h_elo_new = h_elo + K * mult * (S_h - E_h)
        a_elo_new = a_elo + K * mult * (S_a - E_a)
        
        elos[home] = h_elo_new
        elos[away] = a_elo_new
        
    df['home_elo'] = home_elo_before
    df['away_elo'] = away_elo_before
    df['home_rest'] = home_rest_days
    df['away_rest'] = away_rest_days
    
    return df, elos, last_match_dates

def calculate_rolling_features(df):
    # Calculate rolling metrics (goals, xG, PPDA) for each team
    # Note: We must compute these metrics using chronological order for each team
    # to avoid data leakage! We only look at historical matches for a team before the match date.
    
    # Sort chronologically
    df = df.sort_values(by='date').reset_index(drop=True)
    
    # We will keep a running history of stats for each team
    team_history = {} # team -> list of match dicts
    
    rolling_home_goals_3 = []
    rolling_away_goals_3 = []
    rolling_home_goals_15 = []
    rolling_away_goals_15 = []
    
    rolling_home_xg_3 = []
    rolling_away_xg_3 = []
    rolling_home_xg_15 = []
    rolling_away_xg_15 = []
    
    rolling_home_xg_diff_10 = []
    rolling_away_xg_diff_10 = []
    
    for idx, row in df.iterrows():
        home = row['home_team']
        away = row['away_team']
        
        # 1. Retrieve history BEFORE this match
        h_hist = team_history.get(home, [])
        a_hist = team_history.get(away, [])
        
        # Helper to compute EWMA or simple rolling average
        def get_rolling_avg(history, key, window, default_val=1.2):
            # Filter history for matches where key is not None and not NaN
            vals = [h[key] for h in history if h[key] is not None and not pd.isna(h[key])]
            if not vals:
                return default_val
            # Take last 'window' matches
            vals = vals[-window:]
            return np.mean(vals)
            
        def get_rolling_xg_diff(history, window, default_val=0.0):
            # xG difference = xG scored - xG conceded
            diffs = []
            for h in history:
                if (h['xg'] is not None and h['xg_conceded'] is not None and 
                    not pd.isna(h['xg']) and not pd.isna(h['xg_conceded'])):
                    diffs.append(h['xg'] - h['xg_conceded'])
            if not diffs:
                return default_val
            return np.mean(diffs[-window:])
            
        # Append home metrics
        rolling_home_goals_3.append(get_rolling_avg(h_hist, 'goals', 3, 1.3))
        rolling_home_goals_15.append(get_rolling_avg(h_hist, 'goals', 15, 1.3))
        rolling_home_xg_3.append(get_rolling_avg(h_hist, 'xg', 3, 1.3))
        rolling_home_xg_15.append(get_rolling_avg(h_hist, 'xg', 15, 1.3))
        rolling_home_xg_diff_10.append(get_rolling_xg_diff(h_hist, 10, 0.0))
        
        # Append away metrics
        rolling_away_goals_3.append(get_rolling_avg(a_hist, 'goals', 3, 1.2))
        rolling_away_goals_15.append(get_rolling_avg(a_hist, 'goals', 15, 1.2))
        rolling_away_xg_3.append(get_rolling_avg(a_hist, 'xg', 3, 1.2))
        rolling_away_xg_15.append(get_rolling_avg(a_hist, 'xg', 15, 1.2))
        rolling_away_xg_diff_10.append(get_rolling_xg_diff(a_hist, 10, 0.0))
        
        # 2. Update histories with this match's results
        # For home team
        h_hist.append({
            'goals': row['home_goals'],
            'xg': row['home_xg'],
            'xg_conceded': row['away_xg'],
            'goals_conceded': row['away_goals']
        })
        # For away team
        a_hist.append({
            'goals': row['away_goals'],
            'xg': row['away_xg'],
            'xg_conceded': row['home_xg'],
            'goals_conceded': row['home_goals']
        })
        
        team_history[home] = h_hist
        team_history[away] = a_hist
        
    df['home_goals_roll3'] = rolling_home_goals_3
    df['home_goals_roll15'] = rolling_home_goals_15
    df['home_xg_roll3'] = rolling_home_xg_3
    df['home_xg_roll15'] = rolling_home_xg_15
    df['home_xg_diff_roll10'] = rolling_home_xg_diff_10
    
    df['away_goals_roll3'] = rolling_away_goals_3
    df['away_goals_roll15'] = rolling_away_goals_15
    df['away_xg_roll3'] = rolling_away_xg_3
    df['away_xg_roll15'] = rolling_away_xg_15
    df['away_xg_diff_roll10'] = rolling_away_xg_diff_10
    
    return df, team_history

if __name__ == "__main__":
    df = pd.read_csv("bundesliga_multicomp_raw.csv")
    print("Standardizing team names...")
    df['home_team'] = df['home_team'].apply(clean_team_name)
    df['away_team'] = df['away_team'].apply(clean_team_name)
    
    print("Calculating Elo and Rest Days...")
    df, final_elos, last_match_dates = calculate_elo_and_rest(df)
    
    print("Calculating Rolling Features...")
    df, team_history = calculate_rolling_features(df)
    
    print(f"Processed shape: {df.shape}")
    print("\nFinal Top 10 Elo Ratings:")
    sorted_elos = sorted(final_elos.items(), key=lambda x: x[1], reverse=True)
    for team, rating in sorted_elos[:10]:
        print(f"  - {team}: {rating:.1f}")
        
    # Save processed dataset
    df.to_csv("bundesliga_multicomp_processed.csv", index=False)
    print("Saved processed features to 'bundesliga_multicomp_processed.csv'")
    
    # Calculate market value ranks
    print("Adding squad market value ranks...")
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
    
    df.to_csv("bundesliga_multicomp_processed.csv", index=False)
    print("Updated bundesliga_multicomp_processed.csv with squad market value ranks!")
    
    # Save latest state to JSON for production predictions
    import json
    # Convert dates to string format for serialization
    serialized_dates = {team: dt.strftime("%Y-%m-%d %H:%M:%S") for team, dt in last_match_dates.items()}
    
    state = {
        'final_elos': final_elos,
        'last_match_dates': serialized_dates,
        'team_history': team_history
    }
    with open("latest_state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)
    print("Saved latest team ratings and form history to 'latest_state.json'")
