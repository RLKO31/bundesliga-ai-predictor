import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("--- 1. Checking JS Global Variables ---")
for var in [
    'window.stadiums', 'window.predictions_v2', 'window.predictions_v3', 
    'window.predictions_v4', 'window.predictions_v5_m1_4', 'window.predictions_v6', 
    'window.predictions_v6_2stage', 'window.team_vulnerabilities_multiseason', 
    'window.tactical_adaptability', 'window.predicted_fixture_heatmaps'
]:
    pos = html.find(var)
    if pos != -1:
        print(f"  [PASS] {var} declared at pos {pos}")
    else:
        print(f"  [FAIL] {var} NOT DECLARED in html!")

print("\n--- 2. Checking teamLogos coverage ---")
logos_block = re.search(r'const teamLogos\s*=\s*(\{.*?\});', html, re.DOTALL)
if logos_block:
    logos_str = logos_block.group(1)
    logo_keys = set(re.findall(r'"([^"]+)":\s*"http', logos_str))
    print(f"  Total logo keys in teamLogos: {len(logo_keys)}")

all_teams = set(re.findall(r'"home_team": "([^"]+)"', html) + 
                re.findall(r'"away_team": "([^"]+)"', html) + 
                re.findall(r'"team": "([^"]+)"', html))

missing_teams = [t for t in all_teams if t not in logo_keys]
if missing_teams:
    print(f"  [FAIL] {len(missing_teams)} team name variants missing from teamLogos:")
    for t in sorted(missing_teams): print(f"    - {t}")
else:
    print("  [PASS] 100% of team name variants are covered in teamLogos!")

print("\n--- 3. Checking HTML Element IDs for all tab renderers ---")
tab_checks = [
    ("predictions", "predictions-tab", "fixtures-grid"),
    ("standings", "standings-tab", "live-standings-body"),
    ("map", "map-tab", "map"),
    ("tactical", "tactical-tab", "pitch-heatmap-canvas"),
    ("complexity", "complexity-tab", "v4-complexity-standings-body"),
    ("m14", "m14-tab", "v5-m14-standings-body"),
    ("insights", "insights-tab", None),
    ("vulnerability", "vulnerability-tab", "unified-pitch-canvas")
]

for name, sec_id, elem_id in tab_checks:
    sec_found = f'id="{sec_id}"' in html
    elem_found = f'id="{elem_id}"' in html if elem_id else True
    status = "[PASS]" if (sec_found and elem_found) else "[FAIL]"
    print(f"  {status} Tab '{name}': section id='{sec_id}' ({sec_found}), element id='{elem_id}' ({elem_found})")
