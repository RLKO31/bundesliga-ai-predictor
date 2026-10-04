import re, json

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("--- 1. Auditing teamLogos Dictionary in index.html ---")
logos_match = re.search(r'const teamLogos = (\{.*?\});', html, re.DOTALL)
if logos_match:
    logos_str = logos_match.group(1)
    print(f"const teamLogos found! Length: {len(logos_str)}")
    # Extract keys
    keys = re.findall(r'"([^"]+)":\s*"http', logos_str)
    print(f"teamLogos keys ({len(keys)}): {sorted(keys)}")
else:
    print("const teamLogos NOT FOUND!")

print("\n--- 2. Checking Unique Teams in Predictions State ---")
pred_teams = set()
for m in re.findall(r'"home_team": "([^"]+)"', html): pred_teams.add(m)
for m in re.findall(r'"away_team": "([^"]+)"', html): pred_teams.add(m)
print(f"Prediction teams ({len(pred_teams)}): {sorted(list(pred_teams))}")

print("\n--- 3. Checking Missing Logo Keys ---")
if logos_match:
    missing = [t for t in pred_teams if t not in keys]
    print(f"Teams missing from teamLogos ({len(missing)}): {missing}")
