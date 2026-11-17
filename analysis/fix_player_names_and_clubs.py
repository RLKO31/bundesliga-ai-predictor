import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("1. Updating data/all_matchdays_11_der_woche.json...")
with open('data/all_matchdays_11_der_woche.json', 'r', encoding='utf-8') as f:
    totw = json.load(f)

# Update MD3
md3_lineup = totw['3']['lineup']
for p in md3_lineup:
    if p['pos'] == 'TW' and 'Atubolu' in p['name']:
        print(f"  Replacing {p['name']} with Mio Backhaus in MD3")
        p['name'] = "Mio Backhaus"
        p['club'] = "SC Freiburg"
        p['highlight'] = "Starter (90 Min.), 8 Paraden beim sensationellen 3:1 gegen Meister Leverkusen"

# Update MD9
md9_lineup = totw['9']['lineup']
for p in md9_lineup:
    if p['pos'] == 'TW' and 'Atubolu' in p['name']:
        print(f"  Replacing {p['name']} with Mio Backhaus in MD9")
        p['name'] = "Mio Backhaus"
        p['club'] = "SC Freiburg"
        p['highlight'] = "Starter (90 Min.), Weiße Weste, 6 Glanzparaden beim 2:0 gegen Union Berlin"

with open('data/all_matchdays_11_der_woche.json', 'w', encoding='utf-8') as f:
    json.dump(totw, f, ensure_ascii=False, indent=2)
print("  Saved data/all_matchdays_11_der_woche.json")

# Update lineup JSON files
for fn in ['data/bundesliga_lineups_md1_9.json', 'data/bundesliga_lineups_md1_8.json', 'data/bundesliga_lineups_md1_7.json']:
    try:
        with open(fn, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        updated = 0
        for md_str, md_data in data.items():
            for starter in md_data.get('starters', []):
                if starter.get('club') == 'SC Freiburg' and starter.get('pos') == 'TW' and 'Atubolu' in starter.get('name', ''):
                    starter['name'] = 'Mio Backhaus'
                    updated += 1
        
        with open(fn, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"2. Updated {updated} entries in {fn}")
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
        print(f"3. Injected updated totwData into {html_path}")

print("Done successfully!")
