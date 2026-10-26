import urllib.request
import json
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

url = "https://api.openligadb.de/getmatchdata/bl1/2026/7"
print(f"Fetching {url}...")

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    print(f"Successfully fetched {len(data)} matches.")
    
    finished = sum(1 for m in data if m.get('matchIsFinished'))
    print(f"Finished matches: {finished}/{len(data)}")
    
    with open('data/real_openligadb_md7_2026.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved to data/real_openligadb_md7_2026.json")
    
    for m in data:
        t1 = m['team1']['teamName']
        t2 = m['team2']['teamName']
        is_fin = m.get('matchIsFinished')
        res = m.get('matchResults', [])
        fin_res = "vs"
        for r in res:
            if r.get('resultName') == 'Endergebnis' or r.get('resultTypeKind') == 'After90Minutes':
                fin_res = f"{r.get('pointsTeam1')}:{r.get('pointsTeam2')}"
        print(f"[{'FINISHED' if is_fin else 'PENDING'}] {t1} {fin_res} {t2}")
        if m.get('goals'):
            for g in m['goals']:
                pen = " (Pen)" if g.get('isPenalty') else ""
                og = " (ET)" if g.get('isOwnGoal') else ""
                print(f"   Goal {g.get('scoreTeam1')}:{g.get('scoreTeam2')} {g.get('goalGetterName')} ({g.get('matchMinute')}'){pen}{og}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
