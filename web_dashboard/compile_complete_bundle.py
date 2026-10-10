import os
import json
import re

def compile_complete_bundle():
    print("--- Senior Engineer Master Bundle Compiler V5 (Unified Tactical Pitch & Exact Shot Counts) ---")
    
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

    # 3. Replace Section #vulnerability-tab HTML (Unified Full Pitch Visualizer)
    vulnerability_sec_html = """
        <!-- Tab 8: Tactical Vulnerability & Chance Creation Tool -->
        <section id="vulnerability-tab" class="content-section">
            <div style="background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); margin-bottom: 2rem;">
                
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(34, 197, 94, 0.1); padding-bottom: 1rem;">
                    <div>
                        <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; color: #fff; display: flex; align-items: center; gap: 0.6rem;">
                            <i data-lucide="shield-alert" style="color: #ef4444;"></i> Tactical Pitch Map: Defense vs. Attack
                        </h2>
                        <p style="color: var(--text-secondary); font-size: 0.95rem; margin-top: 0.25rem;">
                            100% Authentic shot maps & heatmaps (2021–2027). Left Half = Defensive Conceded Shots | Right Half = Attacking Scored Shots.
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

                <!-- Unified Pitch Map Card -->
                <div style="background: rgba(10, 26, 14, 0.95); border: 2px solid rgba(34, 197, 94, 0.4); border-radius: 20px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: inset 0 0 50px rgba(0,0,0,0.8);">
                    
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem;">
                        <h3 style="font-size: 1.15rem; color: #fff; display: flex; align-items: center; gap: 0.5rem; font-family: 'Space Grotesk', sans-serif;">
                            <i data-lucide="map-pin" style="color: var(--accent-lime);"></i> Unified Full-Pitch Tactical Map (105m x 68m)
                        </h3>
                        
                        <!-- Interactive Filter Controls -->
                        <div style="display: flex; gap: 1rem; align-items: center; flex-wrap: wrap; background: rgba(0,0,0,0.4); padding: 0.4rem 0.8rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); font-size: 0.78rem; color: #fff;">
                            <label style="cursor: pointer; display: flex; align-items: center; gap: 0.35rem;">
                                <input type="checkbox" id="chk-def-goals" checked onchange="drawUnifiedPitch()" style="accent-color: #ef4444;">
                                <span style="width: 9px; height: 9px; background: #ef4444; border-radius: 50%; border: 1px solid #fff;"></span> Conceded Goals (Red)
                            </label>
                            <label style="cursor: pointer; display: flex; align-items: center; gap: 0.35rem;">
                                <input type="checkbox" id="chk-def-chances" checked onchange="drawUnifiedPitch()" style="accent-color: #fb923c;">
                                <span style="width: 9px; height: 9px; background: #fb923c; transform: rotate(45deg); border: 1px solid #fff;"></span> Conceded Chances (Orange)
                            </label>
                            <label style="cursor: pointer; display: flex; align-items: center; gap: 0.35rem; margin-left: 0.4rem;">
                                <input type="checkbox" id="chk-att-goals" checked onchange="drawUnifiedPitch()" style="accent-color: #10b981;">
                                <span style="width: 9px; height: 9px; background: #10b981; border-radius: 50%; border: 1px solid #fff;"></span> Scored Goals (Green)
                            </label>
                            <label style="cursor: pointer; display: flex; align-items: center; gap: 0.35rem;">
                                <input type="checkbox" id="chk-att-chances" checked onchange="drawUnifiedPitch()" style="accent-color: #06b6d4;">
                                <span style="width: 9px; height: 9px; background: #06b6d4; transform: rotate(45deg); border: 1px solid #fff;"></span> Created Chances (Cyan)
                            </label>
                            <label style="cursor: pointer; display: flex; align-items: center; gap: 0.35rem; margin-left: 0.4rem;">
                                <input type="checkbox" id="chk-heatmap" checked onchange="drawUnifiedPitch()" style="accent-color: var(--accent-lime);">
                                <span>Density Heatmap</span>
                            </label>
                        </div>
                    </div>

                    <!-- Canvas -->
                    <div class="pitch-container" style="position: relative; width: 100%; height: 380px; background: rgba(10, 26, 14, 0.98); border: 2px solid rgba(255, 255, 255, 0.2); border-radius: 16px; overflow: hidden;">
                        <canvas id="unified-pitch-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;"></canvas>
                    </div>
                </div>

                <!-- Breakdown Cards (Defensive vs. Attacking) -->
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                    <div id="vuln-team-card" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 16px; padding: 1.25rem;"></div>
                    <div id="attack-team-card" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 16px; padding: 1.25rem;"></div>
                </div>

                <!-- Opponent Adaptability Leaderboard -->
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

    # 4. Replace renderTeamVulnerability & drawUnifiedPitch JS Functions
    js_render_vuln = """
        function resolveTeamData(teamName) {
            if (!window.team_vulnerabilities_multiseason) return null;
            if (window.team_vulnerabilities_multiseason[teamName]) {
                return window.team_vulnerabilities_multiseason[teamName];
            }
            const norm = (teamName || '').replace('FC ', '').replace('1. ', '').replace('SV ', '').replace('VfB ', '').replace('VfL ', '').replace('TSG ', '').trim().toLowerCase();
            for (let k in window.team_vulnerabilities_multiseason) {
                const kNorm = k.replace('FC ', '').replace('1. ', '').replace('SV ', '').replace('VfB ', '').replace('VfL ', '').replace('TSG ', '').trim().toLowerCase();
                if (kNorm.length > 2 && (kNorm.includes(norm) || norm.includes(kNorm))) {
                    return window.team_vulnerabilities_multiseason[k];
                }
            }
            return window.team_vulnerabilities_multiseason['Bayern Munich'];
        }

        function renderTeamVulnerability(teamName, seasonName) {
            teamName = teamName || (document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich');
            seasonName = seasonName || (document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027');
            
            const seasonData = resolveTeamData(teamName);
            if (!seasonData) return;
            const data = seasonData[seasonName] || seasonData['2026-2027'] || Object.values(seasonData)[0];
            const adapt = window.tactical_adaptability && window.tactical_adaptability.team_adaptability ? (window.tactical_adaptability.team_adaptability[teamName] || window.tactical_adaptability.team_adaptability['Bayern Munich']) : null;


            // 1. Defensive Profile Card (#vuln-team-card)
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
                        <strong>Conceded Goals:</strong> <span style="color: #ef4444; font-weight: 700;">${data.conceded_goals}</span> &nbsp;|&nbsp; <strong>Big Chances Conceded:</strong> <span style="color: #fb923c; font-weight: 700;">${data.big_chances_conceded}</span>
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
                    ${adapt ? `
                    <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.6rem; font-size: 0.78rem;">
                        <div style="color: var(--accent-lime); font-weight: 700;">Tactical Archetype: ${adapt.tactical_archetype}</div>
                        <div style="color: var(--text-secondary); font-style: italic;">"${adapt.tactical_motto}"</div>
                    </div>` : ''}
                `;
            }

            // 2. Attacking Profile Card (#attack-team-card)
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
                        <strong>Goals Scored:</strong> <span style="color: #10b981; font-weight: 700;">${data.goals_scored}</span> &nbsp;|&nbsp; <strong>Big Chances Created:</strong> <span style="color: #06b6d4; font-weight: 700;">${data.big_chances_created}</span>
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
                    <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.6rem; font-size: 0.78rem; color: var(--text-secondary);">
                        <span>Primary Chance Zone: <strong>Opponent Penalty Box & Half-Spaces</strong></span>
                    </div>
                `;
            }

            // 3. Draw Unified Pitch Map (Single Full Pitch 105m x 68m)
            drawUnifiedPitch();
        }

        function drawUnifiedPitch() {
            const teamName = document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich';
            const seasonName = document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027';
            
            const seasonData = resolveTeamData(teamName);
            if (!seasonData) return;
            const data = seasonData[seasonName] || seasonData['2026-2027'] || Object.values(seasonData)[0];


            const canvas = document.getElementById("unified-pitch-canvas");
            if (!canvas) return;
            const ctx = canvas.getContext("2d");
            const container = canvas.parentElement;
            canvas.width = container.clientWidth || 900;
            canvas.height = container.clientHeight || 380;
            
            const W = canvas.width;
            const H = canvas.height;
            ctx.clearRect(0, 0, W, H);

            // Outer dark container background
            ctx.fillStyle = "#061208";
            ctx.fillRect(0, 0, W, H);
            
            // Calculate strict 105:68 aspect ratio pitch inside canvas with 16px margins
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

            // Pitch Grass Background
            ctx.fillStyle = "#0a1a0e";
            ctx.fillRect(pitchX, pitchY, pW, pH);

            // Pitch Grass Vertical Stripes
            const numStripes = 10;
            const stripeW = pW / numStripes;
            for (let i = 0; i < numStripes; i++) {
                if (i % 2 === 0) {
                    ctx.fillStyle = "rgba(255, 255, 255, 0.035)";
                    ctx.fillRect(pitchX + i * stripeW, pitchY, stripeW, pH);
                }
            }

            // Coordinate Mappers (Pitch m -> Canvas px)
            const mapX = (x) => pitchX + (x / 105.0) * pW;
            const mapY = (y) => pitchY + (y / 68.0) * pH;

            // Layer Checkboxes
            const showHeatmap = document.getElementById("chk-heatmap") ? document.getElementById("chk-heatmap").checked : true;
            const showDefGoals = document.getElementById("chk-def-goals") ? document.getElementById("chk-def-goals").checked : true;
            const showDefChances = document.getElementById("chk-def-chances") ? document.getElementById("chk-def-chances").checked : true;
            const showAttGoals = document.getElementById("chk-att-goals") ? document.getElementById("chk-att-goals").checked : true;
            const showAttChances = document.getElementById("chk-att-chances") ? document.getElementById("chk-att-chances").checked : true;

            // 1. DENSITY HEATMAPS (DRAWN FIRST, UNDER PITCH LINES)
            if (showHeatmap) {
                // Defending Heatmap (Left Half: X in [0, 52.5]m)
                const defGrid = data.def_heatmap_grid_32x32 || data.heatmap_grid_32x32;
                if (defGrid) {
                    const rows = defGrid.length;
                    const cols = defGrid[0].length;
                    const cellW = pW / rows;
                    const cellH = pH / cols;
                    for (let r = 0; r < rows; r++) {
                        if (r * cellW > pW * 0.49) continue;
                        for (let c = 0; c < cols; c++) {
                            const val = defGrid[r][c];
                            if (val > 0.04) {
                                ctx.fillStyle = `rgba(239, 68, 68, ${Math.min(val * 0.65, 0.7)})`;
                                ctx.fillRect(pitchX + r * cellW, pitchY + c * cellH, cellW + 0.5, cellH + 0.5);
                            }
                        }
                    }
                }

                // Attacking Heatmap (Right Half: X in [52.5, 105]m)
                const attGrid = data.att_heatmap_grid_32x32;
                if (attGrid) {
                    const rows = attGrid.length;
                    const cols = attGrid[0].length;
                    const cellW = pW / rows;
                    const cellH = pH / cols;
                    for (let r = 0; r < rows; r++) {
                        if (r * cellW < pW * 0.51) continue;
                        for (let c = 0; c < cols; c++) {
                            const val = attGrid[r][c];
                            if (val > 0.04) {
                                ctx.fillStyle = `rgba(16, 185, 129, ${Math.min(val * 0.65, 0.7)})`;
                                ctx.fillRect(pitchX + r * cellW, pitchY + c * cellH, cellW + 0.5, cellH + 0.5);
                            }
                        }
                    }
                }
            }

            // 2. PITCH LINES & MARKINGS (DRAWN SECOND, ON TOP OF HEATMAPS)
            ctx.strokeStyle = "rgba(255, 255, 255, 0.85)";
            ctx.lineWidth = 1.8;

            // Pitch Outer Boundary Line
            ctx.strokeRect(pitchX, pitchY, pW, pH);

            // Halfway Line
            ctx.beginPath();
            ctx.moveTo(mapX(52.5), pitchY);
            ctx.lineTo(mapX(52.5), pitchY + pH);
            ctx.stroke();

            // Center Circle & Spot (Radius 9.15m at (52.5, 34.0))
            ctx.beginPath();
            ctx.arc(mapX(52.5), mapY(34.0), (9.15 / 68.0) * pH, 0, 2 * Math.PI);
            ctx.stroke();
            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.arc(mapX(52.5), mapY(34.0), 2.5, 0, 2 * Math.PI);
            ctx.fill();

            // Penalty Areas (18-yard box: 16.5m length, 40.32m width)
            // Left Penalty Box (X: 0 -> 16.5m, Y: 13.84 -> 54.16m)
            ctx.strokeRect(mapX(0), mapY(13.84), mapX(16.5) - mapX(0), mapY(54.16) - mapY(13.84));
            // Right Penalty Box (X: 88.5 -> 105m, Y: 13.84 -> 54.16m)
            ctx.strokeRect(mapX(88.5), mapY(13.84), mapX(105) - mapX(88.5), mapY(54.16) - mapY(13.84));

            // Goal Areas (6-yard box: 5.5m length, 18.32m width)
            // Left Goal Box (X: 0 -> 5.5m, Y: 24.84 -> 43.16m)
            ctx.strokeRect(mapX(0), mapY(24.84), mapX(5.5) - mapX(0), mapY(43.16) - mapY(24.84));
            // Right Goal Box (X: 99.5 -> 105m, Y: 24.84 -> 43.16m)
            ctx.strokeRect(mapX(99.5), mapY(24.84), mapX(105) - mapX(99.5), mapY(43.16) - mapY(24.84));

            // Penalty Spots (11m from goal line, Y = 34.0m)
            // Left Penalty Spot (11.0, 34.0)
            ctx.fillStyle = "#ffffff";
            ctx.beginPath();
            ctx.arc(mapX(11.0), mapY(34.0), 2.5, 0, 2 * Math.PI);
            ctx.fill();
            // Right Penalty Spot (94.0, 34.0)
            ctx.beginPath();
            ctx.arc(mapX(94.0), mapY(34.0), 2.5, 0, 2 * Math.PI);
            ctx.fill();

            // Penalty Arcs (D-arcs: Radius 9.15m centered at penalty spots, drawn outside 18-yard box)
            // cos(alpha) = 5.5 / 9.15 => alpha = acos(5.5 / 9.15)
            const dAlpha = Math.acos(5.5 / 9.15);
            const dRadius = (9.15 / 68.0) * pH;
            // Left D-arc (X > 16.5m)
            ctx.beginPath();
            ctx.arc(mapX(11.0), mapY(34.0), dRadius, -dAlpha, dAlpha);
            ctx.stroke();
            // Right D-arc (X < 88.5m)
            ctx.beginPath();
            ctx.arc(mapX(94.0), mapY(34.0), dRadius, Math.PI - dAlpha, Math.PI + dAlpha);
            ctx.stroke();

            // Corner Arcs (Radius 1.0m at 4 corners)
            const cRadius = (1.0 / 68.0) * pH;
            // Top-Left (0, 0)
            ctx.beginPath();
            ctx.arc(mapX(0), mapY(0), cRadius, 0, Math.PI / 2);
            ctx.stroke();
            // Bottom-Left (0, 68)
            ctx.beginPath();
            ctx.arc(mapX(0), mapY(68), cRadius, 1.5 * Math.PI, 2 * Math.PI);
            ctx.stroke();
            // Top-Right (105, 0)
            ctx.beginPath();
            ctx.arc(mapX(105), mapY(0), cRadius, Math.PI / 2, Math.PI);
            ctx.stroke();
            // Bottom-Right (105, 68)
            ctx.beginPath();
            ctx.arc(mapX(105), mapY(68), cRadius, Math.PI, 1.5 * Math.PI);
            ctx.stroke();

            // Goal Posts & Nets (Width 7.32m, Y in [30.34, 37.66]m)
            const goalH = mapY(37.66) - mapY(30.34);
            const goalY = mapY(30.34);
            const netDepth = 7;
            // Left Goal Net (Defending, Conceded)
            ctx.fillStyle = "rgba(239, 68, 68, 0.4)";
            ctx.fillRect(pitchX - netDepth, goalY, netDepth, goalH);
            ctx.strokeStyle = "#ef4444";
            ctx.lineWidth = 1.5;
            ctx.strokeRect(pitchX - netDepth, goalY, netDepth, goalH);

            // Right Goal Net (Attacking, Scored)
            ctx.fillStyle = "rgba(16, 185, 129, 0.4)";
            ctx.fillRect(pitchX + pW, goalY, netDepth, goalH);
            ctx.strokeStyle = "#10b981";
            ctx.lineWidth = 1.5;
            ctx.strokeRect(pitchX + pW, goalY, netDepth, goalH);

            // 3. SHOT EVENT MARKERS (DRAWN THIRD, ON TOP OF PITCH LINES)
            // Defensive Shots (Left Half)
            if (showDefGoals && data.def_goal_coords_x && data.def_goal_coords_y) {
                for (let i = 0; i < data.def_goal_coords_x.length; i++) {
                    const px = mapX(data.def_goal_coords_x[i]);
                    const py = mapY(data.def_goal_coords_y[i]);
                    ctx.beginPath();
                    ctx.arc(px, py, 5.5, 0, 2 * Math.PI);
                    ctx.fillStyle = "#ef4444";
                    ctx.fill();
                    ctx.lineWidth = 1.5;
                    ctx.strokeStyle = "#ffffff";
                    ctx.stroke();
                }
            }
            if (showDefChances && data.def_chance_coords_x && data.def_chance_coords_y) {
                for (let i = 0; i < data.def_chance_coords_x.length; i++) {
                    const px = mapX(data.def_chance_coords_x[i]);
                    const py = mapY(data.def_chance_coords_y[i]);
                    ctx.fillStyle = "#fb923c";
                    ctx.fillRect(px - 3.5, py - 3.5, 7, 7);
                    ctx.lineWidth = 1.2;
                    ctx.strokeStyle = "#ffffff";
                    ctx.strokeRect(px - 3.5, py - 3.5, 7, 7);
                }
            }

            // Attacking Shots (Right Half)
            if (showAttGoals && data.att_goal_coords_x && data.att_goal_coords_y) {
                for (let i = 0; i < data.att_goal_coords_x.length; i++) {
                    const px = mapX(data.att_goal_coords_x[i]);
                    const py = mapY(data.att_goal_coords_y[i]);
                    ctx.beginPath();
                    ctx.arc(px, py, 5.5, 0, 2 * Math.PI);
                    ctx.fillStyle = "#10b981";
                    ctx.fill();
                    ctx.lineWidth = 1.5;
                    ctx.strokeStyle = "#ffffff";
                    ctx.stroke();
                }
            }
            if (showAttChances && data.att_chance_coords_x && data.att_chance_coords_y) {
                for (let i = 0; i < data.att_chance_coords_x.length; i++) {
                    const px = mapX(data.att_chance_coords_x[i]);
                    const py = mapY(data.att_chance_coords_y[i]);
                    ctx.fillStyle = "#06b6d4";
                    ctx.fillRect(px - 3.5, py - 3.5, 7, 7);
                    ctx.lineWidth = 1.2;
                    ctx.strokeStyle = "#ffffff";
                    ctx.strokeRect(px - 3.5, py - 3.5, 7, 7);
                }
            }

            // 4. TEXT LABELS & ANNOTATIONS (TOPMOST LAYER)
            ctx.font = "700 10px 'Space Grotesk', sans-serif";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

            // Left Goal Text Label
            ctx.fillStyle = "#ef4444";
            ctx.fillText("DEFENDING GOAL", mapX(6.0), mapY(34.0));

            // Right Goal Text Label
            ctx.fillStyle = "#10b981";
            ctx.fillText("ATTACKING GOAL", mapX(99.0), mapY(34.0));

            // Zone Titles
            ctx.font = "600 11px 'Space Grotesk', sans-serif";
            ctx.fillStyle = "rgba(239, 68, 68, 0.9)";
            ctx.fillText("DEFENSIVE ZONE (Conceded Shots)", mapX(26.25), pitchY + 14);

            ctx.fillStyle = "rgba(16, 185, 129, 0.9)";
            ctx.fillText("ATTACKING ZONE (Scored Shots)", mapX(78.75), pitchY + 14);

            // Pitch Scale Info
            ctx.font = "500 9px 'Outfit', sans-serif";
            ctx.fillStyle = "rgba(255, 255, 255, 0.45)";
            ctx.fillText("Standard Pitch Geometry: 105m x 68m", mapX(52.5), pitchY + pH - 10);
        }

        window.addEventListener('resize', function() {
            if (document.getElementById('unified-pitch-canvas')) {
                drawUnifiedPitch();
            }
        });
    """
    pattern_render_vuln = r"function renderTeamVulnerability\(\s*teamName,\s*seasonName\s*\)\s*\{.*?\n        \}"
    html = re.sub(pattern_render_vuln, lambda m: js_render_vuln.strip(), html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Senior Engineer Master Bundle V5 compiled into index.html & web_dashboard/index.html!")

if __name__ == "__main__":
    compile_complete_bundle()

