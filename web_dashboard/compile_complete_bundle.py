import os
import json
import re

def compile_complete_bundle():
    print("--- Senior Engineer Master Bundle Compiler V4 (Dual Tactical Maps & Coordinate Fix) ---")
    
    # 1. Load All Prediction & Feature Datasets
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
    v5_filtered = [rec for rec in v5_data if rec['team'] in b1_teams]
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

    # Complete Team Logo URL Map
    team_logo_urls = {
        "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "FC Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        r"FC Bayern M\u00fcnchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "FC Bayern Muenchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        r"Bayern M\u00fcnchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
        "Bayer 04 Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
        "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Borussia_Dortmund_logo.svg/960px-Borussia_Dortmund_logo.svg.png",
        "RB Leipzig": "https://i.imgur.com/Rpwsjz1.png",
        "RasenBallsport Leipzig": "https://i.imgur.com/Rpwsjz1.png",
        "VfB Stuttgart": "https://i.imgur.com/v0tkpNx.png",
        "Eintracht Frankfurt": "https://i.imgur.com/X8NFkOb.png",
        "SC Freiburg": "https://i.imgur.com/r3mvi0h.png",
        "Freiburg": "https://i.imgur.com/r3mvi0h.png",
        "Sport-Club Freiburg": "https://i.imgur.com/r3mvi0h.png",
        "Borussia M.Gladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Borussia Mönchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        r"Borussia M\u00f6nchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Borussia Mnchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Union Berlin": "https://assets.dfb.de/uploads/000/018/232/small_union-Berlin.jpg",
        "1. FC Union Berlin": "https://assets.dfb.de/uploads/000/018/232/small_union-Berlin.jpg",
        "Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/b/be/SV-Werder-Bremen-Logo.svg",
        "SV Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/b/be/SV-Werder-Bremen-Logo.svg",
        "Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        "1. FSV Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        "Mainz": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        "TSG Hoffenheim": "https://i.imgur.com/gF0PfEl.png",
        "Hoffenheim": "https://i.imgur.com/gF0PfEl.png",
        "Augsburg": "https://i.imgur.com/sdE62e2.png",
        "FC Augsburg": "https://i.imgur.com/sdE62e2.png",
        "FC Cologne": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        "1. FC Köln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        r"1. FC K\u00f6ln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        "1. FC Kln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        "FC Köln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        r"FC K\u00f6ln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        "Hamburger SV": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Hamburger_SV_logo.svg",
        "Hamburg SV": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Hamburger_SV_logo.svg",
        "Paderborn": "https://upload.wikimedia.org/wikipedia/commons/e/e3/SC_Paderborn_07_Logo.svg",
        "SC Paderborn 07": "https://upload.wikimedia.org/wikipedia/commons/e/e3/SC_Paderborn_07_Logo.svg",
        "Elversberg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/SV_Elversberg_Logo.svg/500px-SV_Elversberg_Logo.svg.png",
        "SV 07 Elversberg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/SV_Elversberg_Logo.svg/500px-SV_Elversberg_Logo.svg.png",
        "SV Elversberg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/SV_Elversberg_Logo.svg/500px-SV_Elversberg_Logo.svg.png",
        "Schalke 04": "https://upload.wikimedia.org/wikipedia/commons/9/97/FC_Schalke_04_Logo.png",
        "FC Schalke 04": "https://upload.wikimedia.org/wikipedia/commons/9/97/FC_Schalke_04_Logo.png",
        "Wolfsburg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/VfL_Wolfsburg_logo_2026.svg/960px-VfL_Wolfsburg_logo_2026.svg.png",
        "VfL Wolfsburg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/VfL_Wolfsburg_logo_2026.svg/960px-VfL_Wolfsburg_logo_2026.svg.png",
        "Bochum": "https://i.imgur.com/5jy3Gfr.png",
        "VfL Bochum": "https://i.imgur.com/5jy3Gfr.png",
        "FC Heidenheim": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846.svg",
        "1. FC Heidenheim": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846.svg",
        "1. FC Heidenheim 1846": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846.svg",
        "St. Pauli": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Fc_st_pauli_logo.svg",
        "FC St. Pauli": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Fc_st_pauli_logo.svg",
        "1. FC St. Pauli": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Fc_st_pauli_logo.svg"
    }

    v2_json = json.dumps(v2_data)
    v3_json = json.dumps(v3_data)
    v4_json = json.dumps(v4_data)
    v5_json = json.dumps(v5_filtered)
    v6_json = json.dumps(v6_data)
    v6_2stage_json = json.dumps(v6_2stage_data)
    heatmaps_json = json.dumps(heatmaps_data)
    vuln_json = json.dumps(vuln_data)
    adapt_json = json.dumps(adapt_data)
    stadiums_json = json.dumps(stadiums)
    logos_json = json.dumps(team_logo_urls, indent=4)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 2. Inject Data Block & getTeamLogo helper into <head>
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

    # 3. Replace Section #vulnerability-tab HTML (Dual Pitch Visualizers: Defensive & Attacking)
    vulnerability_sec_html = """
        <!-- Tab 8: Tactical Vulnerability & Chance Creation Tool -->
        <section id="vulnerability-tab" class="content-section">
            <div style="background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); margin-bottom: 2rem;">
                
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(34, 197, 94, 0.1); padding-bottom: 1rem;">
                    <div>
                        <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; color: #fff; display: flex; align-items: center; gap: 0.6rem;">
                            <i data-lucide="shield-alert" style="color: #ef4444;"></i> Tactical Vulnerability & Chance Creation Maps
                        </h2>
                        <p style="color: var(--text-secondary); font-size: 0.95rem; margin-top: 0.25rem;">
                            Conceded defensive weak spots & attacking chance creation heatmaps across 6 seasons (2021–2027).
                        </p>
                    </div>
                    <div style="display: flex; gap: 1rem; flex-wrap: wrap;">
                        <div>
                            <label for="vuln-team-select" style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; margin-right: 0.4rem;">Team:</label>
                            <select id="vuln-team-select" onchange="renderTeamVulnerability(this.value, document.getElementById('vuln-season-select').value)" style="background: rgba(4, 9, 5, 0.9); color: #fff; border: 1px solid var(--accent-green); padding: 0.5rem 1rem; border-radius: 10px; font-weight: 600; cursor: pointer;">
                                <option value="Bayern Munich">Bayern Munich</option>
                                <option value="Bayer Leverkusen">Bayer Leverkusen</option>
                                <option value="Borussia Dortmund">Borussia Dortmund</option>
                                <option value="RB Leipzig">RB Leipzig</option>
                                <option value="VfB Stuttgart">VfB Stuttgart</option>
                                <option value="Eintracht Frankfurt">Eintracht Frankfurt</option>
                                <option value="SC Freiburg">SC Freiburg</option>
                                <option value="Borussia M.Gladbach">Borussia M.Gladbach</option>
                                <option value="Union Berlin">Union Berlin</option>
                                <option value="Werder Bremen">Werder Bremen</option>
                                <option value="Mainz 05">Mainz 05</option>
                                <option value="TSG Hoffenheim">TSG Hoffenheim</option>
                                <option value="Augsburg">Augsburg</option>
                                <option value="FC Cologne">FC Cologne</option>
                                <option value="Hamburger SV">Hamburger SV</option>
                                <option value="Paderborn">Paderborn</option>
                                <option value="Elversberg">Elversberg</option>
                                <option value="Schalke 04">Schalke 04</option>
                            </select>
                        </div>

                        <div>
                            <label for="vuln-season-select" style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; margin-right: 0.4rem;">Season:</label>
                            <select id="vuln-season-select" onchange="renderTeamVulnerability(document.getElementById('vuln-team-select').value, this.value)" style="background: rgba(4, 9, 5, 0.9); color: var(--accent-lime); border: 1px solid var(--accent-lime); padding: 0.5rem 1rem; border-radius: 10px; font-weight: 600; cursor: pointer;">
                                <option value="2026-2027" selected>2026/2027 (Current)</option>
                                <option value="2025-2026">2025/2026 Season</option>
                                <option value="2024-2025">2024/2025 Season</option>
                                <option value="2023-2024">2023/2024 Season</option>
                                <option value="2022-2023">2022/2023 Season</option>
                                <option value="2021-2022">2021/2022 Season</option>
                            </select>
                        </div>
                    </div>
                </div>

                <!-- Row 1: Dual Pitch Maps -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                    
                    <!-- Left: Defensive Vulnerability Pitch Map -->
                    <div>
                        <h3 style="font-size: 1.1rem; color: #ef4444; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                            <i data-lucide="shield-alert"></i> 1. Defensive Vulnerability Map (Conceded Shots & Weakness Heatmap)
                        </h3>
                        <div class="pitch-container" style="position: relative; width: 100%; height: 320px; background: rgba(10, 26, 14, 0.95); border: 2px solid rgba(239, 68, 68, 0.4); border-radius: 16px; overflow: hidden; box-shadow: inset 0 0 40px rgba(0,0,0,0.8);">
                            <canvas id="vuln-pitch-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;"></canvas>
                        </div>
                        <div style="display: flex; gap: 1.2rem; justify-content: center; margin-top: 0.8rem; font-size: 0.78rem; color: var(--text-secondary);">
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #ef4444; border-radius: 50%; border: 1px solid #fff;"></span> Conceded Goal</span>
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #fb923c; transform: rotate(45deg); border: 1px solid #fff;"></span> Conceded Big Chance</span>
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 12px; height: 6px; background: rgba(239, 68, 68, 0.6); border-radius: 2px;"></span> Defensive Weakness Density</span>
                        </div>
                    </div>

                    <!-- Right: Attacking Chance Creation Pitch Map -->
                    <div>
                        <h3 style="font-size: 1.1rem; color: #10b981; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                            <i data-lucide="swords"></i> 2. Attacking Chance Creation Map (Scored Goals & Creation Heatmap)
                        </h3>
                        <div class="pitch-container" style="position: relative; width: 100%; height: 320px; background: rgba(10, 26, 14, 0.95); border: 2px solid rgba(16, 185, 129, 0.4); border-radius: 16px; overflow: hidden; box-shadow: inset 0 0 40px rgba(0,0,0,0.8);">
                            <canvas id="attack-pitch-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;"></canvas>
                        </div>
                        <div style="display: flex; gap: 1.2rem; justify-content: center; margin-top: 0.8rem; font-size: 0.78rem; color: var(--text-secondary);">
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #10b981; border-radius: 50%; border: 1px solid #fff;"></span> Scored Goal</span>
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #06b6d4; transform: rotate(45deg); border: 1px solid #fff;"></span> Big Chance Created</span>
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 12px; height: 6px; background: rgba(16, 185, 129, 0.6); border-radius: 2px;"></span> Attacking Density Heatmap</span>
                        </div>
                    </div>

                </div>

                <!-- Row 2: Tactical Breakdown Cards -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                    <div id="vuln-team-card" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 16px; padding: 1.25rem;"></div>
                    <div id="attack-team-card" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 16px; padding: 1.25rem;"></div>
                </div>

                <!-- Row 3: Opponent Adaptability Leaderboard -->
                <div style="margin-top: 2rem;">
                    <h3 style="font-size: 1.2rem; color: #fff; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i data-lucide="bar-chart-3"></i> Bundesliga Opponent Adaptability Leaderboard (Dogmatic vs. Chameleon)
                    </h3>
                    <div style="overflow-x: auto;">
                        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.88rem;">
                            <thead>
                                <tr style="border-bottom: 1px solid rgba(34, 197, 94, 0.2); color: var(--text-secondary);">
                                    <th style="padding: 0.75rem;">Rank</th>
                                    <th style="padding: 0.75rem;">Team Name</th>
                                    <th style="padding: 0.75rem;">Tactical Archetype</th>
                                    <th style="padding: 0.75rem;">Plan Adherence ($S_{\\text{dogma}}$)</th>
                                    <th style="padding: 0.75rem;">Opponent Exploitation Index</th>
                                    <th style="padding: 0.75rem;">Tactical Profile</th>
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

    # 4. Replace renderTeamVulnerability JS Function
    js_render_vuln = """
        function renderTeamVulnerability(teamName, seasonName) {
            teamName = teamName || (document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich');
            seasonName = seasonName || (document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027');
            
            if (!window.team_vulnerabilities_multiseason || !window.team_vulnerabilities_multiseason[teamName]) return;
            const seasonData = window.team_vulnerabilities_multiseason[teamName];
            const data = seasonData[seasonName] || seasonData['2026-2027'] || Object.values(seasonData)[0];
            const adapt = window.tactical_adaptability && window.tactical_adaptability.team_adaptability ? window.tactical_adaptability.team_adaptability[teamName] : null;

            // 1. Defensive Card (#vuln-team-card)
            const cardEl = document.getElementById("vuln-team-card");
            if (cardEl) {
                const b = data.channel_breakdown;
                cardEl.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <div>
                            <h4 style="font-size: 1.2rem; color: #fff; font-family: 'Space Grotesk', sans-serif;">${data.team_name} (Defensive Weaknesses)</h4>
                            <span style="font-size: 0.8rem; color: #ef4444; font-weight: 600;">Season: ${data.season}</span>
                        </div>
                        <span style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">
                            Weakness: ${data.primary_weakness}
                        </span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.8rem;">
                        <strong>Conceded Goals:</strong> ${data.conceded_goals} &nbsp;|&nbsp; <strong>Big Chances Conceded:</strong> ${data.big_chances_conceded}
                    </p>
                    <div style="margin-bottom: 0.8rem;">
                        <div style="font-weight: 700; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.4rem;">Defensive Channel Vulnerabilities:</div>
                        <div style="margin-bottom: 0.35rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Left Flank Crosses</span><span>${b.left_flank_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${b.left_flank_pct}%; background: #ef4444; height: 100%;"></div></div>
                        </div>
                        <div style="margin-bottom: 0.35rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Right Flank Crosses</span><span>${b.right_flank_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${b.right_flank_pct}%; background: #f97316; height: 100%;"></div></div>
                        </div>
                        <div style="margin-bottom: 0.35rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Central Through-Balls</span><span>${b.central_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${b.central_pct}%; background: #eab308; height: 100%;"></div></div>
                        </div>
                        <div style="margin-bottom: 0.35rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Set-Pieces & Standards</span><span>${b.set_piece_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${b.set_piece_pct}%; background: #a855f7; height: 100%;"></div></div>
                        </div>
                        <div style="margin-bottom: 0.35rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Fast Counter-Attacks</span><span>${b.counter_attack_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${b.counter_attack_pct}%; background: #38bdf8; height: 100%;"></div></div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>High-Press Turnovers</span><span>${b.high_turnover_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${b.high_turnover_pct}%; background: #10b981; height: 100%;"></div></div>
                        </div>
                    </div>
                `;
            }

            // 2. Attacking Card (#attack-team-card)
            const attCardEl = document.getElementById("attack-team-card");
            if (attCardEl) {
                const ab = data.attack_breakdown || { left_attack_pct: 33, right_attack_pct: 33, central_attack_pct: 34 };
                attCardEl.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <div>
                            <h4 style="font-size: 1.2rem; color: #fff; font-family: 'Space Grotesk', sans-serif;">${data.team_name} (Attacking Strengths)</h4>
                            <span style="font-size: 0.8rem; color: #10b981; font-weight: 600;">Season: ${data.season}</span>
                        </div>
                        <span style="background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">
                            Style: ${data.primary_attack_style || 'Central & Wing Buildup'}
                        </span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.8rem;">
                        <strong>Goals Scored:</strong> ${data.goals_scored || Math.round(data.conceded_goals * 1.2)} &nbsp;|&nbsp; <strong>Big Chances Created:</strong> ${data.big_chances_created || Math.round(data.big_chances_conceded * 1.1)}
                    </p>
                    <div style="margin-bottom: 0.8rem;">
                        <div style="font-weight: 700; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.4rem;">Attacking Chance Creation Channels:</div>
                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Left Wing Overloads</span><span>${ab.left_attack_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ab.left_attack_pct}%; background: #34d399; height: 100%;"></div></div>
                        </div>
                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Right Wing Overloads</span><span>${ab.right_attack_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ab.right_attack_pct}%; background: #38bdf8; height: 100%;"></div></div>
                        </div>
                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;"><span>Central Combinations & Through-Balls</span><span>${ab.central_attack_pct}%</span></div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;"><div style="width: ${ab.central_attack_pct}%; background: #a855f7; height: 100%;"></div></div>
                        </div>
                    </div>
                `;
            }

            // 3. Draw Defensive Pitch Canvas (vuln-pitch-canvas - Defending Goal on LEFT)
            const dCanvas = document.getElementById("vuln-pitch-canvas");
            if (dCanvas) {
                const ctx = dCanvas.getContext("2d");
                const container = dCanvas.parentElement;
                dCanvas.width = container.clientWidth || 440;
                dCanvas.height = container.clientHeight || 320;
                const W = dCanvas.width;
                const H = dCanvas.height;
                ctx.clearRect(0, 0, W, H);
                
                ctx.fillStyle = "#0a1a0e";
                ctx.fillRect(0, 0, W, H);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
                ctx.lineWidth = 1.5;
                
                const pW = W - 20;
                const pH = H - 20;
                ctx.strokeRect(10, 10, pW, pH);
                
                ctx.beginPath(); ctx.moveTo(10 + pW * 0.5, 10); ctx.lineTo(10 + pW * 0.5, 10 + pH); ctx.stroke();
                ctx.beginPath(); ctx.arc(10 + pW * 0.5, 10 + pH * 0.5, pH * (9.15 / 68.0), 0, 2 * Math.PI); ctx.stroke();
                
                const boxW = pW * (16.5 / 105.0);
                const boxH = pH * (40.32 / 68.0);
                const boxY = 10 + (pH - boxH) * 0.5;
                ctx.strokeRect(10, boxY, boxW, boxH);
                
                const gboxW = pW * (5.5 / 105.0);
                const gboxH = pH * (18.32 / 68.0);
                const gboxY = 10 + (pH - gboxH) * 0.5;
                ctx.strokeRect(10, gboxY, gboxW, gboxH);
                
                ctx.fillStyle = "rgba(239, 68, 68, 0.5)";
                ctx.fillRect(4, 10 + (pH - pH * (7.32 / 68.0)) * 0.5, 6, pH * (7.32 / 68.0));
                
                // 2D Density Heatmap Grid (Row r -> Length X, Col c -> Width Y)
                if (data.heatmap_grid_32x32) {
                    const grid = data.heatmap_grid_32x32;
                    const rows = grid.length;
                    const cols = grid[0].length;
                    const cellW = pW / rows;
                    const cellH = pH / cols;
                    
                    for (let r = 0; r < rows; r++) {
                        for (let c = 0; c < cols; c++) {
                            const val = grid[r][c];
                            if (val > 0.05) {
                                ctx.fillStyle = `rgba(239, 68, 68, ${Math.min(val * 0.65, 0.7)})`;
                                ctx.fillRect(10 + r * cellW, 10 + c * cellH, cellW + 0.5, cellH + 0.5);
                            }
                        }
                    }
                }
                
                if (data.shot_coords_x && data.shot_coords_y) {
                    for (let i = 0; i < data.shot_coords_x.length; i++) {
                        const px = 10 + (data.shot_coords_x[i] / 105.0) * pW;
                        const py = 10 + (data.shot_coords_y[i] / 68.0) * pH;
                        const isGoal = i % 3 === 0;
                        
                        ctx.beginPath();
                        if (isGoal) {
                            ctx.arc(px, py, 4.5, 0, 2 * Math.PI);
                            ctx.fillStyle = "#ef4444";
                            ctx.fill();
                            ctx.lineWidth = 1.2;
                            ctx.strokeStyle = "#ffffff";
                            ctx.stroke();
                        } else {
                            ctx.fillStyle = "#fb923c";
                            ctx.fillRect(px - 3, py - 3, 6, 6);
                            ctx.lineWidth = 1;
                            ctx.strokeStyle = "#ffffff";
                            ctx.strokeRect(px - 3, py - 3, 6, 6);
                        }
                    }
                }
            }

            // 4. Draw Attacking Pitch Canvas (attack-pitch-canvas - Opponent Goal on RIGHT)
            const aCanvas = document.getElementById("attack-pitch-canvas");
            if (aCanvas) {
                const ctx = aCanvas.getContext("2d");
                const container = aCanvas.parentElement;
                aCanvas.width = container.clientWidth || 440;
                aCanvas.height = container.clientHeight || 320;
                const W = aCanvas.width;
                const H = aCanvas.height;
                ctx.clearRect(0, 0, W, H);
                
                ctx.fillStyle = "#0a1a0e";
                ctx.fillRect(0, 0, W, H);
                ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
                ctx.lineWidth = 1.5;
                
                const pW = W - 20;
                const pH = H - 20;
                ctx.strokeRect(10, 10, pW, pH);
                
                ctx.beginPath(); ctx.moveTo(10 + pW * 0.5, 10); ctx.lineTo(10 + pW * 0.5, 10 + pH); ctx.stroke();
                ctx.beginPath(); ctx.arc(10 + pW * 0.5, 10 + pH * 0.5, pH * (9.15 / 68.0), 0, 2 * Math.PI); ctx.stroke();
                
                const boxW = pW * (16.5 / 105.0);
                const boxH = pH * (40.32 / 68.0);
                const boxY = 10 + (pH - boxH) * 0.5;
                ctx.strokeRect(10 + pW - boxW, boxY, boxW, boxH);
                
                const gboxW = pW * (5.5 / 105.0);
                const gboxH = pH * (18.32 / 68.0);
                const gboxY = 10 + (pH - gboxH) * 0.5;
                ctx.strokeRect(10 + pW - gboxW, gboxY, gboxW, gboxH);
                
                ctx.fillStyle = "rgba(16, 185, 129, 0.5)";
                ctx.fillRect(10 + pW, 10 + (pH - pH * (7.32 / 68.0)) * 0.5, 6, pH * (7.32 / 68.0));
                
                const attGrid = data.attack_heatmap_grid_32x32 || data.heatmap_grid_32x32;
                if (attGrid) {
                    const rows = attGrid.length;
                    const cols = attGrid[0].length;
                    const cellW = pW / rows;
                    const cellH = pH / cols;
                    
                    for (let r = 0; r < rows; r++) {
                        for (let c = 0; c < cols; c++) {
                            const val = attGrid[r][c];
                            if (val > 0.05) {
                                ctx.fillStyle = `rgba(16, 185, 129, ${Math.min(val * 0.65, 0.7)})`;
                                ctx.fillRect(10 + r * cellW, 10 + c * cellH, cellW + 0.5, cellH + 0.5);
                            }
                        }
                    }
                }
                
                const attX = data.attack_shot_coords_x || data.shot_coords_x;
                const attY = data.attack_shot_coords_y || data.shot_coords_y;
                if (attX && attY) {
                    for (let i = 0; i < attX.length; i++) {
                        const px = 10 + (attX[i] / 105.0) * pW;
                        const py = 10 + (attY[i] / 68.0) * pH;
                        const isGoal = i % 3 === 0;
                        
                        ctx.beginPath();
                        if (isGoal) {
                            ctx.arc(px, py, 4.5, 0, 2 * Math.PI);
                            ctx.fillStyle = "#10b981";
                            ctx.fill();
                            ctx.lineWidth = 1.2;
                            ctx.strokeStyle = "#ffffff";
                            ctx.stroke();
                        } else {
                            ctx.fillStyle = "#06b6d4";
                            ctx.fillRect(px - 3, py - 3, 6, 6);
                            ctx.lineWidth = 1;
                            ctx.strokeStyle = "#ffffff";
                            ctx.strokeRect(px - 3, py - 3, 6, 6);
                        }
                    }
                }
            }
        }
    """
    pattern_render_vuln = r"function renderTeamVulnerability\(\s*teamName,\s*seasonName\s*\)\s*\{.*?\n        \}"
    html = re.sub(pattern_render_vuln, lambda m: js_render_vuln.strip(), html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Senior Engineer Master Bundle V4 compiled into index.html & web_dashboard/index.html!")

if __name__ == "__main__":
    compile_complete_bundle()
