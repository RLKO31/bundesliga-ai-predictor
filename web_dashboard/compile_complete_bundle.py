import os
import json
import re

def compile_complete_bundle():
    print("--- Senior Engineer Master Bundle Compiler V3 ---")
    
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

    # Complete Team Logo URL Map (including raw + unicode escaped keys + OpenLigaDB CDN fallbacks)
    team_logo_urls = {
        # Bayern Munich
        "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "FC Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "FC Bayern M\u00fcnchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "FC Bayern Muenchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "Bayern M\u00fcnchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        
        # Bayer Leverkusen
        "Bayer Leverkusen": "https://www.bundesliga-reisefuehrer.de/sites/default/files/B04_Standard_Logo_RGB.png",
        "Bayer 04 Leverkusen": "https://www.bundesliga-reisefuehrer.de/sites/default/files/B04_Standard_Logo_RGB.png",
        
        # Dortmund
        "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/67/Borussia_Dortmund_logo.svg/960px-Borussia_Dortmund_logo.svg.png",
        
        # RB Leipzig
        "RB Leipzig": "https://i.imgur.com/Rpwsjz1.png",
        "RasenBallsport Leipzig": "https://i.imgur.com/Rpwsjz1.png",
        
        # Stuttgart
        "VfB Stuttgart": "https://i.imgur.com/v0tkpNx.png",
        
        # Eintracht Frankfurt
        "Eintracht Frankfurt": "https://i.imgur.com/X8NFkOb.png",
        
        # SC Freiburg
        "SC Freiburg": "https://i.imgur.com/r3mvi0h.png",
        "Freiburg": "https://i.imgur.com/r3mvi0h.png",
        "Sport-Club Freiburg": "https://i.imgur.com/r3mvi0h.png",
        
        # Borussia Mönchengladbach
        "Borussia M.Gladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Borussia Mönchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Borussia M\u00f6nchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Borussia Mnchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        
        # Union Berlin
        "Union Berlin": "https://assets.dfb.de/uploads/000/018/232/small_union-Berlin.jpg",
        "1. FC Union Berlin": "https://assets.dfb.de/uploads/000/018/232/small_union-Berlin.jpg",
        
        # Werder Bremen
        "Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/b/be/SV-Werder-Bremen-Logo.svg",
        "SV Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/b/be/SV-Werder-Bremen-Logo.svg",
        
        # Mainz 05
        "Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        "1. FSV Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        "Mainz": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        
        # Hoffenheim
        "TSG Hoffenheim": "https://i.imgur.com/gF0PfEl.png",
        "Hoffenheim": "https://i.imgur.com/gF0PfEl.png",
        
        # Augsburg
        "Augsburg": "https://i.imgur.com/sdE62e2.png",
        "FC Augsburg": "https://i.imgur.com/sdE62e2.png",
        
        # FC Köln
        "FC Cologne": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        "1. FC Köln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        r"1. FC K\u00f6ln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        "1. FC Kln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        "FC Köln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",
        r"FC K\u00f6ln": "https://upload.wikimedia.org/wikipedia/commons/0/01/1._FC_Koeln_Logo_2014%E2%80%93.svg",

        # Bayern Munich
        "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "FC Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        r"FC Bayern M\u00fcnchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "FC Bayern Muenchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        "Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",
        r"Bayern M\u00fcnchen": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Logo_FC_Bayern_M%C3%BCnchen_%282002%E2%80%932017%29.svg",

        # Borussia Mönchengladbach
        "Borussia M.Gladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Borussia Mönchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        r"Borussia M\u00f6nchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        "Borussia Mnchengladbach": "https://i.imgur.com/KSIk0Eu.png",
        
        # Hamburger SV
        "Hamburger SV": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Hamburger_SV_logo.svg",
        "Hamburg SV": "https://upload.wikimedia.org/wikipedia/commons/f/f7/Hamburger_SV_logo.svg",
        
        # Paderborn
        "Paderborn": "https://upload.wikimedia.org/wikipedia/commons/e/e3/SC_Paderborn_07_Logo.svg",
        "SC Paderborn 07": "https://upload.wikimedia.org/wikipedia/commons/e/e3/SC_Paderborn_07_Logo.svg",
        
        # Elversberg
        "Elversberg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/SV_Elversberg_Logo.svg/500px-SV_Elversberg_Logo.svg.png",
        "SV 07 Elversberg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/SV_Elversberg_Logo.svg/500px-SV_Elversberg_Logo.svg.png",
        "SV Elversberg": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/35/SV_Elversberg_Logo.svg/500px-SV_Elversberg_Logo.svg.png",
        
        # Schalke 04
        "Schalke 04": "https://upload.wikimedia.org/wikipedia/commons/9/97/FC_Schalke_04_Logo.png",
        "FC Schalke 04": "https://upload.wikimedia.org/wikipedia/commons/9/97/FC_Schalke_04_Logo.png",
        
        # Wolfsburg
        "Wolfsburg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/VfL_Wolfsburg_logo_2026.svg/960px-VfL_Wolfsburg_logo_2026.svg.png",
        "VfL Wolfsburg": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/VfL_Wolfsburg_logo_2026.svg/960px-VfL_Wolfsburg_logo_2026.svg.png",
        
        # Bochum
        "Bochum": "https://i.imgur.com/5jy3Gfr.png",
        "VfL Bochum": "https://i.imgur.com/5jy3Gfr.png",
        
        # Heidenheim
        "FC Heidenheim": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846.svg",
        "1. FC Heidenheim": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846.svg",
        "1. FC Heidenheim 1846": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846.svg",
        
        # St. Pauli
        "St. Pauli": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Fc_st_pauli_logo.svg",
        "FC St. Pauli": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Fc_st_pauli_logo.svg",
        "1. FC St. Pauli": "https://upload.wikimedia.org/wikipedia/commons/b/b3/Fc_st_pauli_logo.svg",

        # Additional 2nd/3rd Liga teams
        "Holstein Kiel": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Holstein_Kiel_Logo.svg/330px-Holstein_Kiel_Logo.svg.png",
        "SV Darmstadt 98": "https://upload.wikimedia.org/wikipedia/commons/e/e5/SV_Darmstadt_98_Logo.svg",
        "Darmstadt 98": "https://upload.wikimedia.org/wikipedia/commons/e/e5/SV_Darmstadt_98_Logo.svg",
        "Hertha BSC": "https://i.imgur.com/apFwbYZ.png",
        "Hertha Berlin": "https://i.imgur.com/apFwbYZ.png",
        "Hannover 96": "https://upload.wikimedia.org/wikipedia/commons/c/cd/Hannover_96_Logo.svg",
        "1. FC Kaiserslautern": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Logo_1_FC_Kaiserslautern.svg",
        "Kaiserslautern": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Logo_1_FC_Kaiserslautern.svg",
        "Karlsruher SC": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Karlsruher_SC_Logo_2.svg",
        "Fortuna Düsseldorf": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/94/Fortuna_D%C3%BCsseldorf.svg/960px-Fortuna_D%C3%BCsseldorf.svg.png",
        "SpVgg Greuther Fürth": "https://i.imgur.com/pwuVbKr.png",
        "SpVgg Greuther F\u00fcrth": "https://i.imgur.com/pwuVbKr.png",
        "1. FC Magdeburg": "https://upload.wikimedia.org/wikipedia/commons/8/84/1._FC_Magdeburg.svg",
        "1. FC Nürnberg": "https://upload.wikimedia.org/wikipedia/commons/f/fa/1._FC_N%C3%BCrnberg_logo.svg",
        "1. FC N\u00fcrnberg": "https://upload.wikimedia.org/wikipedia/commons/f/fa/1._FC_N%C3%BCrnberg_logo.svg",
        "Eintracht Braunschweig": "https://upload.wikimedia.org/wikipedia/de/4/45/Logo_Eintracht_Braunschweig.svg",
        "VfL Osnabrück": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/VfL_Osnabrueck_Logo_2021%E2%80%93.svg/960px-VfL_Osnabrueck_Logo_2021%E2%80%93.svg.png",
        "VfL Osnabruck": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/VfL_Osnabrueck_Logo_2021%E2%80%93.svg/960px-VfL_Osnabrueck_Logo_2021%E2%80%93.svg.png",
        "Arminia Bielefeld": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/81/Arminia_Bielefeld_logo.svg/960px-Arminia_Bielefeld_logo.svg.png"
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

    # 3. Replace const teamLogos in JS
    js_logos_block = f"const teamLogos = {logos_json};"
    if "const teamLogos =" in html:
        pattern_logos = r'const teamLogos\s*=\s*\{.*?\};'
        html = re.sub(pattern_logos, lambda m: js_logos_block, html, flags=re.DOTALL)

    # 4. Replace CartoDB Tile Layer with 100% Free Esri World Dark Gray Canvas
    pattern_carto = r"L\.tileLayer\('https://\{s\}\.basemaps\.cartocdn\.com/[^']+',\s*\{.*?\n\s*\}\)\.addTo\(map\);"
    esri_tile_code = """L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', { 
                maxZoom: 16,
                attribution: '&copy; <a href="https://www.esri.com/">Esri</a>, HERE, Garmin, USGS'
            }).addTo(map);"""
    html = re.sub(pattern_carto, lambda m: esri_tile_code.strip(), html, flags=re.DOTALL)

    # 5. Restore Section #standings-tab (live-standings-body & predicted-standings-body)
    standings_sec_html = """
        <!-- Tab 2: Standings Comparison -->
        <section id="standings-tab" class="content-section">
            <div class="standings-grid-container">
                <div class="table-card">
                    <h3>
                        <span><i data-lucide="activity" size="20" style="color: var(--accent-green);"></i> Live DFL Standings</span>
                        <span class="live-badge">Daily API</span>
                    </h3>
                    <div style="overflow-x: auto;">
                        <table class="standings-table">
                            <thead>
                                <tr>
                                    <th class="rank-col">#</th>
                                    <th>Team</th>
                                    <th style="text-align: center;">P</th>
                                    <th style="text-align: center;">W-D-L</th>
                                    <th style="text-align: center;">GD</th>
                                    <th style="text-align: right;">Pts</th>
                                </tr>
                            </thead>
                            <tbody id="live-standings-body"></tbody>
                        </table>
                    </div>
                </div>

                <div class="table-card">
                    <h3>
                        <span><i data-lucide="target" size="20" style="color: var(--accent-lime);"></i> Model Predicted Standings</span>
                        <span class="live-badge" style="background: rgba(34,197,94,0.1); color: var(--accent-lime); border-color: rgba(34,197,94,0.2);">Predicted Table</span>
                    </h3>
                    <div style="overflow-x: auto;">
                        <table class="standings-table">
                            <thead>
                                <tr>
                                    <th class="rank-col">#</th>
                                    <th>Team</th>
                                    <th style="text-align: center;">Elo Rating</th>
                                    <th style="text-align: center;">GD</th>
                                    <th style="text-align: right;">Pred Pts</th>
                                </tr>
                            </thead>
                            <tbody id="predicted-standings-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>
    """
    pattern_standings = r'<section id="standings-tab".*?</section>'
    html = re.sub(pattern_standings, lambda m: standings_sec_html.strip(), html, flags=re.DOTALL)

    # 6. Fix Section #complexity-tab (v4 table body ID: #v4-complexity-standings-body)
    v4_table_html = """
        <!-- Tab 5: Model v4 First 15 Goals Complexity -->
        <section id="complexity-tab" class="content-section">
            <div class="comp-card" style="margin-bottom: 2rem;">
                <h3 style="display: flex; justify-content: space-between; align-items: center;">
                    <span><i data-lucide="sparkles" size="22" style="color: var(--accent-purple);"></i> Model v4: First 15 Goals Complexity Standings</span>
                    <span class="live-badge" style="background: rgba(192, 132, 252, 0.15); color: var(--accent-purple); border-color: rgba(192, 132, 252, 0.3);">R² = 0.7203 | MAE = 6.77 pts</span>
                </h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; margin-bottom: 1.5rem;">
                    Model v4 forecasts end-of-season standings using the 6-dimensional Goal Complexity Vector of each team's first 15 goals:
                </p>
                <div style="overflow-x: auto;">
                    <table class="standings-table">
                        <thead>
                            <tr>
                                <th class="rank-col">Rank</th>
                                <th>Team</th>
                                <th style="text-align: center;">Matches to 15 Goals</th>
                                <th style="text-align: center;">Buildup Skill ($C_{\\\\text{action}}$)</th>
                                <th style="text-align: center;">Assist Entropy ($H_{\\\\text{assist}}$)</th>
                                <th style="text-align: center;">Avg xG / Goal</th>
                                <th style="text-align: right;">Predicted Final Pts</th>
                            </tr>
                        </thead>
                        <tbody id="v4-complexity-standings-body"></tbody>
                    </table>
                </div>
            </div>
        </section>
    """
    pattern_v4_sec = r'<section id="complexity-tab".*?</section>'
    html = re.sub(pattern_v4_sec, lambda m: v4_table_html.strip(), html, flags=re.DOTALL)

    # 7. Fix Section #m14-tab (v5 table body ID: #v5-m14-standings-body)
    v5_table_html = """
        <!-- Tab 6: Model v5 Matchday 1-4 Goal Complexity -->
        <section id="m14-tab" class="content-section">
            <div class="comp-card" style="margin-bottom: 2rem;">
                <h3 style="display: flex; justify-content: space-between; align-items: center;">
                    <span><i data-lucide="clock" size="22" style="color: var(--accent-orange);"></i> Model v5: Matchdays 1-4 Early Goal Complexity Standings</span>
                    <span class="live-badge" style="background: rgba(251, 146, 60, 0.15); color: var(--accent-orange); border-color: rgba(251, 146, 60, 0.3);">R² = 0.6383 | MAE = 7.67 pts</span>
                </h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; margin-bottom: 1.5rem;">
                    Model v5 uses only goals scored during <strong>Matchdays 1 to 4</strong> to forecast final end-of-season standings points:
                </p>
                <div style="overflow-x: auto;">
                    <table class="standings-table">
                        <thead>
                            <tr>
                                <th class="rank-col">Rank</th>
                                <th>Team</th>
                                <th style="text-align: right;">Predicted Final Pts</th>
                                <th style="text-align: center;">MD 1-4 Goals</th>
                                <th style="text-align: center;">Buildup Skill ($C_{\\\\text{action}}$)</th>
                                <th style="text-align: center;">Assist Entropy ($H_{\\\\text{assist}}$)</th>
                                <th style="text-align: center;">Avg xG / Goal</th>
                                <th style="text-align: right;">Finishing Delta ($\\\\Delta_{\\\\text{fin}}$)</th>
                            </tr>
                        </thead>
                        <tbody id="v5-m14-standings-body"></tbody>
                    </table>
                </div>
            </div>
        </section>
    """
    pattern_v5_sec = r'<section id="m14-tab".*?</section>'
    html = re.sub(pattern_v5_sec, lambda m: v5_table_html.strip(), html, flags=re.DOTALL)

    # 8. Fix renderV4ComplexityTable JS function
    js_v4_render = """
        function renderV4ComplexityTable() {
            const body = document.getElementById("v4-complexity-standings-body");
            const data = window.predictions_v4 || (typeof predictions_v4 !== "undefined" ? predictions_v4 : null);
            if (!body || !data) return;
            body.innerHTML = "";

            data.forEach(rec => {
                const logo = window.getTeamLogo ? getTeamLogo(rec.team) : "";
                const logoHtml = logo ? `<img class="team-logo-small" src="${logo}" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='https://upload.wikimedia.org/wikipedia/commons/e/e0/Placeholder_LC.svg';">` : `<div style="width:20px;height:20px;display:inline-block;background:rgba(255,255,255,0.1);border-radius:50%;text-align:center;font-size:10px;line-height:20px;">${rec.team.substring(0,2)}</div>`;
                
                const tr = document.createElement("tr");
                tr.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
                tr.innerHTML = `
                    <td class="rank-col" style="padding: 0.65rem; color: var(--accent-purple); font-weight: 800;">#${rec.rank}</td>
                    <td style="padding: 0.65rem;"><div class="team-col" style="display:flex;align-items:center;gap:0.5rem;">${logoHtml}<span style="font-weight:600;color:#fff;">${rec.team}</span></div></td>
                    <td style="padding: 0.65rem; text-align: center; color: #fff;">${rec.matches_to_15_goals} matches</td>
                    <td style="padding: 0.65rem; text-align: center; font-weight: 700; color: #38bdf8;">${rec.action_complexity_score.toFixed(2)}</td>
                    <td style="padding: 0.65rem; text-align: center; font-weight: 700; color: #c084fc;">${rec.assist_entropy.toFixed(2)}</td>
                    <td style="padding: 0.65rem; text-align: center; color: var(--text-secondary);">${rec.avg_xg_per_goal.toFixed(2)}</td>
                    <td style="padding: 0.65rem; text-align: right; font-weight: 800; color: var(--accent-purple); font-family: 'Space Grotesk', sans-serif;">${rec.predicted_points.toFixed(1)} pts</td>
                `;
                body.appendChild(tr);
            });
        }
    """
    pattern_v4_func = r"function renderV4ComplexityTable\(\) \{.*?\n        \}"
    html = re.sub(pattern_v4_func, lambda m: js_v4_render.strip(), html, flags=re.DOTALL)

    # 9. Fix renderV5ComplexityTable JS function
    js_v5_render = """
        function renderV5ComplexityTable() {
            const tbody = document.getElementById("v5-m14-standings-body");
            const data = window.predictions_v5_m1_4 || (typeof predictions_v5_m1_4 !== "undefined" ? predictions_v5_m1_4 : null);
            if (!tbody || !data) return;
            
            let html = "";
            data.forEach((t, i) => {
                const isTop4 = i < 4;
                const isRelegation = i >= 15;
                const rankColor = isTop4 ? "color: var(--accent-green); font-weight: 800;" : (isRelegation ? "color: #ef4444; font-weight: 800;" : "color: var(--text-secondary);");
                const logo = window.getTeamLogo ? getTeamLogo(t.team) : "";
                const logoHtml = logo ? `<img class="team-logo-small" src="${logo}" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src='https://upload.wikimedia.org/wikipedia/commons/e/e0/Placeholder_LC.svg';" style="width:20px;height:20px;object-fit:contain;">` : "";

                html += `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 0.65rem; ${rankColor}">#${t.rank}</td>
                        <td style="padding: 0.65rem; font-weight: 600; color: #fff;"><div style="display:flex;align-items:center;gap:0.5rem;">${logoHtml}<span>${t.team}</span></div></td>
                        <td style="padding: 0.65rem; text-align: right; color: var(--accent-lime); font-weight: 800; font-family: 'Space Grotesk', sans-serif;">${t.predicted_points.toFixed(1)} pts</td>
                        <td style="padding: 0.65rem; text-align: center; color: #fff; font-weight: 700;">${t.goals_in_first_4_matches}</td>
                        <td style="padding: 0.65rem; text-align: center; color: #38bdf8;">${t.action_complexity_score.toFixed(2)}</td>
                        <td style="padding: 0.65rem; text-align: center; color: #c084fc;">${t.assist_entropy.toFixed(2)}</td>
                        <td style="padding: 0.65rem; text-align: center; color: #9ca3af;">${t.avg_xg_per_goal.toFixed(2)}</td>
                        <td style="padding: 0.65rem; text-align: right; color: ${t.finishing_delta >= 0 ? '#10b981' : '#ef4444'};">${t.finishing_delta >= 0 ? '+' : ''}${t.finishing_delta.toFixed(2)}</td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }
    """
    pattern_v5_func = r"function renderV5ComplexityTable\(\) \{.*?\n        \}"
    html = re.sub(pattern_v5_func, lambda m: js_v5_render.strip(), html, flags=re.DOTALL)

    # 10. Ensure switchTab triggers all tab renderers cleanly
    js_switch_tab = """
        function switchTab(tabId, btnEl) {
            document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            
            const targetSec = document.getElementById(tabId + '-tab');
            if (targetSec) targetSec.classList.add('active');
            if (btnEl) btnEl.classList.add('active');
            
            if (tabId === 'standings') loadLiveTable();
            if (tabId === 'map') initMap();
            if (tabId === 'tactical') populateTacticalMatchSelector();
            if (tabId === 'complexity') renderV4ComplexityTable();
            if (tabId === 'm14') renderV5ComplexityTable();
            if (tabId === 'vulnerability') {
                const teamVal = document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich';
                const seasonVal = document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027';
                renderTeamVulnerability(teamVal, seasonVal);
                populateAdaptabilityTable();
            }
            if (window.lucide) lucide.createIcons();
        }
    """
    pattern_switch_tab = r"function switchTab\(tabId,\s*btnEl\) \{.*?\n        \}"
    html = re.sub(pattern_switch_tab, lambda m: js_switch_tab.strip(), html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Senior Engineer Master Bundle V3 compiled into index.html & web_dashboard/index.html!")

if __name__ == "__main__":
    compile_complete_bundle()
