import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Starting complete roster audit and updates...")

# Load totw
with open('data/all_matchdays_11_der_woche.json', 'r', encoding='utf-8') as f:
    totw = json.load(f)

# 1. MD5: Replace Danilho Doekhi with Leopold Querfeld
for p in totw['5']['lineup']:
    if p['name'] == 'Danilho Doekhi':
        print(f"MD5: Replacing {p['name']} with Leopold Querfeld (1. FC Union Berlin)")
        p['name'] = 'Leopold Querfeld'
        p['club'] = '1. FC Union Berlin'
        p['highlight'] = 'Starter (90 Min.), Weiße Weste & 8 Klärungen beim 1:0-Sieg gegen SV 07 Elversberg'

# 2. MD6: Replace Danilho Doekhi with Leopold Querfeld
for p in totw['6']['lineup']:
    if p['name'] == 'Danilho Doekhi':
        print(f"MD6: Replacing {p['name']} with Leopold Querfeld (1. FC Union Berlin)")
        p['name'] = 'Leopold Querfeld'
        p['club'] = '1. FC Union Berlin'
        p['highlight'] = 'Starter (90 Min.), Weiße Weste & 10 gewonnene Zweikämpfe beim 0:0 gegen Dortmund'

# 3. MD8: Replace Michael Zetterer with Karl Hein
for p in totw['8']['lineup']:
    if p['name'] == 'Michael Zetterer':
        print(f"MD8: Replacing {p['name']} with Karl Hein (SV Werder Bremen)")
        p['name'] = 'Karl Hein'
        p['club'] = 'SV Werder Bremen'
        p['highlight'] = 'Starter (90 Min.), Weiße Weste & 5 Glanzparaden beim 1:0-Heimsieg gegen Union Berlin'

# 4. MD2: Fix typo Florian Rieder -> Fabian Rieder
for j in totw['2'].get('jokers', []):
    if j['name'] == 'Florian Rieder':
        print(f"MD2: Correcting {j['name']} to Fabian Rieder (FC Augsburg)")
        j['name'] = 'Fabian Rieder'

# Save updated all_matchdays_11_der_woche.json
with open('data/all_matchdays_11_der_woche.json', 'w', encoding='utf-8') as f:
    json.dump(totw, f, ensure_ascii=False, indent=2)
print("Saved data/all_matchdays_11_der_woche.json")

# Update lineups files
lineup_files = [
    'data/bundesliga_lineups_md1_9.json',
    'data/bundesliga_lineups_md1_8.json',
    'data/bundesliga_lineups_md1_7.json'
]

for lpath in lineup_files:
    try:
        with open(lpath, 'r', encoding='utf-8') as f:
            lineups = json.load(f)
        
        replaced_count = 0
        for md_key, md_val in lineups.items():
            for s in md_val.get('starters', []):
                if s.get('name') == 'Michael Zetterer':
                    s['name'] = 'Karl Hein'
                    replaced_count += 1
                elif s.get('name') == 'Danilho Doekhi':
                    s['name'] = 'Leopold Querfeld'
                    replaced_count += 1
            for sub in md_val.get('substitutes', []):
                if sub.get('name') == 'Michael Zetterer':
                    sub['name'] = 'Karl Hein'
                    replaced_count += 1
                elif sub.get('name') == 'Danilho Doekhi':
                    sub['name'] = 'Leopold Querfeld'
                    replaced_count += 1
                elif sub.get('name') == 'Florian Rieder':
                    sub['name'] = 'Fabian Rieder'
                    replaced_count += 1
                elif sub.get('name') == 'Winsley Boteli':
                    sub['name'] = 'Tim Kleindienst'
                    replaced_count += 1
        
        with open(lpath, 'w', encoding='utf-8') as f:
            json.dump(lineups, f, ensure_ascii=False, indent=2)
        print(f"Updated {replaced_count} entries in {lpath}")
    except FileNotFoundError:
        pass

# Synchronize totwData into index.html and web_dashboard/index.html
totw_json_str = json.dumps(totw, ensure_ascii=False)
js_line = f"        const totwData = {totw_json_str};\n"

for html_path in ['index.html', 'web_dashboard/index.html']:
    with open(html_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    found = False
    for i, line in enumerate(lines):
        if line.strip().startswith('const totwData ='):
            lines[i] = js_line
            found = True
            break
    
    if not found:
        print(f"ERROR: Could not find const totwData in {html_path}")
    else:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"Synchronized totwData into {html_path}")

print("Roster update script completed successfully.")
