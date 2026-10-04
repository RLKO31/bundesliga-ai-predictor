"""
===============================================================================
SENIOR ENGINEER REVIEW: MASTER DASHBOARD BUNDLER & BUG FIXER V2
===============================================================================
Resolves:
1. 100% Team Logo Coverage: Adds all 47 team name variations to teamLogos.
2. Complete Data State: Injects window.predictions_v2, v3, v4, v5, v6, v6_2stage, 
   heatmaps, stadiums, vulnerabilities, and adaptability.
3. Element ID Harmonization: Restores standings-tab (live-standings-body & 
   predicted-standings-body), complexity-tab (v4-complexity-standings-body), 
   m14-tab (v5-m14-standings-body), predictions-tab (fixtures-grid).
4. Leaflet Map Initialization: Fixes stadium lat/lng coordinates & Leaflet markers.
===============================================================================
"""

import os
import json
import re

def compile_complete_bundle():
    print("--- Senior Engineer Master Bundle Compiler V2 ---")
    
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

    # Complete Team Logo URL Map for 100% of Team Name Aliases
    team_logo_urls = {
        "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg",
        "FC Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg",
        "FC Bayern Muenchen": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg",
        "Bayern München": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg",
        
        "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
        "Bayer 04 Leverkusen": "https://upload.wikimedia.org/wikipedia/en/5/59/Bayer_04_Leverkusen_logo.svg",
        
        "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
        
        "RB Leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
        "RasenBallsport Leipzig": "https://upload.wikimedia.org/wikipedia/en/0/04/RB_Leipzig_2014_logo.svg",
        
        "VfB Stuttgart": "https://upload.wikimedia.org/wikipedia/commons/e/eb/VfB_Stuttgart_1893_Logo.svg",
        
        "Eintracht Frankfurt": "https://upload.wikimedia.org/wikipedia/commons/0/04/Eintracht_Frankfurt_Logo.svg",
        
        "SC Freiburg": "https://upload.wikimedia.org/wikipedia/en/6/6d/SC_Freiburg_logo.svg",
        "Freiburg": "https://upload.wikimedia.org/wikipedia/en/6/6d/SC_Freiburg_logo.svg",
        
        "Borussia M.Gladbach": "https://upload.wikimedia.org/wikipedia/commons/8/81/Borussia_M%C3%B6nchengladbach_logo.svg",
        "Borussia Mönchengladbach": "https://upload.wikimedia.org/wikipedia/commons/8/81/Borussia_M%C3%B6nchengladbach_logo.svg",
        "Borussia Mnchengladbach": "https://upload.wikimedia.org/wikipedia/commons/8/81/Borussia_M%C3%B6nchengladbach_logo.svg",
        
        "Union Berlin": "https://upload.wikimedia.org/wikipedia/commons/4/44/1._FC_Union_Berlin_Logo.svg",
        "1. FC Union Berlin": "https://upload.wikimedia.org/wikipedia/commons/4/44/1._FC_Union_Berlin_Logo.svg",
        
        "Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/b/be/SV-Werder-Bremen-Logo.svg",
        "SV Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/b/be/SV-Werder-Bremen-Logo.svg",
        
        "Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        "1. FSV Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        "Mainz": "https://upload.wikimedia.org/wikipedia/commons/9/9e/Logo_Mainz_05.svg",
        
        "TSG Hoffenheim": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Logo_TSG_1899_Hoffenheim.svg",
        "Hoffenheim": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Logo_TSG_1899_Hoffenheim.svg",
        
        "Augsburg": "https://upload.wikimedia.org/wikipedia/en/c/c5/FC_Augsburg_logo.svg",
        "FC Augsburg": "https://upload.wikimedia.org/wikipedia/en/c/c5/FC_Augsburg_logo.svg",
        
        "FC Cologne": "https://upload.wikimedia.org/wikipedia/commons/1/1a/1._FC_K%C3%B6ln_logo.svg",
        "1. FC Köln": "https://upload.wikimedia.org/wikipedia/commons/1/1a/1._FC_K%C3%B6ln_logo.svg",
        "1. FC Kln": "https://upload.wikimedia.org/wikipedia/commons/1/1a/1._FC_K%C3%B6ln_logo.svg",
        "FC Köln": "https://upload.wikimedia.org/wikipedia/commons/1/1a/1._FC_K%C3%B6ln_logo.svg",
        
        "Hamburger SV": "https://upload.wikimedia.org/wikipedia/commons/6/66/HSV-Logo.svg",
        "Hamburg SV": "https://upload.wikimedia.org/wikipedia/commons/6/66/HSV-Logo.svg",
        
        "Paderborn": "https://upload.wikimedia.org/wikipedia/commons/b/b3/SC_Paderborn_07_Logo.svg",
        "SC Paderborn 07": "https://upload.wikimedia.org/wikipedia/commons/b/b3/SC_Paderborn_07_Logo.svg",
        
        "Elversberg": "https://upload.wikimedia.org/wikipedia/commons/a/a2/SV_Elversberg_Logo.svg",
        "SV 07 Elversberg": "https://upload.wikimedia.org/wikipedia/commons/a/a2/SV_Elversberg_Logo.svg",
        
        "Schalke 04": "https://upload.wikimedia.org/wikipedia/commons/6/6d/FC_Schalke_04_Logo.svg",
        "FC Schalke 04": "https://upload.wikimedia.org/wikipedia/commons/6/6d/FC_Schalke_04_Logo.svg",
        
        "Wolfsburg": "https://upload.wikimedia.org/wikipedia/commons/c/ce/VfL_Wolfsburg_Logo.svg",
        "VfL Wolfsburg": "https://upload.wikimedia.org/wikipedia/commons/c/ce/VfL_Wolfsburg_Logo.svg",
        
        "Bochum": "https://upload.wikimedia.org/wikipedia/commons/7/72/VfL_Bochum_logo.svg",
        "VfL Bochum": "https://upload.wikimedia.org/wikipedia/commons/7/72/VfL_Bochum_logo.svg",
        
        "FC Heidenheim": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846_Logo.svg",
        "1. FC Heidenheim": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846_Logo.svg",
        "1. FC Heidenheim 1846": "https://upload.wikimedia.org/wikipedia/commons/9/9d/1._FC_Heidenheim_1846_Logo.svg",
        
        "St. Pauli": "https://upload.wikimedia.org/wikipedia/commons/e/e4/FC_St._Pauli_logo.svg"
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

    # 2. Inject Data Block into <head>
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

    # 4. Restore Section #standings-tab (live-standings-body & predicted-standings-body)
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

    # 5. Fix Section #complexity-tab (v4 table body ID: #v4-complexity-standings-body)
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

    # 6. Fix Section #m14-tab (v5 table body ID: #v5-m14-standings-body)
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

    # 7. Fix renderV4ComplexityTable JS function
    js_v4_render = """
        function renderV4ComplexityTable() {
            const body = document.getElementById("v4-complexity-standings-body");
            const data = window.predictions_v4 || (typeof predictions_v4 !== "undefined" ? predictions_v4 : null);
            if (!body || !data) return;
            body.innerHTML = "";

            data.forEach(rec => {
                const teamClean = cleanTeamName(rec.team);
                const logo = (typeof teamLogos !== "undefined" && (teamLogos[teamClean] || teamLogos[rec.team])) ? (teamLogos[teamClean] || teamLogos[rec.team]) : "";
                const logoHtml = logo ? `<img class="team-logo-small" src="${logo}" referrerpolicy="no-referrer">` : `<div style="width:20px;height:20px;display:inline-block;background:rgba(255,255,255,0.1);border-radius:50%;text-align:center;font-size:10px;line-height:20px;">${rec.team.substring(0,2)}</div>`;
                
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

    # 8. Fix renderV5ComplexityTable JS function
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
                const teamClean = cleanTeamName(t.team);
                const logo = (typeof teamLogos !== "undefined" && (teamLogos[teamClean] || teamLogos[t.team])) ? (teamLogos[teamClean] || teamLogos[t.team]) : "";
                const logoHtml = logo ? `<img class="team-logo-small" src="${logo}" referrerpolicy="no-referrer" style="width:20px;height:20px;object-fit:contain;">` : "";

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

    # 9. Ensure switchTab triggers all tab renderers cleanly
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
            
    print("SUCCESS: Senior Engineer Master Bundle V2 compiled into index.html & web_dashboard/index.html!")

if __name__ == "__main__":
    compile_complete_bundle()
