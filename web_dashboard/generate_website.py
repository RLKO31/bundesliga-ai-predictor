import pandas as pd
import json
from world_cup_map_data import build_map_payload

def generate_website():
    print("--- Generating World Cup 2026 Dashboard Website ---")
    
    # 1. Load the walkthrough CSV
    csv_path = 'deterministic_tournament_walkthrough.csv'
    df = pd.read_csv(csv_path)
    
    # 2. Reconstruct Standings and matches for Groups A-L
    groups_data = {}
    group_names = [chr(i) for i in range(ord('A'), ord('L') + 1)]
    
    # Define teams per group
    groups_teams = {
        'A': ['Mexico', 'South Korea', 'South Africa', 'Czech Republic'],
        'B': ['Canada', 'Switzerland', 'Qatar', 'Bosnia and Herzegovina'],
        'C': ['Brazil', 'Morocco', 'Scotland', 'Haiti'],
        'D': ['US', 'Paraguay', 'Australia', 'Turkey'],
        'E': ['Germany', 'Ecuador', 'Ivory Coast', 'Curaçao'],
        'F': ['Netherlands', 'Japan', 'Tunisia', 'Sweden'],
        'G': ['Belgium', 'Iran', 'Egypt', 'New Zealand'],
        'H': ['Spain', 'Uruguay', 'Saudi Arabia', 'Cape Verde'],
        'I': ['France', 'Senegal', 'Norway', 'Iraq'],
        'J': ['Argentina', 'Algeria', 'Austria', 'Jordan'],
        'K': ['Portugal', 'Democratic Republic of Congo', 'Uzbekistan', 'Colombia'],
        'L': ['England', 'Croatia', 'Ghana', 'Panama']
    }
    
    # Load countries stats to get Elo for table
    data_df = pd.read_csv('world_cup_modeling_data.csv')
    countries_stats = {}
    for idx, row in data_df.sort_values('date').iterrows():
        countries_stats[row['home_team']] = {'elo': row['elo_A'], 'tier': row['tier_A']}
        countries_stats[row['away_team']] = {'elo': row['elo_B'], 'tier': row['tier_B']}
        
    for team in ['US', 'Mexico', 'Canada']:
        if team not in countries_stats:
            countries_stats[team] = {'elo': 1500.0, 'tier': 2}
            
    # Calculate group tables dynamically based on CSV group matches
    for g_name in group_names:
        teams = groups_teams[g_name]
        standings = {t: {'points': 0, 'goals_diff': 0, 'goals_scored': 0} for t in teams}
        
        # Filter matches for this group
        group_df = df[df['Stage'] == f'Group Stage - Group {g_name}']
        matches_list = []
        
        for idx, row in group_df.iterrows():
            tA = row['Team_A']
            tB = row['Team_B']
            score = row['Result_Score']
            winner = row['Winner']
            
            goals_A, goals_B = map(int, score.split('-'))
            
            # Update standings
            if goals_A > goals_B:
                standings[tA]['points'] += 3
            elif goals_A == goals_B:
                standings[tA]['points'] += 1
                standings[tB]['points'] += 1
            else:
                standings[tB]['points'] += 3
                
            standings[tA]['goals_diff'] += (goals_A - goals_B)
            standings[tB]['goals_diff'] += (goals_B - goals_A)
            standings[tA]['goals_scored'] += goals_A
            standings[tB]['goals_scored'] += goals_B
            
            matches_list.append({
                'teamA': tA,
                'teamB': tB,
                'probaA': row['Proba_A_Win'],
                'probaDraw': row['Proba_Draw'],
                'probaB': row['Proba_B_Win'],
                'score': score,
                'winner': winner
            })
            
        # Sort standings
        sorted_group = sorted(
            teams,
            key=lambda t: (
                standings[t]['points'],
                standings[t]['goals_diff'],
                standings[t]['goals_scored'],
                countries_stats[t]['elo']
            ),
            reverse=True
        )
        
        # Determine advancement (top 2 advance, 3rd place can advance)
        standings_list = []
        for rank, t in enumerate(sorted_group):
            standings_list.append({
                'rank': rank + 1,
                'team': t,
                'points': standings[t]['points'],
                'gd': standings[t]['goals_diff'],
                'gs': standings[t]['goals_scored'],
                'elo': int(countries_stats[t]['elo']),
                'tier': int(countries_stats[t]['tier'])
            })
            
        groups_data[g_name] = {
            'standings': standings_list,
            'matches': matches_list
        }
        
    # 3. Parse Knockout Matches
    knockout_data = {
        'Round of 32': [],
        'Round of 16': [],
        'Quarter-finals': [],
        'Semi-finals': [],
        'World Cup Final': []
    }
    
    for stage in knockout_data.keys():
        stage_df = df[df['Stage'] == stage]
        for idx, row in stage_df.iterrows():
            knockout_data[stage].append({
                'teamA': row['Team_A'],
                'teamB': row['Team_B'],
                'probaA': row['Proba_A_Win'],
                'probaDraw': row['Proba_Draw'],
                'probaB': row['Proba_B_Win'],
                'winner': row['Winner'],
                'score': row['Result_Score']
            })
            
    # 4. Build interactive map payload (stadiums, teams/camps, players)
    tournament_matches = []
    for idx, row in df.iterrows():
        tournament_matches.append({
            'stage': row['Stage'],
            'teamA': row['Team_A'],
            'teamB': row['Team_B'],
            'score': row['Result_Score'],
            'winner': row['Winner'],
        })
    map_data = build_map_payload(tournament_matches)

    # Serialize to JSON strings to embed in the website HTML
    groups_json = json.dumps(groups_data, indent=4)
    knockout_json = json.dumps(knockout_data, indent=4)
    map_json = json.dumps(map_data, indent=4)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FIFA World Cup 2026 - Predictive Dashboard</title>
    
    <!-- Premium Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;600;700&display=swap" rel="stylesheet">
    
    <!-- Lucide CDN for beautiful icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <!-- Leaflet for interactive map -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>
    
    <style>
        :root {{
            --bg-deep: #08060f;
            --bg-card: rgba(20, 16, 36, 0.6);
            --bg-card-hover: rgba(28, 22, 50, 0.85);
            --border-glow: rgba(139, 92, 246, 0.15);
            --border-glow-hover: rgba(139, 92, 246, 0.4);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-purple: #8b5cf6;
            --accent-cyan: #06b6d4;
            --accent-pink: #ec4899;
            --glow-cyan: rgba(6, 182, 212, 0.5);
            --glow-purple: rgba(139, 92, 246, 0.5);
            --accent-win: #10b981;
            --accent-loss: #ef4444;
            --accent-draw: #f59e0b;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
            -webkit-font-smoothing: antialiased;
        }}

        body {{
            background: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 10% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(6, 182, 212, 0.08) 0%, transparent 40%);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
            padding-bottom: 5rem;
        }}

        header {{
            position: relative;
            padding: 3rem 2rem 2rem 2rem;
            text-align: center;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            background: rgba(8, 6, 15, 0.8);
            backdrop-filter: blur(20px);
            z-index: 10;
        }}

        .logo-glow {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 150px;
            height: 150px;
            background: var(--accent-purple);
            filter: blur(80px);
            opacity: 0.2;
            pointer-events: none;
        }}

        h1 {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 3rem;
            font-weight: 700;
            letter-spacing: -0.05em;
            background: linear-gradient(to right, #ffffff, #c084fc, #22d3ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        .subtitle {{
            color: var(--text-secondary);
            font-size: 1.1rem;
            font-weight: 300;
            letter-spacing: 0.05em;
            max-width: 700px;
            margin: 0 auto;
        }}

        /* Stats Section */
        .stats-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            max-width: 1200px;
            margin: 2.5rem auto 1rem auto;
            padding: 0 1.5rem;
        }}

        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            backdrop-filter: blur(16px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 3px;
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));
            opacity: 0.7;
        }}

        .stat-card:hover {{
            transform: translateY(-4px);
            border-color: var(--border-glow-hover);
            box-shadow: 0 10px 30px -10px rgba(139, 92, 246, 0.2);
        }}

        .stat-val {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            color: #fff;
            margin-top: 0.25rem;
            background: linear-gradient(to right, #fff, #c084fc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .stat-label {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}

        /* Navigation Tabs */
        .nav-tabs {{
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin: 2.5rem auto;
            max-width: 920px;
            padding: 0.5rem;
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 50px;
            backdrop-filter: blur(12px);
        }}

        .tab-btn {{
            background: transparent;
            border: none;
            padding: 0.75rem 2rem;
            color: var(--text-secondary);
            font-size: 1rem;
            font-weight: 600;
            border-radius: 40px;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .tab-btn:hover {{
            color: #fff;
        }}

        .tab-btn.active {{
            background: linear-gradient(135deg, var(--accent-purple), #6366f1);
            color: #fff;
            box-shadow: 0 4px 15px -4px rgba(139, 92, 246, 0.4);
        }}

        /* Content Container */
        .content-section {{
            display: none;
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 1.5rem;
            animation: fadeIn 0.4s ease-out forwards;
        }}

        .content-section.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Groups Grid */
        .groups-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 2rem;
        }}

        .group-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 1.75rem;
            backdrop-filter: blur(16px);
            transition: all 0.3s ease;
        }}

        .group-card:hover {{
            border-color: var(--border-glow-hover);
            background: var(--bg-card-hover);
            box-shadow: 0 10px 40px -20px rgba(0,0,0,0.5);
        }}

        .group-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.75rem;
        }}

        .group-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .group-title span {{
            color: var(--accent-cyan);
        }}

        .card-tabs {{
            display: flex;
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            padding: 2px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .card-tab-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 0.8rem;
            font-weight: 600;
            padding: 0.35rem 0.85rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .card-tab-btn.active {{
            background: rgba(255, 255, 255, 0.08);
            color: #fff;
        }}

        /* Standings Table */
        .standings-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
            text-align: left;
        }}

        .standings-table th {{
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.75rem;
            text-transform: uppercase;
            padding: 0.5rem 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .standings-table td {{
            padding: 0.65rem 0.75rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            color: var(--text-primary);
        }}

        .standings-table tr:last-child td {{
            border-bottom: none;
        }}

        .rank-badge {{
            display: inline-flex;
            justify-content: center;
            align-items: center;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            font-weight: 700;
            font-size: 0.75rem;
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
        }}

        .rank-badge.advances {{
            background: rgba(16, 185, 129, 0.15);
            color: var(--accent-win);
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .rank-badge.advances-3rd {{
            background: rgba(245, 158, 11, 0.15);
            color: var(--accent-draw);
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        .team-cell {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
        }}

        .flag-placeholder {{
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: linear-gradient(135deg, var(--accent-purple), var(--accent-cyan));
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 0.6rem;
            color: #fff;
            font-weight: 800;
            text-transform: uppercase;
        }}

        /* Matches List */
        .matches-list {{
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }}

        .match-row {{
            background: rgba(255, 255, 255, 0.015);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 10px;
            padding: 0.75rem 1rem;
            transition: all 0.2s ease;
        }}

        .match-row:hover {{
            background: rgba(255, 255, 255, 0.03);
            border-color: rgba(255, 255, 255, 0.08);
        }}

        .match-teams-score {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}

        .match-squad {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-weight: 600;
            font-size: 0.95rem;
            width: 40%;
        }}

        .match-squad.away {{
            justify-content: flex-end;
            text-align: right;
        }}

        .match-score-badge {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 1.1rem;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 0.15rem 0.75rem;
            border-radius: 6px;
            color: #fff;
            letter-spacing: 0.05em;
        }}

        .proba-bar-container {{
            display: flex;
            height: 5px;
            width: 100%;
            border-radius: 10px;
            overflow: hidden;
            background: rgba(255, 255, 255, 0.05);
            margin-top: 0.4rem;
        }}

        .proba-segment {{
            height: 100%;
            transition: width 0.3s ease;
        }}

        .proba-segment.winA {{ background: var(--accent-purple); }}
        .proba-segment.draw {{ background: var(--text-secondary); }}
        .proba-segment.winB {{ background: var(--accent-cyan); }}

        .proba-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 0.7rem;
            color: var(--text-secondary);
            font-weight: 600;
            margin-top: 0.15rem;
        }}

        /* Knockout Tab styles */
        .bracket-scroll-container {{
            overflow-x: auto;
            padding: 2rem 0;
            display: flex;
            justify-content: flex-start;
        }}

        .bracket-wrapper {{
            display: flex;
            gap: 3rem;
            min-width: 1500px;
            padding: 0 1rem;
        }}

        .bracket-round {{
            display: flex;
            flex-direction: column;
            justify-content: space-around;
            width: 300px;
            position: relative;
        }}

        .round-header-fixed {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.85rem;
            color: var(--accent-cyan);
            letter-spacing: 0.1em;
            text-align: center;
            margin-bottom: 1.5rem;
            background: rgba(6, 182, 212, 0.05);
            border: 1px solid rgba(6, 182, 212, 0.1);
            padding: 0.4rem 1rem;
            border-radius: 8px;
        }}

        .ko-match-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 12px;
            padding: 0.85rem 1rem;
            margin: 1.2rem 0;
            position: relative;
            backdrop-filter: blur(12px);
            transition: all 0.25s ease;
        }}

        .ko-match-card:hover {{
            border-color: var(--border-glow-hover);
            background: rgba(28, 22, 50, 0.85);
            box-shadow: 0 4px 20px -8px rgba(139, 92, 246, 0.4);
        }}

        .ko-team-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.3rem 0;
        }}

        .ko-team-row.winner {{
            color: #fff;
            font-weight: 700;
        }}

        .ko-team-row.winner .flag-placeholder {{
            box-shadow: 0 0 10px var(--accent-purple);
        }}

        .ko-score {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            color: var(--text-secondary);
        }}

        .ko-team-row.winner .ko-score {{
            color: var(--accent-win);
        }}

        .ko-meta-details {{
            font-size: 0.68rem;
            color: var(--text-secondary);
            border-top: 1px solid rgba(255, 255, 255, 0.03);
            padding-top: 0.35rem;
            margin-top: 0.35rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .champion-badge-ko {{
            background: linear-gradient(135deg, #fbbf24, #d97706);
            color: #fff;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.65rem;
            font-weight: 700;
            letter-spacing: 0.05em;
            display: flex;
            align-items: center;
            gap: 2px;
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.5);
        }}

        /* Interactive map tab */
        .map-layout {{
            display: grid;
            grid-template-columns: 300px 1fr;
            gap: 1.5rem;
            min-height: 620px;
        }}

        .map-sidebar {{
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 1.25rem;
            backdrop-filter: blur(16px);
            display: flex;
            flex-direction: column;
            gap: 1rem;
            max-height: 720px;
            overflow-y: auto;
        }}

        .map-sidebar h3 {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.15rem;
            font-weight: 700;
            color: #fff;
            margin-bottom: 0.25rem;
        }}

        .map-sidebar-note {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            line-height: 1.4;
        }}

        .map-mode-group {{
            display: flex;
            flex-direction: column;
            gap: 0.35rem;
        }}

        .map-mode-label {{
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            font-weight: 600;
            margin-bottom: 0.15rem;
        }}

        .map-mode-btn {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.06);
            color: var(--text-secondary);
            padding: 0.65rem 0.85rem;
            border-radius: 10px;
            text-align: left;
            cursor: pointer;
            font-size: 0.88rem;
            font-weight: 600;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .map-mode-btn:hover {{
            color: #fff;
            border-color: var(--border-glow-hover);
        }}

        .map-mode-btn.active {{
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.25), rgba(6, 182, 212, 0.15));
            border-color: var(--accent-purple);
            color: #fff;
        }}

        .map-sub-panel {{
            display: none;
            flex-direction: column;
            gap: 0.75rem;
            padding-top: 0.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .map-sub-panel.visible {{
            display: flex;
        }}

        .map-select {{
            width: 100%;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            padding: 0.55rem 0.75rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-family: 'Outfit', sans-serif;
        }}

        .map-legend {{
            margin-top: auto;
            padding-top: 0.75rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.78rem;
            color: var(--text-secondary);
        }}

        .map-legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 0.35rem;
        }}

        .map-legend-dot {{
            width: 10px;
            height: 10px;
            border-radius: 50%;
            flex-shrink: 0;
        }}

        .map-player-roster {{
            max-height: 220px;
            overflow-y: auto;
            font-size: 0.78rem;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 10px;
            background: rgba(0, 0, 0, 0.2);
        }}

        .map-player-roster .roster-meta {{
            padding: 0.5rem 0.65rem;
            color: var(--text-secondary);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .map-player-roster ul {{
            list-style: none;
            margin: 0;
            padding: 0;
        }}

        .map-player-roster li {{
            padding: 0.4rem 0.65rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.03);
            cursor: pointer;
        }}

        .map-player-roster li:hover {{
            background: rgba(139, 92, 246, 0.12);
        }}

        .map-player-roster li.mapped {{
            border-left: 2px solid var(--accent-cyan);
        }}

        .country-flag-icon {{
            background: transparent !important;
            border: none !important;
        }}

        .country-flag-icon img {{
            width: 48px;
            height: 32px;
            object-fit: cover;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.45);
            border: 1px solid rgba(255, 255, 255, 0.35);
        }}

        .leaflet-country-fill {{
            cursor: pointer;
        }}

        .map-container-wrap {{
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            overflow: hidden;
            position: relative;
            min-height: 620px;
        }}

        #wc-map {{
            width: 100%;
            height: 100%;
            min-height: 620px;
            background: #0d1117;
        }}

        .leaflet-container {{
            background: #0d1117;
            font-family: 'Outfit', sans-serif;
        }}

        .leaflet-popup-content-wrapper {{
            background: rgba(20, 16, 36, 0.95);
            color: #f3f4f6;
            border-radius: 12px;
            border: 1px solid rgba(139, 92, 246, 0.3);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}

        .leaflet-popup-tip {{
            background: rgba(20, 16, 36, 0.95);
        }}

        .map-popup-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 1rem;
            margin-bottom: 0.35rem;
            color: #fff;
        }}

        .map-popup-meta {{
            font-size: 0.8rem;
            color: #9ca3af;
            margin-bottom: 0.5rem;
        }}

        .map-popup-list {{
            font-size: 0.78rem;
            max-height: 160px;
            overflow-y: auto;
            margin: 0;
            padding-left: 1rem;
            color: #d1d5db;
        }}

        .map-popup-list li {{
            margin-bottom: 0.25rem;
        }}

        @media (max-width: 900px) {{
            .map-layout {{
                grid-template-columns: 1fr;
            }}
            .map-sidebar {{
                max-height: none;
            }}
        }}

        /* Insights tab styles */
        .insights-grid {{
            display: grid;
            grid-template-columns: 1fr 1.2fr;
            gap: 2rem;
        }}

        .insight-card-full {{
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 2rem;
            backdrop-filter: blur(16px);
        }}

        .insight-card-full h3 {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: #fff;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 0.75rem;
        }}

        .feature-bar-row {{
            margin-bottom: 1.5rem;
        }}

        .feature-bar-labels {{
            display: flex;
            justify-content: space-between;
            font-weight: 600;
            font-size: 0.9rem;
            margin-bottom: 0.35rem;
        }}

        .feature-bar-label {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .feature-bar-val {{
            color: var(--accent-cyan);
            font-family: 'Space Grotesk', sans-serif;
        }}

        .feature-bar-bg {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            height: 10px;
            width: 100%;
            overflow: hidden;
        }}

        .feature-bar-fill {{
            background: linear-gradient(90deg, var(--accent-purple), var(--accent-cyan));
            height: 100%;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(139, 92, 246, 0.3);
        }}

        .model-card-row {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .model-card {{
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            padding: 1.25rem;
            transition: all 0.2s ease;
        }}

        .model-card:hover {{
            background: rgba(255, 255, 255, 0.025);
            border-color: rgba(255, 255, 255, 0.07);
        }}

        .model-card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}

        .model-name {{
            font-weight: 700;
            font-size: 1.1rem;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .model-acc-badge {{
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            font-size: 0.85rem;
            background: rgba(6, 182, 212, 0.12);
            color: var(--accent-cyan);
            border: 1px solid rgba(6, 182, 212, 0.3);
            padding: 0.2rem 0.6rem;
            border-radius: 6px;
        }}

        .model-details-text {{
            color: var(--text-secondary);
            font-size: 0.85rem;
            line-height: 1.4;
        }}
    </style>
</head>
<body>

    <header>
        <div class="logo-glow"></div>
        <h1>FIFA World Cup 2026 Predictive Modeling</h1>
        <p class="subtitle">An End-to-End Multiclass Machine Learning & Dynamic Tournament Simulator Dashboard</p>
    </header>

    <main>
        <!-- Stats Container -->
        <section class="stats-container">
            <div class="stat-card">
                <div class="stat-label"><i data-lucide="cpu" size="16" style="color: var(--accent-purple);"></i> ML Best Estimator</div>
                <div class="stat-val" style="font-size: 1.7rem; margin-top: 0.5rem;">Random Forest</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><i data-lucide="shield-check" size="16" style="color: var(--accent-cyan);"></i> Classifier Test Acc</div>
                <div class="stat-val">58.41%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><i data-lucide="trophy" size="16" style="color: #fbbf24;"></i> Simulated Champion</div>
                <div class="stat-val" style="font-size: 1.8rem; margin-top: 0.4rem; color: #fbbf24; background: none; -webkit-text-fill-color: initial;">Morocco 🏆</div>
            </div>
            <div class="stat-card">
                <div class="stat-label"><i data-lucide="git-branch" size="16" style="color: var(--accent-pink);"></i> Group Stage Draw Rule</div>
                <div class="stat-val" style="font-size: 1.7rem; margin-top: 0.5rem;"><10% Prob Diff</div>
            </div>
        </section>

        <!-- Nav Tabs -->
        <nav class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('groups')"><i data-lucide="grid" size="16"></i> Groups & Tables</button>
            <button class="tab-btn" onclick="switchTab('knockout')"><i data-lucide="git-merge" size="16"></i> Knockout Bracket</button>
            <button class="tab-btn" onclick="switchTab('insights')"><i data-lucide="bar-chart-3" size="16"></i> Pipeline Insights</button>
            <button class="tab-btn" onclick="switchTab('map')"><i data-lucide="map" size="16"></i> Interactive Map</button>
        </nav>

        <!-- Tab 1: Groups & Tables Content -->
        <section id="groups-tab" class="content-section active">
            <div class="groups-grid" id="groups-grid-container">
                <!-- Group cards will be generated dynamically by JavaScript -->
            </div>
        </section>

        <!-- Tab 2: Knockout Bracket Content -->
        <section id="knockout-tab" class="content-section">
            <div class="bracket-scroll-container">
                <div class="bracket-wrapper" id="bracket-container">
                    <!-- Knockout bracket rounds will be generated dynamically by JavaScript -->
                </div>
            </div>
        </section>

        <!-- Tab 4: Interactive Map -->
        <section id="map-tab" class="content-section">
            <div class="map-layout">
                <aside class="map-sidebar">
                    <div>
                        <h3>World Cup Explorer</h3>
                        <p class="map-sidebar-note">Official FIFA schedule, base camps (USA/Canada/Mexico), and final squads. Simulated scores from the ML model are shown on group/knockout fixtures where teams match.</p>
                    </div>
                    <div class="map-mode-group">
                        <span class="map-mode-label">Map view</span>
                        <button type="button" class="map-mode-btn active" data-map-mode="stadiums" onclick="setMapMode('stadiums')">
                            <i data-lucide="landmark" size="16"></i> Stadiums &amp; fixtures
                        </button>
                        <button type="button" class="map-mode-btn" data-map-mode="teams" onclick="setMapMode('teams')">
                            <i data-lucide="flag" size="16"></i> Nations &amp; base camps
                        </button>
                        <button type="button" class="map-mode-btn" data-map-mode="players" onclick="setMapMode('players')">
                            <i data-lucide="user" size="16"></i> Players &amp; clubs
                        </button>
                    </div>
                    <div id="map-sub-teams" class="map-sub-panel">
                        <span class="map-mode-label">Focus nation</span>
                        <select id="map-team-filter" class="map-select" onchange="renderMapLayers()">
                            <option value="">All 48 nations (flags on map)</option>
                        </select>
                        <p class="map-sidebar-note" style="margin-top:0.25rem;">Countries are shaded with their flag; click a nation for capital and FIFA base camp in North America.</p>
                    </div>
                    <div id="map-sub-players" class="map-sub-panel">
                        <span class="map-mode-label">Squad</span>
                        <select id="map-player-team" class="map-select" onchange="renderMapLayers()"></select>
                        <span class="map-mode-label">Player markers</span>
                        <button type="button" class="map-mode-btn active" data-player-layer="birth" onclick="setPlayerLayer('birth')">Birthplaces</button>
                        <button type="button" class="map-mode-btn" data-player-layer="club" onclick="setPlayerLayer('club')">Current clubs</button>
                        <div id="map-player-roster" class="map-player-roster"></div>
                    </div>
                    <div class="map-legend" id="map-legend"></div>
                </aside>
                <div class="map-container-wrap">
                    <div id="wc-map"></div>
                </div>
            </div>
        </section>

        <!-- Tab 3: Pipeline Insights Content -->
        <section id="insights-tab" class="content-section">
            <div class="insights-grid">
                
                <!-- Feature Importances -->
                <div class="insight-card-full">
                    <h3>Random Forest Feature Importances</h3>
                    
                    <div class="feature-bar-row">
                        <div class="feature-bar-labels">
                            <span class="feature-bar-label"><i data-lucide="award" size="16" style="color: var(--accent-purple);"></i> Elo Rating Difference (elo_diff)</span>
                            <span class="feature-bar-val">45.72%</span>
                        </div>
                        <div class="feature-bar-bg">
                            <div class="feature-bar-fill" style="width: 45.72%;"></div>
                        </div>
                    </div>
                    
                    <div class="feature-bar-row">
                        <div class="feature-bar-labels">
                            <span class="feature-bar-label"><i data-lucide="users" size="16" style="color: var(--accent-purple);"></i> Squad Quality Tiers (tier_diff)</span>
                            <span class="feature-bar-val">19.52%</span>
                        </div>
                        <div class="feature-bar-bg">
                            <div class="feature-bar-fill" style="width: 19.52%;"></div>
                        </div>
                    </div>
                    
                    <div class="feature-bar-row">
                        <div class="feature-bar-labels">
                            <span class="feature-bar-label"><i data-lucide="shuffle" size="16" style="color: var(--accent-purple);"></i> Head-to-Head Win Rate (h2h_diff)</span>
                            <span class="feature-bar-val">13.88%</span>
                        </div>
                        <div class="feature-bar-bg">
                            <div class="feature-bar-fill" style="width: 13.88%;"></div>
                        </div>
                    </div>
                    
                    <div class="feature-bar-row">
                        <div class="feature-bar-labels">
                            <span class="feature-bar-label"><i data-lucide="globe" size="16" style="color: var(--accent-purple);"></i> Population Difference (population_diff)</span>
                            <span class="feature-bar-val">6.87%</span>
                        </div>
                        <div class="feature-bar-bg">
                            <div class="feature-bar-fill" style="width: 6.87%;"></div>
                        </div>
                    </div>
                    
                    <div class="feature-bar-row">
                        <div class="feature-bar-labels">
                            <span class="feature-bar-label"><i data-lucide="trending-up" size="16" style="color: var(--accent-purple);"></i> Recent Form Difference (form_diff)</span>
                            <span class="feature-bar-val">6.72%</span>
                        </div>
                        <div class="feature-bar-bg">
                            <div class="feature-bar-fill" style="width: 6.72%;"></div>
                        </div>
                    </div>
                    
                    <div class="feature-bar-row">
                        <div class="feature-bar-labels">
                            <span class="feature-bar-label"><i data-lucide="dollar-sign" size="16" style="color: var(--accent-purple);"></i> GDP per Capita Difference (gdp_pc_diff)</span>
                            <span class="feature-bar-val">4.28%</span>
                        </div>
                        <div class="feature-bar-bg">
                            <div class="feature-bar-fill" style="width: 4.28%;"></div>
                        </div>
                    </div>
                    
                    <div class="feature-bar-row">
                        <div class="feature-bar-labels">
                            <span class="feature-bar-label"><i data-lucide="home" size="16" style="color: var(--accent-purple);"></i> Host Country Advantage (is_host_A)</span>
                            <span class="feature-bar-val">3.02%</span>
                        </div>
                        <div class="feature-bar-bg">
                            <div class="feature-bar-fill" style="width: 3.02%;"></div>
                        </div>
                    </div>
                </div>
                
                <!-- Model Performance -->
                <div class="insight-card-full">
                    <h3>Multi-Model Pipeline Tuning</h3>
                    
                    <div class="model-card-row">
                        <div class="model-card">
                            <div class="model-card-header">
                                <span class="model-name"><i data-lucide="line-chart" size="16" style="color: var(--accent-cyan);"></i> Multiclass Logistic Regression</span>
                                <span class="model-acc-badge">58.77% CV Acc</span>
                            </div>
                            <p class="model-details-text">A multi-class Softmax baseline optimized with C=0.01 and L2 regularization. Converged perfectly with an exceptionally low generalization gap (0.03%), representing highly stable and low-variance linear modeling.</p>
                        </div>
                        
                        <div class="model-card">
                            <div class="model-card-header">
                                <span class="model-name"><i data-lucide="network" size="16" style="color: var(--accent-purple);"></i> Random Forest Ensemble (Best Model)</span>
                                <span class="model-acc-badge">58.84% CV Acc</span>
                            </div>
                            <p class="model-details-text">Tuned with 500 decision tree estimators, maximum tree depth of 8, and min_samples_leaf=10 to tarnish overfitting. Achieved 58.25% accuracy on unseen test records and was selected as our tournament bracket simulation model.</p>
                        </div>
                        
                        <div class="model-card">
                            <div class="model-card-header">
                                <span class="model-name"><i data-lucide="compass" size="16" style="color: var(--accent-pink);"></i> Support Vector Classifier (SVC)</span>
                                <span class="model-acc-badge">60.10% Sub CV Acc</span>
                            </div>
                            <p class="model-details-text">Fitted with a non-linear RBF kernel (C=0.5, gamma=0.05). Permutation importance analysis confirmed the model heavily prioritized Elo ratings and squad tiers, maintaining a minimal generalization gap (0.11%).</p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    </main>

    <!-- Data Injection -->
    <script>
        const groupsData = {groups_json};
        const knockoutData = {knockout_json};
        const mapData = {map_json};
        
        let wcMap = null;
        let mapLayerGroup = null;
        let countryLayerGroup = null;
        let worldCountriesGeo = null;
        const countryGeoCache = {{}};
        let currentMapMode = 'stadiums';
        let currentPlayerLayer = 'birth';
        let highlightedPlayerMarker = null;

        function isValidCoord(lat, lng) {{
            return typeof lat === 'number' && typeof lng === 'number'
                && Math.abs(lat) > 0.01 && Math.abs(lng) > 0.01
                && !(Math.abs(lat) < 0.5 && Math.abs(lng) < 0.5);
        }}

        function flagIcon(iso2, w, h) {{
            return L.divIcon({{
                className: 'country-flag-icon',
                html: `<img src="https://flagcdn.com/w${{w}}/${{iso2}}.png" alt="" loading="lazy" />`,
                iconSize: [w, h],
                iconAnchor: [w / 2, h / 2],
            }});
        }}

        async function ensureWorldCountries() {{
            if (worldCountriesGeo) return worldCountriesGeo;
            const res = await fetch('https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson');
            worldCountriesGeo = await res.json();
            return worldCountriesGeo;
        }}

        async function loadCountryGeoJson(iso3) {{
            if (countryGeoCache[iso3]) return countryGeoCache[iso3];
            try {{
                const res = await fetch(`https://raw.githubusercontent.com/johan/world.geo.json/master/countries/${{iso3}}.geo.json`);
                if (res.ok) {{
                    countryGeoCache[iso3] = await res.json();
                    return countryGeoCache[iso3];
                }}
            }} catch (e) {{ /* fallback below */ }}
            const world = await ensureWorldCountries();
            const match = world.features.find(f => {{
                const p = f.properties || {{}};
                return (p.ISO_A3 || p.iso_a3 || '') === iso3;
            }});
            if (match) countryGeoCache[iso3] = {{ type: 'FeatureCollection', features: [match] }};
            return countryGeoCache[iso3] || null;
        }}

        function findCountryFeature(geoName) {{
            if (!worldCountriesGeo) return null;
            const target = geoName.toLowerCase();
            return worldCountriesGeo.features.find(f => {{
                const n = (f.properties?.name || f.properties?.ADMIN || '').toLowerCase();
                return n === target || n.includes(target) || target.includes(n);
            }});
        }}
        
        // Tab switching logic
        function switchTab(tabId) {{
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
            
            // Find active button
            const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.textContent.toLowerCase().includes(tabId));
            if (btn) btn.classList.add('active');
            
            const activeSection = document.getElementById(tabId + '-tab');
            if (activeSection) activeSection.classList.add('active');
            
            if (tabId === 'map') {{
                setTimeout(() => {{
                    if (!wcMap) initWorldCupMap();
                    else wcMap.invalidateSize();
                    renderMapLayers();
                }}, 120);
            }}
        }}
        
        function initWorldCupMap() {{
            wcMap = L.map('wc-map', {{
                center: [28, -98],
                zoom: 4,
                minZoom: 2,
                maxZoom: 12,
                worldCopyJump: true
            }});
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
                attribution: '&copy; OpenStreetMap &copy; CARTO',
                subdomains: 'abcd',
                maxZoom: 19
            }}).addTo(wcMap);
            mapLayerGroup = L.layerGroup().addTo(wcMap);
            countryLayerGroup = L.layerGroup().addTo(wcMap);
            ensureWorldCountries();

            const teamSelect = document.getElementById('map-team-filter');
            const playerTeamSelect = document.getElementById('map-player-team');
            const sortedTeams = [...mapData.teams].sort((a, b) => a.name.localeCompare(b.name));
            sortedTeams.forEach(t => {{
                const o1 = document.createElement('option');
                o1.value = t.name;
                o1.textContent = t.name;
                teamSelect.appendChild(o1);
            }});
            const squadTeams = Object.keys(mapData.players || {{}}).filter(k => (mapData.players[k] || []).length).sort();
            squadTeams.forEach(name => {{
                const o2 = document.createElement('option');
                o2.value = name;
                o2.textContent = name;
                playerTeamSelect.appendChild(o2);
            }});
            if (squadTeams.length) playerTeamSelect.value = squadTeams[0];
            else if (sortedTeams.length) playerTeamSelect.value = sortedTeams[0].name;
            updateMapLegend();
        }}
        
        function setMapMode(mode) {{
            currentMapMode = mode;
            document.querySelectorAll('.map-mode-btn[data-map-mode]').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.mapMode === mode);
            }});
            document.getElementById('map-sub-teams').classList.toggle('visible', mode === 'teams');
            document.getElementById('map-sub-players').classList.toggle('visible', mode === 'players');
            renderMapLayers();
            updateMapLegend();
        }}
        
        function setPlayerLayer(layer) {{
            currentPlayerLayer = layer;
            document.querySelectorAll('.map-mode-btn[data-player-layer]').forEach(btn => {{
                btn.classList.toggle('active', btn.dataset.playerLayer === layer);
            }});
            renderMapLayers();
            updateMapLegend();
        }}
        
        function updateMapLegend() {{
            const legend = document.getElementById('map-legend');
            const items = {{
                stadiums: [
                    {{ color: '#8b5cf6', label: 'Host stadium (2026)' }},
                    {{ color: '#06b6d4', label: 'Click marker for simulated fixtures' }}
                ],
                teams: [
                    {{ color: '#8b5cf6', label: 'Nation territory (flag fill)' }},
                    {{ color: '#f59e0b', label: 'FIFA base camp (USA / Canada / Mexico)' }}
                ],
                players: [
                    {{ color: currentPlayerLayer === 'birth' ? '#ec4899' : '#6366f1', label: currentPlayerLayer === 'birth' ? 'Player birthplace' : 'Current club city' }}
                ]
            }};
            const list = items[currentMapMode] || [];
            legend.innerHTML = list.map(i => `
                <div class="map-legend-item">
                    <span class="map-legend-dot" style="background:${{i.color}};"></span>
                    <span>${{i.label}}</span>
                </div>
            `).join('');
        }}
        
        function makeIcon(color, size) {{
            return L.divIcon({{
                className: 'custom-map-marker',
                html: `<span style="display:block;width:${{size}}px;height:${{size}}px;border-radius:50%;background:${{color}};border:2px solid rgba(255,255,255,0.85);box-shadow:0 0 12px ${{color}}88;"></span>`,
                iconSize: [size, size],
                iconAnchor: [size / 2, size / 2]
            }});
        }}
        
        function popupHtml(title, meta, listItems) {{
            const list = listItems && listItems.length
                ? `<ul class="map-popup-list">${{listItems.map(li => `<li>${{li}}</li>`).join('')}}</ul>`
                : '';
            return `<div class="map-popup-title">${{title}}</div><div class="map-popup-meta">${{meta}}</div>${{list}}`;
        }}
        
        function updatePlayerRoster(teamName, squad, mappedCount) {{
            const box = document.getElementById('map-player-roster');
            if (!box) return;
            const layerLabel = currentPlayerLayer === 'birth' ? 'birthplace' : 'club';
            let html = `<div class="roster-meta">${{mappedCount}} of ${{squad.length}} on map · click a name to zoom</div><ul>`;
            squad.forEach(p => {{
                const loc = currentPlayerLayer === 'birth' ? p.birthplace : p.club;
                const sub = currentPlayerLayer === 'birth' ? loc.city : `${{p.club.name}} (${{loc.city || '—'}})`;
                const mapped = isValidCoord(loc.lat, loc.lng) ? 'mapped' : '';
                html += `<li class="${{mapped}}" data-lat="${{loc.lat}}" data-lng="${{loc.lng}}" data-name="${{p.name}}">${{p.position}} · <strong>${{p.name}}</strong><br><span style="color:var(--text-secondary)">${{sub}}</span></li>`;
            }});
            html += '</ul>';
            box.innerHTML = html;
            box.querySelectorAll('li').forEach(li => {{
                li.addEventListener('click', () => {{
                    const lat = parseFloat(li.dataset.lat);
                    const lng = parseFloat(li.dataset.lng);
                    if (!isValidCoord(lat, lng)) return;
                    wcMap.setView([lat, lng], 6);
                    if (highlightedPlayerMarker) mapLayerGroup.removeLayer(highlightedPlayerMarker);
                    highlightedPlayerMarker = L.marker([lat, lng], {{ icon: makeIcon('#fbbf24', 14) }}).addTo(mapLayerGroup);
                    highlightedPlayerMarker.bindPopup(popupHtml(li.dataset.name, teamName, [])).openPopup();
                }});
            }});
        }}

        async function renderTeamsOnMap(filter) {{
            countryLayerGroup.clearLayers();
            const teams = filter ? mapData.teams.filter(t => t.name === filter) : mapData.teams;
            const bounds = [];

            for (const t of teams) {{
                if (!t.iso2) continue;
                let geo = null;
                if (t.iso3) geo = await loadCountryGeoJson(t.iso3);
                if (!geo || !geo.features?.length) {{
                    const feat = findCountryFeature(t.geoName || t.name);
                    if (feat) geo = {{ type: 'FeatureCollection', features: [feat] }};
                }}
                if (geo && geo.features?.length) {{
                    const layer = L.geoJSON(geo, {{
                        className: 'leaflet-country-fill',
                        style: {{
                            color: '#ffffff',
                            weight: filter ? 2.5 : 1.2,
                            fillOpacity: filter ? 0.55 : 0.42,
                            fillColor: '#1e1b4b',
                        }},
                    }});
                    layer.eachLayer(polygon => {{
                        const b = polygon.getBounds();
                        const center = b.getCenter();
                        const span = Math.max(b.getNorth() - b.getSouth(), (b.getEast() - b.getWest()) * 0.6);
                        const fw = Math.min(96, Math.max(36, span * 18));
                        const fh = Math.round(fw * 0.65);
                        const flag = L.marker(center, {{ icon: flagIcon(t.iso2, fw, fh) }});
                        flag.addTo(countryLayerGroup);
                        polygon.bindPopup(popupHtml(
                            t.name,
                            `Capital: ${{t.capital}}`,
                            [
                                `<img src="${{t.flagUrl}}" alt="" style="width:120px;border-radius:6px;margin-bottom:6px;display:block;" />`,
                                `Base camp: ${{t.camp.name}}`,
                                `${{t.camp.city}} (USA / Canada / Mexico)`,
                            ]
                        ));
                        polygon.on('mouseover', () => polygon.setStyle({{ fillOpacity: 0.72, weight: 2 }}));
                        polygon.on('mouseout', () => polygon.setStyle({{ fillOpacity: filter ? 0.55 : 0.42, weight: filter ? 2.5 : 1.2 }}));
                    }});
                    layer.addTo(countryLayerGroup);
                    bounds.push(layer.getBounds());
                }} else if (isValidCoord(t.lat, t.lng)) {{
                    const flag = L.marker([t.lat, t.lng], {{ icon: flagIcon(t.iso2, 48, 32) }});
                    flag.bindPopup(popupHtml(t.name, t.capital, [t.camp.name, t.camp.city]));
                    flag.addTo(countryLayerGroup);
                    bounds.push(L.latLngBounds([[t.lat, t.lng]]));
                }}

                if (isValidCoord(t.camp.lat, t.camp.lng)) {{
                    const camp = L.marker([t.camp.lat, t.camp.lng], {{ icon: makeIcon('#f59e0b', 12) }});
                    camp.bindPopup(popupHtml(`${{t.name}} — base camp`, t.camp.name, [t.camp.city]));
                    camp.addTo(mapLayerGroup);
                    bounds.push(L.latLngBounds([[t.camp.lat, t.camp.lng]]));
                }}
            }}

            if (bounds.length) {{
                const combined = bounds.reduce((acc, b) => acc.extend(b));
                wcMap.fitBounds(combined, {{ padding: [40, 40], maxZoom: filter ? 5 : 2 }});
            }} else {{
                wcMap.setView([20, 0], 2);
            }}
        }}

        function renderMapLayers() {{
            if (!wcMap || !mapLayerGroup) return;
            mapLayerGroup.clearLayers();
            countryLayerGroup.clearLayers();
            highlightedPlayerMarker = null;
            
            if (currentMapMode === 'stadiums') {{
                mapData.stadiums.forEach(st => {{
                    const matchLines = st.matches.map(m => {{
                        const grp = m.stage ? m.stage.replace('Group Stage - ', 'Grp ') : 'Match';
                        const score = m.score ? ` · ${{m.score}}` : '';
                        return `${{m.date || ''}} · ${{grp}} · ${{m.teamA}} vs ${{m.teamB}}${{score}}`;
                    }});
                    const marker = L.marker([st.lat, st.lng], {{ icon: makeIcon('#8b5cf6', 14) }});
                    marker.bindPopup(popupHtml(
                        st.name,
                        `${{st.city}} · ${{st.country}} · ${{st.capacity.toLocaleString()}} seats · ${{st.matches.length}} matches`,
                        matchLines.length ? matchLines : ['No matches assigned']
                    ));
                    marker.addTo(mapLayerGroup);
                }});
                wcMap.setView([28, -98], 4);
            }} else if (currentMapMode === 'teams') {{
                const filter = document.getElementById('map-team-filter').value;
                renderTeamsOnMap(filter);
            }} else if (currentMapMode === 'players') {{
                const teamName = document.getElementById('map-player-team').value;
                const squad = mapData.players[teamName] || [];
                const color = currentPlayerLayer === 'birth' ? '#ec4899' : '#6366f1';
                const bounds = [];
                let mappedCount = 0;
                squad.forEach(p => {{
                    const loc = currentPlayerLayer === 'birth' ? p.birthplace : p.club;
                    if (!isValidCoord(loc.lat, loc.lng)) return;
                    mappedCount++;
                    const marker = L.marker([loc.lat, loc.lng], {{ icon: makeIcon(color, 10) }});
                    marker.bindPopup(popupHtml(
                        p.name,
                        `${{teamName}} · ${{p.position}}`,
                        [currentPlayerLayer === 'birth'
                            ? `Born: ${{p.birthplace.city}}`
                            : `Club: ${{p.club.name}} (${{p.club.city || ''}})`]
                    ));
                    marker.addTo(mapLayerGroup);
                    bounds.push([loc.lat, loc.lng]);
                }});
                updatePlayerRoster(teamName, squad, mappedCount);
                if (bounds.length) {{
                    wcMap.fitBounds(bounds, {{ padding: [48, 48], maxZoom: 6 }});
                }} else {{
                    wcMap.setView([20, 0], 2);
                }}
            }}
        }}
        
        // Generate Group Cards
        function renderGroups() {{
            const container = document.getElementById('groups-grid-container');
            container.innerHTML = '';
            
            Object.keys(groupsData).forEach(gName => {{
                const group = groupsData[gName];
                const card = document.createElement('div');
                card.className = 'group-card';
                
                // Card header
                let html = `
                    <div class="group-header">
                        <div class="group-title">Group <span>${{gName}}</span></div>
                        <div class="card-tabs">
                            <button class="card-tab-btn active" id="tab-standings-${{gName}}" onclick="toggleCardTab('${{gName}}', 'standings')">Tables</button>
                            <button class="card-tab-btn" id="tab-matches-${{gName}}" onclick="toggleCardTab('${{gName}}', 'matches')">Matches</button>
                        </div>
                    </div>
                `;
                
                // 1. Standings HTML
                html += `
                    <div id="card-standings-container-${{gName}}">
                        <table class="standings-table">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Team</th>
                                    <th style="text-align: center;">Pts</th>
                                    <th style="text-align: center;">GD</th>
                                    <th style="text-align: center;">GS</th>
                                    <th style="text-align: center;">Elo</th>
                                </tr>
                            </thead>
                            <tbody>
                `;
                
                group.standings.forEach(s => {{
                    const advancesClass = s.rank <= 2 ? 'advances' : (s.points >= 3 && (s.team === 'Belgium' || s.team === 'Norway' || s.team === 'Democratic Republic of Congo' || s.team === 'Austria' || s.team === 'Panama' || s.team === 'Scotland' || s.team === 'Ivory Coast' || s.team === 'Bosnia and Herzegovina') ? 'advances-3rd' : '');
                    const advancesText = s.rank <= 2 ? 'advances' : (s.points >= 3 && (s.team === 'Belgium' || s.team === 'Norway' || s.team === 'Democratic Republic of Congo' || s.team === 'Austria' || s.team === 'Panama' || s.team === 'Scotland' || s.team === 'Ivory Coast' || s.team === 'Bosnia and Herzegovina') ? 'advances-3rd' : '');
                    
                    html += `
                        <tr>
                            <td><span class="rank-badge ${{advancesText}}">${{s.rank}}</span></td>
                            <td>
                                <div class="team-cell">
                                    <div class="flag-placeholder" style="background: linear-gradient(135deg, ${{s.tier === 5 ? 'var(--accent-pink)' : (s.tier >= 3 ? 'var(--accent-purple)' : 'var(--text-secondary)')}}, var(--accent-cyan));">${{s.team.substring(0,2)}}</div>
                                    ${{s.team}}
                                </div>
                            </td>
                            <td style="text-align: center; font-weight: 700;">${{s.points}}</td>
                            <td style="text-align: center; color: ${{s.gd > 0 ? 'var(--accent-win)' : (s.gd < 0 ? 'var(--accent-loss)' : 'var(--text-secondary)')}};">${{s.gd > 0 ? '+' + s.gd : s.gd}}</td>
                            <td style="text-align: center;">${{s.gs}}</td>
                            <td style="text-align: center; color: var(--text-secondary); font-size: 0.8rem;">${{s.elo}}</td>
                        </tr>
                    `;
                }});
                
                html += `
                            </tbody>
                        </table>
                    </div>
                `;
                
                // 2. Matches HTML (hidden by default)
                html += `
                    <div id="card-matches-container-${{gName}}" style="display: none;" class="matches-list">
                `;
                
                group.matches.forEach(m => {{
                    html += `
                        <div class="match-row">
                            <div class="match-teams-score">
                                <div class="match-squad">
                                    <div class="flag-placeholder">${{m.teamA.substring(0,2)}}</div>
                                    <span>${{m.teamA}}</span>
                                </div>
                                <div class="match-score-badge">${{m.score}}</div>
                                <div class="match-squad away">
                                    <span>${{m.teamB}}</span>
                                    <div class="flag-placeholder">${{m.teamB.substring(0,2)}}</div>
                                </div>
                            </div>
                            
                            <!-- Proba Bar -->
                            <div class="proba-bar-container">
                                <div class="proba-segment winA" style="width: ${{m.probaA}};"></div>
                                <div class="proba-segment draw" style="width: ${{m.probaDraw}};"></div>
                                <div class="proba-segment winB" style="width: ${{m.probaB}};"></div>
                            </div>
                            <div class="proba-labels">
                                <span>Win ${{m.teamA}}: ${{m.probaA}}</span>
                                <span>Draw: ${{m.probaDraw}}</span>
                                <span>Win ${{m.teamB}}: ${{m.probaB}}</span>
                            </div>
                        </div>
                    `;
                }});
                
                html += `
                    </div>
                `;
                
                card.innerHTML = html;
                container.appendChild(card);
            }});
        }}
        
        function toggleCardTab(gName, tab) {{
            const standingsContainer = document.getElementById(`card-standings-container-${{gName}}`);
            const matchesContainer = document.getElementById(`card-matches-container-${{gName}}`);
            const standingsTab = document.getElementById(`tab-standings-${{gName}}`);
            const matchesTab = document.getElementById(`tab-matches-${{gName}}`);
            
            if (tab === 'standings') {{
                standingsContainer.style.display = 'block';
                matchesContainer.style.display = 'none';
                standingsTab.classList.add('active');
                matchesTab.classList.remove('active');
            }} else {{
                standingsContainer.style.display = 'none';
                matchesContainer.style.display = 'block';
                standingsTab.classList.remove('active');
                matchesTab.classList.add('active');
            }}
        }}
        
        // Generate Knockout Bracket View
        function renderBracket() {{
            const container = document.getElementById('bracket-container');
            container.innerHTML = '';
            
            const rounds = ['Round of 32', 'Round of 16', 'Quarter-finals', 'Semi-finals', 'World Cup Final'];
            
            rounds.forEach(rName => {{
                const rCol = document.createElement('div');
                rCol.className = 'bracket-round';
                
                let html = `<div class="round-header-fixed">${{rName === 'World Cup Final' ? '🏆 Grand Final' : rName}}</div>`;
                
                knockoutData[rName].forEach(m => {{
                    const winnerClassA = m.winner === m.teamA ? 'winner' : '';
                    const winnerClassB = m.winner === m.teamB ? 'winner' : '';
                    const scoreA = m.score.includes('wins on pen') ? (m.winner === m.teamA ? '1 (Pen)' : '1') : (m.score.split('-')[0] || '0');
                    const scoreB = m.score.includes('wins on pen') ? (m.winner === m.teamB ? '1 (Pen)' : '1') : (m.score.split('-')[1] || '0');
                    
                    const isChampion = rName === 'World Cup Final' && m.winner === 'Morocco' ? '<span class="champion-badge-ko"><i data-lucide="sparkles" size="10"></i> Champion</span>' : '';
                    
                    html += `
                        <div class="ko-match-card">
                            <div class="ko-team-row ${{winnerClassA}}">
                                <div class="team-cell">
                                    <div class="flag-placeholder">${{m.teamA.substring(0,2)}}</div>
                                    <span>${{m.teamA}}</span>
                                </div>
                                <span class="ko-score">${{scoreA}}</span>
                            </div>
                            <div class="ko-team-row ${{winnerClassB}}">
                                <div class="team-cell">
                                    <div class="flag-placeholder">${{m.teamB.substring(0,2)}}</div>
                                    <span>${{m.teamB}}</span>
                                </div>
                                <span class="ko-score">${{scoreB}}</span>
                            </div>
                            <div class="ko-meta-details">
                                <span>Win ${{m.teamA.substring(0,6)}}: ${{m.probaA}} vs ${{m.teamB.substring(0,6)}}: ${{m.probaB}}</span>
                                ${{isChampion}}
                            </div>
                        </div>
                    `;
                }});
                
                rCol.innerHTML = html;
                container.appendChild(rCol);
            }});
        }}
        
        // Initial setup
        window.addEventListener('DOMContentLoaded', () => {{
            renderGroups();
            renderBracket();
            lucide.createIcons();
            setMapMode('stadiums');
        }});
    </script>
</body>
</html>
"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Dashboard website successfully written to 'index.html'.")

if __name__ == '__main__':
    generate_website()
