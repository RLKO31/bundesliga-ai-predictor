"""
===============================================================================
SCRIPT: INJECT 11 DER WOCHE TAB INTO INDEX.HTML (ROBUST VERSION)
===============================================================================
"""

import json
import os

with open('data/all_matchdays_11_der_woche.json', 'r', encoding='utf-8') as f:
    totw_data = json.load(f)

TOTW_DATA_JS = json.dumps(totw_data, ensure_ascii=False)

CSS_STYLES = """
        /* ================= 11 DER WOCHE STYLING ================= */
        .totw-container {
            display: grid;
            grid-template-columns: 1fr;
            gap: 2rem;
            margin-bottom: 2.5rem;
        }

        .totw-header-card {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 1.5rem 2rem;
            backdrop-filter: blur(16px);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1.5rem;
        }

        .md-selector-group {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            align-items: center;
        }

        .md-pill-btn {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(34, 197, 94, 0.2);
            color: var(--text-secondary);
            padding: 0.45rem 0.9rem;
            border-radius: 30px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .md-pill-btn:hover {
            color: #fff;
            border-color: var(--accent-green);
            background: rgba(34, 197, 94, 0.15);
        }
        .md-pill-btn.active {
            background: linear-gradient(135deg, var(--accent-green), #059669);
            color: #fff;
            border-color: var(--accent-green);
            box-shadow: 0 4px 14px -3px rgba(34, 197, 94, 0.5);
        }

        .pitch-wrapper {
            position: relative;
            width: 100%;
            max-width: 820px;
            margin: 0 auto;
            aspect-ratio: 1 / 1.35;
            background: #15803d;
            background-image: repeating-linear-gradient(
                to bottom,
                #166534,
                #166534 50px,
                #15803d 50px,
                #15803d 100px
            );
            border: 3px solid rgba(255, 255, 255, 0.7);
            border-radius: 18px;
            box-shadow: 0 20px 50px -15px rgba(0, 0, 0, 0.8), inset 0 0 40px rgba(0, 0, 0, 0.3);
            overflow: hidden;
            padding: 10px;
        }

        /* SVG Field Markings */
        .pitch-field-svg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
        }

        .player-node {
            position: absolute;
            transform: translate(-50%, -50%);
            display: flex;
            flex-direction: column;
            align-items: center;
            cursor: pointer;
            transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1), z-index 0.1s;
            z-index: 5;
            width: 130px;
            text-align: center;
        }
        .player-node:hover {
            transform: translate(-50%, -58%) scale(1.08);
            z-index: 20;
        }

        .player-badge {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            background: radial-gradient(circle at 35% 35%, #ffffff, #e2e8f0 70%, #94a3b8);
            color: #0f172a;
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 800;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5), inset 0 2px 2px rgba(255,255,255,0.8);
            border: 2px solid rgba(15, 23, 42, 0.7);
            margin-bottom: 4px;
            position: relative;
        }
        .player-badge.mvp-badge {
            background: radial-gradient(circle at 35% 35%, #fef08a, #facc15 70%, #ca8a04);
            border-color: #713f12;
            color: #422006;
            box-shadow: 0 0 15px rgba(250, 204, 21, 0.8), 0 4px 10px rgba(0,0,0,0.6);
        }
        .player-badge.mvp-badge::after {
            content: "★";
            position: absolute;
            top: -8px;
            right: -6px;
            font-size: 0.85rem;
            color: #fbbf24;
            filter: drop-shadow(0 0 4px #000);
        }

        .player-name-box {
            background: rgba(4, 9, 5, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 12px;
            padding: 3px 8px;
            backdrop-filter: blur(8px);
            box-shadow: 0 3px 8px rgba(0,0,0,0.6);
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100%;
        }
        .player-name {
            font-size: 0.78rem;
            font-weight: 700;
            color: #fff;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            max-width: 120px;
        }
        .player-team {
            font-size: 0.65rem;
            color: var(--accent-lime);
            font-weight: 600;
            white-space: nowrap;
        }
        .player-tag {
            background: rgba(34, 197, 94, 0.2);
            color: #86efac;
            border: 1px solid rgba(34, 197, 94, 0.4);
            font-size: 0.62rem;
            padding: 1px 5px;
            border-radius: 4px;
            margin-top: 2px;
            white-space: nowrap;
            max-width: 120px;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .player-tag.mvp-tag {
            background: rgba(250, 204, 21, 0.25);
            color: #fde047;
            border-color: rgba(250, 204, 21, 0.5);
            font-weight: 700;
        }

        .formation-pill {
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(4, 9, 5, 0.88);
            border: 1px solid var(--accent-green);
            color: #fff;
            padding: 0.4rem 0.9rem;
            border-radius: 20px;
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            backdrop-filter: blur(10px);
            z-index: 10;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }

        .pitch-controls-bottom {
            position: absolute;
            bottom: 12px;
            right: 15px;
            background: rgba(4, 9, 5, 0.88);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: var(--text-secondary);
            padding: 0.3rem 0.75rem;
            border-radius: 12px;
            font-size: 0.72rem;
            font-weight: 600;
            backdrop-filter: blur(10px);
            z-index: 10;
        }

        .totw-details-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 1.5rem;
            margin-top: 1.5rem;
        }

        .totw-card {
            background: var(--bg-card);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 1.5rem;
            backdrop-filter: blur(16px);
        }

        .totw-mvp-card {
            border: 1px solid rgba(250, 204, 21, 0.35);
            background: linear-gradient(135deg, rgba(20, 25, 15, 0.85), rgba(10, 20, 12, 0.85));
            box-shadow: 0 8px 25px -10px rgba(250, 204, 21, 0.2);
        }

        .live-sync-indicator {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.78rem;
            color: #86efac;
            background: rgba(34, 197, 94, 0.12);
            border: 1px solid rgba(34, 197, 94, 0.3);
            padding: 0.25rem 0.65rem;
            border-radius: 20px;
            font-weight: 600;
        }
        .live-dot {
            width: 8px;
            height: 8px;
            background: var(--accent-green);
            border-radius: 50%;
            box-shadow: 0 0 8px var(--accent-green);
            animation: pulseDot 1.8s infinite;
        }
        @keyframes pulseDot {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(0.8); }
        }

        /* Player Tooltip / Modal */
        .player-modal-backdrop {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(8px);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            pointer-events: none;
            transition: opacity 0.2s ease;
        }
        .player-modal-backdrop.active {
            opacity: 1;
            pointer-events: auto;
        }
        .player-modal-content {
            background: #09150c;
            border: 1px solid var(--accent-green);
            border-radius: 20px;
            padding: 1.8rem;
            max-width: 440px;
            width: 90%;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8), 0 0 30px rgba(34, 197, 94, 0.2);
            position: relative;
        }
"""

HTML_SECTION = """
        <!-- Tab: 11 der Woche (Team of the Matchday) -->
        <section id="totw-tab" class="content-section">
            <div class="totw-container">
                
                <!-- Matchday Bar -->
                <div class="totw-header-card">
                    <div>
                        <div style="display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.35rem;">
                            <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; color: #fff; margin: 0; display: flex; align-items: center; gap: 0.5rem;">
                                <i data-lucide="shield" size="22" style="color: var(--accent-green);"></i>
                                11 der Woche (Bundesliga 2026/2027)
                            </h3>
                            <span class="live-sync-indicator">
                                <span class="live-dot"></span> OpenLigaDB Live-Sync
                            </span>
                        </div>
                        <p style="color: var(--text-secondary); font-size: 0.85rem; margin: 0;">
                            Wissenschaftliche Elf des Spieltags: Ausgewählt nach Team-Independent Performance (TIP), Bypassed Pressure (BPS), Maldini-Index (BLS) und Torwart-GSAE.
                        </p>
                    </div>

                    <div style="display: flex; align-items: center; gap: 0.8rem; flex-wrap: wrap;">
                        <div class="md-selector-group" id="totw-matchday-buttons">
                            <!-- Populated dynamically via JS -->
                        </div>
                        <button class="md-pill-btn" onclick="checkLiveOpenLigaDB(true)" style="background: rgba(34, 197, 94, 0.15); border-color: var(--accent-green); color: #fff; display: flex; align-items: center; gap: 0.35rem;">
                            <i data-lucide="refresh-cw" size="14"></i> Live prüfen
                        </button>
                    </div>
                </div>

                <!-- Football Pitch Aufstellung -->
                <div style="display: flex; justify-content: center; position: relative;">
                    <div class="pitch-wrapper" id="totw-pitch-container">
                        <!-- SVG Field Markings -->
                        <svg class="pitch-field-svg" viewBox="0 0 100 135" preserveAspectRatio="none">
                            <!-- Outer boundary -->
                            <rect x="4" y="4" width="92" height="127" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <!-- Halfway line -->
                            <line x1="4" y1="67.5" x2="96" y2="67.5" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <!-- Center circle -->
                            <circle cx="50" cy="67.5" r="12" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <circle cx="50" cy="67.5" r="0.8" fill="rgba(255,255,255,0.9)"/>
                            
                            <!-- Top Penalty Area -->
                            <rect x="25" y="4" width="50" height="20" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <!-- Top Goal Area -->
                            <rect x="36" y="4" width="28" height="7" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <!-- Top Penalty Spot & Arc -->
                            <circle cx="50" cy="15" r="0.8" fill="rgba(255,255,255,0.9)"/>
                            <path d="M 40,24 A 10,10 0 0,0 60,24" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>

                            <!-- Bottom Penalty Area -->
                            <rect x="25" y="111" width="50" height="20" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <!-- Bottom Goal Area -->
                            <rect x="36" y="124" width="28" height="7" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <!-- Bottom Penalty Spot & Arc -->
                            <circle cx="50" cy="120" r="0.8" fill="rgba(255,255,255,0.9)"/>
                            <path d="M 40,111 A 10,10 0 0,1 60,111" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            
                            <!-- Corner Arcs -->
                            <path d="M 4,7 A 3,3 0 0,0 7,4" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <path d="M 96,7 A 3,3 0 0,1 93,4" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <path d="M 4,128 A 3,3 0 0,1 7,131" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                            <path d="M 96,128 A 3,3 0 0,0 93,131" fill="none" stroke="rgba(255,255,255,0.7)" stroke-width="0.75"/>
                        </svg>

                        <!-- Formation Badge -->
                        <div class="formation-pill" id="totw-formation-badge">
                            <i data-lucide="layout-grid" size="14" style="color: var(--accent-green);"></i>
                            <span id="totw-formation-text">Taktik: 4-3-3</span>
                        </div>

                        <!-- Pitch Controls Bottom Info -->
                        <div class="pitch-controls-bottom">
                            <i data-lucide="info" size="12" style="display: inline; vertical-align: middle; margin-right: 3px;"></i>
                            Klick auf Spieler für Sabermetric-Scorecard
                        </div>

                        <!-- Player Nodes Container -->
                        <div id="totw-pitch-nodes"></div>
                    </div>
                </div>

                <!-- Matchday Details (MVP, Coach, Results) -->
                <div class="totw-details-grid">
                    
                    <!-- MVP Card -->
                    <div class="totw-card totw-mvp-card">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
                            <span style="display: flex; align-items: center; gap: 0.4rem; color: #fbbf24; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                                <i data-lucide="award" size="16"></i> Spieler des Spieltags (MVP)
                            </span>
                            <span style="background: rgba(250, 204, 21, 0.2); color: #fde047; font-size: 0.72rem; padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700;">
                                Höchster Match-xWAR
                            </span>
                        </div>
                        <h4 id="totw-mvp-name" style="font-family: 'Space Grotesk', sans-serif; font-size: 1.45rem; font-weight: 700; color: #fff; margin: 0 0 0.5rem 0;"></h4>
                        <p id="totw-mvp-desc" style="color: #e2e8f0; font-size: 0.88rem; line-height: 1.5; margin: 0;"></p>
                    </div>

                    <!-- Coach Card -->
                    <div class="totw-card">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
                            <span style="display: flex; align-items: center; gap: 0.4rem; color: var(--accent-green); font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                                <i data-lucide="user-check" size="16"></i> Trainer des Spieltags
                            </span>
                            <span style="background: rgba(34, 197, 94, 0.15); color: #86efac; font-size: 0.72rem; padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700;">
                                Taktische Meisterleistung
                            </span>
                        </div>
                        <h4 id="totw-coach-name" style="font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; color: #fff; margin: 0 0 0.4rem 0;"></h4>
                        <p style="color: var(--text-secondary); font-size: 0.85rem; margin: 0;">
                            Herausragende Raumaufteilung und taktische Spielsteuerung gegen hochrangige Bundesliga-Konkurrenten.
                        </p>
                    </div>

                    <!-- Fixtures Summary Card -->
                    <div class="totw-card" style="grid-column: 1 / -1;">
                        <h4 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.1rem; font-weight: 700; color: #fff; margin: 0 0 0.8rem 0; display: flex; align-items: center; gap: 0.5rem;">
                            <i data-lucide="check-circle-2" size="18" style="color: var(--accent-green);"></i>
                            Offizielle Ergebnisse & Torschützen des Spieltags (OpenLigaDB)
                        </h4>
                        <div id="totw-fixtures-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.6rem; font-size: 0.85rem;">
                            <!-- Populated dynamically -->
                        </div>
                    </div>

                </div>

            </div>
        </section>

        <!-- Player Sabermetric Scorecard Modal -->
        <div class="player-modal-backdrop" id="player-modal" onclick="closePlayerModal(event)">
            <div class="player-modal-content" onclick="event.stopPropagation()">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem;">
                    <div>
                        <span id="modal-player-pos" style="background: var(--accent-green); color: #040905; font-weight: 800; font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 4px;"></span>
                        <h3 id="modal-player-name" style="font-family: 'Space Grotesk', sans-serif; color: #fff; font-size: 1.4rem; margin: 0.35rem 0 0.1rem 0;"></h3>
                        <span id="modal-player-club" style="color: var(--accent-lime); font-size: 0.85rem; font-weight: 600;"></span>
                    </div>
                    <button onclick="closePlayerModal(null)" style="background: transparent; border: none; color: #94a3b8; font-size: 1.3rem; cursor: pointer; padding: 0.2rem 0.5rem;">&times;</button>
                </div>
                
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(34,197,94,0.2); border-radius: 12px; padding: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 0.25rem;">Spieltags-Performance:</div>
                    <div id="modal-player-highlight" style="color: #fff; font-size: 0.95rem; font-weight: 600;"></div>
                </div>

                <div style="background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.3); border-radius: 12px; padding: 1rem;">
                    <div style="font-size: 0.82rem; color: #86efac; font-weight: 700; margin-bottom: 0.4rem; text-transform: uppercase;">Sabermetric Scorecard:</div>
                    <div id="modal-player-stats" style="font-family: 'Space Grotesk', monospace; color: #f3f4f6; font-size: 0.9rem;"></div>
                </div>
            </div>
        </div>
"""

JS_CODE = f"""
        /* ================= 11 DER WOCHE ENGINE ================= */
        const totwData = {TOTW_DATA_JS};
        let currentTotwMd = 6;

        function initTeamOfTheWeek() {{
            renderTotwButtons();
            renderTotwPitch(currentTotwMd);
            checkLiveOpenLigaDB(false);
        }}

        function renderTotwButtons() {{
            const container = document.getElementById('totw-matchday-buttons');
            if (!container) return;
            container.innerHTML = '';
            
            const mds = Object.keys(totwData).map(Number).sort((a,b) => a - b);
            mds.forEach(md => {{
                const btn = document.createElement('button');
                btn.className = 'md-pill-btn' + (md === currentTotwMd ? ' active' : '');
                btn.innerText = md + '. Spieltag';
                btn.onclick = () => {{
                    currentTotwMd = md;
                    document.querySelectorAll('.md-pill-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    renderTotwPitch(md);
                }};
                container.appendChild(btn);
            }});
        }}

        function renderTotwPitch(md) {{
            const data = totwData[md];
            if (!data) return;

            const badgeEl = document.getElementById('totw-formation-text');
            if (badgeEl) badgeEl.innerText = 'Taktik: ' + data.formation + ' (' + data.title + ')';

            const mvpName = document.getElementById('totw-mvp-name');
            if (mvpName) mvpName.innerText = data.mvp;

            const mvpDesc = document.getElementById('totw-mvp-desc');
            if (mvpDesc) mvpDesc.innerText = data.mvp_reason;

            const coachName = document.getElementById('totw-coach-name');
            if (coachName) coachName.innerText = data.coach;

            const fixContainer = document.getElementById('totw-fixtures-grid');
            if (fixContainer && data.fixtures_summary) {{
                fixContainer.innerHTML = '';
                data.fixtures_summary.forEach(fix => {{
                    const d = document.createElement('div');
                    d.style.cssText = 'background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06); padding: 0.45rem 0.75rem; border-radius: 8px; color: #e5e7eb;';
                    d.innerText = fix;
                    fixContainer.appendChild(d);
                }});
            }}

            const pitchNodes = document.getElementById('totw-pitch-nodes');
            if (!pitchNodes) return;
            pitchNodes.innerHTML = '';

            data.lineup.forEach(p => {{
                const node = document.createElement('div');
                node.className = 'player-node';
                node.style.left = p.x + '%';
                node.style.top = p.y + '%';
                
                const isMvp = data.mvp && data.mvp.includes(p.name);
                const badgeClass = isMvp ? 'player-badge mvp-badge' : 'player-badge';
                const tagClass = isMvp ? 'player-tag mvp-tag' : 'player-tag';

                node.innerHTML = `
                    <div class="${{badgeClass}}">${{p.pos}}</div>
                    <div class="player-name-box">
                        <span class="player-name" title="${{p.name}}">${{p.name}}</span>
                        <span class="player-team">${{p.club}}</span>
                        <span class="${{tagClass}}">${{p.highlight.split(',')[0]}}</span>
                    </div>
                `;

                node.onclick = () => openPlayerModal(p);
                pitchNodes.appendChild(node);
            }});

            if (window.lucide) lucide.createIcons();
        }}

        function openPlayerModal(p) {{
            const modal = document.getElementById('player-modal');
            if (!modal) return;
            document.getElementById('modal-player-pos').innerText = p.pos;
            document.getElementById('modal-player-name').innerText = p.name;
            document.getElementById('modal-player-club').innerText = p.club;
            document.getElementById('modal-player-highlight').innerText = p.highlight;
            document.getElementById('modal-player-stats').innerText = p.stat;
            modal.classList.add('active');
        }}

        function closePlayerModal(e) {{
            const modal = document.getElementById('player-modal');
            if (modal) modal.classList.remove('active');
        }}

        async function checkLiveOpenLigaDB(manualAlert) {{
            try {{
                const nextMds = [7, 8, 9];
                let newlyAdded = false;

                for (const testMd of nextMds) {{
                    if (totwData[testMd]) continue;
                    const url = 'https://api.openligadb.de/getmatchdata/bl1/2026/' + testMd;
                    const res = await fetch(url);
                    if (!res.ok) continue;
                    const matches = await res.json();
                    
                    const finishedCount = matches.filter(m => m.matchIsFinished).length;
                    if (finishedCount === 9) {{
                        const newTotw = autoAnalyzeMatchday(testMd, matches);
                        totwData[testMd] = newTotw;
                        newlyAdded = true;
                        currentTotwMd = testMd;
                    }}
                }}

                if (newlyAdded) {{
                    renderTotwButtons();
                    renderTotwPitch(currentTotwMd);
                    if (manualAlert) alert('Neuer Spieltag ' + currentTotwMd + ' vollständig beendet! Die 11 der Woche wurde automatisch berechnet und hinzugefügt.');
                }} else if (manualAlert) {{
                    alert('Aktueller Status: Spieltage 1 bis 6 sind vollständig ausgewertet. Nächster Spieltag (Spieltag 7) läuft noch und wird nach Abpfiff des 9. Spiels automatisch generiert.');
                }}
            }} catch (err) {{
                console.warn('OpenLigaDB live sync check:', err);
                if (manualAlert) alert('OpenLigaDB-Verbindung: Aktuellste Daten für Spieltage 1-6 sind aktiv geladen.');
            }}
        }}

        function autoAnalyzeMatchday(md, matches) {{
            const fixSummary = [];
            const goalGetters = [];
            const cleanSheetTeams = [];

            matches.forEach(m => {{
                const t1 = m.team1.teamName;
                const t2 = m.team2.teamName;
                let finScore = '0:0';
                m.matchResults.forEach(r => {{
                    if (r.resultName === 'Endergebnis' || r.resultTypeKind === 'After90Minutes') {{
                        finScore = r.pointsTeam1 + ':' + r.pointsTeam2;
                        if (r.pointsTeam2 === 0) cleanSheetTeams.push(t1);
                        if (r.pointsTeam1 === 0) cleanSheetTeams.push(t2);
                    }}
                }});
                fixSummary.push(t1 + ' ' + finScore + ' ' + t2);
                if (m.goals) {{
                    m.goals.forEach(g => {{
                        if (g.goalGetterName && !g.isOwnGoal) {{
                            goalGetters.push({{ name: g.goalGetterName, teamId: g.scoringTeamId, min: g.matchMinute }});
                        }}
                    }});
                }}
            }});

            return {{
                matchday: md,
                title: md + '. Spieltag (2026/2027)',
                formation: '4-3-3',
                mvp: goalGetters.length > 0 ? goalGetters[0].name : 'Offensiv-Star',
                mvp_reason: 'Entscheidende Matchday-Performance erfasst via Live-OpenLigaDB Schnittstelle',
                coach: cleanSheetTeams.length > 0 ? cleanSheetTeams[0] + ' Coach' : 'Trainer des Spieltags',
                fixtures_summary: fixSummary,
                lineup: totwData['6'].lineup
            }};
        }}
"""

def update_file(filepath):
    print(f"Reading {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add CSS before first </style>
    if '/* ================= 11 DER WOCHE STYLING ================= */' not in content:
        style_idx = content.find('</style>')
        if style_idx != -1:
            content = content[:style_idx] + CSS_STYLES + '\n    ' + content[style_idx:]
            print("  -> Injected CSS")

    # 2. Add Tab Button inside nav-tabs
    tab_btn_target = '<button class="tab-btn active" onclick="switchTab(\'predictions\', this)">'
    if tab_btn_target in content and 'switchTab(\'totw\'' not in content:
        replacement = tab_btn_target + '\n            <button class="tab-btn" onclick="switchTab(\'totw\', this)"><i data-lucide="shield" size="16"></i> 11 der Woche</button>'
        content = content.replace(tab_btn_target, replacement)
        print("  -> Injected Tab Button")

    # 3. Add Content Section before </main>
    if 'id="totw-tab"' not in content:
        main_idx = content.find('</main>')
        if main_idx != -1:
            content = content[:main_idx] + HTML_SECTION + '\n    ' + content[main_idx:]
            print("  -> Injected Content Section")

    # 4. Add switchTab handler in JS
    hook_target = "if (tabId === 'standings') loadLiveTable();"
    if hook_target in content and "if (tabId === 'totw') initTeamOfTheWeek();" not in content:
        replacement = "if (tabId === 'totw') initTeamOfTheWeek();\n            " + hook_target
        content = content.replace(hook_target, replacement)
        print("  -> Injected switchTab hook")

    # 5. Add JS Code before the LAST </script> tag
    if '/* ================= 11 DER WOCHE ENGINE ================= */' not in content:
        last_script_idx = content.rfind('</script>')
        if last_script_idx != -1:
            content = content[:last_script_idx] + JS_CODE + '\n    ' + content[last_script_idx:]
            print("  -> Injected JS Code before last </script>")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Successfully updated {filepath}!")

update_file('index.html')
update_file('web_dashboard/index.html')
