import json, glob, re

team_names = set()

def extract_strings(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ['home_team', 'away_team', 'team', 'Team', 'team_name', 'club', 'opponent']:
                if isinstance(v, str): team_names.add(v)
            extract_strings(v)
    elif isinstance(obj, list):
        for item in obj:
            extract_strings(item)

files = glob.glob("**/*.json", recursive=True)
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as fp:
            data = json.load(fp)
            extract_strings(data)
    except Exception:
        pass

print(f"Total extracted team names across all JSON files: {len(team_names)}")
for t in sorted(team_names):
    print(f"  - '{t}'")
