import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load existing all_matchdays_11_der_woche.json
totw_path = 'data/all_matchdays_11_der_woche.json'
with open(totw_path, 'r', encoding='utf-8') as f:
    totw_data = json.load(f)

# 2. Add Matchday 8
md8_entry = {
    "matchday": 8,
    "title": "8. Spieltag (2026/2027)",
    "formation": "4-3-3",
    "mvp": "Ermedin Demirovic (VfB Stuttgart)",
    "mvp_reason": "⭐ DOPPELPACK (14', 66') aus dem Spiel heraus beim grandiosen 4:2-Erfolg bei Meister Bayer Leverkusen (TIP: 1.85, TDI: 3.10, xWAR: +0.85)",
    "coach": "Sebastian Hoeneß (VfB Stuttgart)",
    "jokers": [
        {
            "rank": 1,
            "name": "Fábio Silva",
            "club": "Borussia Dortmund",
            "min_in": "Eingewechselt (76')",
            "stat": "Tor in 89. Min. (2:2 vs Bayern) | TIP: 1.45",
            "highlight": "Klassiker-Coup: Schockt die Bayern in der 89. Minute zum 2:2-Remis in der Allianz Arena!"
        },
        {
            "rank": 2,
            "name": "Cyriaque Irié",
            "club": "SC Freiburg",
            "min_in": "Eingewechselt (83')",
            "stat": "Siegtor in 85. Min. (2:1 bei Augsburg) | TIP: 1.35",
            "highlight": "Blitz-Joker: Erzielt 120 Sekunden nach Einwechslung das umjubelte 2:1-Siegtor beim FC Augsburg!"
        },
        {
            "rank": 3,
            "name": "Malek El Mala",
            "club": "1. FC Köln",
            "min_in": "Eingewechselt (71')",
            "stat": "Bundesligadebüt-Tor (79') | TIP: 1.30",
            "highlight": "Traumdebüt par excellence: Trifft 8 Minuten nach Einwechslung mit seinem allerersten Bundesliga-Schuss zum 1:1 bei Union Berlin!"
        }
    ],
    "fixtures_summary": [
        "SV 07 Elversberg 4:1 1. FSV Mainz 05",
        "Bayer 04 Leverkusen 2:4 VfB Stuttgart",
        "FC Augsburg 1:2 SC Freiburg",
        "Borussia Mönchengladbach 0:0 SC Paderborn 07",
        "SV Werder Bremen 2:0 TSG Hoffenheim",
        "FC Schalke 04 0:2 RB Leipzig",
        "FC Bayern München 2:2 Borussia Dortmund",
        "1. FC Union Berlin 1:1 1. FC Köln",
        "Eintracht Frankfurt 3:1 Hamburger SV"
    ],
    "lineup": [
        { "pos": "TW", "name": "Michael Zetterer", "club": "SV Werder Bremen", "x": 50, "y": 88, "stat": "GSAE: +1.45 | QRSR: 1.82", "highlight": "Starter (90 Min.), Weiße Weste, 5 Paraden beim 2:0 gegen Hoffenheim" },
        { "pos": "RV", "name": "Konrad Laimer", "club": "FC Bayern München", "x": 82, "y": 70, "stat": "TIP: 1.05 | DSI: 2.30", "highlight": "Starter (90 Min.), Führungstor (38') im Klassiker gegen den BVB" },
        { "pos": "IV", "name": "Dayot Upamecano", "club": "FC Bayern München", "x": 60, "y": 74, "stat": "BLS: 2.35 | CDE: 5.50", "highlight": "Starter (90 Min.), Führungstor (66') im Klassiker, 94% Passquote" },
        { "pos": "IV", "name": "Willi Orbán", "club": "RB Leipzig", "x": 40, "y": 74, "stat": "BLS: 2.40 | CDE: 6.00", "highlight": "Starter (90 Min.), Weiße Weste, 100% Luftduelle (5/5) beim 2:0 auf Schalke" },
        { "pos": "LV", "name": "Felix Götze", "club": "SC Paderborn 07", "x": 18, "y": 70, "stat": "BLS: 2.30 | DSI: 2.85", "highlight": "Starter (90 Min.), Weiße Weste, 11 Klärungen/Blocks beim 0:0 in Gladbach" },
        { "pos": "ZM", "name": "Felix Keidel", "club": "SV 07 Elversberg", "x": 35, "y": 50, "stat": "TIP: 1.15 | BPS: 1.25", "highlight": "Starter (90 Min.), Traum-Freistoßtor (7') & Taktgeber beim 4:1 gegen Mainz" },
        { "pos": "ZM", "name": "Raphael Onyedika", "club": "Eintracht Frankfurt", "x": 65, "y": 50, "stat": "BPS: 1.28 | TIP: 1.10", "highlight": "Starter (90 Min.), Führungstor (47') & 8 Balleroberungen beim 3:1 vs HSV" },
        { "pos": "OM", "name": "Bilal El Khannouss", "club": "VfB Stuttgart", "x": 50, "y": 36, "stat": "TIP: 1.45 | TDI: 2.40", "highlight": "Starter (85 Min.), Traumtor (51') & 5 Vorlagenläufe beim 4:2 in Leverkusen" },
        { "pos": "RA", "name": "Jamie Leweling", "club": "VfB Stuttgart", "x": 80, "y": 20, "stat": "TIP: 1.55 | TDI: 2.50", "highlight": "Starter (85 Min.), Tor (22') & Vorlage beim 4:2-Auswärtscoup in Leverkusen" },
        { "pos": "MS", "name": "Ermedin Demirovic", "club": "VfB Stuttgart", "x": 50, "y": 16, "stat": "TIP: 1.85 | TDI: 3.10", "highlight": "⭐ MVP: Starter (90 Min.), 2 Feldtore (14', 66') beim 4:2-Sieg in Leverkusen" },
        { "pos": "LA", "name": "Antonio Nusa", "club": "RB Leipzig", "x": 20, "y": 20, "stat": "TIP: 1.35 | TDI: 2.20", "highlight": "Starter (90 Min.), Tor (35' FE) + Assist (78') beim 2:0 auf Schalke" }
    ]
}

totw_data["8"] = md8_entry

# Validation: ensure 11 starters and 3 jokers
for md_str, entry in totw_data.items():
    assert len(entry["lineup"]) == 11, f"MD {md_str} has {len(entry['lineup'])} players, expected 11"
    assert len(entry["jokers"]) == 3, f"MD {md_str} has {len(entry['jokers'])} jokers, expected 3"
    for p in entry["lineup"]:
        assert "Starter" in p["highlight"], f"Player {p['name']} in MD {md_str} must be starter"
        assert 0 <= p["x"] <= 100 and 0 <= p["y"] <= 100, f"Coords out of bounds for {p['name']}"

with open(totw_path, 'w', encoding='utf-8') as f:
    json.dump(totw_data, f, ensure_ascii=False, indent=2)
print("Saved data/all_matchdays_11_der_woche.json with Matchday 8!")

# Update lineups json
lineups_path = 'data/bundesliga_lineups_md1_7.json'
with open(lineups_path, 'r', encoding='utf-8') as f:
    lineups_data = json.load(f)

lineups_data["8"] = {
    "starters": [
        { "name": "Michael Zetterer", "club": "SV Werder Bremen", "pos": "TW", "minutes": 90, "clean_sheet": True, "saves": 5 },
        { "name": "Konrad Laimer", "club": "FC Bayern München", "pos": "RV", "minutes": 90, "goals": 1, "is_penalty": False },
        { "name": "Dayot Upamecano", "club": "FC Bayern München", "pos": "IV", "minutes": 90, "goals": 1, "is_penalty": False },
        { "name": "Willi Orbán", "club": "RB Leipzig", "pos": "IV", "minutes": 90, "clean_sheet": True },
        { "name": "Felix Götze", "club": "SC Paderborn 07", "pos": "LV", "minutes": 90, "clean_sheet": True, "clearances": 11 },
        { "name": "Felix Keidel", "club": "SV 07 Elversberg", "pos": "ZM", "minutes": 90, "goals": 1, "is_penalty": False },
        { "name": "Raphael Onyedika", "club": "Eintracht Frankfurt", "pos": "ZM", "minutes": 90, "goals": 1, "is_penalty": False },
        { "name": "Bilal El Khannouss", "club": "VfB Stuttgart", "pos": "OM", "minutes": 85, "goals": 1, "is_penalty": False },
        { "name": "Jamie Leweling", "club": "VfB Stuttgart", "pos": "RA", "minutes": 85, "goals": 1, "assists": 1, "is_penalty": False },
        { "name": "Ermedin Demirovic", "club": "VfB Stuttgart", "pos": "MS", "minutes": 90, "goals": 2, "is_penalty": False },
        { "name": "Antonio Nusa", "club": "RB Leipzig", "pos": "LA", "minutes": 90, "goals": 1, "is_penalty": True, "assists": 1 }
    ],
    "substitutes": [
        { "name": "Fábio Silva", "club": "Borussia Dortmund", "sub_minute": 76, "minutes": 14, "goals": 1, "is_penalty": False, "highlight": "Klassiker-Coup: Schockt die Bayern in der 89. Minute zum 2:2-Remis in der Allianz Arena!" },
        { "name": "Cyriaque Irié", "club": "SC Freiburg", "sub_minute": 83, "minutes": 7, "goals": 1, "is_penalty": False, "highlight": "Blitz-Joker: Erzielt 120 Sekunden nach Einwechslung das umjubelte 2:1-Siegtor beim FC Augsburg!" },
        { "name": "Malek El Mala", "club": "1. FC Köln", "sub_minute": 71, "minutes": 19, "goals": 1, "is_penalty": False, "highlight": "Traumdebüt par excellence: Trifft 8 Minuten nach Einwechslung mit seinem allerersten Bundesliga-Schuss zum 1:1 bei Union Berlin!" },
        { "name": "Cole Campbell", "club": "SV 07 Elversberg", "sub_minute": 77, "minutes": 13, "goals": 1, "is_penalty": False },
        { "name": "Igor Matanović", "club": "SC Freiburg", "sub_minute": 46, "minutes": 44, "goals": 1, "is_penalty": False }
    ]
}

with open('data/bundesliga_lineups_md1_8.json', 'w', encoding='utf-8') as f:
    json.dump(lineups_data, f, ensure_ascii=False, indent=2)
with open('data/bundesliga_lineups_md1_7.json', 'w', encoding='utf-8') as f:
    json.dump(lineups_data, f, ensure_ascii=False, indent=2)
print("Updated lineups database.")

# Update index.html and web_dashboard/index.html
totw_json_str = json.dumps(totw_data, ensure_ascii=False)

for target_file in ['index.html', 'web_dashboard/index.html']:
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Update totwData
    s_idx = content.find('const totwData = {')
    n_idx = content.find('let currentTotwMd =', s_idx)
    e_idx = content.rfind(';', s_idx, n_idx)
    content = content[:s_idx] + f"const totwData = {totw_json_str};" + content[e_idx+1:]
    
    # 2. Update currentTotwMd default to 8
    content = content.replace('let currentTotwMd = 7;', 'let currentTotwMd = 8;')
    
    # 3. Update nextMds in checkLiveOpenLigaDB
    content = content.replace('const nextMds = [8, 9, 10];', 'const nextMds = [9, 10, 11];')
    content = content.replace('Spieltage 1 bis 7 sind vollständig ausgewertet. Nächster Spieltag (Spieltag 8)', 'Spieltage 1 bis 8 sind vollständig ausgewertet. Nächster Spieltag (Spieltag 9)')
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {target_file}")

print("All files updated successfully for Matchday 8!")
