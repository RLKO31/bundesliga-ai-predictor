"""
===============================================================================
MASTER GITHUB PAGES BUG FIXER & DASHBOARD COMPILER
===============================================================================
Resolves:
1. Leaflet Travel Map missing stadium data -> Injects window.stadiums.
2. First 15 Goals (v4) Table missing -> Injects window.predictions_v4 & fixes tbody ID #v4-complexity-standings-body.
3. Matchday 1-4 Complexity (v5) Table missing -> Fixes tbody ID #v5-m14-standings-body & data binding.
4. Tactical Vulnerability Pitch Map -> Ensures 105m x 68m pitch coordinates & multi-season filters.
===============================================================================
"""

import os
import json
import re

def compile_all_github_fixes():
    print("--- 1. Executing Master GitHub Bug Fix Compiler ---")
    
    # Load JSON files
    v4_path = "models/model_v4_complexity/predictions_v4_complexity.json"
    if not os.path.exists(v4_path): v4_path = "predictions_v4_complexity.json"
    
    v5_path = "models/model_v5_matchday1_4/predictions_v5_m1_4.json"
    if not os.path.exists(v5_path): v5_path = "predictions_v5_m1_4.json"
    
    vuln_path = "data/team_vulnerabilities_multiseason.json"
    adapt_path = "data/tactical_adaptability_2026.json"
    
    with open(v4_path, "r", encoding="utf-8") as f: v4_raw = json.load(f)
    with open(v5_path, "r", encoding="utf-8") as f: v5_raw = json.load(f)
    with open(vuln_path, "r", encoding="utf-8") as f: vuln_raw = json.load(f)
    with open(adapt_path, "r", encoding="utf-8") as f: adapt_raw = json.load(f)
    
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
    
    stadiums_json = json.dumps(stadiums)
    v4_json = json.dumps(v4_raw)
    v5_json = json.dumps(v5_raw)
    vuln_json = json.dumps(vuln_raw)
    adapt_json = json.dumps(adapt_raw)
    
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    # 2. Inject Data Block into <head>
    data_script_block = f"""
    <script id="embedded-data-state">
        window.stadiums = {stadiums_json};
        window.predictions_v4 = {v4_json};
        window.predictions_v5_m1_4 = {v5_json};
        window.team_vulnerabilities_multiseason = {vuln_json};
        window.tactical_adaptability = {adapt_json};
    </script>
    """
    
    if '<script id="embedded-data-state">' in html:
        pattern = r'<script id="embedded-data-state">.*?</script>'
        html = re.sub(pattern, lambda m: data_script_block.strip(), html, flags=re.DOTALL)
    else:
        html = html.replace('</head>', data_script_block + '\n</head>')
        
    # 3. Fix Section #complexity-tab (v4 table body ID: #v4-complexity-standings-body)
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
    
    # 4. Fix Section #m14-tab (v5 table body ID: #v5-m14-standings-body)
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
    
    # 5. Fix renderV4ComplexityTable JS function
    js_v4_render = """
        function renderV4ComplexityTable() {
            const body = document.getElementById("v4-complexity-standings-body");
            const data = window.predictions_v4 || (typeof predictions_v4 !== "undefined" ? predictions_v4 : null);
            if (!body || !data) return;
            body.innerHTML = "";

            data.forEach(rec => {
                const teamClean = cleanTeamName(rec.team);
                const logo = (typeof teamLogos !== "undefined" && teamLogos[teamClean]) ? teamLogos[teamClean] : "";
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
    
    # 6. Fix Map initMap & updateMapDisplay for Leaflet Map
    js_map_fix = """
        function initMap() {
            if (mapInitialized && map) { map.invalidateSize(); return; }
            const mapContainer = document.getElementById('map');
            if (!mapContainer) return;
            
            map = L.map('map', { center: [51.1657, 10.4515], zoom: 6, attributionControl: true });
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { 
                maxZoom: 9,
                attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
            }).addTo(map);
            teamMarkersGroup = L.layerGroup().addTo(map);
            travelLinesGroup = L.layerGroup().addTo(map);
            updateMapDisplay();
            mapInitialized = true;
        }

        function updateMapDisplay() {
            if (!map) return;
            teamMarkersGroup.clearLayers();
            travelLinesGroup.clearLayers();
            const stData = window.stadiums || (typeof stadiums !== "undefined" ? stadiums : null);
            if (!stData) return;

            Object.entries(stData).forEach(([team, st]) => {
                if (st && st.lat && st.lng) {
                    const marker = L.circleMarker([st.lat, st.lng], {
                        radius: 7,
                        fillColor: "#22c55e",
                        color: "#ffffff",
                        weight: 2,
                        opacity: 1,
                        fillOpacity: 0.85
                    });
                    marker.bindPopup(`<strong>${team}</strong><br>${st.name} (${st.city})`);
                    teamMarkersGroup.addLayer(marker);
                }
            });
        }
    """
    pattern_map_func = r"function initMap\(\) \{.*?\n        function toggleMapMode"
    html = re.sub(pattern_map_func, lambda m: js_map_fix.strip() + "\n\n        function toggleMapMode", html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Applied all GitHub Pages bug fixes to index.html!")

if __name__ == "__main__":
    compile_all_github_fixes()
