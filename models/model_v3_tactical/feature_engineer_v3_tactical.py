import pandas as pd
import numpy as np
import json
from datetime import datetime

def engineer_v3_features(input_csv="bundesliga_multicomp_processed_v2.csv", output_csv="bundesliga_multicomp_processed_v3_tactical.csv"):
    print("--- Running Feature Engineering v3 (Pure Tactical & 1D Time-Decay Model) ---")
    df = pd.read_csv(input_csv)
    df['date_dt'] = pd.to_datetime(df['date'])
    df = df.sort_values('date_dt').reset_index(drop=True)
    
    # Exclude all Elo metrics
    elo_cols = [c for c in df.columns if 'elo' in c]
    print(f"Excluding Elo columns: {elo_cols}")
    
    # Store team match histories chronologically
    # Each entry: {'date': dt, 'goals': g, 'goals_conceded': gc, 'xg': xg, 'xg_conceded': xgc, 'ppda': ppda, 'xpts': xpts}
    team_histories = {}
    
    # We will compute decay-weighted metrics for window sizes 1 to 10 and gamma = 0.85
    gamma = 0.85 # Decay factor per game back
    
    # Lists to hold new engineered columns
    new_columns = {}
    for W in range(1, 11):
        for prefix in ['home', 'away']:
            new_columns[f'{prefix}_goals_decay_{W}'] = []
            new_columns[f'{prefix}_xg_decay_{W}'] = []
            new_columns[f'{prefix}_ppda_decay_{W}'] = []
            new_columns[f'{prefix}_xpts_decay_{W}'] = []
            new_columns[f'{prefix}_finishing_eff_decay_{W}'] = []
            new_columns[f'{prefix}_xg_diff_decay_{W}'] = []
            new_columns[f'{prefix}_win_rate_decay_{W}'] = []
            
        # Spatial Pitch Control (3-Zone Dominance)
        for prefix in ['home', 'away']:
            new_columns[f'{prefix}_def_third_{W}'] = []
            new_columns[f'{prefix}_mid_third_{W}'] = []
            new_columns[f'{prefix}_att_third_{W}'] = []
            
        new_columns[f'pressing_diff_{W}'] = []
        new_columns[f'xg_diff_matchup_{W}'] = []

    for idx, row in df.iterrows():
        h_team = row['home_team']
        a_team = row['away_team']
        match_date = row['date_dt']
        
        # Helper to compute weighted rolling statistics for a team over window W
        def get_weighted_stats(team, W, current_date):
            history = team_histories.get(team, [])
            if not history:
                # Default baseline values if no prior history
                return {
                    'goals': 1.3, 'xg': 1.3, 'ppda': 11.5, 'xpts': 1.3,
                    'finishing_eff': 0.0, 'xg_diff': 0.0, 'win_rate': 0.33,
                    'def_third': 30.0, 'mid_third': 40.0, 'att_third': 30.0
                }
            
            # Select last W games
            recent = history[-W:]
            n = len(recent)
            
            # 1D Exponential Time-Decay weights based on days ago: w_k = exp(-lambda * days)
            # or recency position decay: w_k = gamma^(n - 1 - k)
            weights = []
            for k_idx, entry in enumerate(recent):
                days_ago = max((current_date - entry['date']).days, 1)
                # Combine recency index decay and calendar days decay
                w = np.exp(-0.02 * days_ago) * (gamma ** (n - 1 - k_idx))
                weights.append(w)
                
            weights = np.array(weights)
            w_sum = np.sum(weights)
            if w_sum == 0:
                weights = np.ones(n) / n
            else:
                weights = weights / w_sum
                
            g_vals = np.array([e['goals'] for e in recent])
            xg_vals = np.array([e['xg'] for e in recent])
            xgc_vals = np.array([e['xg_conceded'] for e in recent])
            ppda_vals = np.array([e['ppda'] for e in recent])
            xpts_vals = np.array([e['xpts'] for e in recent])
            win_vals = np.array([1.0 if e['goals'] > e['goals_conceded'] else 0.0 for e in recent])
            
            goals_w = np.sum(g_vals * weights)
            xg_w = np.sum(xg_vals * weights)
            xgc_w = np.sum(xgc_vals * weights)
            ppda_w = np.sum(ppda_vals * weights)
            xpts_w = np.sum(xpts_vals * weights)
            fin_eff_w = goals_w - xg_w
            xg_diff_w = xg_w - xgc_w
            win_rate_w = np.sum(win_vals * weights)
            
            # Calculate 3-Zone Spatial Control Ratios
            # High xG creation & low PPDA (high press) yields higher Attacking 1/3 share
            tot_xg = max(xg_w + xgc_w, 0.5)
            xg_share = xg_w / tot_xg
            ppda_factor = np.clip(1.0 - (ppda_w / 25.0), 0.1, 0.9)
            
            att_third = np.clip((xg_share * 0.6 + ppda_factor * 0.4) * 100.0, 15.0, 60.0)
            def_third = np.clip(((1.0 - xg_share) * 0.6 + (1.0 - ppda_factor) * 0.4) * 100.0, 15.0, 60.0)
            mid_third = max(100.0 - (att_third + def_third), 20.0)
            
            # Renormalize to sum to 100%
            tot_zone = att_third + def_third + mid_third
            att_third = (att_third / tot_zone) * 100.0
            def_third = (def_third / tot_zone) * 100.0
            mid_third = (mid_third / tot_zone) * 100.0
            
            return {
                'goals': goals_w, 'xg': xg_w, 'ppda': ppda_w, 'xpts': xpts_w,
                'finishing_eff': fin_eff_w, 'xg_diff': xg_diff_w, 'win_rate': win_rate_w,
                'def_third': def_third, 'mid_third': mid_third, 'att_third': att_third
            }

        # Calculate features for windows 1..10 for home and away
        for W in range(1, 11):
            h_s = get_weighted_stats(h_team, W, match_date)
            a_s = get_weighted_stats(a_team, W, match_date)
            
            new_columns[f'home_goals_decay_{W}'].append(h_s['goals'])
            new_columns[f'home_xg_decay_{W}'].append(h_s['xg'])
            new_columns[f'home_ppda_decay_{W}'].append(h_s['ppda'])
            new_columns[f'home_xpts_decay_{W}'].append(h_s['xpts'])
            new_columns[f'home_finishing_eff_decay_{W}'].append(h_s['finishing_eff'])
            new_columns[f'home_xg_diff_decay_{W}'].append(h_s['xg_diff'])
            new_columns[f'home_win_rate_decay_{W}'].append(h_s['win_rate'])
            new_columns[f'home_def_third_{W}'].append(h_s['def_third'])
            new_columns[f'home_mid_third_{W}'].append(h_s['mid_third'])
            new_columns[f'home_att_third_{W}'].append(h_s['att_third'])
            
            new_columns[f'away_goals_decay_{W}'].append(a_s['goals'])
            new_columns[f'away_xg_decay_{W}'].append(a_s['xg'])
            new_columns[f'away_ppda_decay_{W}'].append(a_s['ppda'])
            new_columns[f'away_xpts_decay_{W}'].append(a_s['xpts'])
            new_columns[f'away_finishing_eff_decay_{W}'].append(a_s['finishing_eff'])
            new_columns[f'away_xg_diff_decay_{W}'].append(a_s['xg_diff'])
            new_columns[f'away_win_rate_decay_{W}'].append(a_s['win_rate'])
            new_columns[f'away_def_third_{W}'].append(a_s['def_third'])
            new_columns[f'away_mid_third_{W}'].append(a_s['mid_third'])
            new_columns[f'away_att_third_{W}'].append(a_s['att_third'])
            
            new_columns[f'pressing_diff_{W}'].append(h_s['ppda'] - a_s['ppda'])
            new_columns[f'xg_diff_matchup_{W}'].append(h_s['xg_diff'] - a_s['xg_diff'])
            
        # Update team history if match was played
        hg = row['home_goals']
        ag = row['away_goals']
        h_xg = row['home_xg'] if not pd.isna(row['home_xg']) else 1.3
        a_xg = row['away_xg'] if not pd.isna(row['away_xg']) else 1.2
        h_ppda = row['home_ppda'] if not pd.isna(row['home_ppda']) else 10.5
        a_ppda = row['away_ppda'] if not pd.isna(row['away_ppda']) else 11.5
        h_xpts = row['home_xpts'] if not pd.isna(row['home_xpts']) else 1.3
        a_xpts = row['away_xpts'] if not pd.isna(row['away_xpts']) else 1.2
        
        if not pd.isna(hg) and not pd.isna(ag):
            if h_team not in team_histories: team_histories[h_team] = []
            if a_team not in team_histories: team_histories[a_team] = []
            
            team_histories[h_team].append({
                'date': match_date, 'goals': float(hg), 'goals_conceded': float(ag),
                'xg': float(h_xg), 'xg_conceded': float(a_xg),
                'ppda': float(h_ppda), 'xpts': float(h_xpts)
            })
            team_histories[a_team].append({
                'date': match_date, 'goals': float(ag), 'goals_conceded': float(hg),
                'xg': float(a_xg), 'xg_conceded': float(h_xg),
                'ppda': float(a_ppda), 'xpts': float(a_xpts)
            })

    # Attach engineered columns to DataFrame
    for col_name, col_data in new_columns.items():
        df[col_name] = col_data
        
    df.to_csv(output_csv, index=False)
    print(f"SUCCESS: Saved {df.shape[0]} rows with {df.shape[1]} features to {output_csv}")

if __name__ == "__main__":
    engineer_v3_features()
