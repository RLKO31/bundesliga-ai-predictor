import json

with open('data/all_matchdays_11_der_woche.json', 'r', encoding='utf-8') as f:
    all_totw = json.load(f)

md7_entry = {
  "matchday": 7,
  "title": "7. Spieltag (2026/2027)",
  "formation": "3-5-2",
  "mvp": "Andrej Kramarić (TSG Hoffenheim)",
  "mvp_reason": "⭐ Matchwinner (78' FE) & Geniestreich-Dirigent beim 3:0-Triumph über Meister Leverkusen (TIP: 1.40, TDI: 2.45, xWAR: +0.78)",
  "coach": "Christian Ilzer (TSG Hoffenheim)",
  "fixtures_summary": [
    "VfB Stuttgart 2:3 Borussia Mönchengladbach",
    "RB Leipzig 4:0 SV 07 Elversberg",
    "FC Augsburg 1:1 1. FC Union Berlin",
    "1. FSV Mainz 05 2:3 SV Werder Bremen",
    "1. FC Köln 0:0 FC Schalke 04",
    "SC Paderborn 07 1:0 Hamburger SV",
    "Borussia Dortmund 1:0 Eintracht Frankfurt",
    "TSG Hoffenheim 3:0 Bayer 04 Leverkusen",
    "SC Freiburg 1:3 FC Bayern München"
  ],
  "lineup": [
    {
      "pos": "TW",
      "name": "Oliver Baumann",
      "club": "TSG Hoffenheim",
      "x": 50,
      "y": 88,
      "stat": "GSAE: +1.82 | QRSR: 2.15",
      "highlight": "Weiße Weste, 7 Glanzparaden (GSAE +1.82) beim 3:0 vs Leverkusen"
    },
    {
      "pos": "IV",
      "name": "Dayot Upamecano",
      "club": "FC Bayern München",
      "x": 25,
      "y": 72,
      "stat": "BLS: 2.35 | CDE: 5.50",
      "highlight": "Führungstor (16') + 95% Passquote beim 3:1 in Freiburg"
    },
    {
      "pos": "IV",
      "name": "Willi Orbán",
      "club": "RB Leipzig",
      "x": 50,
      "y": 74,
      "stat": "BLS: 2.40 | CDE: 6.00",
      "highlight": "Weiße Weste, 100% Luftduelle (6/6) beim 4:0 vs Elversberg"
    },
    {
      "pos": "IV",
      "name": "Felix Götze",
      "club": "SC Paderborn 07",
      "x": 75,
      "y": 72,
      "stat": "BLS: 2.28 | DSI: 2.90",
      "highlight": "Weiße Weste, 12 Klärungen beim 1:0-Sensationssieg vs HSV"
    },
    {
      "pos": "LM",
      "name": "Christoph Baumgartner",
      "club": "RB Leipzig",
      "x": 15,
      "y": 48,
      "stat": "TIP: 1.38 | BPS: 1.25",
      "highlight": "Tor (84') + 5 Großchancen-Kreationen beim 4:0 gegen Elversberg"
    },
    {
      "pos": "ZM",
      "name": "Alexander Prass",
      "club": "TSG Hoffenheim",
      "x": 35,
      "y": 50,
      "stat": "BPS: 1.35 | TIP: 1.25",
      "highlight": "Konter-Traumtor (90') + 6 Balleroberungen beim 3:0 vs Leverkusen"
    },
    {
      "pos": "ZM",
      "name": "Ludovit Reis",
      "club": "SV Werder Bremen",
      "x": 65,
      "y": 50,
      "stat": "TIP: 1.15 | BPS: 1.18",
      "highlight": "Entscheidendes Siegtor (61') beim 3:2-Auswärtssieg in Mainz"
    },
    {
      "pos": "RM",
      "name": "Joe Scally",
      "club": "Borussia Mönchengladbach",
      "x": 85,
      "y": 48,
      "stat": "TIP: 1.12 | DSI: 2.10",
      "highlight": "Wende-Ausgleichstor (38') beim 3:2-Auswärtscoup in Stuttgart"
    },
    {
      "pos": "OM",
      "name": "Andrej Kramarić",
      "club": "TSG Hoffenheim",
      "x": 50,
      "y": 36,
      "stat": "TIP: 1.40 | TDI: 2.45",
      "highlight": "⭐ MVP: Tor (78' FE) + Spielmacher-Dominanz beim 3:0 vs Leverkusen"
    },
    {
      "pos": "ST",
      "name": "Romulo",
      "club": "RB Leipzig",
      "x": 35,
      "y": 18,
      "stat": "TIP: 1.48 | Finishing: +1.55",
      "highlight": "Joker-Doppelpack (66', 94') beim 4:0-Kantersieg vs Elversberg"
    },
    {
      "pos": "ST",
      "name": "Niclas Füllkrug",
      "club": "SV Werder Bremen",
      "x": 65,
      "y": 18,
      "stat": "TIP: 1.42 | TDI: 2.85",
      "highlight": "Blitz-Doppelpack (6' FE, 24' FE) sichert 3:2-Auswärtssieg in Mainz"
    }
  ]
}

all_totw["7"] = md7_entry

with open('data/all_matchdays_11_der_woche.json', 'w', encoding='utf-8') as f:
    json.dump(all_totw, f, ensure_ascii=False, indent=2)

print("Updated data/all_matchdays_11_der_woche.json with Matchday 7!")
