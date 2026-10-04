import urllib.request
import json
import pandas as pd
import soccerdata as sd
import time
from datetime import datetime

def harvest_season_data(season_years):
    """
    season_years: string like '2023-2024'
    """
    print(f"\n==================== HARVESTING SEASON {season_years} ====================")
    
    year_start = season_years.split("-")[0]
    year_end = season_years.split("-")[1]
    
    espn_dates = f"{year_start}0801-{year_end}0630"
    understat_season = season_years
    
    all_matches = []

    # 1. Gather Bundesliga via Understat (gives advanced xG, PPDA, etc.)
    print("--- 1. Harvesting Bundesliga from Understat ---")
    try:
        us = sd.Understat(leagues="GER-Bundesliga", seasons=understat_season)
        us_stats = us.read_team_match_stats()
        print(f"Retrieved {len(us_stats)} match rows from Understat.")
        
        # Understat returns exactly 1 row per game with home_ and away_ columns
        us_stats = us_stats.reset_index()
        for idx, row in us_stats.iterrows():
            all_matches.append({
                'competition': 'Bundesliga',
                'season': season_years,
                'date': str(row['date']),
                'home_team': row['home_team'],
                'away_team': row['away_team'],
                'home_goals': int(row['home_goals']) if not pd.isna(row['home_goals']) else None,
                'away_goals': int(row['away_goals']) if not pd.isna(row['away_goals']) else None,
                'home_xg': float(row['home_xg']) if not pd.isna(row['home_xg']) else None,
                'away_xg': float(row['away_xg']) if not pd.isna(row['away_xg']) else None,
                'home_ppda': float(row['home_ppda']) if not pd.isna(row['home_ppda']) else None,
                'away_ppda': float(row['away_ppda']) if not pd.isna(row['away_ppda']) else None,
                'home_xpts': float(row['home_expected_points']) if not pd.isna(row['home_expected_points']) else None,
                'away_xpts': float(row['away_expected_points']) if not pd.isna(row['away_expected_points']) else None,
                'status': 'STATUS_FULL_TIME'
            })
    except Exception as e:
        print("Error harvesting Understat:", e)

    # 2. Gather DFB-Pokal & European Cups via ESPN API
    espn_comps = {
        'DFB-Pokal': 'ger.dfb_pokal',
        'Champions League': 'uefa.champions',
        'Europa League': 'uefa.europa'
    }
    
    for comp_name, slug in espn_comps.items():
        print(f"--- Harvesting {comp_name} from ESPN API ---")
        url = f"http://site.api.espn.com/apis/site/v2/sports/soccer/{slug}/scoreboard?dates={espn_dates}&limit=1000"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            events = data.get("events", [])
            print(f"Retrieved {len(events)} matches for {comp_name}.")
            
            for e in events:
                try:
                    date_str = e.get("date")
                    name = e.get("name")
                    status_type = e.get("status", {}).get("type", {})
                    status_name = status_type.get("name") # e.g. STATUS_FULL_TIME
                    
                    comp = e['competitions'][0]
                    home_data = comp['competitors'][0]
                    away_data = comp['competitors'][1]
                    
                    # ESPN home/away is defined by competitor order or homeAway field
                    if home_data.get("homeAway") == "away":
                        home_data, away_data = away_data, home_data
                        
                    home_team = home_data['team']['displayName']
                    away_team = away_data['team']['displayName']
                    
                    home_goals = int(home_data.get('score', 0))
                    away_goals = int(away_data.get('score', 0))
                    
                    # Add to matches
                    all_matches.append({
                        'competition': comp_name,
                        'season': season_years,
                        'date': date_str,
                        'home_team': home_team,
                        'away_team': away_team,
                        'home_goals': home_goals,
                        'away_goals': away_goals,
                        'home_xg': None,
                        'away_xg': None,
                        'home_ppda': None,
                        'away_ppda': None,
                        'home_xpts': None,
                        'away_xpts': None,
                        'status': status_name
                    })
                except Exception as ex:
                    pass
        except Exception as e:
            print(f"Error harvesting ESPN {comp_name}:", e)
        time.sleep(1) # Polite pause

    return pd.DataFrame(all_matches)

if __name__ == "__main__":
    seasons = [
        "2021-2022",
        "2022-2023",
        "2023-2024",
        "2024-2025",
        "2025-2026"
    ]
    
    all_seasons_dfs = []
    for s in seasons:
        df_season = harvest_season_data(s)
        all_seasons_dfs.append(df_season)
        # Sleep to be friendly to APIs
        time.sleep(2)
        
    df_all = pd.concat(all_seasons_dfs, ignore_index=True)
    print(f"\n==================== HARVESTING SUMMARY ====================")
    print(f"Total matches harvested: {len(df_all)}")
    print(df_all['competition'].value_counts())
    
    # Save to CSV
    df_all.to_csv("bundesliga_multicomp_raw.csv", index=False)
    print("Saved combined raw harvested data to 'bundesliga_multicomp_raw.csv'")
