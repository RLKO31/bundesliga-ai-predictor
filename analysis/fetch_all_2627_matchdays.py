import urllib.request
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

all_md_data = {}

for md in range(1, 8):
    url = f"https://api.openligadb.de/getmatchdata/bl1/2026/{md}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        finished = sum(1 for m in data if m.get('matchIsFinished'))
        print(f"Matchday {md}: {len(data)} matches, {finished} finished")
        all_md_data[md] = []
        for m in data:
            res = m.get('matchResults', [])
            fin_res = None
            for r in res:
                if r.get('resultName') == 'Endergebnis' or r.get('resultTypeKind') == 'After90Minutes':
                    fin_res = f"{r.get('pointsTeam1')}:{r.get('pointsTeam2')}"
            t1 = m['team1']['teamName']
            t2 = m['team2']['teamName']
            goals = m.get('goals', [])
            goals_list = []
            for g in goals:
                goals_list.append({
                    'minute': g.get('matchMinute'),
                    'scorer': g.get('goalGetterName'),
                    'score': f"{g.get('scoreTeam1')}:{g.get('scoreTeam2')}",
                    'is_penalty': g.get('isPenalty'),
                    'is_own_goal': g.get('isOwnGoal')
                })
            match_entry = {
                'match_id': m.get('matchID'),
                'match_date': m.get('matchDateTime'),
                'home_team': t1,
                'away_team': t2,
                'is_finished': m.get('matchIsFinished'),
                'score': fin_res,
                'goals': goals_list
            }
            all_md_data[md].append(match_entry)
            if m.get('matchIsFinished'):
                print(f"  {t1} {fin_res} {t2}")
                for g in goals_list:
                    p = " (Pen)" if g['is_penalty'] else ""
                    og = " (OG)" if g['is_own_goal'] else ""
                    print(f"     ⚽ {g['minute']}' {g['scorer']} [{g['score']}]{p}{og}")
    except Exception as e:
        print(f"Matchday {md} error: {e}")

os.makedirs('data', exist_ok=True)
with open('data/real_openligadb_md1_6_2026.json', 'w', encoding='utf-8') as f:
    json.dump(all_md_data, f, indent=4, ensure_ascii=False)
print("\n[SUCCESS] Saved all matchday data to data/real_openligadb_md1_6_2026.json")
