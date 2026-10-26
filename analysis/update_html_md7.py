import json
import re

with open('data/all_matchdays_11_der_woche.json', 'r', encoding='utf-8') as f:
    all_totw = json.load(f)

totw_json_str = json.dumps(all_totw, ensure_ascii=False)

def update_file(filepath):
    print(f"Updating {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Replace const totwData = {...};
    # Find start and end of const totwData =
    idx_start = content.find('const totwData = {')
    if idx_start == -1:
        print("ERROR: const totwData not found!")
        return False
    
    # Find the closing semicolon of totwData
    # It is right before 'let currentTotwMd ='
    idx_next = content.find('let currentTotwMd =', idx_start)
    if idx_next == -1:
        print("ERROR: let currentTotwMd not found after totwData!")
        return False
    
    idx_end = content.rfind(';', idx_start, idx_next)
    if idx_end == -1:
        print("ERROR: closing semicolon of totwData not found!")
        return False

    old_totw_def = content[idx_start:idx_end+1]
    new_totw_def = f"const totwData = {totw_json_str};"
    content = content[:idx_start] + new_totw_def + content[idx_end+1:]
    print("  [OK] Replaced totwData")

    # 2. Update currentTotwMd = 6 -> currentTotwMd = 7
    content = re.sub(r'let currentTotwMd\s*=\s*\d+;', 'let currentTotwMd = 7;', content, count=1)
    print("  [OK] Set currentTotwMd = 7")

    # 3. Update default selectedMatchday = 6 -> selectedMatchday = 7
    content = content.replace('if (!selectedMatchday) selectedMatchday = 6;', 'if (!selectedMatchday) selectedMatchday = 7;')
    content = content.replace("switchTab('predictions') { loadMatchday(selectedMatchday || 6); }", "switchTab('predictions') { loadMatchday(selectedMatchday || 7); }")
    content = content.replace("selectedMatchday = Number(matchday) || 6;", "selectedMatchday = Number(matchday) || 7;")
    print("  [OK] Set default selectedMatchday = 7")

    # 4. Update checkLiveOpenLigaDB text
    content = content.replace('const nextMds = [7, 8, 9];', 'const nextMds = [8, 9, 10];')
    content = content.replace('Spieltage 1 bis 6 sind vollständig ausgewertet. Nächster Spieltag (Spieltag 7)', 'Spieltage 1 bis 7 sind vollständig ausgewertet. Nächster Spieltag (Spieltag 8)')
    print("  [OK] Updated live sync check for Spieltag 8")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Finished {filepath}")
    return True

update_file('index.html')
update_file('web_dashboard/index.html')
