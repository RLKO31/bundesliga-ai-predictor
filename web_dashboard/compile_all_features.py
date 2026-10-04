"""
===============================================================================
MASTER WEB DASHBOARD COMPILLER & DATA BINDER
===============================================================================
Binds predictions_v5_m1_4.json, team_vulnerabilities_2026.json, and 
tactical_adaptability_2026.json directly into index.html script state and 
fixes all HTML element IDs & renderer functions.
===============================================================================
"""

import os
import json
import re

def compile_all_features():
    print("--- Master Web Dashboard Compilation & Data Binding ---")
    
    # 1. Load JSON Data
    v5_path = "models/model_v5_matchday1_4/predictions_v5_m1_4.json"
    if not os.path.exists(v5_path): v5_path = "predictions_v5_m1_4.json"
    
    vuln_path = "data/team_vulnerabilities_2026.json"
    adapt_path = "data/tactical_adaptability_2026.json"
    
    with open(v5_path, "r", encoding="utf-8") as f:
        v5_raw = json.load(f)
        
    with open(vuln_path, "r", encoding="utf-8") as f:
        vuln_raw = json.load(f)
        
    with open(adapt_path, "r", encoding="utf-8") as f:
        adapt_raw = json.load(f)
        
    # Filter Model v5 to 18 Bundesliga teams
    b1_teams = [
        "Bayern Munich", "Bayer Leverkusen", "Borussia Dortmund", "SC Freiburg", 
        "RB Leipzig", "Eintracht Frankfurt", "VfB Stuttgart", "Mainz 05", 
        "Augsburg", "Werder Bremen", "Wolfsburg", "Bochum", "TSG Hoffenheim", 
        "FC Heidenheim", "Borussia M.Gladbach", "FC Cologne", "Union Berlin", "Hamburger SV"
    ]
    v5_data = [rec for rec in v5_raw if rec['team'] in b1_teams]
    for idx, rec in enumerate(v5_data): rec['rank'] = idx + 1
    
    v5_json = json.dumps(v5_data)
    vuln_json = json.dumps(vuln_raw)
    adapt_json = json.dumps(adapt_raw)
    
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    # 2. Inject Data Block into <head>
    data_script_block = f"""
    <script id="embedded-data-state">
        window.predictions_v5_m1_4 = {v5_json};
        window.team_vulnerabilities = {vuln_json};
        window.tactical_adaptability = {adapt_json};
    </script>
    """
    
    if '<script id="embedded-data-state">' in html:
        pattern = r'<script id="embedded-data-state">.*?</script>'
        html = re.sub(pattern, data_script_block.strip(), html, flags=re.DOTALL)
    else:
        html = html.replace('</head>', data_script_block + '\n</head>')
        
    # 3. Ensure nav tab buttons pass correct tabId
    if "switchTab('vulnerability-tab'" in html:
        html = html.replace("switchTab('vulnerability-tab'", "switchTab('vulnerability'")
        
    # 4. Fix renderV5ComplexityTable JS function to target #v5-m14-standings-body
    js_v5_render = """
        function renderV5ComplexityTable() {
            const tbody = document.getElementById("v5-m14-standings-body") || document.getElementById("v5-complexity-tbody");
            if (!tbody || !window.predictions_v5_m1_4) return;
            
            let html = "";
            window.predictions_v5_m1_4.forEach((t, i) => {
                const isTop4 = i < 4;
                const isRelegation = i >= 15;
                const rankColor = isTop4 ? "color: var(--accent-green); font-weight: 800;" : (isRelegation ? "color: #ef4444; font-weight: 800;" : "color: var(--text-secondary);");
                
                html += `
                    <tr style="border-bottom: 1px solid rgba(255,255,255,0.05);">
                        <td style="padding: 0.65rem; ${rankColor}">#${t.rank}</td>
                        <td style="padding: 0.65rem; font-weight: 600; color: #fff;">${t.team}</td>
                        <td style="padding: 0.65rem; color: var(--accent-lime); font-weight: 800; font-family: 'Space Grotesk', sans-serif;">${t.predicted_points.toFixed(1)} pts</td>
                        <td style="padding: 0.65rem; color: #fff; font-weight: 700;">${t.goals_in_first_4_matches}</td>
                        <td style="padding: 0.65rem; color: #38bdf8;">${t.action_complexity_score.toFixed(2)}</td>
                        <td style="padding: 0.65rem; color: #c084fc;">${t.assist_entropy.toFixed(2)}</td>
                        <td style="padding: 0.65rem; color: #9ca3af;">${t.avg_xg_per_goal.toFixed(2)}</td>
                        <td style="padding: 0.65rem; color: ${t.finishing_delta >= 0 ? '#10b981' : '#ef4444'};">${t.finishing_delta >= 0 ? '+' : ''}${t.finishing_delta.toFixed(2)}</td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        }
    """
    
    if "function renderV5ComplexityTable" in html:
        pattern = r"function renderV5ComplexityTable\(\) \{.*?\n        \}"
        html = re.sub(pattern, js_v5_render.strip(), html, flags=re.DOTALL)
    else:
        html = html.replace("function switchTab", js_v5_render + "\n        function switchTab")
        
    # 5. Update switchTab function logic
    if "if (tabId === 'vulnerability')" not in html:
        html = html.replace("if (tabId === 'm14') renderV5ComplexityTable();", "if (tabId === 'm14') renderV5ComplexityTable();\n            if (tabId === 'vulnerability') { renderTeamVulnerability(document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich'); populateAdaptabilityTable(); }")

    # 6. Ensure page initialization triggers all table renders
    init_trigger = "renderTacticalPitchMatch();\n            renderV5ComplexityTable();\n            renderTeamVulnerability('Bayern Munich');\n            populateAdaptabilityTable();"
    if "renderV5ComplexityTable();" not in html:
        html = html.replace("renderTacticalPitchMatch();", init_trigger)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Master data binding & renderer fixes applied to index.html!")

if __name__ == "__main__":
    compile_all_features()
