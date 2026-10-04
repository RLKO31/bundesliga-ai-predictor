import re, json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

logos_block = re.search(r'const teamLogos = (\{.*?\});', html, re.DOTALL)
if not logos_block:
    print("Error: teamLogos not found")
    exit(1)

team_logos = json.loads(logos_block.group(1))

# Search for all strings inside predictions objects
patterns = [
    r'"home_team":\s*"([^"]+)"',
    r'"away_team":\s*"([^"]+)"',
    r'"team":\s*"([^"]+)"',
    r'"Team":\s*"([^"]+)"',
    r'"team_name":\s*"([^"]+)"',
    r'"club":\s*"([^"]+)"'
]

found_teams = set()
for pat in patterns:
    matches = re.findall(pat, html)
    for m in matches:
        found_teams.add(m)

print(f"Total unique team names found across all dataset objects: {len(found_teams)}")
missing = [t for t in found_teams if t not in team_logos]
if missing:
    print(f"\n[FAIL] {len(missing)} team names missing from teamLogos:")
    for t in sorted(missing):
        print(f"  - '{t}'")
else:
    print("\n[PASS] All team names found in datasets exist in teamLogos!")
