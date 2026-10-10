"""
===============================================================================
MASTER WEB DASHBOARD COMPILER: REAL DFL/UNDERSTAT TACTICAL ENGINE
MULTI-SEASON (2021-2027) OFFENSE & DEFENSE SPATIAL PITCH CALIBRATION
===============================================================================
- Binds authentic multi-season chance creation and concession dataset (2021-2027).
- Interactive Defense (Conceded Weaknesses) vs. Offense (Created Threats) modes.
- Filter by: All Shots, Goals Only, Big Chances (xG >= 0.3), Open Play, Set-Pieces.
- Calibrated 105m x 68m pitch with orientation indicators and live mouse hover tooltips.
- Dynamic Season Team Selector based on historical Bundesliga participation.
- Leaderboard table with real tactical archetypes, plan adherence, and exploitation indexes.
===============================================================================
"""

import os
import json
import re

def compile_all_features():
    print("--- Master Web Dashboard Compilation: Authentic Tactical Engine ---")
    
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
        
    v5_json = json.dumps(v5_data, separators=(',', ':'))
    vuln_json = json.dumps(vuln_multi, separators=(',', ':'))
    adapt_json = json.dumps(adapt_raw, separators=(',', ':'))
    
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
        html = re.sub(pattern, lambda m: data_script_block.strip(), html, flags=re.DOTALL)
    else:
        html = html.replace('</head>', data_script_block + '\n</head>')

    # 3. Inject CSS for Filter Pills and Tooltips if missing
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

    # 4. Inject Rich #vulnerability-tab Section
    vuln_section_html = """
    <!-- Tactical Vulnerabilities & Threat Mapping Section -->
    <section id="vulnerability-tab" class="content-section">
        <div style="background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); margin-bottom: 2rem;">
            
            <!-- Header & Season/Team Controls -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(34, 197, 94, 0.1); padding-bottom: 1.25rem;">
                <div>
                    <h2 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.8rem; color: #fff; display: flex; align-items: center; gap: 0.6rem;">
                        <i data-lucide="shield-alert" style="color: #ef4444;"></i> Tactical Vulnerability & Threat Mapping Engine
                    </h2>
                    <p style="color: var(--text-secondary); font-size: 0.95rem; margin-top: 0.25rem;">
                        Authentic DFL & Understat match events: Conceded vulnerabilities vs. created attacking threats across 6 seasons (2021–2027).
                    </p>
                </div>
                
                <div style="display: flex; gap: 1rem; flex-wrap: wrap; align-items: center;">
                    <!-- Season Dropdown -->
                    <div>
                        <label for="vuln-season-select" style="font-size: 0.82rem; color: var(--text-secondary); font-weight: 600; margin-right: 0.4rem;">Season:</label>
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
                        <label for="vuln-team-select" style="font-size: 0.82rem; color: var(--text-secondary); font-weight: 600; margin-right: 0.4rem;">Team:</label>
                        <select id="vuln-team-select" onchange="renderTeamVulnerability(this.value, document.getElementById('vuln-season-select').value)" style="background: rgba(4, 9, 5, 0.95); color: #fff; border: 1px solid var(--accent-green); padding: 0.5rem 1rem; border-radius: 10px; font-weight: 600; cursor: pointer; font-size: 0.88rem; outline: none;">
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
                </div>
            </div>

            <!-- Perspective Mode Switcher: Defense (Conceded) vs Offense (Created) -->
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.5rem; background: rgba(255, 255, 255, 0.02); padding: 0.85rem 1.25rem; border-radius: 14px; border: 1px solid rgba(255, 255, 255, 0.06);">
                <div style="display: flex; gap: 0.6rem; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600; margin-right: 0.4rem;">Tactical Perspective:</span>
                    <button id="btn-vuln-mode-def" class="vuln-mode-btn" onclick="setVulnMode('defense')" style="border: 1px solid var(--accent-loss); background: rgba(239, 68, 68, 0.18); color: #f87171;">
                        <i data-lucide="shield" size="16"></i> Defensive Vulnerability (Conceded)
                    </button>
                    <button id="btn-vuln-mode-off" class="vuln-mode-btn" onclick="setVulnMode('offense')" style="border: 1px solid rgba(255,255,255,0.15); background: transparent; color: var(--text-secondary);">
                        <i data-lucide="swords" size="16"></i> Attacking Threat (Created)
                    </button>
                </div>

                <!-- Event Filter Pills -->
                <div style="display: flex; gap: 0.45rem; align-items: center; flex-wrap: wrap;">
                    <span style="font-size: 0.8rem; color: var(--text-secondary); margin-right: 0.25rem;">Filter:</span>
                    <button class="vuln-filter-pill active" onclick="setVulnFilter('all', this)">All Actions</button>
                    <button class="vuln-filter-pill" onclick="setVulnFilter('goals', this)">⚽ Goals Only</button>
                    <button class="vuln-filter-pill" onclick="setVulnFilter('big', this)">🔶 Big Chances (xG ≥ 0.3)</button>
                    <button class="vuln-filter-pill" onclick="setVulnFilter('open', this)">🎯 Open Play</button>
                    <button class="vuln-filter-pill" onclick="setVulnFilter('setpiece', this)">🚩 Set-Pieces</button>
                </div>
            </div>

            <!-- Pitch Visualizer & Radar Cards Grid -->
            <div style="display: grid; grid-template-columns: 1.15fr 0.85fr; gap: 2rem; margin-bottom: 2rem;">
                
                <!-- Left: Interactive Calibrated Pitch Map -->
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
                        <h3 id="vuln-pitch-title" style="font-size: 1.1rem; color: var(--accent-lime); display: flex; align-items: center; gap: 0.5rem; margin: 0;">
                            <i data-lucide="map-pin"></i> Conceded Goals & Big Chances Pitch Map (105m x 68m)
                        </h3>
                        <!-- Quick KPI Pills -->
                        <div id="vuln-kpi-strip" style="display: flex; gap: 0.6rem; font-size: 0.78rem; font-weight: 700;"></div>
                    </div>
                    
                    <div class="pitch-container" style="position: relative; width: 100%; height: 350px; background: rgba(5, 18, 9, 0.98); border: 2px solid rgba(34, 197, 94, 0.4); border-radius: 16px; overflow: hidden; box-shadow: inset 0 0 50px rgba(0,0,0,0.85);">
                        <canvas id="vuln-pitch-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; cursor: crosshair;"></canvas>
                        <!-- Interactive Tooltip -->
                        <div id="vuln-pitch-tooltip" style="position: absolute; display: none; z-index: 10; pointer-events: none; background: rgba(9, 20, 12, 0.95); border: 1px solid var(--accent-lime); padding: 0.5rem 0.75rem; border-radius: 8px; font-size: 0.75rem; color: #fff; box-shadow: 0 4px 20px rgba(0,0,0,0.6); transform: translate(-50%, -120%); backdrop-filter: blur(8px);"></div>
                    </div>
                    
                    <!-- Pitch Legend & Orientation Indicator -->
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.8rem; font-size: 0.8rem; color: var(--text-secondary); flex-wrap: wrap; gap: 0.5rem;">
                        <div style="display: flex; gap: 1.25rem;">
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #ef4444; border-radius: 50%; border: 1px solid #fff; box-shadow: 0 0 6px #ef4444;"></span> Goal</span>
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 10px; height: 10px; background: #fb923c; transform: rotate(45deg); border: 1px solid #fff;"></span> Big Chance (xG ≥ 0.3)</span>
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 8px; height: 8px; background: #38bdf8; border-radius: 50%;"></span> Other Shot</span>
                            <span style="display: flex; align-items: center; gap: 0.4rem;"><span style="width: 14px; height: 4px; background: rgba(239, 68, 68, 0.6); border-radius: 2px;"></span> xG Density Heatmap</span>
                        </div>
                        <div id="vuln-orientation-label" style="font-weight: 600; color: #9ca3af; font-size: 0.78rem;"></div>
                    </div>
                </div>

                <!-- Right: 6-Channel Breakdown & Archetype Card -->
                <div>
                    <div id="vuln-team-card" style="background: rgba(255,255,255,0.02); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 16px; padding: 1.35rem; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
                        <!-- Rendered by JS -->
                    </div>
                </div>
            </div>

            <!-- Bottom: Leaderboard & Case Studies -->
            <div style="margin-top: 2rem; border-top: 1px solid rgba(34, 197, 94, 0.1); padding-top: 1.5rem;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem;">
                    <h3 style="font-size: 1.2rem; color: #fff; display: flex; align-items: center; gap: 0.5rem; margin: 0;">
                        <i data-lucide="bar-chart-3" style="color: var(--accent-lime);"></i> Bundesliga Opponent Adaptability Leaderboard
                    </h3>
                    <span style="font-size: 0.8rem; color: var(--text-secondary);">Click any team to inspect full tactical profile</span>
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
    html = re.sub(pattern_vuln_sec, lambda m: vuln_section_html.strip(), html, flags=re.DOTALL)

    # 5. Inject Master JavaScript State & Rendering Functions
    js_vuln_master = """
        window.currentVulnMode = 'defense';
        window.currentVulnFilter = 'all';
        window.vulnPlottedShots = [];

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

        function setVulnMode(mode) {
            window.currentVulnMode = mode;
            const btnDef = document.getElementById('btn-vuln-mode-def');
            const btnOff = document.getElementById('btn-vuln-mode-off');
            if (btnDef && btnOff) {
                if (mode === 'defense') {
                    btnDef.style.background = 'rgba(239, 68, 68, 0.18)';
                    btnDef.style.borderColor = 'var(--accent-loss)';
                    btnDef.style.color = '#f87171';
                    btnOff.style.background = 'transparent';
                    btnOff.style.borderColor = 'rgba(255,255,255,0.15)';
                    btnOff.style.color = 'var(--text-secondary)';
                } else {
                    btnOff.style.background = 'rgba(34, 197, 94, 0.18)';
                    btnOff.style.borderColor = 'var(--accent-green)';
                    btnOff.style.color = 'var(--accent-lime)';
                    btnDef.style.background = 'transparent';
                    btnDef.style.borderColor = 'rgba(255,255,255,0.15)';
                    btnDef.style.color = 'var(--text-secondary)';
                }
            }
            renderTeamVulnerability();
        }

        function setVulnFilter(filter, btn) {
            window.currentVulnFilter = filter;
            document.querySelectorAll('.vuln-filter-pill').forEach(el => el.classList.remove('active'));
            if (btn) btn.classList.add('active');
            renderTeamVulnerability();
        }

        function renderTeamVulnerability(teamName, seasonName) {
            teamName = teamName || (document.getElementById('vuln-team-select') ? document.getElementById('vuln-team-select').value : 'Bayern Munich');
            seasonName = seasonName || (document.getElementById('vuln-season-select') ? document.getElementById('vuln-season-select').value : '2026-2027');
            
            if (!window.team_vulnerabilities_multiseason) return;
            const root = window.team_vulnerabilities_multiseason;
            const teamsObj = root.teams || root;
            if (!teamsObj[teamName]) return;
            
            const seasonData = teamsObj[teamName][seasonName] || Object.values(teamsObj[teamName])[0];
            if (!seasonData) return;
            
            const mode = window.currentVulnMode || 'defense';
            const mData = seasonData[mode] || seasonData;
            const prof = seasonData.tactical_profile || {};
            const filter = window.currentVulnFilter || 'all';

            // 1. Update Title & Header KPIs
            const titleEl = document.getElementById("vuln-pitch-title");
            if (titleEl) {
                titleEl.innerHTML = mode === 'defense' ? 
                    `<i data-lucide="shield-alert" style="color: #ef4444;"></i> Conceded Weakness Pitch Map (105m x 68m)` :
                    `<i data-lucide="crosshair" style="color: var(--accent-lime);"></i> Created Attacking Threat Pitch Map (105m x 68m)`;
            }

            const kpiEl = document.getElementById("vuln-kpi-strip");
            if (kpiEl) {
                if (mode === 'defense') {
                    kpiEl.innerHTML = `
                        <span style="background: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Goals Conceded: ${mData.conceded_goals}</span>
                        <span style="background: rgba(251, 146, 60, 0.15); color: #fb923c; border: 1px solid rgba(251,146,60,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Big Chances: ${mData.big_chances_conceded}</span>
                        <span style="background: rgba(255,255,255,0.05); color: #9ca3af; border: 1px solid rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 6px;">xGA: ${mData.xg_conceded || 'N/A'}</span>
                    `;
                } else {
                    kpiEl.innerHTML = `
                        <span style="background: rgba(34, 197, 94, 0.15); color: var(--accent-lime); border: 1px solid rgba(34,197,94,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Goals Scored: ${mData.goals_scored}</span>
                        <span style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56,189,248,0.3); padding: 0.2rem 0.5rem; border-radius: 6px;">Big Chances: ${mData.big_chances_created}</span>
                        <span style="background: rgba(255,255,255,0.05); color: #9ca3af; border: 1px solid rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 6px;">xG: ${mData.xg_created || 'N/A'}</span>
                    `;
                }
            }

            const orientEl = document.getElementById("vuln-orientation-label");
            if (orientEl) {
                orientEl.innerHTML = mode === 'defense' ?
                    `<span style="color: #f87171;">🛡️ OUR DEFENDING GOAL (Left [X=0m])</span> &nbsp;⬅️ Opponent Infiltration` :
                    `<span style="color: var(--accent-lime);">🎯 TARGET OPPONENT GOAL (Right [X=105m])</span> &nbsp;➡️ Attack Direction`;
            }

            // 2. Render Team Card
            const cardEl = document.getElementById("vuln-team-card");
            if (cardEl) {
                const b = mData.channel_breakdown || {};
                const topLabel = mode === 'defense' ? 'Primary Vulnerability' : 'Primary Weapon';
                const topVal = mode === 'defense' ? mData.primary_weakness : mData.primary_strength;
                const topBadgeColor = mode === 'defense' ? 'background: rgba(239, 68, 68, 0.2); color: #f87171; border-color: rgba(239, 68, 68, 0.4);' : 'background: rgba(34, 197, 94, 0.2); color: var(--accent-lime); border-color: rgba(34, 197, 94, 0.4);';

                cardEl.innerHTML = `
                    <div>
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
                            <div>
                                <h4 style="font-size: 1.35rem; color: #fff; font-family: 'Space Grotesk', sans-serif;">${seasonData.team_name}</h4>
                                <span style="font-size: 0.8rem; color: var(--accent-lime); font-weight: 600;">Season: ${seasonData.season}</span>
                            </div>
                            <span style="border: 1px solid; padding: 0.25rem 0.65rem; border-radius: 6px; font-size: 0.78rem; font-weight: 700; ${topBadgeColor}">
                                ${topLabel}: ${topVal || 'Balanced'}
                            </span>
                        </div>
                        
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; background: rgba(0,0,0,0.25); padding: 0.75rem; border-radius: 10px; margin-bottom: 1.25rem; font-size: 0.82rem;">
                            <div><span style="color: var(--text-secondary);">${mode === 'defense' ? 'Conceded Goals:' : 'Goals Scored:'}</span> <strong style="color: #fff;">${mode === 'defense' ? mData.conceded_goals : mData.goals_scored}</strong></div>
                            <div><span style="color: var(--text-secondary);">${mode === 'defense' ? 'Shots Conceded:' : 'Shots Created:'}</span> <strong style="color: #fff;">${mode === 'defense' ? mData.total_shots_conceded : mData.total_shots_created}</strong></div>
                            <div><span style="color: var(--text-secondary);">${mode === 'defense' ? 'Total xGA:' : 'Total xG:'}</span> <strong style="color: var(--accent-lime);">${mode === 'defense' ? mData.xg_conceded : mData.xg_created}</strong></div>
                            <div><span style="color: var(--text-secondary);">Conversion Rate:</span> <strong style="color: #38bdf8;">${mData.conversion_rate_pct}%</strong></div>
                        </div>
                        
                        <div style="margin-bottom: 1.25rem;">
                            <div style="font-weight: 700; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.6rem;">6-Channel Tactical Action Profile:</div>
                            
                            <div style="margin-bottom: 0.45rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff; margin-bottom: 0.15rem;">
                                    <span>Left Flank Crosses</span><span style="font-weight: 700;">${b.left_flank_pct}%</span>
                                </div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;">
                                    <div style="width: ${b.left_flank_pct}%; background: #ef4444; height: 100%;"></div>
                                </div>
                            </div>

                            <div style="margin-bottom: 0.45rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff; margin-bottom: 0.15rem;">
                                    <span>Right Flank Crosses</span><span style="font-weight: 700;">${b.right_flank_pct}%</span>
                                </div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;">
                                    <div style="width: ${b.right_flank_pct}%; background: #f97316; height: 100%;"></div>
                                </div>
                            </div>

                            <div style="margin-bottom: 0.45rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff; margin-bottom: 0.15rem;">
                                    <span>Central Combinations</span><span style="font-weight: 700;">${b.central_pct}%</span>
                                </div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;">
                                    <div style="width: ${b.central_pct}%; background: #eab308; height: 100%;"></div>
                                </div>
                            </div>

                            <div style="margin-bottom: 0.45rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff; margin-bottom: 0.15rem;">
                                    <span>Set-Pieces & Standards</span><span style="font-weight: 700;">${b.set_piece_pct}%</span>
                                </div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;">
                                    <div style="width: ${b.set_piece_pct}%; background: #a855f7; height: 100%;"></div>
                                </div>
                            </div>

                            <div style="margin-bottom: 0.45rem;">
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff; margin-bottom: 0.15rem;">
                                    <span>Fast Counter-Attacks</span><span style="font-weight: 700;">${b.counter_attack_pct}%</span>
                                </div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;">
                                    <div style="width: ${b.counter_attack_pct}%; background: #38bdf8; height: 100%;"></div>
                                </div>
                            </div>

                            <div>
                                <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #fff; margin-bottom: 0.15rem;">
                                    <span>High-Press Turnovers</span><span style="font-weight: 700;">${b.high_turnover_pct}%</span>
                                </div>
                                <div style="background: rgba(255,255,255,0.08); height: 6px; border-radius: 4px; overflow: hidden;">
                                    <div style="width: ${b.high_turnover_pct}%; background: #10b981; height: 100%;"></div>
                                </div>
                            </div>
                        </div>
                    </div>

                    ${prof.archetype ? `
                    <div style="border-top: 1px solid rgba(255,255,255,0.1); padding-top: 0.85rem; font-size: 0.8rem; margin-top: auto;">
                        <div style="color: var(--accent-lime); font-weight: 700; margin-bottom: 0.25rem;">Archetype: ${prof.archetype}</div>
                        <div style="color: var(--text-secondary); font-style: italic;">"${prof.motto}"</div>
                    </div>` : ''}
                `;
            }

            // 3. Render Pitch Canvas (105m x 68m)
            const canvas = document.getElementById("vuln-pitch-canvas");
            if (canvas) {
                const ctx = canvas.getContext("2d");
                const container = canvas.parentElement;
                canvas.width = container.clientWidth || 460;
                canvas.height = container.clientHeight || 350;
                
                const W = canvas.width;
                const H = canvas.height;
                ctx.clearRect(0, 0, W, H);
                
                // Deep Turf Background
                ctx.fillStyle = "#051308";
                ctx.fillRect(0, 0, W, H);
                
                // Pitch Margins
                const pad = 12;
                const pW = W - pad * 2;
                const pH = H - pad * 2;
                
                // Outer Boundary
                ctx.strokeStyle = "rgba(255, 255, 255, 0.28)";
                ctx.lineWidth = 1.5;
                ctx.strokeRect(pad, pad, pW, pH);
                
                // Halfway Line
                ctx.beginPath();
                ctx.moveTo(pad + pW * 0.5, pad);
                ctx.lineTo(pad + pW * 0.5, pad + pH);
                ctx.stroke();
                
                // Center Circle
                ctx.beginPath();
                ctx.arc(pad + pW * 0.5, pad + pH * 0.5, pH * (9.15 / 68.0), 0, 2 * Math.PI);
                ctx.stroke();
                
                // Center Spot
                ctx.fillStyle = "rgba(255, 255, 255, 0.5)";
                ctx.beginPath();
                ctx.arc(pad + pW * 0.5, pad + pH * 0.5, 2.5, 0, 2 * Math.PI);
                ctx.fill();

                // Pitch Lanes (Subtle Dashed Guidelines)
                ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
                ctx.setLineDash([4, 6]);
                // Left Wing lane (14m)
                ctx.beginPath(); ctx.moveTo(pad, pad + pH * (14.0/68.0)); ctx.lineTo(pad + pW, pad + pH * (14.0/68.0)); ctx.stroke();
                // Right Wing lane (54m)
                ctx.beginPath(); ctx.moveTo(pad, pad + pH * (54.0/68.0)); ctx.lineTo(pad + pW, pad + pH * (54.0/68.0)); ctx.stroke();
                ctx.setLineDash([]); // Reset dash

                // Goal Markings Based on Perspective
                ctx.strokeStyle = "rgba(255, 255, 255, 0.32)";
                ctx.lineWidth = 1.5;

                if (mode === 'defense') {
                    // Defending Goal on the LEFT (X = 0)
                    const boxW = pW * (16.5 / 105.0);
                    const boxH = pH * (40.32 / 68.0);
                    const boxY = pad + (pH - boxH) * 0.5;
                    ctx.strokeRect(pad, boxY, boxW, boxH);
                    
                    const gboxW = pW * (5.5 / 105.0);
                    const gboxH = pH * (18.32 / 68.0);
                    const gboxY = pad + (pH - gboxH) * 0.5;
                    ctx.strokeRect(pad, gboxY, gboxW, gboxH);
                    
                    // Penalty Spot (11m)
                    const pSpotX = pad + pW * (11.0 / 105.0);
                    const pSpotY = pad + pH * 0.5;
                    ctx.fillStyle = "#fff";
                    ctx.beginPath(); ctx.arc(pSpotX, pSpotY, 2.5, 0, 2*Math.PI); ctx.fill();
                    
                    // Penalty Arc
                    ctx.beginPath();
                    ctx.arc(pSpotX, pSpotY, pH * (9.15 / 68.0), -0.65, 0.65);
                    ctx.stroke();

                    // Defending Goal Mesh (Left)
                    const goalH = pH * (7.32 / 68.0);
                    const goalY = pad + (pH - goalH) * 0.5;
                    ctx.fillStyle = "rgba(239, 68, 68, 0.35)";
                    ctx.fillRect(pad - 6, goalY, 6, goalH);
                    ctx.strokeStyle = "#ef4444";
                    ctx.strokeRect(pad - 6, goalY, 6, goalH);

                } else {
                    // Attacking Goal on the RIGHT (X = 105m)
                    const boxW = pW * (16.5 / 105.0);
                    const boxH = pH * (40.32 / 68.0);
                    const boxY = pad + (pH - boxH) * 0.5;
                    ctx.strokeRect(pad + pW - boxW, boxY, boxW, boxH);
                    
                    const gboxW = pW * (5.5 / 105.0);
                    const gboxH = pH * (18.32 / 68.0);
                    const gboxY = pad + (pH - gboxH) * 0.5;
                    ctx.strokeRect(pad + pW - gboxW, gboxY, gboxW, gboxH);
                    
                    // Penalty Spot (11m from right goal)
                    const pSpotX = pad + pW - pW * (11.0 / 105.0);
                    const pSpotY = pad + pH * 0.5;
                    ctx.fillStyle = "#fff";
                    ctx.beginPath(); ctx.arc(pSpotX, pSpotY, 2.5, 0, 2*Math.PI); ctx.fill();
                    
                    // Penalty Arc (curving left)
                    ctx.beginPath();
                    ctx.arc(pSpotX, pSpotY, pH * (9.15 / 68.0), Math.PI - 0.65, Math.PI + 0.65);
                    ctx.stroke();

                    // Target Goal Mesh (Right)
                    const goalH = pH * (7.32 / 68.0);
                    const goalY = pad + (pH - goalH) * 0.5;
                    ctx.fillStyle = "rgba(34, 197, 94, 0.4)";
                    ctx.fillRect(pad + pW, goalY, 6, goalH);
                    ctx.strokeStyle = "var(--accent-lime)";
                    ctx.strokeRect(pad + pW, goalY, 6, goalH);
                }

                // Filter Shots
                const rawShots = mData.shots || [];
                const filteredShots = rawShots.filter(sh => {
                    const isGoal = Array.isArray(sh) ? sh[3] === 1 : sh.is_goal;
                    const xg = Array.isArray(sh) ? sh[2] : sh.xg;
                    const sit = Array.isArray(sh) ? sh[7] : sh.situation;
                    
                    if (filter === 'goals') return isGoal;
                    if (filter === 'big') return xg >= 0.30;
                    if (filter === 'open') return sit === 'OpenPlay';
                    if (filter === 'setpiece') return sit !== 'OpenPlay';
                    return true;
                });

                // 4. Draw 2D Danger Density Heatmap (Gaussian Radial Glow)
                filteredShots.forEach(sh => {
                    const sx = Array.isArray(sh) ? sh[0] : sh.x;
                    const sy = Array.isArray(sh) ? sh[1] : sh.y;
                    const sXg = Array.isArray(sh) ? sh[2] : sh.xg;
                    
                    const px = pad + (sx / 105.0) * pW;
                    const py = pad + (sy / 68.0) * pH;
                    const radius = Math.min(32, Math.max(16, sXg * 50));
                    
                    const grad = ctx.createRadialGradient(px, py, 0, px, py, radius);
                    if (mode === 'defense') {
                        grad.addColorStop(0, `rgba(239, 68, 68, ${Math.min(0.45, sXg * 0.85)})`);
                        grad.addColorStop(1, 'rgba(239, 68, 68, 0)');
                    } else {
                        grad.addColorStop(0, `rgba(34, 197, 94, ${Math.min(0.45, sXg * 0.85)})`);
                        grad.addColorStop(1, 'rgba(34, 197, 94, 0)');
                    }
                    ctx.fillStyle = grad;
                    ctx.beginPath();
                    ctx.arc(px, py, radius, 0, 2 * Math.PI);
                    ctx.fill();
                });

                // 5. Draw Precise Shot Marks & Cache Coordinates for Hover
                window.vulnPlottedShots = [];
                
                filteredShots.forEach(sh => {
                    const sx = Array.isArray(sh) ? sh[0] : sh.x;
                    const sy = Array.isArray(sh) ? sh[1] : sh.y;
                    const sXg = Array.isArray(sh) ? sh[2] : sh.xg;
                    const isGoal = Array.isArray(sh) ? sh[3] === 1 : sh.is_goal;
                    
                    const px = pad + (sx / 105.0) * pW;
                    const py = pad + (sy / 68.0) * pH;
                    
                    window.vulnPlottedShots.push({ px, py, raw: sh });

                    if (isGoal) {
                        // Goal: Glowing Red Circle with White Border
                        ctx.beginPath();
                        ctx.arc(px, py, 5.5, 0, 2 * Math.PI);
                        ctx.fillStyle = "#ef4444";
                        ctx.fill();
                        ctx.lineWidth = 1.6;
                        ctx.strokeStyle = "#ffffff";
                        ctx.stroke();
                        // Inner Dot
                        ctx.beginPath();
                        ctx.arc(px, py, 2, 0, 2 * Math.PI);
                        ctx.fillStyle = "#ffffff";
                        ctx.fill();
                    } else if (sXg >= 0.30) {
                        // Big Chance: Bright Orange Diamond
                        ctx.fillStyle = "#fb923c";
                        ctx.beginPath();
                        ctx.moveTo(px, py - 4.5);
                        ctx.lineTo(px + 4.5, py);
                        ctx.lineTo(px, py + 4.5);
                        ctx.lineTo(px - 4.5, py);
                        ctx.closePath();
                        ctx.fill();
                        ctx.lineWidth = 1.2;
                        ctx.strokeStyle = "#ffffff";
                        ctx.stroke();
                    } else {
                        // Other Shot: Cyan Dot
                        const r = Math.min(4, Math.max(2.5, sXg * 15));
                        ctx.beginPath();
                        ctx.arc(px, py, r, 0, 2 * Math.PI);
                        ctx.fillStyle = "#38bdf8";
                        ctx.fill();
                        ctx.lineWidth = 0.8;
                        ctx.strokeStyle = "rgba(255,255,255,0.7)";
                        ctx.stroke();
                    }
                });
            }

            // Bind Canvas Tooltip Events
            setupCanvasTooltipEvents();
            if (window.lucide) window.lucide.createIcons();
        }

        function setupCanvasTooltipEvents() {
            const canvas = document.getElementById("vuln-pitch-canvas");
            const tooltip = document.getElementById("vuln-pitch-tooltip");
            if (!canvas || !tooltip || canvas.dataset.hasEvents) return;
            canvas.dataset.hasEvents = "true";

            canvas.addEventListener("mousemove", (e) => {
                const rect = canvas.getBoundingClientRect();
                const mx = e.clientX - rect.left;
                const my = e.clientY - rect.top;
                
                let closest = null;
                let minDist = 14;

                (window.vulnPlottedShots || []).forEach(pt => {
                    const dist = Math.hypot(pt.px - mx, pt.py - my);
                    if (dist < minDist) {
                        minDist = dist;
                        closest = pt;
                    }
                });

                if (closest) {
                    const sh = closest.raw;
                    const isGoal = Array.isArray(sh) ? sh[3] === 1 : sh.is_goal;
                    const xg = Array.isArray(sh) ? sh[2] : sh.xg;
                    const min = Array.isArray(sh) ? sh[4] : sh.minute;
                    const player = Array.isArray(sh) ? sh[5] : sh.player;
                    const opp = Array.isArray(sh) ? sh[6] : sh.opponent;
                    const sit = Array.isArray(sh) ? sh[7] : sh.situation;
                    const act = Array.isArray(sh) ? sh[8] : sh.last_action;
                    const ch = Array.isArray(sh) ? sh[9] : sh.channel;

                    const outcomeTag = isGoal ? '<span style="color:#ef4444; font-weight:800;">⚽ GOAL</span>' : (xg >= 0.3 ? '<span style="color:#fb923c; font-weight:700;">🔶 Big Chance</span>' : '<span style="color:#38bdf8;">Shot</span>');

                    tooltip.style.display = "block";
                    tooltip.style.left = closest.px + "px";
                    tooltip.style.top = closest.py + "px";
                    tooltip.innerHTML = `
                        <div style="font-weight:700; margin-bottom:0.2rem; display:flex; justify-content:space-between; gap:0.5rem;">
                            <span>${player} (${min}')</span>
                            <span>${outcomeTag}</span>
                        </div>
                        <div style="color:var(--text-secondary); font-size:0.72rem; line-height:1.3;">
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
    """

    pattern_func2 = r"function renderTeamVulnerability\(\w*,?\s*\w*\) \{.*?\n        \}"
    if re.search(pattern_func2, html, flags=re.DOTALL):
        html = re.sub(pattern_func2, lambda m: js_vuln_master.strip(), html, flags=re.DOTALL)
    else:
        html = html.replace("function drawPitchHeatmapCanvas", js_vuln_master.strip() + "\n        function drawPitchHeatmapCanvas")

    # 6. Ensure switchTab triggers renderTeamVulnerability
    switch_trigger = "if (tabId === 'vulnerability') { updateTeamDropdown(document.getElementById('vuln-season-select').value); renderTeamVulnerability(); populateAdaptabilityTable(); }"
    if "if (tabId === 'vulnerability')" in html:
        pattern_switch = r"if \(tabId === 'vulnerability'\) \{.*?\}"
        html = re.sub(pattern_switch, lambda m: switch_trigger, html, flags=re.DOTALL)

    # 7. Ensure page init initializes the tactical vulnerability engine
    if "updateTeamDropdown('2026-2027')" not in html:
        dom_pattern = r'window\.addEventListener\("DOMContentLoaded",\s*\(\)\s*=>\s*\{'
        dom_replacement = """window.addEventListener("DOMContentLoaded", () => {
            updateTeamDropdown('2026-2027');
            populateAdaptabilityTable('2026-2027');"""
        html = re.sub(dom_pattern, dom_replacement, html)

    # 8. Add resize handler for responsive pitch canvas
    if 'window.addEventListener("resize"' not in html:
        resize_code = """
        window.addEventListener("resize", () => {
            const vulnTab = document.getElementById("vulnerability-tab");
            if (vulnTab && vulnTab.classList.contains("active")) {
                renderTeamVulnerability();
            }
        });
        """
        html = html.replace('</script>\n\n    <!-- Footer', resize_code + '\n    </script>\n\n    <!-- Footer')

    # Write updated index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Master Tactical Vulnerability & Threat engine compiled into index.html!")

if __name__ == "__main__":
    compile_all_features()
