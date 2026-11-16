import json
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# 1. Load existing all_matchdays_11_der_woche.json
totw_path = 'data/all_matchdays_11_der_woche.json'
with open(totw_path, 'r', encoding='utf-8') as f:
    totw_data = json.load(f)

# 2. Add Matchday 9
md9_entry = {
    "matchday": 9,
    "title": "9. Spieltag (2026/2027)",
    "formation": "4-3-3",
    "mvp": "Felix Nmecha (Borussia Dortmund)",
    "mvp_reason": "⭐ DOPPELPACK (55', 71') aus dem Mittelfeld heraus entscheidet den packenden 2:1-Heimsieg gegen den SV 07 Elversberg (TIP: 1.80, BPS: 1.45, xWAR: +0.82)",
    "coach": "Merlin Polzin (Hamburger SV)",
    "jokers": [
        {
            "rank": 1,
            "name": "Christoph Baumgartner",
            "club": "RB Leipzig",
            "min_in": "Eingewechselt (65')",
            "stat": "Tor in 66. Min. (60 Sek. nach Einwechslung) | TIP: 1.40",
            "highlight": "Blitz-Joker par excellence: Trifft nur eine Minute nach seiner Einwechslung eiskalt zum 5:1 gegen den FC Augsburg!"
        },
        {
            "rank": 2,
            "name": "Marvin Pieringer",
            "club": "SC Paderborn 07",
            "min_in": "Eingewechselt (65')",
            "stat": "Elfmetertor in 73. Min. | TIP: 1.25",
            "highlight": "Kaltblütiger Strafstoß-Joker: Verwandelt 8 Minuten nach Betreten des Rasens zur zwischenzeitlichen 2:1-Führung gegen Eintracht Frankfurt!"
        },
        {
            "rank": 3,
            "name": "Noel Futkeu",
            "club": "SV 07 Elversberg",
            "min_in": "Eingewechselt (78')",
            "stat": "Traumtor in 81. Min. | TIP: 1.20",
            "highlight": "Spektakulärer Seitfallzieher im Signal Iduna Park: Verkürzt nur drei Minuten nach Einwechslung zum 1:2 bei Borussia Dortmund!"
        }
    ],
    "fixtures_summary": [
        "Hamburger SV 3:1 Borussia Mönchengladbach",
        "Borussia Dortmund 2:1 SV 07 Elversberg",
        "RB Leipzig 5:2 FC Augsburg",
        "1. FSV Mainz 05 1:2 FC Bayern München",
        "SC Paderborn 07 2:2 Eintracht Frankfurt",
        "VfB Stuttgart 1:0 SV Werder Bremen",
        "1. FC Köln 1:2 Bayer 04 Leverkusen",
        "SC Freiburg 2:0 1. FC Union Berlin",
        "TSG Hoffenheim 2:1 FC Schalke 04"
    ],
    "lineup": [
        { "pos": "TW", "name": "Noah Atubolu", "club": "SC Freiburg", "x": 50, "y": 88, "stat": "GSAE: +1.50 | QRSR: 1.85", "highlight": "Starter (90 Min.), Weiße Weste, 6 Glanzparaden beim 2:0 gegen Union Berlin" },
        { "pos": "RV", "name": "Joe Scally", "club": "Borussia Mönchengladbach", "x": 82, "y": 70, "stat": "TIP: 1.10 | DSI: 2.45", "highlight": "Starter (90 Min.), Wuchtiger Ausgleichstreffer (44') & 7 Tackles beim HSV" },
        { "pos": "IV", "name": "Julian Chabot", "club": "VfB Stuttgart", "x": 60, "y": 74, "stat": "BLS: 2.45 | CDE: 6.50", "highlight": "Starter (90 Min.), Weiße Weste, 12 Klärungen/Blocks beim 1:0 gegen Bremen" },
        { "pos": "IV", "name": "Matthias Ginter", "club": "SC Freiburg", "x": 40, "y": 74, "stat": "BLS: 2.35 | CDE: 5.80", "highlight": "Starter (90 Min.), Weiße Weste, 100% Luftduelle beim 2:0 gegen Union" },
        { "pos": "LV", "name": "David Raum", "club": "RB Leipzig", "x": 18, "y": 70, "stat": "TIP: 1.55 | BPS: 1.35", "highlight": "Starter (90 Min.), Direktes Freistoßtor (46') + Vorlage beim 5:2 gegen Augsburg" },
        { "pos": "ZM", "name": "Joshua Kimmich", "club": "FC Bayern München", "x": 35, "y": 50, "stat": "BPS: 1.40 | xG Buildup: 1.35", "highlight": "Starter (86 Min.), Führungstor (14') & 96% Passquote beim 2:1 in Mainz" },
        { "pos": "ZM", "name": "Felix Nmecha", "club": "Borussia Dortmund", "x": 50, "y": 38, "stat": "TIP: 1.80 | xWAR: +0.82", "highlight": "⭐ MVP: Starter (90 Min.), Doppelpack (55', 71') sichert 2:1-Sieg gegen Elversberg" },
        { "pos": "ZM", "name": "Aleix García", "club": "Bayer 04 Leverkusen", "x": 65, "y": 50, "stat": "TIP: 1.25 | BPS: 1.30", "highlight": "Starter (90 Min.), Traum-Freistoßtor (7') & Taktgeber beim 2:1-Derbysieg in Köln" },
        { "pos": "RA", "name": "Fisnik Asllani", "club": "TSG Hoffenheim", "x": 80, "y": 20, "stat": "TIP: 1.55 | TDI: 2.65", "highlight": "Starter (78 Min.), Tor (10') + Vorlage (26') beim 2:1 gegen Schalke 04" },
        { "pos": "MS", "name": "Jonathan Burkardt", "club": "Eintracht Frankfurt", "x": 50, "y": 16, "stat": "TIP: 1.85 | TDI: 2.85", "highlight": "Starter (90 Min.), 2 Feldtore (23', 93' Hacke) retten 2:2 in Paderborn" },
        { "pos": "LA", "name": "Christopher Nkunku", "club": "RB Leipzig", "x": 20, "y": 20, "stat": "TIP: 1.55 | TDI: 2.40", "highlight": "Starter (75 Min.), Tor (35') + Vorlage beim 5:2-Torfestival gegen Augsburg" }
    ]
}

totw_data["9"] = md9_entry

# Validation: ensure 11 starters and 3 jokers for every matchday
for md_str, entry in totw_data.items():
    assert len(entry["lineup"]) == 11, f"MD {md_str} has {len(entry['lineup'])} players, expected 11"
    assert len(entry["jokers"]) == 3, f"MD {md_str} has {len(entry['jokers'])} jokers, expected 3"
    for p in entry["lineup"]:
        assert "Starter" in p["highlight"], f"Player {p['name']} in MD {md_str} must be starter"
        assert 0 <= p["x"] <= 100 and 0 <= p["y"] <= 100, f"Coords out of bounds for {p['name']}"

with open(totw_path, 'w', encoding='utf-8') as f:
    json.dump(totw_data, f, ensure_ascii=False, indent=2)
print("Saved data/all_matchdays_11_der_woche.json with Matchday 9!")

# Update lineups json
lineups_path = 'data/bundesliga_lineups_md1_8.json'
with open(lineups_path, 'r', encoding='utf-8') as f:
    lineups_data = json.load(f)

lineups_data["9"] = {
    "starters": [
        { "name": "Noah Atubolu", "club": "SC Freiburg", "pos": "TW", "minutes": 90, "clean_sheet": True, "saves": 6 },
        { "name": "Joe Scally", "club": "Borussia Mönchengladbach", "pos": "RV", "minutes": 90, "goals": 1, "is_penalty": False },
        { "name": "Julian Chabot", "club": "VfB Stuttgart", "pos": "IV", "minutes": 90, "clean_sheet": True, "clearances": 12 },
        { "name": "Matthias Ginter", "club": "SC Freiburg", "pos": "IV", "minutes": 90, "clean_sheet": True },
        { "name": "David Raum", "club": "RB Leipzig", "pos": "LV", "minutes": 90, "goals": 1, "assists": 1, "is_penalty": False },
        { "name": "Joshua Kimmich", "club": "FC Bayern München", "pos": "ZM", "minutes": 86, "goals": 1, "is_penalty": False },
        { "name": "Felix Nmecha", "club": "Borussia Dortmund", "pos": "ZM", "minutes": 90, "goals": 2, "is_penalty": False },
        { "name": "Aleix García", "club": "Bayer 04 Leverkusen", "pos": "ZM", "minutes": 90, "goals": 1, "is_penalty": False },
        { "name": "Fisnik Asllani", "club": "TSG Hoffenheim", "pos": "RA", "minutes": 78, "goals": 1, "assists": 1, "is_penalty": False },
        { "name": "Jonathan Burkardt", "club": "Eintracht Frankfurt", "pos": "MS", "minutes": 90, "goals": 2, "is_penalty": False },
        { "name": "Christopher Nkunku", "club": "RB Leipzig", "pos": "LA", "minutes": 75, "goals": 1, "assists": 1, "is_penalty": False }
    ],
    "substitutes": [
        { "name": "Christoph Baumgartner", "club": "RB Leipzig", "sub_minute": 65, "minutes": 25, "goals": 1, "is_penalty": False, "highlight": "Blitz-Joker par excellence: Trifft nur eine Minute nach seiner Einwechslung eiskalt zum 5:1 gegen den FC Augsburg!" },
        { "name": "Marvin Pieringer", "club": "SC Paderborn 07", "sub_minute": 65, "minutes": 25, "goals": 1, "is_penalty": True, "highlight": "Kaltblütiger Strafstoß-Joker: Verwandelt 8 Minuten nach Betreten des Rasens zur zwischenzeitlichen 2:1-Führung gegen Eintracht Frankfurt!" },
        { "name": "Noel Futkeu", "club": "SV 07 Elversberg", "sub_minute": 78, "minutes": 12, "goals": 1, "is_penalty": False, "highlight": "Spektakulärer Seitfallzieher im Signal Iduna Park: Verkürzt nur drei Minuten nach Einwechslung zum 1:2 bei Borussia Dortmund!" },
        { "name": "Junior Adamu", "club": "FC Schalke 04", "sub_minute": 70, "minutes": 20, "goals": 1, "is_penalty": False },
        { "name": "Uchenna Ogundu", "club": "FC Augsburg", "sub_minute": 80, "minutes": 10, "goals": 1, "is_penalty": False }
    ]
}

with open('data/bundesliga_lineups_md1_9.json', 'w', encoding='utf-8') as f:
    json.dump(lineups_data, f, ensure_ascii=False, indent=2)
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
    
    # 2. Update currentTotwMd default to 9
    content = content.replace('let currentTotwMd = 8;', 'let currentTotwMd = 9;')
    
    # 3. Update nextMds in checkLiveOpenLigaDB
    content = content.replace('const nextMds = [9, 10, 11];', 'const nextMds = [10, 11, 12];')
    content = content.replace('Spieltage 1 bis 8 sind vollständig ausgewertet. Nächster Spieltag (Spieltag 9)', 'Spieltage 1 bis 9 sind vollständig ausgewertet. Nächster Spieltag (Spieltag 10)')
    
    with open(target_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Updated {target_file}")

print("All files updated successfully for Matchday 9!")
