import json
import re

with open('data/all_matchdays_11_der_woche.json', 'r', encoding='utf-8') as f:
    totw_data = json.load(f)

totw_json_str = json.dumps(totw_data, ensure_ascii=False)

def update_html_file(filepath):
    print(f"Applying updates to {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add CSS for Joker Card if not already present
    joker_css = '''
        /* Joker Card & Sub Styling */
        .totw-joker-card {
            border: 1px solid rgba(249, 115, 22, 0.35);
            background: linear-gradient(135deg, rgba(30, 18, 8, 0.88), rgba(18, 12, 6, 0.9));
            box-shadow: 0 8px 25px -10px rgba(249, 115, 22, 0.25);
        }
        .joker-list {
            display: flex;
            flex-direction: column;
            gap: 0.6rem;
        }
        .joker-item {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(249, 115, 22, 0.22);
            border-radius: 12px;
            padding: 0.65rem 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            transition: all 0.2s ease;
        }
        .joker-item:hover {
            border-color: rgba(249, 115, 22, 0.5);
            background: rgba(249, 115, 22, 0.06);
        }
        .joker-top-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .joker-badge-row {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .joker-rank-pill {
            background: linear-gradient(135deg, #f97316, #ea580c);
            color: #fff;
            font-size: 0.72rem;
            font-weight: 800;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 6px rgba(249, 115, 22, 0.4);
        }
        .joker-player-name {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700;
            color: #fff;
            font-size: 0.95rem;
        }
        .joker-club-tag {
            font-size: 0.72rem;
            color: #fdba74;
            font-weight: 600;
        }
        .joker-desc-text {
            font-size: 0.8rem;
            color: #e2e8f0;
            line-height: 1.4;
        }
'''
    if '/* Joker Card & Sub Styling */' not in content:
        style_idx = content.find('</style>')
        if style_idx != -1:
            content = content[:style_idx] + joker_css + '\n' + content[style_idx:]
            print("  [OK] Added Joker CSS")

    # 2. Add Joker Card HTML into totw-details-grid if not present
    joker_card_html = '''                    <!-- Joker Card -->
                    <div class="totw-card totw-joker-card">
                        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.8rem;">
                            <span style="display: flex; align-items: center; gap: 0.4rem; color: #fb923c; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em;">
                                <i data-lucide="zap" size="16"></i> Joker des Spieltags (Top 3)
                            </span>
                            <span style="background: rgba(249, 115, 22, 0.2); color: #fdba74; font-size: 0.72rem; padding: 0.2rem 0.5rem; border-radius: 6px; font-weight: 700;">
                                &lt; 60 Min. Einsatz
                            </span>
                        </div>
                        <div id="totw-jokers-list" class="joker-list">
                            <!-- Populated dynamically via JS -->
                        </div>
                    </div>'''

    if '<!-- Joker Card -->' not in content:
        # Find where Coach card ends
        coach_card_end = '''                        <h4 id="totw-coach-name" style="font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; color: #fff; margin: 0 0 0.4rem 0;"></h4>
                        <p style="color: var(--text-secondary); font-size: 0.85rem; margin: 0;">
                            Herausragende Raumaufteilung und taktische Spielsteuerung gegen hochrangige Bundesliga-Konkurrenten.
                        </p>
                    </div>'''
        if coach_card_end in content:
            content = content.replace(coach_card_end, coach_card_end + '\n\n' + joker_card_html, 1)
            print("  [OK] Injected Joker Card HTML")
        else:
            print("  [WARN] Coach card end not found!")

    # 3. Update renderTotwPitch in JS to populate Jokers
    old_coach_js = '''            const coachName = document.getElementById('totw-coach-name');
            if (coachName) coachName.innerText = data.coach;'''

    new_coach_js = '''            const coachName = document.getElementById('totw-coach-name');
            if (coachName) coachName.innerText = data.coach;

            // Render Jokers of the Week (Super-Subs < 60 Min)
            const jokersList = document.getElementById('totw-jokers-list');
            if (jokersList && data.jokers) {
                jokersList.innerHTML = '';
                data.jokers.forEach(jk => {
                    const el = document.createElement('div');
                    el.className = 'joker-item';
                    el.innerHTML = `
                        <div class="joker-top-row">
                            <div class="joker-badge-row">
                                <span class="joker-rank-pill">${jk.rank}</span>
                                <span class="joker-player-name">${jk.name}</span>
                                <span class="joker-club-tag">(${jk.club})</span>
                            </div>
                            <span style="font-size: 0.7rem; color: #fb923c; background: rgba(249, 115, 22, 0.15); border: 1px solid rgba(249, 115, 22, 0.3); padding: 0.15rem 0.45rem; border-radius: 4px; font-weight: 700;">${jk.min_in}</span>
                        </div>
                        <div class="joker-desc-text">${jk.highlight}</div>
                        <div style="font-family: 'Space Grotesk', monospace; font-size: 0.72rem; color: #cbd5e1; margin-top: 0.15rem;">${jk.stat}</div>
                    `;
                    jokersList.appendChild(el);
                });
            }'''

    if old_coach_js in content and '// Render Jokers of the Week' not in content:
        content = content.replace(old_coach_js, new_coach_js, 1)
        print("  [OK] Injected Joker rendering into renderTotwPitch")

    # 4. Update totwData JSON
    idx_start = content.find('const totwData = {')
    idx_next = content.find('let currentTotwMd =', idx_start)
    idx_end = content.rfind(';', idx_start, idx_next)
    content = content[:idx_start] + f"const totwData = {totw_json_str};" + content[idx_end+1:]
    print("  [OK] Replaced totwData with 7 revised matchdays")

    # 5. Update Sabermetrics Legend for Penalty / Assist valuation & 60+ min starter rule
    old_tip_desc = '''                                    <div class="stat-legend-desc">
                                        Misst die reine individuelle Torgefahr und Kreation bereinigt um die Ballbesitz-Dominanz des eigenen Teams. Verhindert, dass Topteam-Spieler allein durch Klub-Überlegenheit bevorteilt werden.
                                    </div>
                                </div>
                                <div class="stat-legend-formula">Formel: (xG + 0.8×xA) ÷ (Team-Possession / 50%)</div>'''

    new_tip_desc = '''                                    <div class="stat-legend-desc">
                                        Misst die individuelle Torgefahr und Kreation bereinigt um Team-Ballbesitz mit <strong>differenzierter Torbewertung</strong>: Ein Elfmetertor (0,70) wird geringer gewichtet als ein Feldtor (1,00), jedoch höher als ein Assist (0,55). Dadurch gilt mathematisch: <em>1 Feldtor + 1 Assist (1,55) zählen mehr als 2 Elfmetertore (1,40)</em>.
                                    </div>
                                </div>
                                <div class="stat-legend-formula">Formel: (npxG × 1,00 + Pen_xG × 0,70 + xA × 0,55) ÷ (Possession / 50%)</div>'''

    if old_tip_desc in content:
        content = content.replace(old_tip_desc, new_tip_desc, 1)
        print("  [OK] Updated TIP formula and penalty discount in legend")

    # Update subtitle in legend
    old_sub = '''                            <p style="color: var(--text-secondary); font-size: 0.82rem; margin: 0;">
                                Erklärung aller wissenschaftlichen Metriken der „11 der Woche“ für Feldspieler und Torhüter
                            </p>'''

    new_sub = '''                            <p style="color: var(--text-secondary); font-size: 0.82rem; margin: 0;">
                                Erklärung aller wissenschaftlichen Metriken der „11 der Woche“. <strong>Startelf-Regel:</strong> Nur Spieler mit Startelf-Einsatz oder mindestens 60 Spielminuten. Einwechselspieler (&lt; 60 Min.) werden in der separaten Kategorie <em>„Joker des Spieltags (Top 3)“</em> gewürdigt.
                            </p>'''

    if old_sub in content:
        content = content.replace(old_sub, new_sub, 1)
        print("  [OK] Updated legend subtitle with 60+ min rule")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Finished {filepath}\n")

update_html_file('index.html')
update_html_file('web_dashboard/index.html')
