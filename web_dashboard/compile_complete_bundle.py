"""
===============================================================================
SENIOR ENGINEER MASTER BUNDLE COMPILER V6
REAL DFL / UNDERSTAT MULTI-SEASON TACTICAL ENGINE & DUAL PITCH CALIBRATION
===============================================================================
- Authentic match events from DFL / Understat across 6 seasons (2021-2027).
- Calibrated 105m x 68m pitch canvas with exact goal orientations.
- Dual Perspective: Unified Pitch (Defense on Left & Offense on Right simultaneously)
  or focused isolated views (Defensive Vulnerability vs. Attacking Threat).
- Action Filters: All Actions, Goals Only, Big Chances (xG >= 0.3), Open Play, Set-Pieces.
- Real player names, minutes, xG, situations, actions, and opponent tags on hover tooltip.
- 6-Channel Tactical Profiles with live progress bars for Defense and Offense.
- Dynamic Season Team Selector based on historical Bundesliga participation.
- Opponent Adaptability Leaderboard with archetypes and exploitation indexes.
===============================================================================
"""

import os
import json
import re

def compile_complete_bundle():
    print("--- Senior Engineer Master Bundle Compiler V6 (Authentic Multi-Season Tactical Engine) ---")
    
    # 1. Load All Datasets
    p2_path = "models/model_v1_v2_baseline/predictions_26_27_all.json" if os.path.exists("models/model_v1_v2_baseline/predictions_26_27_all.json") else "predictions_26_27_all.json"
    p3_path = "models/model_v3_tactical/predictions_v3_tactical.json" if os.path.exists("models/model_v3_tactical/predictions_v3_tactical.json") else "predictions_v3_tactical.json"
    p4_path = "models/model_v4_complexity/predictions_v4_complexity.json" if os.path.exists("models/model_v4_complexity/predictions_v4_complexity.json") else "predictions_v4_complexity.json"
    p5_path = "models/model_v5_matchday1_4/predictions_v5_m1_4.json" if os.path.exists("models/model_v5_matchday1_4/predictions_v5_m1_4.json") else "predictions_v5_m1_4.json"
    p6_path = "models/spatial_ai_kaggle/predictions_v6_spatial.json" if os.path.exists("models/spatial_ai_kaggle/predictions_v6_spatial.json") else "predictions_v6_spatial.json"
    p6_2stage_path = "models/spatial_ai_kaggle/predictions_v6_spatial_2stage.json" if os.path.exists("models/spatial_ai_kaggle/predictions_v6_spatial_2stage.json") else "predictions_v6_spatial_2stage.json"
    heatmaps_path = "models/spatial_ai_kaggle/predicted_fixture_heatmaps_v6.json" if os.path.exists("models/spatial_ai_kaggle/predicted_fixture_heatmaps_v6.json") else "predicted_fixture_heatmaps_v6.json"
    vuln_path = "data/team_vulnerabilities_multiseason.json" if os.path.exists("data/team_vulnerabilities_multiseason.json") else "team_vulnerabilities_multiseason.json"
    adapt_path = "data/tactical_adaptability_2026.json" if os.path.exists("data/tactical_adaptability_2026.json") else "tactical_adaptability_2026.json"

    with open(p2_path, "r", encoding="utf-8") as f: v2_data = json.load(f)
    with open(p3_path, "r", encoding="utf-8") as f: v3_data = json.load(f)
    with open(p4_path, "r", encoding="utf-8") as f: v4_data = json.load(f)
    with open(p5_path, "r", encoding="utf-8") as f: v5_data = json.load(f)
    with open(p6_path, "r", encoding="utf-8") as f: v6_data = json.load(f)
    with open(p6_2stage_path, "r", encoding="utf-8") as f: v6_2stage_data = json.load(f)
    with open(heatmaps_path, "r", encoding="utf-8") as f: heatmaps_data = json.load(f)
    with open(vuln_path, "r", encoding="utf-8") as f: vuln_data = json.load(f)
    with open(adapt_path, "r", encoding="utf-8") as f: adapt_data = json.load(f)

    # Filter Model v5 to 18 real teams
    b1_teams = [
        "Bayern Munich", "Bayer Leverkusen", "Borussia Dortmund", "SC Freiburg", 
        "RB Leipzig", "Eintracht Frankfurt", "VfB Stuttgart", "Mainz 05", 
        "Augsburg", "Werder Bremen", "Wolfsburg", "Bochum", "TSG Hoffenheim", 
        "FC Heidenheim", "Borussia M.Gladbach", "FC Cologne", "Union Berlin", "Hamburger SV"
    ]
    v5_filtered = [rec for rec in v5_data if rec.get('team') in b1_teams]
    for idx, rec in enumerate(v5_filtered): rec['rank'] = idx + 1

    # Stadium coordinates for all 18 Bundesliga teams
    stadiums = {
        "Bayern Munich": { "name": "Allianz Arena", "city": "Munich", "lat": 48.2188, "lng": 11.6247 },
        "Bayer Leverkusen": { "name": "BayArena", "city": "Leverkusen", "lat": 51.0383, "lng": 6.9839 },
        "Borussia Dortmund": { "name": "Signal Iduna Park", "city": "Dortmund", "lat": 51.4926, "lng": 7.4518 },
        "RB Leipzig": { "name": "Red Bull Arena", "city": "Leipzig", "lat": 51.3458, "lng": 12.3483 },
        "VfB Stuttgart": { "name": "MHPArena", "city": "Stuttgart", "lat": 48.7922, "lng": 9.2320 },
        "Eintracht Frankfurt": { "name": "Deutsche Bank Park", "city": "Frankfurt", "lat": 50.0686, "lng": 8.6455 },
        "SC Freiburg": { "name": "Europa-Park Stadion", "city": "Freiburg", "lat": 48.0208, "lng": 7.8228 },
        "Borussia M.Gladbach": { "name": "BORUSSIA-PARK", "city": "Mönchengladbach", "lat": 51.1747, "lng": 6.3856 },
        "Union Berlin": { "name": "Stadion An der Alten Försterei", "city": "Berlin", "lat": 52.4572, "lng": 13.5681 },
        "Werder Bremen": { "name": "Weserstadion", "city": "Bremen", "lat": 53.0664, "lng": 8.8377 },
        "Mainz 05": { "name": "MEWA ARENA", "city": "Mainz", "lat": 49.9841, "lng": 8.2242 },
        "TSG Hoffenheim": { "name": "PreZero Arena", "city": "Sinsheim", "lat": 49.2393, "lng": 8.8872 },
        "Augsburg": { "name": "WWK ARENA", "city": "Augsburg", "lat": 48.3228, "lng": 10.8860 },
        "FC Cologne": { "name": "RheinEnergieSTADION", "city": "Cologne", "lat": 50.9335, "lng": 6.8751 },
        "Hamburger SV": { "name": "Volksparkstadion", "city": "Hamburg", "lat": 53.5872, "lng": 9.8986 },
        "Paderborn": { "name": "Home Deluxe Arena", "city": "Paderborn", "lat": 51.7308, "lng": 8.7117 },
        "Elversberg": { "name": "URSAPHARM-Arena", "city": "Spiesen-Elversberg", "lat": 49.3131, "lng": 7.1286 },
        "Schalke 04": { "name": "VELTINS-Arena", "city": "Gelsenkirchen", "lat": 51.5545, "lng": 7.0675 }
    }

    team_logo_urls = {
        "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "FC Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
        "Bayer 04 Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
        "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Borussia_Dortmund_logo.svg/960px-Borussia_Dortmund_logo.svg.png",
        "RB Leipzig": "https://i.imgur.com/Rpwsjz1.png",
        "VfB Stuttgart": "https://i.imgur.com/v0tkpNx.png",
        "Eintracht Frankfurt": "https://i.imgur.com/X8NFkOb.png",
        "SC Freiburg": "https://i.imgur.com/r3mvi0h.png",
        "Borussia M.Gladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Union Berlin": "https://assets.dfb.de/uploads/000/018/232/small_union-Berlin.jpg",
        "Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/b/be/SV-Werder-Bremen-Logo.svg",
        "Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        "TSG Hoffenheim": "https://i.imgur.com/gF0PfEl.png",
        "Augsburg": "https://i.imgur.com/sdE62e2.png",
        "FC Cologne": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        "Hamburger SV": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Hamburger_SV_logo.svg",
        "Paderborn": "https://upload.wikimedia.org/wikipedia/commons/e/e3/SC_Paderborn_07_Logo.svg",
        "Elversberg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/SV_Elversberg_Logo.svg/500px-SV_Elversberg_Logo.svg.png",
        "Schalke 04": "https://upload.wikimedia.org/wikipedia/commons/9/97/FC_Schalke_04_Logo.png",
        "Wolfsburg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/VfL_Wolfsburg_logo_2026.svg/960px-VfL_Wolfsburg_logo_2026.svg.png",
        "Bochum": "https://i.imgur.com/5jy3Gfr.png",
        "FC Heidenheim": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846.svg",
        "St. Pauli": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Fc_st_pauli_logo.svg"
    }

    v2_json = json.dumps(v2_data, separators=(',', ':'))
    v3_json = json.dumps(v3_data, separators=(',', ':'))
    v4_json = json.dumps(v4_data, separators=(',', ':'))
    v5_json = json.dumps(v5_filtered, separators=(',', ':'))
    v6_json = json.dumps(v6_data, separators=(',', ':'))
    v6_2stage_json = json.dumps(v6_2stage_data, separators=(',', ':'))
    heatmaps_json = json.dumps(heatmaps_data, separators=(',', ':'))
    vuln_json = json.dumps(vuln_data, separators=(',', ':'))
    adapt_json = json.dumps(adapt_data, separators=(',', ':'))
    stadiums_json = json.dumps(stadiums, separators=(',', ':'))

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 2. Inject Data Block & getTeamLogo into <head>
    data_script_block = f"""
    <script id="embedded-data-state">
        window.stadiums = {stadiums_json};
        window.predictions_v2 = {v2_json};
        window.predictions_v3 = {v3_json};
        window.predictions_v4 = {v4_json};
        window.predictions_v5_m1_4 = {v5_json};
        window.predictions_v6 = {v6_json};
        window.predictions_v6_2stage = {v6_2stage_json};
        window.predicted_fixture_heatmaps = {heatmaps_json};
        window.team_vulnerabilities_multiseason = {vuln_json};
        window.real_bundesliga_match_events = {vuln_json};
        window.tactical_adaptability = {adapt_json};

        window.getTeamLogo = function(teamName) {{
            if (!teamName) return 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Placeholder_LC.svg';
            if (typeof teamLogos !== 'undefined' && teamLogos[teamName]) return teamLogos[teamName];
            let s = String(teamName);
            try {{ s = s.replace(/\\\\u[0-9a-f]{{4}}/gi, c => JSON.parse('"' + c + '"')); }} catch(e) {{}}
            const norm = s.toLowerCase().replace(/[äöüß]/g, m => ({{'ä':'a','ö':'o','ü':'u','ß':'ss'}}[m])).replace(/[^a-z0-9]/g, '');
            if (typeof teamLogos !== 'undefined') {{
                for (const k in teamLogos) {{
                    let kS = k;
                    try {{ kS = kS.replace(/\\\\u[0-9a-f]{{4}}/gi, c => JSON.parse('"' + c + '"')); }} catch(e) {{}}
                    const kNorm = kS.toLowerCase().replace(/[äöüß]/g, m => ({{'ä':'a','ö':'o','ü':'u','ß':'ss'}}[m])).replace(/[^a-z0-9]/g, '');
                    if (norm === kNorm || (norm.length > 3 && kNorm.includes(norm)) || (kNorm.length > 3 && norm.includes(kNorm))) {{
                        return teamLogos[k];
                    }}
                }}
            }}
            return 'https://upload.wikimedia.org/wikipedia/commons/e/e0/Placeholder_LC.svg';
        }};
    </script>
    """

    if '<script id="embedded-data-state">' in html:
        pattern = r'<script id="embedded-data-state">.*?</script>'
        html = re.sub(pattern, lambda m: data_script_block.strip(), html, flags=re.DOTALL)
    else:
        html = html.replace('</head>', data_script_block + '\n</head>')

    # 3. Add Custom CSS for Pills and Mode Buttons
    css_additions = """
        .vuln-filter-pill {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.12);
            color: var(--text-secondary);
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .vuln-filter-pill:hover {
            color: #fff;
            border-color: rgba(34, 197, 94, 0.4);
            background: rgba(255, 255, 255, 0.08);
        }
        .vuln-filter-pill.active {
            background: rgba(34, 197, 94, 0.2);
            color: var(--accent-lime);
            border-color: var(--accent-green);
            font-weight: 700;
            box-shadow: 0 0 10px rgba(34, 197, 94, 0.15);
        }
        .vuln-mode-btn {
            padding: 0.5rem 1.15rem;
            border-radius: 8px;
            font-size: 0.85rem;
            font-weight: 700;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.45rem;
            transition: all 0.2s;
            outline: none;
        }
    """
    if ".vuln-filter-pill" not in html:
        html = html.replace("</style>", css_additions + "\n    </style>")

    # 4. Replace Section #vulnerability-tab HTML
    vulnerability_sec_html = """
    <!-- Tab 8: Tactical Vulnerability & Chance Creation Tool -->
    <section id="vulnerability-tab" class="content-section">
        <div style="background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); margin-bottom: 2rem;">
            
            <!-- Header & Season/Team Controls -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(34, 197, 94, 0.1); padding-bottom: 1.25rem;">
                <div>
                    <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; color: #fff; display: flex; align-items: center; gap: 0.6rem;">
                        <i data-lucide="shield-alert" style="color: #ef4444;"></i> Tactical Pitch Map: Defense vs. Attack
                    </h2>
                    <p style="color: var(--text-secondary); font-size: 0.95rem; margin-top: 0.25rem;">
                        Authentic DFL & Understat match events (2021–2027). Conceded defensive vulnerabilities vs. created attacking threats with calibrated spatial pitch mapping.
                    </p>
                </div>
                
                <div style="display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;">
                    <!-- Season Dropdown -->
                    <div>
                        <label for="vuln-season-select" style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; margin-right: 0.4rem;">Season:</label>
                        <select id="vuln-season-select" onchange="onVulnSeasonChange(this.value)" style="background: rgba(4, 9, 5, 0.95); color: var(--accent-lime); border: 1px solid var(--accent-lime); padding: 0.5rem 1rem; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 0.88rem; outline: none;">
                            <option value="2026-2027" selected>2026/2027 (Current)</option>
                            <option value="2025-2026">2025/2026 Season</option>
                            <option value="2024-2025">2024/2025 Season</option>
                            <option value="2023-2024">2023/2024 Season</option>
                            <option value="2022-2023">2022/2023 Season</option>
                            <option value="2021-2022">2021/2022 Season</option>
                        </select>
                    </div>

                    <!-- Team Dropdown (Populated Dynamically) -->
                    <div>
                        <label for="vuln-team-select" style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; margin-right: 0.4rem;">Team:</label>
                        <select id="vuln-team-select" onchange="renderTeamVulnerability(this.value, document.getElementById('vuln-season-select').value)" style="background: rgba(4, 9, 5, 0.95); color: #fff; border: 1px solid var(--accent-green); padding: 0.5rem 1rem; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.88rem; outline: none;">
                            <option value="Bayern Munich">Bayern Munich</option>
                            <option value="Bayer Leverkusen">Bayer Leverkusen</option>
                            <option value="Borussia Dortmund">Borussia Dortmund</option>
                            <option value="RB Leipzig">RB Leipzig</option>
                        </select>
                    </div>
                </div>
            </div>

            <!-- Tactical Perspective & Filter Bar -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; background: rgba(255, 255, 255, 0.02); padding: 0.85rem 1.25rem; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.06);">
                <div style="display: flex; gap: 0.5rem; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; margin-right: 0.2rem;">Perspective:</span>
                    <button id="btn-persp-unified" class="vuln-mode-btn" onclick="setTacticalPerspective('unified')" style="border: 1px solid var(--accent-green); background: rgba(34, 197, 94, 0.2); color: var(--accent-lime);">
                        <i data-lucide="split" size="15"></i> Unified Pitch (Dual View)
                    </button>
                    <button id="btn-persp-def" class="vuln-mode-btn" onclick="setTacticalPerspective('defense')" style="border: 1px solid rgba(255,255,255,0.15); background: transparent; color: var(--text-secondary);">
                        <i data-lucide="shield" size="15"></i> Defensive Vulnerability (Conceded)
                    </button>
                    <button id="btn-persp-off" class="vuln-mode-btn" onclick="setTacticalPerspective('offense')" style="border: 1px solid rgba(255,255,255,0.15); background: transparent; color: var(--text-secondary);">
                        <i data-lucide="swords" size="15"></i> Attacking Threat (Created)
                    </button>
                </div>

                <!-- Event Filter Pills -->
                <div style="display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 0.8rem; color: var(--text-secondary); margin-right: 0.2rem;">Filter:</span>
                    <button class="vuln-filter-pill active" onclick="setTacticalFilter('all', this)">All Actions</button>
                    <button class="vuln-filter-pill" onclick="setTacticalFilter('goals', this)">⚽ Goals Only</button>
                    <button class="vuln-filter-pill" onclick="setTacticalFilter('big', this)">🔶 Big Chances (xG ≥ 0.3)</button>
                    <button class="vuln-filter-pill" onclick="setTacticalFilter('open', this)">🎯 Open Play</button>
                    <button class="vuln-filter-pill" onclick="setTacticalFilter('setpiece', this)">🚩 Set-Pieces</button>
                </div>
            </div>

            <!-- Pitch Visualizer Card -->
            <div style="background: rgba(10, 26, 14, 0.95); border: 2px solid rgba(34, 197, 94, 0.4); border-radius: 20px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: inset 0 0 50px rgba(0,0,0,0.85);">
                
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 0.75rem;">
                    <h3 id="tactical-pitch-heading" style="font-size: 1.15rem; color: #fff; display: flex; align-items: center; gap: 0.5rem; font-family: 'Space Grotesk', sans-serif; margin: 0;">
                        <i data-lucide="map-pin" style="color: var(--accent-lime);"></i> Unified Full-Pitch Tactical Map (105m x 68m)
                    </h3>
                    
                    <div id="tactical-kpi-strip" style="display: flex; gap: 0.6rem; font-size: 0.78rem; font-weight: 700; align-items: center;"></div>
                </div>

                <!-- Canvas Pitch Container -->
                <div class="pitch-container" style="position: relative; width: 100%; height: 380px; background: rgba(5, 18, 9, 0.98); border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 16px; overflow: hidden; box-shadow: inset 0 0 50px rgba(0,0,0,0.85);">
                    <canvas id="unified-pitch-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; cursor: crosshair;"></canvas>
                    <!-- Floating Shot Tooltip -->
                    <div id="unified-pitch-tooltip" style="position: absolute; display: none; z-index: 20; pointer-events: none; background: rgba(9, 20, 12, 0.96); border: 1px solid var(--accent-lime); padding: 0.55rem 0.85rem; border-radius: 8px; font-size: 0.76rem; color: #fff; box-shadow: 0 4px 20px rgba(0,0,0,0.7); transform: translate(-50%, -120%); backdrop-filter: blur(10px); min-width: 170px;"></div>
                </div>

                <!-- Legend & Orientation Bar -->
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.85rem; font-size: 0.8rem; color: var(--text-secondary); flex-wrap: wrap; gap: 0.5rem;">
                    <div style="display: flex; gap: 1.25rem; align-items: center; flex-wrap: wrap;">
                        <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #ef4444; border-radius: 50%; border: 1px solid #fff;"></span> Conceded Goal</span>
                        <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #fb923c; transform: rotate(45deg); border: 1px solid #fff;"></span> Conceded Big Chance</span>
                        <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #10b981; border-radius: 50%; border: 1px solid #fff;"></span> Scored Goal</span>
                        <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #38bdf8; transform: rotate(45deg); border: 1px solid #fff;"></span> Created Big Chance</span>
                        <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 14px; height: 5px; background: rgba(239, 68, 68, 0.6); border-radius: 2px;"></span> xG Density Heatmap</span>
                    </div>
                    <div id="tactical-orientation-indicator" style="font-weight: 600; color: #9ca3af; font-size: 0.78rem;"></div>
                </div>
            </div>

            <!-- Breakdown Cards (Defensive vs. Attacking) -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                <div id="vuln-team-card" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(239, 68, 68, 0.25); border-radius: 16px; padding: 1.35rem; display: flex; flex-direction: column; justify-content: space-between;"></div>
                <div id="attack-team-card" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(16, 185, 129, 0.25); border-radius: 16px; padding: 1.35rem; display: flex; flex-direction: column; justify-content: space-between;"></div>
            </div>

            <!-- Opponent Adaptability Leaderboard -->
            <div style="margin-top: 2rem; border-top: 1px solid rgba(34, 197, 94, 0.1); padding-top: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
                    <h3 style="font-size: 1.2rem; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem; font-family: 'Space Grotesk', sans-serif;">
                        <i data-lucide="bar-chart-3" style="color: var(--accent-lime);"></i> Bundesliga Opponent Adaptability Leaderboard (Dogmatic vs. Chameleon)
                    </h3>
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">Click any club to inspect their spatial shot profile</span>
                </div>
                <div style="overflow-x: auto;">
                    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem;">
                        <thead>
                            <tr style="border-bottom: 1px solid rgba(34, 197, 94, 0.2); color: var(--text-secondary);">
                                <th style="padding: 0.75rem;">Rank</th>
                                <th style="padding: 0.75rem;">Team Name</th>
                                <th style="padding: 0.75rem;">Tactical Archetype</th>
                                <th style="padding: 0.75rem;">Plan Adherence ($S_{\\text{dogma}}$)</th>
                                <th style="padding: 0.75rem;">Opponent Exploitation Index</th>
                                <th style="padding: 0.75rem;">Tactical Motto</th>
                            </tr>
                        </thead>
                        <tbody id="adaptability-table-body"></tbody>
                    </table>
                </div>
            </div>

        </div>
    </section>
    """

    pattern_vulnerability_sec = r'<section id="vulnerability-tab".*?</section>'
    html = re.sub(pattern_vulnerability_sec, lambda m: vulnerability_sec_html.strip(), html, flags=re.DOTALL)

    # 5. Master JavaScript Tactical Engine
    js_tactical_master = """
        window.currentTacticalPerspective = 'unified';
        window.currentTacticalFilter = 'all';
        window.unifiedPlottedShots = [];

        function resolveTeamData(teamName) {
            if (!window.team_vulnerabilities_multiseason) return null;
            const root = window.team_vulnerabilities_multiseason;
            const teamsObj = root.teams || root;
            if (teamsObj[teamName]) return teamsObj[teamName];
            
            const norm = (teamName || '').replace('FC ', '').replace('1. ', '').replace('SV ', '').replace('VfB ', '').replace('VfL ', '').replace('TSG ', '').trim().toLowerCase();
            for (let k in teamsObj) {
                const kNorm = k.replace('FC ', '').replace('1. ', '').replace('SV ', '').replace('VfB ', '').replace('VfL ', '').replace('TSG ', '').trim().toLowerCase();
                if (kNorm.length > 2 && (kNorm.includes(norm) || norm.includes(kNorm))) {
                    return teamsObj[k];
                }
            }
            return teamsObj['Bayern Munich'] || Object.values(teamsObj)[0];
        }

        function updateTeamDropdown(season) {
            const select = document.getElementById('vuln-team-select');
            if (!select || !window.team_vulnerabilities_multiseason) return;
            const root = window.team_vulnerabilities_multiseason;
            const catalog = root.catalog || {};
            const teamsObj = root.teams || root;
            const teamsForSeason = catalog[season] || Object.keys(teamsObj).filter(t => teamsObj[t][season]);
            
            const currentVal = select.value;
            select.innerHTML = '';
            teamsForSeason.forEach(t => {
                const opt = document.createElement('option');
                opt.value = t;
                opt.textContent = t;
                if (t === currentVal) opt.selected = true;
                select.appendChild(opt);
            });
            if (!select.value && teamsForSeason.length > 0) {
                select.value = teamsForSeason.includes("Bayern Munich") ? "Bayern Munich" : teamsForSeason[0];
            }
        }

        function onVulnSeasonChange(season) {
            updateTeamDropdown(season);
            const team = document.getElementById('vuln-team-select').value;
            renderTeamVulnerability(team, season);
            populateAdaptabilityTable(season);
        }

        function setTacticalPerspective(mode) {
            window.currentTacticalPerspective = mode;
            const btnUni = document.getElementById('btn-persp-unified');
            const btnDef = document.getElementById('btn-persp-def');
            const btnOff = document.getElementById('btn-persp-off');
            
            [btnUni, btnDef, btnOff].forEach(b => {
                if (b) {
                    b.style.background = 'transparent';
                    b.style.borderColor = 'rgba(255,255,255,0.15)';
                    b.style.color = 'var(--text-secondary)';
                }
            });

            if (mode === 'unified' && btnUni) {
                btnUni.style.background = 'rgba(34, 197, 94, 0.2)';
                btnUni.style.borderColor = 'var(--accent-green)';
                btnUni.style.color = 'var(--accent-lime)';
            } else if (mode === 'defense' && btnDef) {
                btnDef.style.background = 'rgba(239, 68, 68, 0.2)';
                btnDef.style.borderColor = '#ef4444';
                btnDef.style.color = '#f87171';
            } else if (mode === 'offense' && btnOff) {
                btnOff.style.background = 'rgba(56, 189, 248, 0.2)';
                btnOff.style.borderColor = '#38bdf8';
                btnOff.style.color = '#38bdf8';
            }

            drawUnifiedPitch();
        }

        function setTacticalFilter(filter, btn) {
            window.currentTacticalFilter = filter;
            document.querySelectorAll('.vuln-filter-pill').forEach(el => el.classList.remove('active'));
            if (btn) btn.classList.add('active');
            drawUnifiedPitch();
        }

        function renderTeamVulnerability(teamName, seasonName) {
            teamName = teamName || (document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich');
            seasonName = seasonName || (document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027');
            
            const seasonData = resolveTeamData(teamName);
            if (!seasonData) return;
            const data = seasonData[seasonName] || seasonData['2026-2027'] || Object.values(seasonData)[0];
            if (!data) return;

            const def = data.defense || data;
            const off = data.offense || data;
            const prof = data.tactical_profile || {};

            // 1. Render Left Card: Defensive Weaknesses
            const vulnCard = document.getElementById("vuln-team-card");
            if (vulnCard) {
                const db = def.channel_breakdown || {};
                vulnCard.innerHTML = `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
                            <div>
                                <h4 style="font-size: 1.25rem; color: #fff; font-family: 'Space Grotesk', sans-serif;">${data.team_name} (Defensive Weaknesses)</h4>
                                <span style="font-size: 0.8rem; color: #ef4444; font-weight: 600;">Season: ${data.season}</span>
                            </div>
                            <span style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 0.25rem 0.65rem; border-radius: 6px; font-size: 0.78rem; font-weight: 700;">
                                Weakness: ${def.primary_weakness || 'Balanced'}
                            </span>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; background: rgba(0,0,0,0.25); padding: 0.75rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.82rem;">
                            <div><span style="color: var(--text-secondary);">Goals Conceded:</span> <strong style="color: #ef4444;">${def.conceded_goals}</strong></div>
                            <div><span style="color: var(--text-secondary);">Shots Conceded:</span> <strong style="color: #fff;">${def.total_shots_conceded}</strong></div>
                            <div><span style="color: var(--text-secondary);">Expected xGA:</span> <strong style="color: var(--accent-lime);">${def.xg_conceded || 'N/A'}</strong></div>
                            <div><span style="color: var(--text-secondary);">Big Chances Conceded:</span> <strong style="color: #fb923c;">${def.big_chances_conceded}</strong></div>
                        </div>

                        <div style="margin-bottom: 0.75rem;">
                            <div style="font-weight: 700; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.45rem;">6-Channel Conceded Vulnerabilities:</div>
                            
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Left Flank Crosses</span><span style="font-weight: 700;">${db.left_flank_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${db.left_flank_pct}%; background: #ef4444; height: 100%;"></div></div>
                            </div>
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Right Flank Crosses</span><span style="font-weight: 700;">${db.right_flank_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${db.right_flank_pct}%; background: #f97316; height: 100%;"></div></div>
                            </div>
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Central Combinations</span><span style="font-weight: 700;">${db.central_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${db.central_pct}%; background: #eab308; height: 100%;"></div></div>
                            </div>
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Set-Pieces & Standards</span><span style="font-weight: 700;">${db.set_piece_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${db.set_piece_pct}%; background: #a855f7; height: 100%;"></div></div>
                            </div>
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Fast Counter-Attacks</span><span style="font-weight: 700;">${db.counter_attack_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${db.counter_attack_pct}%; background: #38bdf8; height: 100%;"></div></div>
                            </div>
                            <div>
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>High-Press Turnovers</span><span style="font-weight: 700;">${db.high_turnover_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${db.high_turnover_pct}%; background: #10b981; height: 100%;"></div></div>
                            </div>
                        </div>
                    </div>
                    <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.65rem; font-size: 0.78rem; color: var(--text-secondary); margin-top: 0.5rem;">
                        <span>Defending Net Orientation: <strong>Left Touchline & Goal (X = 0m)</strong></span>
                    </div>
                `;
            }

            // 2. Render Right Card: Attacking Weapons
            const attackCard = document.getElementById("attack-team-card");
            if (attackCard) {
                const ob = off.channel_breakdown || {};
                attackCard.innerHTML = `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
                            <div>
                                <h4 style="font-size: 1.25rem; color: #fff; font-family: 'Space Grotesk', sans-serif;">${data.team_name} (Attacking Weapons)</h4>
                                <span style="font-size: 0.8rem; color: var(--accent-lime); font-weight: 600;">Season: ${data.season}</span>
                            </div>
                            <span style="background: rgba(34, 197, 94, 0.2); color: var(--accent-lime); border: 1px solid rgba(34, 197, 94, 0.4); padding: 0.25rem 0.65rem; border-radius: 6px; font-size: 0.78rem; font-weight: 700;">
                                Strength: ${off.primary_strength || 'Balanced'}
                            </span>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; background: rgba(0,0,0,0.25); padding: 0.75rem; border-radius: 10px; margin-bottom: 1rem; font-size: 0.82rem;">
                            <div><span style="color: var(--text-secondary);">Goals Scored:</span> <strong style="color: var(--accent-lime);">${off.goals_scored}</strong></div>
                            <div><span style="color: var(--text-secondary);">Shots Created:</span> <strong style="color: #fff;">${off.total_shots_created}</strong></div>
                            <div><span style="color: var(--text-secondary);">Expected xG:</span> <strong style="color: var(--accent-lime);">${off.xg_created || 'N/A'}</strong></div>
                            <div><span style="color: var(--text-secondary);">Big Chances Created:</span> <strong style="color: #38bdf8;">${off.big_chances_created}</strong></div>
                        </div>

                        <div style="margin-bottom: 0.75rem;">
                            <div style="font-weight: 700; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.45rem;">6-Channel Attack Creation Profile:</div>
                            
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Left Flank Crosses</span><span style="font-weight: 700;">${ob.left_flank_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ob.left_flank_pct}%; background: #ef4444; height: 100%;"></div></div>
                            </div>
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Right Flank Crosses</span><span style="font-weight: 700;">${ob.right_flank_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ob.right_flank_pct}%; background: #f97316; height: 100%;"></div></div>
                            </div>
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Central Combinations</span><span style="font-weight: 700;">${ob.central_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ob.central_pct}%; background: #eab308; height: 100%;"></div></div>
                            </div>
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Set-Pieces & Standards</span><span style="font-weight: 700;">${ob.set_piece_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ob.set_piece_pct}%; background: #a855f7; height: 100%;"></div></div>
                            </div>
                            <div style="margin-bottom: 0.35rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Fast Counter-Attacks</span><span style="font-weight: 700;">${ob.counter_attack_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ob.counter_attack_pct}%; background: #38bdf8; height: 100%;"></div></div>
                            </div>
                            <div>
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>High-Press Turnovers</span><span style="font-weight: 700;">${ob.high_turnover_pct}%</span></div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ob.high_turnover_pct}%; background: #10b981; height: 100%;"></div></div>
                            </div>
                        </div>
                    </div>
                    ${prof.archetype ? `
                    <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.65rem; font-size: 0.78rem; margin-top: 0.5rem;">
                        <div style="color: var(--accent-lime); font-weight: 700;">Tactical Archetype: ${prof.archetype}</div>
                        <div style="color: var(--text-secondary); font-style: italic;">"${prof.motto}"</div>
                    </div>` : ''}
                `;
            }

            // 3. Draw Pitch Canvas
            drawUnifiedPitch();
            if (window.lucide) window.lucide.createIcons();
        }

        function drawUnifiedPitch() {
            const teamName = document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich';
            const seasonName = document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027';
            
            const seasonData = resolveTeamData(teamName);
            if (!seasonData) return;
            const data = seasonData[seasonName] || seasonData['2026-2027'] || Object.values(seasonData)[0];
            if (!data) return;

            const def = data.defense || data;
            const off = data.offense || data;
            const mode = window.currentTacticalPerspective || 'unified';
            const filter = window.currentTacticalFilter || 'all';

            // Update Heading & Strip
            const headEl = document.getElementById("tactical-pitch-heading");
            const stripEl = document.getElementById("tactical-kpi-strip");
            const orientEl = document.getElementById("tactical-orientation-indicator");

            if (headEl) {
                if (mode === 'unified') headEl.innerHTML = '<i data-lucide="map-pin" style="color: var(--accent-lime);"></i> Unified Tactical Pitch: Defense vs. Attack (105m x 68m)';
                else if (mode === 'defense') headEl.innerHTML = '<i data-lucide="shield-alert" style="color: #ef4444;"></i> Defensive Vulnerabilities: Conceded Chances & Goals (105m x 68m)';
                else headEl.innerHTML = '<i data-lucide="crosshair" style="color: var(--accent-lime);"></i> Attacking Weapons: Created Chances & Goals Scored (105m x 68m)';
            }

            if (stripEl) {
                if (mode === 'unified') {
                    stripEl.innerHTML = `
                        <span style="background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid rgba(239,68,68,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Conceded: ${def.conceded_goals} (${def.big_chances_conceded} BC)</span>
                        <span style="background: rgba(34, 197, 94, 0.18); color: var(--accent-lime); border: 1px solid rgba(34,197,94,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Scored: ${off.goals_scored} (${off.big_chances_created} BC)</span>
                    `;
                } else if (mode === 'defense') {
                    stripEl.innerHTML = `
                        <span style="background: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid rgba(239,68,68,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Goals Conceded: ${def.conceded_goals}</span>
                        <span style="background: rgba(251, 146, 60, 0.18); color: #fb923c; border: 1px solid rgba(251,146,60,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Big Chances: ${def.big_chances_conceded}</span>
                        <span style="background: rgba(255,255,255,0.06); color: #9ca3af; border: 1px solid rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 6px;">xGA: ${def.xg_conceded || 'N/A'}</span>
                    `;
                } else {
                    stripEl.innerHTML = `
                        <span style="background: rgba(34, 197, 94, 0.18); color: var(--accent-lime); border: 1px solid rgba(34,197,94,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Goals Scored: ${off.goals_scored}</span>
                        <span style="background: rgba(56, 189, 248, 0.18); color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Big Chances: ${off.big_chances_created}</span>
                        <span style="background: rgba(255,255,255,0.06); color: #9ca3af; border: 1px solid rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 6px;">xG: ${off.xg_created || 'N/A'}</span>
                    `;
                }
            }

            if (orientEl) {
                if (mode === 'unified') {
                    orientEl.innerHTML = '<span style="color:#f87171;">🛡️ DEFENDING (Left [X=0m])</span> &nbsp;|&nbsp; <span style="color:var(--accent-lime);">🎯 ATTACKING (Right [X=105m])</span>';
                } else if (mode === 'defense') {
                    orientEl.innerHTML = '<span style="color:#f87171;">🛡️ DEFENDING NET (Left [X=0m])</span> &nbsp;⬅️ Opponent Infiltration';
                } else {
                    orientEl.innerHTML = '<span style="color:var(--accent-lime);">🎯 TARGET NET (Right [X=105m])</span> &nbsp;➡️ Attack Trajectory';
                }
            }

            const canvas = document.getElementById("unified-pitch-canvas");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            const container = canvas.parentElement;
            canvas.width = container.clientWidth || 900;
            canvas.height = container.clientHeight || 380;
            
            const W = canvas.width;
            const H = canvas.height;
            ctx.clearRect(0, 0, W, H);

            // Container turf background
            ctx.fillStyle = "#051208";
            ctx.fillRect(0, 0, W, H);

            // Strict 105:68 aspect ratio
            const pitchRatio = 105.0 / 68.0;
            const margin = 16;
            const maxPWidth = W - margin * 2;
            const maxPHeight = H - margin * 2;
            let pW, pH;
            if (maxPWidth / maxPHeight > pitchRatio) {
                pH = maxPHeight;
                pW = pH * pitchRatio;
            } else {
                pW = maxPWidth;
                pH = pW / pitchRatio;
            }
            const pitchX = (W - pW) / 2;
            const pitchY = (H - pH) / 2;

            // Grass Fill & Stripes
            ctx.fillStyle = "#091c0f";
            ctx.fillRect(pitchX, pitchY, pW, pH);

            const numStripes = 10;
            const stripeW = pW / numStripes;
            for (let i = 0; i < numStripes; i++) {
                if (i % 2 === 0) {
                    ctx.fillStyle = "rgba(255, 255, 255, 0.03)";
                    ctx.fillRect(pitchX + i * stripeW, pitchY, stripeW, pH);
                }
            }

            const mapX = (x) => pitchX + (x / 105.0) * pW;
            const mapY = (y) => pitchY + (y / 68.0) * pH;

            function shotPassesFilter(sh) {
                const isGoal = Array.isArray(sh) ? sh[3] === 1 : (sh.is_goal || false);
                const xg = Array.isArray(sh) ? sh[2] : (sh.xg || 0);
                const sit = Array.isArray(sh) ? sh[7] : (sh.situation || 'OpenPlay');
                if (filter === 'goals') return isGoal;
                if (filter === 'big') return xg >= 0.30;
                if (filter === 'open') return sit === 'OpenPlay';
                if (filter === 'setpiece') return sit !== 'OpenPlay';
                return true;
            }

            const defShots = (def.shots || []).filter(shotPassesFilter);
            const offShots = (off.shots || []).filter(shotPassesFilter);

            // 1. Density Heatmaps (Radial Gaussian Glows under pitch lines)
            if (mode === 'unified' || mode === 'defense') {
                defShots.forEach(sh => {
                    const sx = Array.isArray(sh) ? sh[0] : sh.x;
                    const sy = Array.isArray(sh) ? sh[1] : sh.y;
                    const xg = Array.isArray(sh) ? sh[2] : sh.xg;
                    const px = mapX(sx);
                    const py = mapY(sy);
                    const radius = Math.min(36, Math.max(16, xg * 50));
                    const grad = ctx.createRadialGradient(px, py, 0, px, py, radius);
                    grad.addColorStop(0, `rgba(239, 68, 68, ${Math.min(0.48, xg * 0.85)})`);
                    grad.addColorStop(1, 'rgba(239, 68, 68, 0)');
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(px, py, radius, 0, 2 * Math.PI);
                    ctx.fill();
                });
            }

            if (mode === 'unified' || mode === 'offense') {
                offShots.forEach(sh => {
                    const sx = Array.isArray(sh) ? sh[0] : sh.x;
                    const sy = Array.isArray(sh) ? sh[1] : sh.y;
                    const xg = Array.isArray(sh) ? sh[2] : sh.xg;
                    const px = mapX(sx);
                    const py = mapY(sy);
                    const radius = Math.min(36, Math.max(16, xg * 50));
                    const grad = ctx.createRadialGradient(px, py, 0, px, py, radius);
                    grad.addColorStop(0, `rgba(34, 197, 94, ${Math.min(0.48, xg * 0.85)})`);
                    grad.addColorStop(1, 'rgba(34, 197, 94, 0)');
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(px, py, radius, 0, 2 * Math.PI);
                    ctx.fill();
                });
            }

            // 2. Pitch Geometry Markings
            ctx.strokeStyle = "rgba(255, 255, 255, 0.45)";
            ctx.lineWidth = 1.6;

            // Boundary
            ctx.strokeRect(pitchX, pitchY, pW, pH);

            // Halfway Line
            ctx.beginPath();
            ctx.moveTo(mapX(52.5), pitchY);
            ctx.lineTo(mapX(52.5), pitchY + pH);
            ctx.stroke();

            // Center Circle & Spot
            ctx.beginPath();
            ctx.arc(mapX(52.5), mapY(34.0), (9.15 / 68.0) * pH, 0, 2 * Math.PI);
            ctx.stroke();
            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.arc(mapX(52.5), mapY(34.0), 2.5, 0, 2 * Math.PI);
            ctx.fill();

            // 18-Yard Boxes
            ctx.strokeRect(mapX(0), mapY(13.84), mapX(16.5) - mapX(0), mapY(54.16) - mapY(13.84));
            ctx.strokeRect(mapX(88.5), mapY(13.84), mapX(105) - mapX(88.5), mapY(54.16) - mapY(13.84));

            // 6-Yard Boxes
            ctx.strokeRect(mapX(0), mapY(24.84), mapX(5.5) - mapX(0), mapY(43.16) - mapY(24.84));
            ctx.strokeRect(mapX(99.5), mapY(24.84), mapX(105) - mapX(99.5), mapY(43.16) - mapY(24.84));

            // Penalty Spots
            ctx.fillStyle = "#ffffff";
            ctx.beginPath(); ctx.arc(mapX(11.0), mapY(34.0), 2.5, 0, 2 * Math.PI); ctx.fill();
            ctx.beginPath(); ctx.arc(mapX(94.0), mapY(34.0), 2.5, 0, 2 * Math.PI); ctx.fill();

            // Penalty D-Arcs
            const dAlpha = Math.acos(5.5 / 9.15);
            const dRadius = (9.15 / 68.0) * pH;
            ctx.beginPath(); ctx.arc(mapX(11.0), mapY(34.0), dRadius, -dAlpha, dAlpha); ctx.stroke();
            ctx.beginPath(); ctx.arc(mapX(94.0), mapY(34.0), dRadius, Math.PI - dAlpha, Math.PI + dAlpha); ctx.stroke();

            // Goal Posts & Nets
            const goalH = mapY(37.66) - mapY(30.34);
            const goalY = mapY(30.34);
            const netD = 7;

            // Defending Goal (Left)
            ctx.fillStyle = "rgba(239, 68, 68, 0.4)";
            ctx.fillRect(pitchX - netD, goalY, netD, goalH);
            ctx.strokeStyle = "#ef4444";
            ctx.strokeRect(pitchX - netD, goalY, netD, goalH);

            // Attacking Goal (Right)
            ctx.fillStyle = "rgba(34, 197, 94, 0.4)";
            ctx.fillRect(pitchX + pW, goalY, netD, goalH);
            ctx.strokeStyle = "var(--accent-lime)";
            ctx.strokeRect(pitchX + pW, goalY, netD, goalH);

            // 3. Precise Shot Markers & Live Tooltip Cache
            window.unifiedPlottedShots = [];

            if (mode === 'unified' || mode === 'defense') {
                defShots.forEach(sh => {
                    const sx = Array.isArray(sh) ? sh[0] : sh.x;
                    const sy = Array.isArray(sh) ? sh[1] : sh.y;
                    const xg = Array.isArray(sh) ? sh[2] : sh.xg;
                    const isGoal = Array.isArray(sh) ? sh[3] === 1 : sh.is_goal;

                    const px = mapX(sx);
                    const py = mapY(sy);
                    window.unifiedPlottedShots.push({ px, py, raw: sh, isDef: true });

                    if (isGoal) {
                        ctx.beginPath();
                        ctx.arc(px, py, 5.5, 0, 2 * Math.PI);
                        ctx.fillStyle = "#ef4444";
                        ctx.fill();
                        ctx.lineWidth = 1.6;
                        ctx.strokeStyle = "#ffffff";
                        ctx.stroke();
                        ctx.beginPath(); ctx.arc(px, py, 2, 0, 2 * Math.PI); ctx.fillStyle = "#ffffff"; ctx.fill();
                    } else if (xg >= 0.30) {
                        ctx.fillStyle = "#fb923c";
                        ctx.beginPath();
                        ctx.moveTo(px, py - 4.5); ctx.lineTo(px + 4.5, py); ctx.lineTo(px, py + 4.5); ctx.lineTo(px - 4.5, py);
                        ctx.closePath(); ctx.fill();
                        ctx.lineWidth = 1.2; ctx.strokeStyle = "#ffffff"; ctx.stroke();
                    } else {
                        const r = Math.min(4, Math.max(2.5, xg * 14));
                        ctx.beginPath(); ctx.arc(px, py, r, 0, 2 * Math.PI);
                        ctx.fillStyle = "#38bdf8"; ctx.fill();
                        ctx.lineWidth = 0.8; ctx.strokeStyle = "rgba(255,255,255,0.7)"; ctx.stroke();
                    }
                });
            }

            if (mode === 'unified' || mode === 'offense') {
                offShots.forEach(sh => {
                    const sx = Array.isArray(sh) ? sh[0] : sh.x;
                    const sy = Array.isArray(sh) ? sh[1] : sh.y;
                    const xg = Array.isArray(sh) ? sh[2] : sh.xg;
                    const isGoal = Array.isArray(sh) ? sh[3] === 1 : sh.is_goal;

                    const px = mapX(sx);
                    const py = mapY(sy);
                    window.unifiedPlottedShots.push({ px, py, raw: sh, isDef: false });

                    if (isGoal) {
                        ctx.beginPath();
                        ctx.arc(px, py, 5.5, 0, 2 * Math.PI);
                        ctx.fillStyle = "#10b981";
                        ctx.fill();
                        ctx.lineWidth = 1.6;
                        ctx.strokeStyle = "#ffffff";
                        ctx.stroke();
                        ctx.beginPath(); ctx.arc(px, py, 2, 0, 2 * Math.PI); ctx.fillStyle = "#ffffff"; ctx.fill();
                    } else if (xg >= 0.30) {
                        ctx.fillStyle = "#38bdf8";
                        ctx.beginPath();
                        ctx.moveTo(px, py - 4.5); ctx.lineTo(px + 4.5, py); ctx.lineTo(px, py + 4.5); ctx.lineTo(px - 4.5, py);
                        ctx.closePath(); ctx.fill();
                        ctx.lineWidth = 1.2; ctx.strokeStyle = "#ffffff"; ctx.stroke();
                    } else {
                        const r = Math.min(4, Math.max(2.5, xg * 14));
                        ctx.beginPath(); ctx.arc(px, py, r, 0, 2 * Math.PI);
                        ctx.fillStyle = "#4ade80"; ctx.fill();
                        ctx.lineWidth = 0.8; ctx.strokeStyle = "rgba(255,255,255,0.7)"; ctx.stroke();
                    }
                });
            }

            // 4. Goal Orientation Text Labels
            ctx.font = "700 10px 'Space Grotesk', sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            if (mode === 'unified' || mode === 'defense') {
                ctx.fillStyle = "#ef4444";
                ctx.fillText("DEFENDING GOAL", mapX(6.0), mapY(34.0));
            }
            if (mode === 'unified' || mode === 'offense') {
                ctx.fillStyle = "var(--accent-lime)";
                ctx.fillText("TARGET GOAL", mapX(99.0), mapY(34.0));
            }

            setupPitchTooltipEvents();
        }

        function setupPitchTooltipEvents() {
            const canvas = document.getElementById("unified-pitch-canvas");
            const tooltip = document.getElementById("unified-pitch-tooltip");
            if (!canvas || !tooltip || canvas.dataset.tooltipBound) return;
            canvas.dataset.tooltipBound = "true";

            canvas.addEventListener("mousemove", (e) => {
                const rect = canvas.getBoundingClientRect();
                const mx = e.clientX - rect.left;
                const my = e.clientY - rect.top;

                let closest = null;
                let minDist = 14;

                (window.unifiedPlottedShots || []).forEach(pt => {
                    const dist = Math.hypot(pt.px - mx, pt.py - my);
                    if (dist < minDist) {
                        minDist = dist;
                        closest = pt;
                    }
                });

                if (closest) {
                    const sh = closest.raw;
                    const isGoal = Array.isArray(sh) ? sh[3] === 1 : (sh.is_goal || false);
                    const xg = Array.isArray(sh) ? sh[2] : (sh.xg || 0);
                    const min = Array.isArray(sh) ? sh[4] : (sh.minute || 0);
                    const player = Array.isArray(sh) ? sh[5] : (sh.player || 'Player');
                    const opp = Array.isArray(sh) ? sh[6] : (sh.opponent || 'Opponent');
                    const sit = Array.isArray(sh) ? sh[7] : (sh.situation || 'OpenPlay');
                    const act = Array.isArray(sh) ? sh[8] : (sh.last_action || 'Action');
                    const ch = Array.isArray(sh) ? sh[9] : (sh.channel || 'Channel');

                    const tag = isGoal ? '<span style="color:#ef4444; font-weight:800;">⚽ GOAL</span>' : (xg >= 0.3 ? '<span style="color:#fb923c; font-weight:700;">🔶 Big Chance</span>' : '<span style="color:#38bdf8;">Shot</span>');

                    tooltip.style.display = "block";
                    tooltip.style.left = closest.px + "px";
                    tooltip.style.top = closest.py + "px";
                    tooltip.innerHTML = `
                        <div style="font-weight:700; margin-bottom:0.25rem; display:flex; justify-content:space-between; gap:0.6rem;">
                            <span>${player} (${min}')</span>
                            <span>${tag}</span>
                        </div>
                        <div style="color:var(--text-secondary); font-size:0.73rem; line-height:1.35;">
                            <div><strong>xG:</strong> <span style="color:var(--accent-lime);">${xg}</span> &nbsp;|&nbsp; <strong>${sit}</strong> (${act})</div>
                            <div><strong>Channel:</strong> ${ch} &nbsp;|&nbsp; <strong>vs</strong> ${opp}</div>
                        </div>
                    `;
                } else {
                    tooltip.style.display = "none";
                }
            });

            canvas.addEventListener("mouseleave", () => {
                tooltip.style.display = "none";
            });
        }

        function populateAdaptabilityTable(seasonName) {
            const tbody = document.getElementById("adaptability-table-body");
            if (!tbody || !window.team_vulnerabilities_multiseason) return;
            seasonName = seasonName || (document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027');
            
            const root = window.team_vulnerabilities_multiseason;
            const teamsObj = root.teams || root;
            
            const list = [];
            Object.keys(teamsObj).forEach(t => {
                const sData = teamsObj[t][seasonName];
                if (sData && sData.tactical_profile) {
                    list.push({
                        team_name: t,
                        archetype: sData.tactical_profile.archetype || "Tactical Chameleon",
                        plan_adherence: sData.tactical_profile.plan_adherence_score || 80.0,
                        exploitation: sData.tactical_profile.opponent_exploitation_index || 80.0,
                        motto: sData.tactical_profile.motto || "Dynamic adaptability."
                    });
                }
            });

            list.sort((a, b) => b.exploitation - a.exploitation);
            
            let html = "";
            list.forEach((t, i) => {
                const badgeColor = t.archetype.includes("Dominator") ? "var(--accent-lime)" : (t.archetype.includes("Infiltrator") ? "#ef4444" : (t.archetype.includes("Specialist") ? "#c084fc" : "#38bdf8"));
                html += `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05); cursor: pointer;" onclick="renderTeamVulnerability('${t.team_name}', '${seasonName}'); document.getElementById('vuln-team-select').value='${t.team_name}'; window.scrollTo({top: document.getElementById('vulnerability-tab').offsetTop - 60, behavior: 'smooth'});">
                        <td style="padding: 0.7rem; font-weight: 700; color: var(--text-secondary);">#${i+1}</td>
                        <td style="padding: 0.7rem; font-weight: 600; color: #fff;">${t.team_name}</td>
                        <td style="padding: 0.7rem;"><span style="color: ${badgeColor}; font-weight: 700; font-size: 0.82rem;">${t.archetype}</span></td>
                        <td style="padding: 0.7rem; color: #9ca3af;">${t.plan_adherence}%</td>
                        <td style="padding: 0.7rem; color: var(--accent-lime); font-weight: 800;">${t.exploitation}%</td>
                        <td style="padding: 0.7rem; color: var(--text-secondary); font-size: 0.78rem;">${t.motto}</td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }

        window.addEventListener('resize', function() {
            const vulnTab = document.getElementById('vulnerability-tab');
            if (vulnTab && vulnTab.classList.contains('active')) {
                drawUnifiedPitch();
            }
        });
    """

    pattern_render_vuln = r"function resolveTeamData\(.*?\n        \}\n    "
    if re.search(pattern_render_vuln, html, flags=re.DOTALL):
        html = re.sub(pattern_render_vuln, lambda m: js_tactical_master.strip() + "\n    ", html, flags=re.DOTALL)
    else:
        # Fallback to replacing renderTeamVulnerability
        pattern_func = r"function renderTeamVulnerability\(\s*teamName,\s*seasonName\s*\)\s*\{.*?\n        \}"
        if re.search(pattern_func, html, flags=re.DOTALL):
            html = re.sub(pattern_func, lambda m: js_tactical_master.strip(), html, flags=re.DOTALL)
        else:
            html = html.replace("function drawUnifiedPitch", js_tactical_master.strip() + "\n        function drawUnifiedPitch")

    # 6. Ensure switchTab triggers tactical pitch update
    switch_trigger = "if (tabId === 'vulnerability') { updateTeamDropdown(document.getElementById('vuln-season-select').value); renderTeamVulnerability(); populateAdaptabilityTable(); }"
    if "if (tabId === 'vulnerability')" in html:
        pattern_switch = r"if \(tabId === 'vulnerability'\) \{.*?\}"
        html = re.sub(pattern_switch, lambda m: switch_trigger, html, flags=re.DOTALL)

    # 7. Ensure DOMContentLoaded initializes tactical engine
    if "updateTeamDropdown('2026-2027')" not in html:
        dom_pattern = r'window\.addEventListener\("DOMContentLoaded",\s*\(\)\s*=>\s*\{'
        dom_replacement = """window.addEventListener("DOMContentLoaded", () => {
            updateTeamDropdown('2026-2027');
            populateAdaptabilityTable('2026-2027');"""
        html = re.sub(dom_pattern, dom_replacement, html)

    # 8. Write to index.html and web_dashboard/index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Senior Engineer Master Bundle V6 compiled into index.html & web_dashboard/index.html!")

if __name__ == "__main__":
    compile_complete_bundle()
