"""
===============================================================================
WEB DASHBOARD COMPILLER: MODEL V5 REAL MATCHDAY 1-4 RESULTS INTEGRATION
===============================================================================
Embeds predictions_v5_m1_4.json into index.html and updates renderV5ComplexityTable.
===============================================================================
"""

import os
import json
import re

def compile_m1_4_real_dashboard():
    print("--- Compiling Web Dashboard with Real Model v5 (Matchdays 1-4) Results ---")
    
    json_path = "models/model_v5_matchday1_4/predictions_v5_m1_4.json"
    if not os.path.exists(json_path):
        json_path = "predictions_v5_m1_4.json"
        
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    with open(json_path, "r", encoding="utf-8") as f:
        v5_data = json.load(f)
        
    # Filter to top 18 Bundesliga 1 teams
    b1_teams = [
        "Bayern Munich", "Borussia Dortmund", "Bayer Leverkusen", "SC Freiburg", 
        "RB Leipzig", "Eintracht Frankfurt", "VfB Stuttgart", "Mainz 05", 
        "Augsburg", "Werder Bremen", "Wolfsburg", "Bochum", "TSG Hoffenheim", 
        "FC Heidenheim", "Borussia M.Gladbach", "FC Cologne", "Union Berlin", "Hamburger SV"
    ]
    
    filtered_v5 = [rec for rec in v5_data if rec['team'] in b1_teams]
    for idx, rec in enumerate(filtered_v5):
        rec['rank'] = idx + 1
        
    v5_json = json.dumps(filtered_v5)
    
    # 1. Inject window.predictions_v5_m1_4 = [...]
    js_var = f"window.predictions_v5_m1_4 = {v5_json};\n"
    if "window.predictions_v5_m1_4 =" not in html:
        html = html.replace("window.predictions_v6_2stage =", js_var + "        window.predictions_v6_2stage =")
    else:
        pattern = r"window\.predictions_v5_m1_4 = \[.*?\];"
        html = re.sub(pattern, f"window.predictions_v5_m1_4 = {v5_json};", html, flags=re.DOTALL)
        
    # 2. Update renderV5ComplexityTable JS function
    js_render_func = """
        function renderV5ComplexityTable() {
            const tbody = document.getElementById("v5-complexity-tbody");
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
    
    if "function renderV5ComplexityTable" not in html:
        html = html.replace("function renderV4ComplexityTable", js_render_func + "\n        function renderV4ComplexityTable")
    else:
        # Replace existing function
        pattern = r"function renderV5ComplexityTable\(\) \{.*?\n        \}"
        html = re.sub(pattern, js_render_func.strip(), html, flags=re.DOTALL)
        
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Updated dashboard with real Matchday 1-4 Model v5 predictions!")

if __name__ == "__main__":
    compile_m1_4_real_dashboard()
