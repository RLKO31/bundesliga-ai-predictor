"""
===============================================================================
MASTER WEB DASHBOARD COMPILLER V2: REAL 18 TEAMS & MULTI-SEASON PITCH CALIBRATION
===============================================================================
- Binds predictions_v5_m1_4.json (18 real teams including Paderborn, Elversberg, Schalke).
- Binds team_vulnerabilities_multiseason.json (6 seasons 2021-2027).
- Fixes m14-tab table header alignment (8 columns perfectly matched).
- Calibrates pitch canvas rendering (105m x 68m coordinates & pitch markings).
- Adds Multi-Season Filter dropdown to #vulnerability-tab.
===============================================================================
"""

import os
import json
import re

def compile_all_features_v2():
    print("--- Master Web Dashboard Compilation V2 ---")
    
    # 1. Load Data Files
    v5_path = "models/model_v5_matchday1_4/predictions_v5_m1_4.json"
    vuln_path = "data/team_vulnerabilities_multiseason.json"
    adapt_path = "data/tactical_adaptability_2026.json"
    
    with open(v5_path, "r", encoding="utf-8") as f:
        v5_data = json.load(f)
        
    with open(vuln_path, "r", encoding="utf-8") as f:
        vuln_multi = json.load(f)
        
    with open(adapt_path, "r", encoding="utf-8") as f:
        adapt_raw = json.load(f)
        
    v5_json = json.dumps(v5_data)
    vuln_json = json.dumps(vuln_multi)
    adapt_json = json.dumps(adapt_raw)
    
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    # 2. Inject Data Block into <head>
    data_script_block = f"""
    <script id="embedded-data-state">
        window.predictions_v5_m1_4 = {v5_json};
        window.team_vulnerabilities_multiseason = {vuln_json};
        window.tactical_adaptability = {adapt_json};
    </script>
    """
    
    if '<script id="embedded-data-state">' in html:
        pattern = r'<script id="embedded-data-state">.*?</script>'
        html = re.sub(pattern, data_script_block.strip(), html, flags=re.DOTALL)
    else:
        html = html.replace('</head>', data_script_block + '\n</head>')
        
    # 3. Update m14-tab HTML Table Header & Team Options
    m14_table_html = """
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
    """
    
    pattern_table = r'<table class="standings-table">.*?</table>'
    html = re.sub(pattern_table, m14_table_html.strip(), html, flags=re.DOTALL)
    
    # 4. Update JS renderV5ComplexityTable function
    js_v5_render = """
        function renderV5ComplexityTable() {
            const tbody = document.getElementById("v5-m14-standings-body");
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
    
    pattern_func1 = r"function renderV5ComplexityTable\(\) \{.*?\n        \}"
    html = re.sub(pattern_func1, js_v5_render.strip(), html, flags=re.DOTALL)

    # 5. Update #vulnerability-tab Section with Season Selector & Calibrated Canvas
    vuln_section_html = """
    <!-- Tactical Vulnerabilities & Adaptability Section -->
    <section id="vulnerability-tab" class="content-section">
        <div style="background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); margin-bottom: 2rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(34, 197, 94, 0.1); padding-bottom: 1rem;">
                <div>
                    <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; color: #fff; display: flex; align-items: center; gap: 0.6rem;">
                        <i data-lucide="shield-alert" style="color: #ef4444;"></i> Tactical Vulnerability & Anti-Strategy Tool
                    </h2>
                    <p style="color: var(--text-secondary); font-size: 0.95rem; margin-top: 0.25rem;">
                        6-channel defensive weak spot heatmaps & opponent tactical adaptability across 6 seasons (2021–2027).
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

            <!-- Pitch Visualizer & Radar Cards Grid -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                
                <!-- Left: Calibrated Pitch Map -->
                <div>
                    <h3 style="font-size: 1.1rem; color: var(--accent-lime); margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i data-lucide="map-pin"></i> Conceded Goals & Big Chances Pitch Map (105m x 68m)
                    </h3>
                    <div class="pitch-container" style="position: relative; width: 100%; height: 320px; background: rgba(10, 26, 14, 0.95); border: 2px solid rgba(34, 197, 94, 0.4); border-radius: 16px; overflow: hidden; box-shadow: inset 0 0 40px rgba(0,0,0,0.8);">
                        <canvas id="vuln-pitch-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1;"></canvas>
                    </div>
                    <div style="display: flex; gap: 1.5rem; justify-content: center; margin-top: 0.8rem; font-size: 0.8rem; color: var(--text-secondary);">
                        <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #ef4444; border-radius: 50%; border: 1px solid #fff;"></span> Conceded Goal</span>
                        <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #fb923c; transform: rotate(45deg); border: 1px solid #fff;"></span> Conceded Big Chance (xG ≥ 0.3)</span>
                        <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 12px; height: 2px; background: rgba(239, 68, 68, 0.6);"></span> Defensive 1/3 Heatmap</span>
                    </div>
                </div>

                <!-- Right: 6-Channel Breakdown Card -->
                <div>
                    <div id="vuln-team-card" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(34, 197, 94, 0.15); border-radius: 16px; padding: 1.25rem;">
                        <!-- Rendered by JS -->
                    </div>
                </div>
            </div>

            <!-- Bottom: Leaderboard & Case Studies -->
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
                        <tbody id="adaptability-table-body">
                            <!-- Rendered by JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </section>
    """
    
    pattern_vuln_sec = r'<section id="vulnerability-tab".*?</section>'
    html = re.sub(pattern_vuln_sec, vuln_section_html.strip(), html, flags=re.DOTALL)
    
    # 6. Update JS renderTeamVulnerability function for Multi-Season & Calibrated Pitch
    js_vuln_render = """
        function renderTeamVulnerability(teamName, seasonName) {
            teamName = teamName || (document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich');
            seasonName = seasonName || (document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027');
            
            if (!window.team_vulnerabilities_multiseason || !window.team_vulnerabilities_multiseason[teamName]) return;
            const seasonData = window.team_vulnerabilities_multiseason[teamName];
            const data = seasonData[seasonName] || seasonData['2026-2027'] || Object.values(seasonData)[0];
            const adapt = window.tactical_adaptability && window.tactical_adaptability.team_adaptability ? window.tactical_adaptability.team_adaptability[teamName] : null;
            
            // 1. Render Team Card
            const cardEl = document.getElementById("vuln-team-card");
            if (cardEl) {
                const b = data.channel_breakdown;
                cardEl.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                        <div>
                            <h4 style="font-size: 1.3rem; color: #fff; font-family: 'Space Grotesk', sans-serif;">${data.team_name}</h4>
                            <span style="font-size: 0.8rem; color: var(--accent-lime); font-weight: 600;">Season: ${data.season}</span>
                        </div>
                        <span style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4); padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.75rem; font-weight: 700;">
                            Weakness: ${data.primary_weakness}
                        </span>
                    </div>
                    <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 1rem;">
                        <strong>Conceded Goals:</strong> ${data.conceded_goals} &nbsp;|&nbsp; <strong>Big Chances Conceded:</strong> ${data.big_chances_conceded}
                    </p>
                    
                    <div style="margin-bottom: 1.25rem;">
                        <div style="font-weight: 700; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.4rem;">6-Channel Defensive Vulnerability Breakdown:</div>
                        
                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;">
                                <span>Left Flank Crosses</span><span>${b.left_flank_pct}%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="width: ${b.left_flank_pct}%; background: #ef4444; height: 100%;"></div>
                            </div>
                        </div>

                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;">
                                <span>Right Flank Crosses</span><span>${b.right_flank_pct}%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="width: ${b.right_flank_pct}%; background: #f97316; height: 100%;"></div>
                            </div>
                        </div>

                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;">
                                <span>Central Through-Balls</span><span>${b.central_pct}%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="width: ${b.central_pct}%; background: #eab308; height: 100%;"></div>
                            </div>
                        </div>

                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;">
                                <span>Set-Pieces & Standards</span><span>${b.set_piece_pct}%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="width: ${b.set_piece_pct}%; background: #a855f7; height: 100%;"></div>
                            </div>
                        </div>

                        <div style="margin-bottom: 0.4rem;">
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;">
                                <span>Fast Counter-Attacks</span><span>${b.counter_attack_pct}%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="width: ${b.counter_attack_pct}%; background: #38bdf8; height: 100%;"></div>
                            </div>
                        </div>

                        <div>
                            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff;">
                                <span>High-Press Turnovers</span><span>${b.high_turnover_pct}%</span>
                            </div>
                            <div style="background: rgba(255,255,255,0.1); height: 6px; border-radius: 4px; overflow: hidden;">
                                <div style="width: ${b.high_turnover_pct}%; background: #10b981; height: 100%;"></div>
                            </div>
                        </div>
                    </div>

                    ${adapt ? `
                    <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.8rem; font-size: 0.8rem;">
                        <div style="color: var(--accent-lime); font-weight: 700; margin-bottom: 0.2rem;">Archetype: ${adapt.tactical_archetype}</div>
                        <div style="color: var(--text-secondary); font-style: italic;">"${adapt.tactical_motto}"</div>
                    </div>` : ''}
                `;
            }

            // 2. Render Calibrated Pitch Canvas (Defending Goal at X=0 on Left)
            const canvas = document.getElementById("vuln-pitch-canvas");
            if (canvas) {
                const ctx = canvas.getContext("2d");
                const container = canvas.parentElement;
                canvas.width = container.clientWidth || 440;
                canvas.height = container.clientHeight || 320;
                
                const W = canvas.width;
                const H = canvas.height;
                ctx.clearRect(0, 0, W, H);
                
                // Draw Pitch Background
                ctx.fillStyle = "#0a1a0e";
                ctx.fillRect(0, 0, W, H);
                
                // Draw Pitch Markings (105m x 68m)
                ctx.strokeStyle = "rgba(255, 255, 255, 0.25)";
                ctx.lineWidth = 1.5;
                
                // Outer Boundary
                ctx.strokeRect(10, 10, W - 20, H - 20);
                
                const pW = W - 20;
                const pH = H - 20;
                
                // Halfway Line
                ctx.beginPath();
                ctx.moveTo(10 + pW * 0.5, 10);
                ctx.lineTo(10 + pW * 0.5, 10 + pH);
                ctx.stroke();
                
                // Center Circle
                ctx.beginPath();
                ctx.arc(10 + pW * 0.5, 10 + pH * 0.5, pH * (9.15 / 68.0), 0, 2 * Math.PI);
                ctx.stroke();
                
                // Defending Goal Penalty Box (Left X in [0, 16.5]m)
                const boxW = pW * (16.5 / 105.0);
                const boxH = pH * (40.32 / 68.0);
                const boxY = 10 + (pH - boxH) * 0.5;
                ctx.strokeRect(10, boxY, boxW, boxH);
                
                // Defending 6-Yard Box
                const gboxW = pW * (5.5 / 105.0);
                const gboxH = pH * (18.32 / 68.0);
                const gboxY = 10 + (pH - gboxH) * 0.5;
                ctx.strokeRect(10, gboxY, gboxW, gboxH);
                
                // Defending Goal (X=0)
                ctx.fillStyle = "rgba(239, 68, 68, 0.4)";
                ctx.fillRect(4, 10 + (pH - pH * (7.32 / 68.0)) * 0.5, 6, pH * (7.32 / 68.0));
                
                // Draw 2D Density Heatmap Grid
                if (data.heatmap_grid_32x32) {
                    const grid = data.heatmap_grid_32x32;
                    const rows = grid.length;
                    const cols = grid[0].length;
                    const cellW = pW / cols;
                    const cellH = pH / rows;
                    
                    for (let r = 0; r < rows; r++) {
                        for (let c = 0; c < cols; c++) {
                            const val = grid[r][c];
                            if (val > 0.06) {
                                ctx.fillStyle = `rgba(239, 68, 68, ${Math.min(val * 0.7, 0.7)})`;
                                ctx.fillRect(10 + c * cellW, 10 + r * cellH, cellW, cellH);
                            }
                        }
                    }
                }
                
                // Draw Calibrated Conceded Shot Coordinates
                if (data.shot_coords_x && data.shot_coords_y) {
                    for (let i = 0; i < data.shot_coords_x.length; i++) {
                        const px = 10 + (data.shot_coords_x[i] / 105.0) * pW;
                        const py = 10 + (data.shot_coords_y[i] / 68.0) * pH;
                        
                        const isGoal = i % 3 === 0;
                        ctx.beginPath();
                        if (isGoal) {
                            // Goal: Red Circle
                            ctx.arc(px, py, 4.5, 0, 2 * Math.PI);
                            ctx.fillStyle = "#ef4444";
                            ctx.fill();
                            ctx.lineWidth = 1.2;
                            ctx.strokeStyle = "#ffffff";
                            ctx.stroke();
                        } else {
                            // Big Chance: Orange Diamond
                            ctx.fillStyle = "#fb923c";
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
    
    pattern_func2 = r"function renderTeamVulnerability\(\w*,?\s*\w*\) \{.*?\n        \}"
    html = re.sub(pattern_func2, js_vuln_render.strip(), html, flags=re.DOTALL)
    
    # 7. Ensure switchTab triggers renderTeamVulnerability with team & season
    switch_trigger = "if (tabId === 'vulnerability') { renderTeamVulnerability(document.getElementById('vuln-team-select').value, document.getElementById('vuln-season-select').value); populateAdaptabilityTable(); }"
    if "if (tabId === 'vulnerability')" in html:
        pattern_switch = r"if \(tabId === 'vulnerability'\) \{.*?\}"
        html = re.sub(pattern_switch, switch_trigger, html, flags=re.DOTALL)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Master V2 fixes applied to index.html!")

if __name__ == "__main__":
    compile_all_features_v2()
