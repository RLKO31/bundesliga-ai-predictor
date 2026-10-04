import json

def rebuild_dashboard_v5():
    print("--- Rebuilding index.html with Model v5 Integration ---")
    
    with open("predictions_26_27_all.json", "r", encoding="utf-8") as f:
        preds_v2 = json.load(f)
        
    with open("predictions_v3_tactical.json", "r", encoding="utf-8") as f:
        preds_v3 = json.load(f)

    with open("predictions_v4_complexity.json", "r", encoding="utf-8") as f:
        preds_v4 = json.load(f)

    with open("predictions_v5_m1_4.json", "r", encoding="utf-8") as f:
        preds_v5 = json.load(f)
        
    with open("latest_state_v2.json", "r", encoding="utf-8") as f:
        state = json.load(f)
        
    preds_v2_json = json.dumps(preds_v2)
    preds_v3_json = json.dumps(preds_v3)
    preds_v4_json = json.dumps(preds_v4)
    preds_v5_json = json.dumps(preds_v5)
    elos_json = json.dumps(state['final_elos'])
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bundesliga prediction</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <!-- Leaflet Map CSS & JS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin=""/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
    
    <style>
        :root {
            --bg-deep: #040905;
            --bg-card: rgba(10, 24, 13, 0.65);
            --bg-card-hover: rgba(16, 38, 20, 0.85);
            --border-glow: rgba(34, 197, 94, 0.15);
            --border-glow-hover: rgba(34, 197, 94, 0.4);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-green: #22c55e;
            --accent-lime: #a3e635;
            --glow-green: rgba(34, 197, 94, 0.5);
            --accent-win: #10b981;
            --accent-loss: #ef4444;
            --accent-draw: #fbbf24;
            --accent-tactical: #38bdf8;
            --accent-purple: #c084fc;
            --accent-orange: #fb923c;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; -webkit-font-smoothing: antialiased; }

        body {
            background: var(--bg-deep);
            background-image: 
                radial-gradient(circle at 15% 20%, rgba(34, 197, 94, 0.08) 0%, transparent 45%),
                radial-gradient(circle at 85% 75%, rgba(163, 230, 53, 0.06) 0%, transparent 45%),
                linear-gradient(to right, rgba(255, 255, 255, 0.003) 50%, transparent 50%);
            background-size: 100% 100%, 100% 100%, 120px 100%;
            color: var(--text-primary); min-height: 100vh; overflow-x: hidden; padding-bottom: 5rem;
        }

        .pitch-overlay {
            position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                radial-gradient(circle at 50% 50%, transparent 120px, rgba(255, 255, 255, 0.01) 120px, rgba(255, 255, 255, 0.01) 122px, transparent 122px),
                linear-gradient(to right, transparent 49.9%, rgba(255, 255, 255, 0.01) 49.9%, rgba(255, 255, 255, 0.01) 50.1%, transparent 50.1%);
            pointer-events: none; z-index: 0;
        }

        header {
            position: relative; padding: 3rem 2rem; text-align: center;
            border-bottom: 1px solid rgba(34, 197, 94, 0.08);
            background: rgba(4, 9, 5, 0.85); backdrop-filter: blur(20px); z-index: 10;
        }

        .logo-glow { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 180px; height: 180px; background: var(--accent-green); filter: blur(90px); opacity: 0.15; pointer-events: none; }
        .header-content { display: flex; align-items: center; justify-content: center; gap: 1.5rem; max-width: 900px; margin: 0 auto 0.5rem auto; flex-wrap: wrap; }

        h1 {
            font-family: 'Space Grotesk', sans-serif; font-size: 2.8rem; font-weight: 700; letter-spacing: -0.04em;
            background: linear-gradient(to right, #ffffff, #86efac, #a3e635); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }

        .subtitle { color: var(--text-secondary); font-size: 1.1rem; font-weight: 300; letter-spacing: 0.05em; max-width: 800px; margin: 0 auto; }

        .nav-tabs {
            display: flex; justify-content: center; gap: 0.6rem; margin: 2.5rem auto; max-width: 1150px; padding: 0.5rem;
            background: rgba(255, 255, 255, 0.01); border: 1px solid rgba(34, 197, 94, 0.1); border-radius: 50px; backdrop-filter: blur(12px); z-index: 1; position: relative; flex-wrap: wrap;
        }

        .tab-btn {
            background: transparent; border: none; padding: 0.65rem 1.25rem; color: var(--text-secondary); font-size: 0.9rem; font-weight: 600; border-radius: 40px; cursor: pointer; transition: all 0.25s ease; display: flex; align-items: center; gap: 0.4rem;
        }
        .tab-btn:hover { color: #fff; }
        .tab-btn.active { background: linear-gradient(135deg, var(--accent-green), #059669); color: #fff; box-shadow: 0 4px 15px -4px rgba(34, 197, 94, 0.4); }

        .content-section { display: none; max-width: 1280px; margin: 0 auto; padding: 0 1.5rem; animation: fadeIn 0.4s ease-out forwards; position: relative; z-index: 1; }
        .content-section.active { display: block; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .matches-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)); gap: 1.5rem; }

        .match-card {
            background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 1.5rem; backdrop-filter: blur(16px); transition: all 0.3s ease; display: flex; flex-direction: column; justify-content: space-between;
        }
        .match-card:hover { border-color: var(--border-glow-hover); background: var(--bg-card-hover); transform: translateY(-2px); box-shadow: 0 10px 30px -15px rgba(34, 197, 94, 0.2); }

        .match-header { display: flex; justify-content: space-between; align-items: center; font-size: 0.75rem; color: var(--text-secondary); margin-bottom: 1.25rem; border-bottom: 1px solid rgba(34, 197, 94, 0.08); padding-bottom: 0.5rem; }
        .match-date { display: flex; align-items: center; gap: 0.35rem; }

        .tip-badge { background: rgba(34, 197, 94, 0.15); color: var(--accent-green); border: 1px solid rgba(34, 197, 94, 0.3); padding: 0.2rem 0.6rem; border-radius: 6px; font-weight: 700; letter-spacing: 0.02em; }
        .tip-badge.away-win { background: rgba(163, 230, 53, 0.15); color: var(--accent-lime); border: 1px solid rgba(163, 230, 53, 0.3); }

        .match-body { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; }
        .team-side { display: flex; flex-direction: column; align-items: center; width: 42%; text-align: center; }
        .logo-circle-img { width: 52px; height: 52px; object-fit: contain; margin-bottom: 0.5rem; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.4)); transition: transform 0.2s ease; }
        .match-card:hover .logo-circle-img { transform: scale(1.08); }
        .team-name { font-weight: 600; font-size: 0.95rem; color: #fff; line-height: 1.2; }
        .vs-text { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 1.1rem; color: var(--text-secondary); width: 16%; text-align: center; }

        .prob-section { border-top: 1px solid rgba(34, 197, 94, 0.08); padding-top: 1rem; }
        .prob-bar { display: flex; height: 8px; border-radius: 10px; overflow: hidden; background: rgba(255, 255, 255, 0.05); margin-bottom: 0.5rem; }
        .prob-segment { height: 100%; }
        .prob-segment.home { background: var(--accent-green); }
        .prob-segment.draw { background: #6b7280; }
        .prob-segment.away { background: var(--accent-lime); }
        .prob-labels { display: flex; justify-content: space-between; font-size: 0.72rem; color: var(--text-secondary); font-weight: 600; }
        .prob-val { color: #fff; }

        .tactical-card-strip { display: flex; justify-content: space-between; align-items: center; background: rgba(56, 189, 248, 0.06); border: 1px solid rgba(56, 189, 248, 0.2); padding: 0.4rem 0.75rem; border-radius: 8px; margin-top: 0.75rem; font-size: 0.75rem; }
        .tactical-style-tag { color: var(--accent-tactical); font-weight: 700; display: flex; align-items: center; gap: 0.25rem; }

        .standings-grid-container { display: grid; grid-template-columns: 1.1fr 1fr; gap: 2rem; margin-bottom: 2rem; }
        .table-card { background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); }
        .table-card h3 { font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; color: #fff; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(34, 197, 94, 0.1); padding-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between; }
        .live-badge { background: rgba(16, 185, 129, 0.15); color: var(--accent-win); border: 1px solid rgba(16, 185, 129, 0.3); font-size: 0.7rem; padding: 0.15rem 0.5rem; border-radius: 4px; letter-spacing: 0.05em; text-transform: uppercase; }

        .standings-table { width: 100%; border-collapse: collapse; text-align: left; }
        .standings-table th { color: var(--text-secondary); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; padding: 0.75rem 0.5rem; border-bottom: 1px solid rgba(34, 197, 94, 0.12); }
        .standings-table td { padding: 0.75rem 0.5rem; border-bottom: 1px solid rgba(255, 255, 255, 0.02); font-size: 0.9rem; }
        .rank-col { font-weight: 700; color: var(--accent-lime); width: 45px; }
        .team-col { font-weight: 600; color: #fff; display: flex; align-items: center; gap: 0.5rem; }
        .team-logo-small { width: 24px; height: 24px; object-fit: contain; }

        .map-card { background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); margin-bottom: 2rem; }
        .map-card h3 { font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 700; color: #fff; margin-bottom: 1rem; border-bottom: 1px solid rgba(34, 197, 94, 0.1); padding-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between; }
        .map-controls { display: flex; gap: 0.5rem; }
        .map-control-btn { background: rgba(255,255,255,0.02); border: 1px solid rgba(34,197,94,0.2); color: var(--text-secondary); font-size: 0.8rem; font-weight: 600; padding: 0.35rem 0.85rem; border-radius: 6px; cursor: pointer; transition: all 0.2s ease; }
        .map-control-btn.active { background: rgba(34,197,94,0.12); color: var(--accent-lime); border-color: var(--accent-green); }
        #map { height: 600px; width: 100%; border-radius: 12px; border: 1px solid rgba(34, 197, 94, 0.15); background: #090f0b; }

        .leaflet-popup-content-wrapper { background: #09140c !important; border: 1px solid rgba(34, 197, 94, 0.3) !important; border-radius: 12px !important; color: #fff !important; }
        .leaflet-popup-tip { background: #09140c !important; }

        .comparison-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }
        .comp-card { background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); }
        .comp-card h3 { font-family: 'Space Grotesk', sans-serif; font-size: 1.35rem; font-weight: 700; color: #fff; margin-bottom: 1.5rem; border-bottom: 1px solid rgba(34, 197, 94, 0.1); padding-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem; }
        .comp-row { display: flex; flex-direction: column; gap: 0.35rem; margin-bottom: 1.25rem; }
        .comp-meta { display: flex; justify-content: space-between; font-weight: 600; font-size: 0.88rem; }
        .comp-track { height: 10px; background: rgba(255,255,255,0.03); border-radius: 10px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }
        .comp-fill { height: 100%; border-radius: 10px; transition: width 0.6s ease; }

        .pitch-container-card { background: var(--bg-card); border: 1px solid var(--border-glow); border-radius: 20px; padding: 2rem; backdrop-filter: blur(16px); margin-bottom: 2rem; }
        .pitch-visualizer { background: linear-gradient(180deg, #09200f 0%, #041208 100%); border: 2px solid rgba(34, 197, 94, 0.4); border-radius: 16px; height: 380px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; padding: 1.5rem; box-shadow: inset 0 0 50px rgba(0,0,0,0.8); }
        .pitch-lines { position: absolute; top: 0; left: 0; right: 0; bottom: 0; border: 2px solid rgba(255, 255, 255, 0.15); margin: 15px; pointer-events: none; }
        .pitch-half-line { position: absolute; top: 50%; left: 15px; right: 15px; height: 2px; background: rgba(255, 255, 255, 0.15); }
        .pitch-center-circle { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 100px; height: 100px; border: 2px solid rgba(255, 255, 255, 0.15); border-radius: 50%; }

        .zones-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; height: 100%; position: relative; z-index: 2; gap: 1rem; }
        .zone-card { background: rgba(4, 9, 5, 0.75); border: 1px solid rgba(34, 197, 94, 0.25); border-radius: 12px; padding: 1rem; display: flex; flex-direction: column; justify-content: space-between; backdrop-filter: blur(8px); }
        .zone-title { font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); text-transform: uppercase; letter-spacing: 0.05em; }
        .zone-pct { font-family: 'Space Grotesk', sans-serif; font-size: 2.2rem; font-weight: 700; color: var(--accent-lime); }

        @media (max-width: 992px) { .standings-grid-container { grid-template-columns: 1fr; } .comparison-grid { grid-template-columns: 1fr; } }
        @media (max-width: 768px) { .header-content { gap: 0.75rem; } h1 { font-size: 2.1rem; } .nav-tabs { flex-wrap: wrap; border-radius: 20px; } .tab-btn { padding: 0.6rem 1.2rem; font-size: 0.9rem; } }
    </style>
</head>
<body>

    <div class="pitch-overlay"></div>

    <header>
        <div class="logo-glow"></div>
        <div class="header-content">
            <img src="https://upload.wikimedia.org/wikipedia/en/d/df/Bundesliga_logo_%282017%29.svg" referrerpolicy="no-referrer" alt="Bundesliga Logo" style="height: 65px; filter: drop-shadow(0 0 15px rgba(255,255,255,0.25));">
            <h1>Bundesliga prediction</h1>
        </div>
        <p class="subtitle">Interactive Matchday Travel Map, Multi-Model Selector & Matchday 1-4 Early Goal Complexity Model</p>
    </header>

    <main style="padding-top: 2rem;">

        <!-- Navigation Tabs -->
        <nav class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('predictions', this)"><i data-lucide="calendar" size="16"></i> Matchday Predictions</button>
            <button class="tab-btn" onclick="switchTab('standings', this)"><i data-lucide="list-ordered" size="16"></i> Standings Comparison</button>
            <button class="tab-btn" onclick="switchTab('map', this)"><i data-lucide="map" size="16"></i> Matchday Travel Map</button>
            <button class="tab-btn" onclick="switchTab('tactical', this)"><i data-lucide="compass" size="16"></i> Tactical Pitch Map & Form</button>
            <button class="tab-btn" onclick="switchTab('complexity', this)"><i data-lucide="sparkles" size="16"></i> First 15 Goals (v4)</button>
            <button class="tab-btn" onclick="switchTab('m14', this)"><i data-lucide="clock" size="16"></i> Matchday 1-4 Complexity (v5)</button>
            <button class="tab-btn" onclick="switchTab('insights', this)"><i data-lucide="cpu" size="16"></i> Model Efficiency & Data Impact</button>
        </nav>

        <!-- Tab 1: Predictions & Results -->
        <section id="predictions-tab" class="content-section active">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; background: var(--bg-card); padding: 1rem 1.5rem; border-radius: 16px; border: 1px solid var(--border-glow); backdrop-filter: blur(16px);">
                <div style="display: flex; align-items: center; gap: 1.5rem; flex-wrap: wrap;">
                    <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.2rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 0.5rem; margin: 0;">
                        <i data-lucide="calendar" size="18" style="color: var(--accent-green);"></i>
                        Predictions
                    </h3>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;">Model Engine:</span>
                        <select id="model-version-selector" onchange="switchModelVersion(this.value)" style="background: rgba(4,9,5,0.85); border: 1px solid var(--accent-tactical); color: #fff; font-weight: 700; border-radius: 8px; padding: 0.4rem 1.2rem; outline: none; cursor: pointer; font-family: 'Outfit', sans-serif; font-size: 0.88rem;">
                            <option value="v3" selected>Model v3 (Pure Tactical & 1D Time-Decay)</option>
                            <option value="v2">Model v2 (Elo + Form Hybrid)</option>
                        </select>
                    </div>
                </div>
                
                <div style="display: flex; align-items: center; gap: 1rem; flex-wrap: wrap;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;">Matchday:</span>
                        <select id="matchday-selector" onchange="loadMatchday(Number(this.value))" style="background: rgba(4,9,5,0.85); border: 1px solid var(--accent-green); color: #fff; font-weight: 700; border-radius: 8px; padding: 0.4rem 1.2rem; outline: none; cursor: pointer; font-family: 'Outfit', sans-serif; font-size: 0.88rem;">
                            <!-- Options -->
                        </select>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.5rem; background: rgba(34,197,94,0.08); border: 1px solid rgba(34,197,94,0.2); padding: 0.4rem 1rem; border-radius: 8px;">
                        <span style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;">Points Total:</span>
                        <strong id="matchday-points-total" style="color: var(--accent-lime); font-size: 1.15rem; font-family: 'Space Grotesk', sans-serif;">0 pts</strong>
                    </div>
                </div>
            </div>
            
            <div class="matches-grid" id="fixtures-grid"></div>
        </section>

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
                                    <th class="rank-col">Rank</th>
                                    <th>Team</th>
                                    <th style="text-align: center;">Pl</th>
                                    <th style="text-align: center;">GD</th>
                                    <th style="text-align: right;">Points</th>
                                </tr>
                            </thead>
                            <tbody id="live-standings-body">
                                <tr><td colspan="5" style="text-align: center; color: var(--text-secondary); padding: 2rem;">Loading live table...</td></tr>
                            </tbody>
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
                                    <th class="rank-col">Rank</th>
                                    <th>Team</th>
                                    <th style="text-align: center;">Pl</th>
                                    <th style="text-align: center;">GD</th>
                                    <th style="text-align: right;">Points</th>
                                </tr>
                            </thead>
                            <tbody id="predicted-standings-body"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>

        <!-- Tab 3: Matchday Travel Map -->
        <section id="map-tab" class="content-section">
            <div class="map-card">
                <h3>
                    <span><i data-lucide="map" size="20" style="color: var(--accent-green);"></i> Bundesliga Travel Map</span>
                    <div class="map-controls">
                        <button id="btn-show-teams" class="map-control-btn active" onclick="toggleMapMode('teams')">Teams Locations</button>
                        <button id="btn-show-travel" class="map-control-btn" onclick="toggleMapMode('travel')">Selected Matchday Travel</button>
                    </div>
                </h3>
                <div id="map"></div>
            </div>
        </section>

        <!-- Tab 4: Tactical Pitch Map & Form -->
        <section id="tactical-tab" class="content-section">
            <div class="pitch-container-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem;">
                    <h3 style="font-family: 'Space Grotesk', sans-serif; font-size: 1.5rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 0.5rem; margin: 0;">
                        <i data-lucide="compass" size="22" style="color: var(--accent-tactical);"></i>
                        Tactical 3-Zone Pitch Control & 1D Time-Decay Model
                    </h3>
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="color: var(--text-secondary); font-size: 0.85rem; font-weight: 600;">Select Matchup:</span>
                        <select id="tactical-match-selector" onchange="renderTacticalPitchMatch(this.value)" style="background: rgba(4,9,5,0.85); border: 1px solid var(--accent-tactical); color: #fff; font-weight: 700; border-radius: 8px; padding: 0.4rem 1.2rem; outline: none; cursor: pointer; font-family: 'Outfit', sans-serif; font-size: 0.88rem;">
                            <!-- Dynamic -->
                        </select>
                    </div>
                </div>

                <div class="pitch-visualizer">
                    <div class="pitch-lines"></div>
                    <div class="pitch-half-line"></div>
                    <div class="pitch-center-circle"></div>

                    <div class="zones-grid">
                        <div class="zone-card">
                            <span class="zone-title" id="zone-def-label">Defensive 1/3</span>
                            <div>
                                <div class="zone-pct" id="zone-def-val">32.4%</div>
                                <span style="font-size:0.75rem; color:var(--text-secondary);">Possession Share</span>
                            </div>
                        </div>
                        <div class="zone-card" style="border-color: rgba(56, 189, 248, 0.4);">
                            <span class="zone-title" id="zone-mid-label">Middle 1/3</span>
                            <div>
                                <div class="zone-pct" id="zone-mid-val" style="color: var(--accent-tactical);">41.2%</div>
                                <span style="font-size:0.75rem; color:var(--text-secondary);">Midfield Buildup</span>
                            </div>
                        </div>
                        <div class="zone-card" style="border-color: rgba(34, 197, 94, 0.4);">
                            <span class="zone-title" id="zone-att-label">Attacking 1/3</span>
                            <div>
                                <div class="zone-pct" id="zone-att-val" style="color: var(--accent-green);">26.4%</div>
                                <span style="font-size:0.75rem; color:var(--text-secondary);">Final 1/3 Creation</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Tab 5: Model v4 First 15 Goals Complexity -->
        <section id="complexity-tab" class="content-section">
            <div class="comp-card" style="margin-bottom: 2rem;">
                <h3 style="display: flex; justify-content: space-between; align-items: center;">
                    <span><i data-lucide="sparkles" size="22" style="color: var(--accent-purple);"></i> Model v4: First 15 Goals Complexity Predicted Standings</span>
                    <span class="live-badge" style="background: rgba(192, 132, 252, 0.15); color: var(--accent-purple); border-color: rgba(192, 132, 252, 0.3);">R² = 0.7203</span>
                </h3>
                <div style="overflow-x: auto;">
                    <table class="standings-table">
                        <thead>
                            <tr>
                                <th class="rank-col">Rank</th>
                                <th>Team</th>
                                <th style="text-align: center;">Matches to 15 Goals</th>
                                <th style="text-align: center;">Action Skill ($C$)</th>
                                <th style="text-align: center;">Assist Entropy ($H$)</th>
                                <th style="text-align: center;">Mean xG / Goal</th>
                                <th style="text-align: right;">Predicted Pts</th>
                            </tr>
                        </thead>
                        <tbody id="v4-complexity-standings-body"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- Tab 6: Model v5 Matchday 1-4 Goal Complexity -->
        <section id="m14-tab" class="content-section">
            <div class="comp-card" style="margin-bottom: 2rem;">
                <h3 style="display: flex; justify-content: space-between; align-items: center;">
                    <span><i data-lucide="clock" size="22" style="color: var(--accent-orange);"></i> Model v5: Matchdays 1-4 Early Goal Complexity Standings</span>
                    <span class="live-badge" style="background: rgba(251, 146, 60, 0.15); color: var(--accent-orange); border-color: rgba(251, 146, 60, 0.3);">R² = 0.6383 | MAE = 7.67 pts</span>
                </h3>
                <p style="color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; margin-bottom: 1.5rem;">
                    Model v5 uses only the goals scored during <strong>Matchdays 1 to 4</strong> (early September) to forecast final end-of-season standings points:
                </p>
                <div style="overflow-x: auto;">
                    <table class="standings-table">
                        <thead>
                            <tr>
                                <th class="rank-col">Rank</th>
                                <th>Team</th>
                                <th style="text-align: center;">Goals in M1-4</th>
                                <th style="text-align: center;">Action Skill ($C$)</th>
                                <th style="text-align: center;">Assist Entropy ($H$)</th>
                                <th style="text-align: center;">Mean xG / Goal</th>
                                <th style="text-align: right;">Predicted Pts</th>
                            </tr>
                        </thead>
                        <tbody id="v5-m14-standings-body"></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- Tab 7: Model Efficiency & Data Importance -->
        <section id="insights-tab" class="content-section">
            <div class="comparison-grid">
                
                <div class="comp-card">
                    <h3><i data-lucide="activity" size="20" style="color: var(--accent-green);"></i> Model Accuracy & Efficiency Comparison</h3>
                    
                    <div class="comp-row">
                        <div class="comp-meta">
                            <span style="color:#fff;"><i data-lucide="sparkles" size="14" style="color:var(--accent-purple);"></i> Model v4 (First 15 Goals Complexity)</span>
                            <span style="color:var(--accent-purple); font-family:'Space Grotesk';">R² = 0.7203 | MAE = 6.77 Pts</span>
                        </div>
                        <div class="comp-track">
                            <div class="comp-fill" style="width: 96.5%; background: linear-gradient(90deg, #c084fc, #a855f7);"></div>
                        </div>
                    </div>

                    <div class="comp-row">
                        <div class="comp-meta">
                            <span style="color:#fff;"><i data-lucide="clock" size="14" style="color:var(--accent-orange);"></i> Model v5 (Matchdays 1-4 Early Goals)</span>
                            <span style="color:var(--accent-orange); font-family:'Space Grotesk';">R² = 0.6383 | MAE = 7.67 Pts</span>
                        </div>
                        <div class="comp-track">
                            <div class="comp-fill" style="width: 94.2%; background: linear-gradient(90deg, #fb923c, #f97316);"></div>
                        </div>
                    </div>

                    <div class="comp-row">
                        <div class="comp-meta">
                            <span style="color:#fff;"><i data-lucide="shield" size="14" style="color:var(--accent-green);"></i> Model v2 (Elo + Form Ensemble)</span>
                            <span style="color:var(--accent-lime); font-family:'Space Grotesk';">57.52% Acc | 0.962 Loss</span>
                        </div>
                        <div class="comp-track">
                            <div class="comp-fill" style="width: 95.8%; background: linear-gradient(90deg, #10b981, #a3e635);"></div>
                        </div>
                    </div>

                    <div class="comp-row">
                        <div class="comp-meta">
                            <span style="color:#fff;"><i data-lucide="compass" size="14" style="color:var(--accent-tactical);"></i> Model v3 (Pure Tactical & 1D Decay)</span>
                            <span style="color:var(--accent-tactical); font-family:'Space Grotesk';">54.58% Acc | 1.012 Loss</span>
                        </div>
                        <div class="comp-track">
                            <div class="comp-fill" style="width: 90.9%; background: linear-gradient(90deg, #0284c7, #38bdf8);"></div>
                        </div>
                    </div>
                </div>

                <div class="comp-card">
                    <h3><i data-lucide="bar-chart-2" size="20" style="color: var(--accent-orange);"></i> Model v5 Learned Weights ("Matchdays 1-4")</h3>

                    <div class="comp-row">
                        <div class="comp-meta">
                            <span style="color:#fff;">1. Early Playmaker Assist Entropy ($H_{\\text{assist}}$)</span>
                            <span style="color:var(--accent-orange); font-family:'Space Grotesk';">+10.15 Pts Weight</span>
                        </div>
                        <div class="comp-track">
                            <div class="comp-fill" style="width: 100%; background: linear-gradient(90deg, var(--accent-orange), var(--accent-lime));"></div>
                        </div>
                    </div>

                    <div class="comp-row">
                        <div class="comp-meta">
                            <span style="color:#fff;">2. Early Clinical Finishing Delta ($\Delta_{\\text{fin}}$)</span>
                            <span style="color:var(--accent-orange); font-family:'Space Grotesk';">+4.54 Pts Weight</span>
                        </div>
                        <div class="comp-track">
                            <div class="comp-fill" style="width: 44.7%; background: linear-gradient(90deg, var(--accent-orange), var(--accent-lime));"></div>
                        </div>
                    </div>

                    <div class="comp-row">
                        <div class="comp-meta">
                            <span style="color:#fff;">3. Matchday 1-4 Expected Points ($xPTS$)</span>
                            <span style="color:var(--accent-orange); font-family:'Space Grotesk';">+4.43 Pts Weight</span>
                        </div>
                        <div class="comp-track">
                            <div class="comp-fill" style="width: 43.6%; background: linear-gradient(90deg, var(--accent-orange), var(--accent-lime));"></div>
                        </div>
                    </div>
                </div>

            </div>
        </section>

    </main>

    <script>
        const predictions_v2 = PREDS_V2_PLACEHOLDER;
        const predictions_v3 = PREDS_V3_PLACEHOLDER;
        const predictions_v4 = PREDS_V4_PLACEHOLDER;
        const predictions_v5 = PREDS_V5_PLACEHOLDER;
        const elos_info = ELOS_PLACEHOLDER;

        let activeModelVersion = 'v3';
        let currentMatchday = 1;
        let selectedMatchday = 1;
        let liveDataLoaded = false;
        let mapInitialized = false;
        let map, teamMarkersGroup, travelLinesGroup;
        let currentMapMode = 'teams';

        function getActivePredictions() {
            return activeModelVersion === 'v3' ? predictions_v3 : predictions_v2;
        }

        function switchModelVersion(ver) {
            activeModelVersion = ver;
            loadMatchday(selectedMatchday);
            renderPredictedStandings();
        }

        function formatDate(dateStr) {
            const dt = new Date(dateStr.replace(' ', 'T'));
            return dt.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }) + ' at ' + dt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
        }

        function switchTab(tabId, btnEl) {
            document.querySelectorAll('.content-section').forEach(sec => sec.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            
            document.getElementById(tabId + '-tab').classList.add('active');
            if (btnEl) btnEl.classList.add('active');
            
            if (tabId === 'standings') loadLiveTable();
            if (tabId === 'map') initMap();
            if (tabId === 'tactical') populateTacticalMatchSelector();
            if (tabId === 'complexity') renderV4ComplexityTable();
            if (tabId === 'm14') renderV5ComplexityTable();
        }

        function cleanTeamName(name) {
            if (!name) return "";
            const replacements = {
                "FC Bayern München": "Bayern Munich", "FC Bayern Muenchen": "Bayern Munich",
                "Bayern München": "Bayern Munich", "Bayern Muenchen": "Bayern Munich",
                "Bayer 04 Leverkusen": "Bayer Leverkusen", "Bayer Leverkusen": "Bayer Leverkusen",
                "FC Augsburg": "Augsburg", "VfL Bochum": "Bochum", "SV Darmstadt 98": "Darmstadt",
                "1. FC Heidenheim 1846": "FC Heidenheim", "1. FC Heidenheim": "FC Heidenheim",
                "SC Freiburg": "Freiburg", "SpVgg Greuther Frth": "Greuther Fuerth",
                "SpVgg Greuther Fürth": "Greuther Fuerth", "SpVgg Greuther Fűrth": "Greuther Fuerth",
                "Hamburg SV": "Hamburger SV", "TSG Hoffenheim": "Hoffenheim", "Mainz": "Mainz 05",
                "RB Leipzig": "RasenBallsport Leipzig", "1. FC Union Berlin": "Union Berlin",
                "VfL Wolfsburg": "Wolfsburg", "Borussia Mnchengladbach": "Borussia M.Gladbach",
                "Borussia Mönchengladbach": "Borussia M.Gladbach", "FC Schalke 04": "Schalke 04",
                "1. FC Kln": "FC Cologne", "1. FC Köln": "FC Cologne", "FC Kln": "FC Cologne",
                "FC Köln": "FC Cologne", "VfB Stuttgart": "VfB Stuttgart", "Eintracht Frankfurt": "Eintracht Frankfurt",
                "SV 07 Elversberg": "Elversberg", "SC Paderborn 07": "Paderborn", "SV Werder Bremen": "Werder Bremen"
            };
            for (const [k, v] of Object.entries(replacements)) {
                if (name.includes(k) || name === k) return v;
            }
            return name.trim();
        }

        const teamLogos = {
            "Bayern Munich": "https://upload.wikimedia.org/wikipedia/commons/1/1b/FC_Bayern_M%C3%BCnchen_logo_%282017%29.svg",
            "VfB Stuttgart": "https://upload.wikimedia.org/wikipedia/commons/e/eb/VfB_Stuttgart_1893_Logo.svg",
            "Borussia Dortmund": "https://upload.wikimedia.org/wikipedia/commons/6/67/Borussia_Dortmund_logo.svg",
            "Hamburger SV": "https://upload.wikimedia.org/wikipedia/commons/6/6a/Hamburger_SV_logo.svg",
            "RasenBallsport Leipzig": "https://upload.wikimedia.org/wikipedia/commons/0/04/RB_Leipzig_2014_logo.svg",
            "Borussia M.Gladbach": "https://upload.wikimedia.org/wikipedia/commons/a/ae/Borussia_M%C3%B6nchengladbach_Logo.svg",
            "Freiburg": "https://upload.wikimedia.org/wikipedia/commons/f/f1/SC_Freiburg_Logo.svg",
            "Werder Bremen": "https://upload.wikimedia.org/wikipedia/commons/b/be/SV-Werder-Bremen-Logo.svg",
            "Augsburg": "https://upload.wikimedia.org/wikipedia/en/c/c5/FC_Augsburg_logo.svg",
            "Schalke 04": "https://upload.wikimedia.org/wikipedia/commons/6/6d/FC_Schalke_04_Logo.svg",
            "Mainz 05": "https://upload.wikimedia.org/wikipedia/commons/d/d6/1._FSV_Mainz_05_Logo.svg",
            "Paderborn": "https://upload.wikimedia.org/wikipedia/commons/e/e3/SC_Paderborn_07_Logo.svg",
            "Union Berlin": "https://upload.wikimedia.org/wikipedia/commons/4/44/1._FC_Union_Berlin_Logo.svg",
            "Eintracht Frankfurt": "https://upload.wikimedia.org/wikipedia/commons/0/04/Eintracht_Front_Logo.svg",
            "FC Cologne": "https://upload.wikimedia.org/wikipedia/commons/a/a3/1._FC_K%C3%B6ln_Logo.svg",
            "Hoffenheim": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Logo_TSG_Hoffenheim.svg",
            "Elversberg": "https://upload.wikimedia.org/wikipedia/commons/a/a2/SV_07_Elversberg_Logo.svg",
            "Bayer Leverkusen": "https://upload.wikimedia.org/wikipedia/commons/5/58/Bayer_04_Leverkusen_Logo.svg"
        };

        const teamCoordinates = {
            "Bayern Munich": [48.2188, 11.6248], "Bayer Leverkusen": [51.0382, 7.0022],
            "Borussia Dortmund": [51.4926, 7.4519], "RasenBallsport Leipzig": [51.3458, 12.3483],
            "VfB Stuttgart": [48.7923, 9.2320], "Eintracht Frankfurt": [50.0686, 8.6455],
            "Freiburg": [47.9889, 7.8283], "Hoffenheim": [49.2393, 8.8875],
            "Borussia M.Gladbach": [51.1747, 6.3855], "Union Berlin": [52.4578, 13.5681],
            "Mainz 05": [49.9840, 8.2241], "Werder Bremen": [53.0664, 8.8376],
            "Augsburg": [48.3232, 10.8858], "Hamburger SV": [53.5872, 9.8987],
            "FC Cologne": [50.9338, 6.8750], "Schalke 04": [51.5546, 7.0675],
            "Paderborn": [51.7297, 8.7106], "Elversberg": [49.3218, 7.1278]
        };

        async function initMatchdaySelector() {
            const selector = document.getElementById("matchday-selector");
            selector.innerHTML = "";
            for (let i = 1; i <= 34; i++) {
                const opt = document.createElement("option");
                opt.value = i; opt.textContent = `Matchday ${i}`;
                selector.appendChild(opt);
            }

            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 1500);
                const response = await fetch("https://api.openligadb.de/getcurrentgroup/bl1", { signal: controller.signal });
                clearTimeout(timeoutId);
                if (response.ok) {
                    const data = await response.json();
                    if (data && data.groupOrderID) {
                        currentMatchday = data.groupOrderID;
                        selectedMatchday = currentMatchday;
                    }
                }
            } catch (err) {}

            selector.value = selectedMatchday;
            loadMatchday(selectedMatchday);
        }

        function loadMatchday(matchday) {
            selectedMatchday = matchday;
            renderOfflinePredictions(matchday);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 1500);

            fetch(`https://api.openligadb.de/getmatchdata/bl1/2026/${matchday}`, { signal: controller.signal })
                .then(res => { clearTimeout(timeoutId); if (!res.ok) throw new Error("Fetch error"); return res.json(); })
                .then(liveMatches => { renderMatchdayPredictions(liveMatches, matchday); })
                .catch(err => {});
        }

        function renderMatchdayPredictions(liveMatches, matchday) {
            const grid = document.getElementById("fixtures-grid");
            grid.innerHTML = "";
            let matchdayTotalPoints = 0; let finishedCount = 0;
            const activePreds = getActivePredictions();
            liveMatches.sort((a,b) => new Date(a.matchDateTime) - new Date(b.matchDateTime));

            liveMatches.forEach(m => {
                const homeNameRaw = m.team1.teamName; const awayNameRaw = m.team2.teamName;
                const homeClean = cleanTeamName(homeNameRaw); const awayClean = cleanTeamName(awayNameRaw);

                const pred = activePreds.find(p => p.matchday === matchday && cleanTeamName(p.home_clean) === homeClean && cleanTeamName(p.away_clean) === awayClean);
                if (!pred) return;

                const hPct = (pred.p_home * 100).toFixed(1); const dPct = (pred.p_draw * 100).toFixed(1); const aPct = (pred.p_away * 100).toFixed(1);
                const badgeClass = pred.tip === "AWAY WIN" ? "tip-badge away-win" : "tip-badge";

                let actualScoreHtml = ""; let pointsBadgeHtml = "";
                if (m.matchIsFinished && m.matchResults && m.matchResults.length > 0) {
                    const finalResult = m.matchResults.find(r => r.resultName === "Endergebnis") || m.matchResults[0];
                    if (finalResult) {
                        const actHome = finalResult.pointsTeam1; const actAway = finalResult.pointsTeam2;
                        actualScoreHtml = `<span style="font-size: 0.95rem; color: var(--text-secondary); font-weight:600;">Actual: <strong style="color:#fff;">${actHome}:${actAway}</strong></span>`;
                        
                        const [prHome, prAway] = pred.score.split(':').map(Number);
                        let pts = 0;
                        if (prHome === actHome && prAway === actAway) pts = 4;
                        else {
                            const prO = prHome > prAway ? 0 : (prHome < prAway ? 2 : 1);
                            const actO = actHome > actAway ? 0 : (actHome < actAway ? 2 : 1);
                            if (prO === actO) pts = (prHome - prAway) === (actHome - actAway) ? 3 : 2;
                        }
                        pointsBadgeHtml = `<span style="font-size:0.72rem; font-weight:700; padding:0.15rem 0.5rem; border-radius:4px; background:rgba(16,185,129,0.15); color:var(--accent-win);">+${pts} pts</span>`;
                        matchdayTotalPoints += pts; finishedCount++;
                    }
                } else {
                    actualScoreHtml = `<span style="font-size: 0.8rem; color: #fbbf24; font-weight:600;">Scheduled</span>`;
                }

                const homeLogo = teamLogos[homeClean] || ""; const awayLogo = teamLogos[awayClean] || "";
                const homeLogoHtml = homeLogo ? `<img class="logo-circle-img" src="${homeLogo}" referrerpolicy="no-referrer">` : `<div style="font-weight:700;">${homeNameRaw.substring(0,2)}</div>`;
                const awayLogoHtml = awayLogo ? `<img class="logo-circle-img" src="${awayLogo}" referrerpolicy="no-referrer">` : `<div style="font-weight:700;">${awayNameRaw.substring(0,2)}</div>`;

                let tacticalStripHtml = "";
                if (pred.tactical_info) {
                    tacticalStripHtml = `
                        <div class="tactical-card-strip">
                            <span class="tactical-style-tag"><i data-lucide="shield" size="12"></i> ${pred.tactical_info.home_style}</span>
                            <span style="color:var(--text-secondary); font-size:0.72rem;">Att 1/3: <strong>${pred.tactical_info.home_att_third}%</strong> vs <strong>${pred.tactical_info.away_att_third}%</strong></span>
                        </div>
                    `;
                }

                const card = document.createElement("div");
                card.className = "match-card";
                card.innerHTML = `
                    <div>
                        <div class="match-header">
                            <span class="match-date"><i data-lucide="clock" size="12"></i> ${formatDate(pred.date)}</span>
                            <div style="display:flex; gap:0.5rem; align-items:center;">
                                ${pointsBadgeHtml}
                                <span class="${badgeClass}">${pred.tip}</span>
                            </div>
                        </div>
                        <div class="match-body">
                            <div class="team-side">${homeLogoHtml}<span class="team-name">${homeNameRaw}</span></div>
                            <div class="vs-text" style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                                <span style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase;">Score Tip</span>
                                <span style="font-size: 1.3rem; font-weight: 700; color: var(--accent-lime); font-family: 'Space Grotesk', sans-serif;">${pred.score}</span>
                                ${actualScoreHtml}
                            </div>
                            <div class="team-side">${awayLogoHtml}<span class="team-name">${awayNameRaw}</span></div>
                        </div>
                        ${tacticalStripHtml}
                    </div>
                    <div class="prob-section">
                        <div class="prob-bar">
                            <div class="prob-segment home" style="width: ${hPct}%"></div>
                            <div class="prob-segment draw" style="width: ${dPct}%"></div>
                            <div class="prob-segment away" style="width: ${aPct}%"></div>
                        </div>
                        <div class="prob-labels">
                            <span>H: <span class="prob-val">${hPct}%</span></span>
                            <span>D: <span class="prob-val">${dPct}%</span></span>
                            <span>A: <span class="prob-val">${aPct}%</span></span>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });

            document.getElementById("matchday-points-total").textContent = `${matchdayTotalPoints} pts (${finishedCount}/9 played)`;
            lucide.createIcons();
        }

        function renderOfflinePredictions(matchday) {
            const grid = document.getElementById("fixtures-grid");
            grid.innerHTML = "";
            const activePreds = getActivePredictions();
            const matchdayPreds = activePreds.filter(p => p.matchday === matchday);

            matchdayPreds.forEach(p => {
                const hPct = (p.p_home * 100).toFixed(1); const dPct = (p.p_draw * 100).toFixed(1); const aPct = (p.p_away * 100).toFixed(1);
                const badgeClass = p.tip === "AWAY WIN" ? "tip-badge away-win" : "tip-badge";
                const cleanHome = cleanTeamName(p.home_clean); const cleanAway = cleanTeamName(p.away_clean);
                const homeLogo = teamLogos[cleanHome] || ""; const awayLogo = teamLogos[cleanAway] || "";
                
                const homeLogoHtml = homeLogo ? `<img class="logo-circle-img" src="${homeLogo}" referrerpolicy="no-referrer">` : `<div>${p.home_team.substring(0,2)}</div>`;
                const awayLogoHtml = awayLogo ? `<img class="logo-circle-img" src="${awayLogo}" referrerpolicy="no-referrer">` : `<div>${p.away_team.substring(0,2)}</div>`;

                let tacticalStripHtml = "";
                if (p.tactical_info) {
                    tacticalStripHtml = `
                        <div class="tactical-card-strip">
                            <span class="tactical-style-tag"><i data-lucide="shield" size="12"></i> ${p.tactical_info.home_style}</span>
                            <span style="color:var(--text-secondary); font-size:0.72rem;">Att 1/3: <strong>${p.tactical_info.home_att_third}%</strong> vs <strong>${p.tactical_info.away_att_third}%</strong></span>
                        </div>
                    `;
                }

                const card = document.createElement("div");
                card.className = "match-card";
                card.innerHTML = `
                    <div>
                        <div class="match-header">
                            <span class="match-date"><i data-lucide="clock" size="12"></i> ${formatDate(p.date)}</span>
                            <span class="${badgeClass}">${p.tip}</span>
                        </div>
                        <div class="match-body">
                            <div class="team-side">${homeLogoHtml}<span class="team-name">${p.home_team}</span></div>
                            <div class="vs-text" style="display: flex; flex-direction: column; align-items: center; gap: 0.25rem;">
                                <span style="font-size: 0.65rem; color: var(--text-secondary); text-transform: uppercase;">Score Tip</span>
                                <span style="font-size: 1.3rem; font-weight: 700; color: var(--accent-lime); font-family: 'Space Grotesk', sans-serif;">${p.score}</span>
                            </div>
                            <div class="team-side">${awayLogoHtml}<span class="team-name">${p.away_team}</span></div>
                        </div>
                        ${tacticalStripHtml}
                    </div>
                    <div class="prob-section">
                        <div class="prob-bar">
                            <div class="prob-segment home" style="width: ${hPct}%"></div>
                            <div class="prob-segment draw" style="width: ${dPct}%"></div>
                            <div class="prob-segment away" style="width: ${aPct}%"></div>
                        </div>
                        <div class="prob-labels">
                            <span>H: <span class="prob-val">${hPct}%</span></span>
                            <span>D: <span class="prob-val">${dPct}%</span></span>
                            <span>A: <span class="prob-val">${aPct}%</span></span>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            });
            lucide.createIcons();
        }

        function renderPredictedStandings() {
            const predBody = document.getElementById("predicted-standings-body");
            if (!predBody) return;
            predBody.innerHTML = "";

            const activePreds = getActivePredictions();
            const teamNames = [
                "Bayern Munich", "Bayer Leverkusen", "Borussia Dortmund", "RasenBallsport Leipzig",
                "VfB Stuttgart", "Eintracht Frankfurt", "Freiburg", "Hoffenheim", "Borussia M.Gladbach",
                "Union Berlin", "Mainz 05", "Werder Bremen", "Augsburg", "Hamburger SV",
                "FC Cologne", "Schalke 04", "Paderborn", "Elversberg"
            ];
            
            let stats = {};
            teamNames.forEach(name => { stats[name] = { name: name, points: 0, goalsScored: 0, goalsConceded: 0, matches: 0 }; });

            activePreds.forEach(p => {
                const [gh, ga] = p.score.split(':').map(Number);
                const home = cleanTeamName(p.home_clean); const away = cleanTeamName(p.away_clean);
                if (!stats[home] || !stats[away]) return;
                
                stats[home].matches++; stats[away].matches++;
                stats[home].goalsScored += gh; stats[home].goalsConceded += ga;
                stats[away].goalsScored += ga; stats[away].goalsConceded += gh;
                
                if (gh > ga) stats[home].points += 3;
                else if (gh < ga) stats[away].points += 3;
                else { stats[home].points += 1; stats[away].points += 1; }
            });

            let sorted = Object.values(stats).sort((a, b) => (b.points - a.points) || ((b.goalsScored - b.goalsConceded) - (a.goalsScored - a.goalsConceded)));

            sorted.forEach((team, index) => {
                const logo = teamLogos[team.name] || "";
                const logoHtml = logo ? `<img class="team-logo-small" src="${logo}" referrerpolicy="no-referrer">` : `<div>${team.name.substring(0,2)}</div>`;
                const gd = team.goalsScored - team.goalsConceded;
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="rank-col">#${index + 1}</td>
                    <td><div class="team-col">${logoHtml}<span>${team.name}</span></div></td>
                    <td style="text-align: center; color: #fff;">${team.matches}</td>
                    <td style="text-align: center; color: var(--text-secondary);">${gd > 0 ? '+' : ''}${gd}</td>
                    <td style="text-align: right; font-weight: 700; color: var(--accent-lime);">${team.points}</td>
                `;
                predBody.appendChild(tr);
            });
        }

        function renderV4ComplexityTable() {
            const body = document.getElementById("v4-complexity-standings-body");
            if (!body) return;
            body.innerHTML = "";

            predictions_v4.forEach(rec => {
                const logo = teamLogos[cleanTeamName(rec.team)] || "";
                const logoHtml = logo ? `<img class="team-logo-small" src="${logo}" referrerpolicy="no-referrer">` : `<div>${rec.team.substring(0,2)}</div>`;
                
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="rank-col" style="color: var(--accent-purple);">#${rec.rank}</td>
                    <td><div class="team-col">${logoHtml}<span>${rec.team}</span></div></td>
                    <td style="text-align: center; color: #fff;">${rec.matches_to_15_goals} matches</td>
                    <td style="text-align: center; font-weight: 700; color: var(--accent-tactical);">${rec.action_complexity_score.toFixed(2)}</td>
                    <td style="text-align: center; font-weight: 700; color: var(--accent-lime);">${rec.assist_entropy.toFixed(2)}</td>
                    <td style="text-align: center; color: var(--text-secondary);">${rec.avg_xg_per_goal.toFixed(2)} xG</td>
                    <td style="text-align: right; font-weight: 800; font-size: 1.05rem; color: var(--accent-purple); font-family: 'Space Grotesk', sans-serif;">${rec.predicted_points.toFixed(1)} pts</td>
                `;
                body.appendChild(tr);
            });
        }

        function renderV5ComplexityTable() {
            const body = document.getElementById("v5-m14-standings-body");
            if (!body) return;
            body.innerHTML = "";

            predictions_v5.forEach(rec => {
                const logo = teamLogos[cleanTeamName(rec.team)] || "";
                const logoHtml = logo ? `<img class="team-logo-small" src="${logo}" referrerpolicy="no-referrer">` : `<div>${rec.team.substring(0,2)}</div>`;
                
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td class="rank-col" style="color: var(--accent-orange);">#${rec.rank}</td>
                    <td><div class="team-col">${logoHtml}<span>${rec.team}</span></div></td>
                    <td style="text-align: center; color: #fff;">${rec.goals_in_first_4_matches} goals</td>
                    <td style="text-align: center; font-weight: 700; color: var(--accent-tactical);">${rec.action_complexity_score.toFixed(2)}</td>
                    <td style="text-align: center; font-weight: 700; color: var(--accent-lime);">${rec.assist_entropy.toFixed(2)}</td>
                    <td style="text-align: center; color: var(--text-secondary);">${rec.avg_xg_per_goal.toFixed(2)} xG</td>
                    <td style="text-align: right; font-weight: 800; font-size: 1.05rem; color: var(--accent-orange); font-family: 'Space Grotesk', sans-serif;">${rec.predicted_points.toFixed(1)} pts</td>
                `;
                body.appendChild(tr);
            });
        }

        async function loadLiveTable() {
            if (liveDataLoaded) return;
            const liveBody = document.getElementById("live-standings-body");
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 1500);
                const response = await fetch("https://api.openligadb.de/getbltable/bl1/2026", { signal: controller.signal });
                clearTimeout(timeoutId);
                if (!response.ok) throw new Error("Error");
                const data = await response.json();
                liveBody.innerHTML = "";
                data.forEach((team, index) => {
                    const cleanName = cleanTeamName(team.teamName);
                    const logoUrl = teamLogos[cleanName] || team.teamIconUrl;
                    const logoHtml = logoUrl ? `<img class="team-logo-small" src="${logoUrl}" referrerpolicy="no-referrer">` : `<div>${team.teamName.substring(0,2)}</div>`;
                    const tr = document.createElement("tr");
                    tr.innerHTML = `
                        <td class="rank-col">#${index + 1}</td>
                        <td><div class="team-col">${logoHtml}<span>${team.teamName}</span></div></td>
                        <td style="text-align: center; color: #fff;">${team.matches}</td>
                        <td style="text-align: center; color: var(--text-secondary);">${team.goalDiff > 0 ? '+' : ''}${team.goalDiff}</td>
                        <td style="text-align: right; font-weight: 700; color: var(--accent-green);">${team.points}</td>
                    `;
                    liveBody.appendChild(tr);
                });
                liveDataLoaded = true;
            } catch (err) {}
        }

        function populateTacticalMatchSelector() {
            const selector = document.getElementById("tactical-match-selector");
            selector.innerHTML = "";
            const activePreds = getActivePredictions();
            const mdPreds = activePreds.filter(p => p.matchday === selectedMatchday);

            mdPreds.forEach((p, idx) => {
                const opt = document.createElement("option");
                opt.value = idx; opt.textContent = `${p.home_team} vs ${p.away_team}`;
                selector.appendChild(opt);
            });

            if (mdPreds.length > 0) renderTacticalPitchMatch(0);
        }

        function renderTacticalPitchMatch(idx) {
            const activePreds = getActivePredictions();
            const mdPreds = activePreds.filter(p => p.matchday === selectedMatchday);
            const match = mdPreds[idx];
            if (!match || !match.tactical_info) return;

            const t = match.tactical_info;
            document.getElementById("zone-def-val").textContent = `${t.home_def_third}%`;
            document.getElementById("zone-mid-val").textContent = `${t.home_mid_third}%`;
            document.getElementById("zone-att-val").textContent = `${t.home_att_third}%`;

            document.getElementById("zone-def-label").textContent = `${match.home_clean} Defensive 1/3`;
            document.getElementById("zone-mid-label").textContent = `Midfield Buildup`;
            document.getElementById("zone-att-label").textContent = `${match.home_clean} Attacking 1/3`;
        }

        function initMap() {
            if (mapInitialized) { map.invalidateSize(); return; }
            map = L.map('map', { center: [51.1657, 10.4515], zoom: 6, attributionControl: false });
            L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 9 }).addTo(map);
            teamMarkersGroup = L.layerGroup().addTo(map);
            travelLinesGroup = L.layerGroup().addTo(map);
            updateMapDisplay();
            mapInitialized = true;
        }

        function toggleMapMode(mode) {
            currentMapMode = mode;
            document.getElementById("btn-show-teams").classList.toggle("active", mode === 'teams');
            document.getElementById("btn-show-travel").classList.toggle("active", mode === 'travel');
            updateMapDisplay();
        }

        function updateMapDisplay() {
            teamMarkersGroup.clearLayers(); travelLinesGroup.clearLayers();
            if (currentMapMode === 'teams') {
                for (const [name, coords] of Object.entries(teamCoordinates)) {
                    const logoUrl = teamLogos[name];
                    const customIcon = L.divIcon({
                        html: `<div style="width:30px; height:30px; border-radius:50%; background:#fff; border:2px solid var(--accent-green); display:flex; align-items:center; justify-content:center;"><img src="${logoUrl}" referrerpolicy="no-referrer" style="width:20px; height:20px; object-fit:contain;"></div>`,
                        className: '', iconSize: [30, 30], iconAnchor: [15, 15]
                    });
                    L.marker(coords, { icon: customIcon }).bindPopup(`<b>${name}</b>`).addTo(teamMarkersGroup);
                }
            } else {
                const activePreds = getActivePredictions();
                const mdPreds = activePreds.filter(p => p.matchday === selectedMatchday);
                mdPreds.forEach(pred => {
                    const hCoords = teamCoordinates[cleanTeamName(pred.home_clean)];
                    const aCoords = teamCoordinates[cleanTeamName(pred.away_clean)];
                    if (!hCoords || !aCoords) return;
                    L.polyline([aCoords, hCoords], { color: 'var(--accent-lime)', weight: 3, dashArray: '5, 10' }).addTo(travelLinesGroup);
                });
            }
        }

        window.addEventListener("DOMContentLoaded", () => {
            initMatchdaySelector();
            renderPredictedStandings();
        });
    </script>
</body>
</html>
"""
    
    html_filled = html_template.replace("PREDS_V2_PLACEHOLDER", preds_v2_json)
    html_filled = html_filled.replace("PREDS_V3_PLACEHOLDER", preds_v3_json)
    html_filled = html_filled.replace("PREDS_V4_PLACEHOLDER", preds_v4_json)
    html_filled = html_filled.replace("PREDS_V5_PLACEHOLDER", preds_v5_json)
    html_filled = html_filled.replace("ELOS_PLACEHOLDER", elos_json)
    
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_filled)
        
    print("SUCCESS: Updated index.html with Model v5 Matchday 1-4 Integration!")

if __name__ == "__main__":
    rebuild_dashboard_v5()
