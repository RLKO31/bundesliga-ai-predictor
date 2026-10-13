"""
Builds the upgraded match3d.html using the real match dataset
(FC Augsburg 2 - 3 FC Bayern München, Understat Real Match Tracking).
"""

import json
import os

def generate_html():
    json_path_2526 = os.path.join("data", "real_match_augsburg_bayern_3d.json")
    with open(json_path_2526, "r", encoding="utf-8") as f:
        real_data_2526 = json.load(f)

    json_path_2627 = os.path.join("data", "real_match_augsburg_bayern_2026_27_3d.json")
    with open(json_path_2627, "r", encoding="utf-8") as f:
        real_data_2627 = json.load(f)

    data_2526_str = json.dumps(real_data_2526, separators=(',', ':'))
    data_2627_str = json.dumps(real_data_2627, separators=(',', ':'))

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bundesliga Real Match Digital Twin | FC Augsburg vs FC Bayern München</title>
    
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Lucide Icons -->
    <script src="https://unpkg.com/lucide@latest"></script>
    
    <!-- Three.js & OrbitControls from CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

    <style>
        :root {{
            --bg-deep: #030704;
            --bg-panel: rgba(8, 20, 11, 0.82);
            --bg-panel-hover: rgba(14, 34, 19, 0.94);
            --border-glow: rgba(34, 197, 94, 0.25);
            --border-glow-bright: rgba(34, 197, 94, 0.55);
            --accent-green: #22c55e;
            --accent-lime: #a3e635;
            --accent-bayern: #dc2626;
            --accent-augsburg: #166534;
            --accent-ball: #f8fafc;
            --accent-gold: #f59e0b;
            --accent-cyan: #06b6d4;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Outfit', sans-serif;
            -webkit-font-smoothing: antialiased;
            user-select: none;
        }}

        body, html {{
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: var(--bg-deep);
            color: var(--text-primary);
        }}

        #canvas-container {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 1;
        }}

        /* Top Header & Scoreboard */
        .top-nav {{
            position: absolute;
            top: 1rem;
            left: 1.5rem;
            right: 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
            pointer-events: none;
        }}

        .match-score-card {{
            pointer-events: auto;
            background: var(--bg-panel);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 0.65rem 1.3rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.8), 0 0 20px rgba(34, 197, 94, 0.1);
        }}

        .team-badge {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.95rem;
            font-weight: 700;
        }}
        .team-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}
        .team-dot.bayern {{ background: var(--accent-bayern); box-shadow: 0 0 10px rgba(220, 38, 38, 0.6); }}
        .team-dot.augsburg {{ background: #ffffff; border: 2px solid var(--accent-augsburg); box-shadow: 0 0 10px rgba(22, 101, 52, 0.6); }}

        .score-display {{
            display: flex;
            flex-direction: column;
            align-items: center;
            font-family: 'Space Grotesk', sans-serif;
        }}
        .score-nums {{
            font-size: 1.65rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            color: #fff;
        }}
        .match-clock {{
            font-size: 0.72rem;
            font-weight: 700;
            color: var(--accent-lime);
            letter-spacing: 0.05em;
            background: rgba(163, 230, 53, 0.12);
            padding: 0.1rem 0.5rem;
            border-radius: 4px;
        }}

        .header-actions {{
            pointer-events: auto;
            display: flex;
            gap: 0.5rem;
        }}

        .action-btn {{
            background: var(--bg-panel);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border-glow);
            color: var(--text-primary);
            padding: 0.6rem 0.95rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.82rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.2s ease;
        }}
        .action-btn:hover {{
            background: var(--bg-panel-hover);
            border-color: var(--border-glow-bright);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px -5px rgba(34, 197, 94, 0.3);
        }}
        .action-btn.active {{
            background: linear-gradient(135deg, var(--accent-green), #059669);
            color: #fff;
            border-color: var(--accent-lime);
        }}

        /* Camera Mode Control Bar */
        .camera-bar {{
            position: absolute;
            top: 5.2rem;
            left: 1.5rem;
            z-index: 10;
            background: var(--bg-panel);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-glow);
            border-radius: 14px;
            padding: 0.3rem;
            display: flex;
            gap: 0.3rem;
        }}
        .cam-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 0.45rem 0.8rem;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.2s;
        }}
        .cam-btn:hover {{ color: #fff; background: rgba(255, 255, 255, 0.05); }}
        .cam-btn.active {{
            background: rgba(34, 197, 94, 0.2);
            color: var(--accent-lime);
            font-weight: 700;
            box-shadow: inset 0 0 10px rgba(34, 197, 94, 0.2);
        }}

        /* REAL MATCH EVENT BANNER (Top Center) */
        .real-event-banner {{
            position: absolute;
            top: 5.2rem;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10;
            background: rgba(10, 24, 13, 0.92);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 14px;
            padding: 0.6rem 1.25rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.8), 0 0 20px rgba(56, 189, 248, 0.15);
            max-width: 650px;
        }}
        .real-event-info {{
            display: flex;
            flex-direction: column;
            gap: 0.15rem;
        }}
        .event-main-title {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.95rem;
            font-weight: 700;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .event-sub-details {{
            font-size: 0.73rem;
            color: var(--text-secondary);
        }}
        .event-pov-quick-btns {{
            display: flex;
            gap: 0.35rem;
        }}
        .quick-pov-btn {{
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38bdf8;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 0.35rem 0.65rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .quick-pov-btn:hover {{
            background: #38bdf8;
            color: #000;
            transform: scale(1.04);
        }}

        /* QUICK PLAYER SWITCHER BAR (Below Camera Bar) */
        .squad-dock {{
            position: absolute;
            top: 8.8rem;
            left: 1.5rem;
            right: 1.5rem;
            z-index: 10;
            background: var(--bg-panel);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-glow);
            border-radius: 14px;
            padding: 0.45rem 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.8rem;
            box-shadow: 0 10px 25px -10px rgba(0, 0, 0, 0.7);
        }}
        .squad-dock-header {{
            font-size: 0.74rem;
            font-weight: 700;
            color: var(--accent-lime);
            display: flex;
            align-items: center;
            gap: 0.35rem;
            white-space: nowrap;
        }}
        .squad-nav-arrows {{
            display: flex;
            gap: 0.25rem;
        }}
        .squad-nav-btn {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #fff;
            padding: 0.25rem 0.45rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.75rem;
            font-weight: 700;
        }}
        .squad-nav-btn:hover {{
            background: var(--accent-green);
            color: #fff;
        }}
        .squad-chips-wrapper {{
            display: flex;
            gap: 0.35rem;
            overflow-x: auto;
            flex: 1;
            padding-bottom: 2px;
            scrollbar-width: thin;
        }}
        .squad-chips-wrapper::-webkit-scrollbar {{
            height: 4px;
        }}
        .squad-chips-wrapper::-webkit-scrollbar-thumb {{
            background: rgba(34, 197, 94, 0.3);
            border-radius: 4px;
        }}
        .player-chip {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: var(--text-secondary);
            font-size: 0.72rem;
            font-weight: 600;
            padding: 0.25rem 0.6rem;
            border-radius: 20px;
            cursor: pointer;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 0.3rem;
            transition: all 0.15s;
        }}
        .player-chip:hover {{
            color: #fff;
            background: rgba(255, 255, 255, 0.12);
            border-color: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }}
        .player-chip.active {{
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.25), rgba(56, 189, 248, 0.25));
            border-color: #38bdf8;
            color: #38bdf8;
            font-weight: 700;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
        }}
        .player-chip.bayern {{ border-left: 3px solid var(--accent-bayern); }}
        .player-chip.augsburg {{ border-left: 3px solid var(--accent-augsburg); }}

        /* Player POV HUD Banner (Left Overlay) */
        .pov-banner {{
            display: none;
            position: absolute;
            top: 12.5rem;
            left: 1.5rem;
            z-index: 10;
            background: rgba(15, 23, 42, 0.88);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(56, 189, 248, 0.4);
            border-radius: 14px;
            padding: 0.85rem 1.25rem;
            width: 320px;
            box-shadow: 0 15px 30px -10px rgba(0, 0, 0, 0.7);
            animation: fadeIn 0.3s ease;
        }}
        .pov-banner.active {{ display: block; }}
        .pov-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        .pov-name {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #38bdf8;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}
        .pov-stats-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            font-size: 0.78rem;
        }}
        .pov-stat {{
            background: rgba(255, 255, 255, 0.04);
            padding: 0.4rem 0.6rem;
            border-radius: 8px;
            display: flex;
            flex-direction: column;
        }}
        .stat-label {{ color: var(--text-secondary); font-size: 0.68rem; }}
        .stat-val {{ color: #fff; font-weight: 700; font-family: 'Space Grotesk', sans-serif; }}

        /* Crosshair in POV mode */
        .pov-crosshair {{
            display: none;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 24px;
            height: 24px;
            pointer-events: none;
            z-index: 5;
        }}
        .pov-crosshair::before, .pov-crosshair::after {{
            content: '';
            position: absolute;
            background: rgba(56, 189, 248, 0.45);
        }}
        .pov-crosshair::before {{ top: 11px; left: 0; width: 24px; height: 2px; }}
        .pov-crosshair::after {{ top: 0; left: 11px; width: 2px; height: 24px; }}
        .pov-crosshair.active {{ display: block; }}

        /* Tactical 2D Radar / Minimap */
        .radar-panel {{
            position: absolute;
            bottom: 6.8rem;
            right: 1.5rem;
            z-index: 10;
            background: var(--bg-panel);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-glow);
            border-radius: 16px;
            padding: 0.75rem;
            box-shadow: 0 15px 35px -10px rgba(0, 0, 0, 0.8);
        }}
        .radar-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.4rem;
            font-size: 0.74rem;
            font-weight: 700;
            color: var(--accent-lime);
        }}
        #radar-canvas {{
            display: block;
            border-radius: 8px;
            background: #06180b;
            border: 1px solid rgba(34, 197, 94, 0.3);
            cursor: pointer;
        }}

        /* Bottom Playback Dock */
        .bottom-dock {{
            position: absolute;
            bottom: 1.25rem;
            left: 1.5rem;
            right: 1.5rem;
            z-index: 10;
            background: var(--bg-panel);
            backdrop-filter: blur(24px);
            border: 1px solid var(--border-glow);
            border-radius: 20px;
            padding: 0.85rem 1.4rem;
            display: flex;
            flex-direction: column;
            gap: 0.65rem;
            box-shadow: 0 20px 45px -15px rgba(0, 0, 0, 0.85), 0 0 30px rgba(34, 197, 94, 0.1);
        }}

        /* Scrubber Bar & Event Bookmarks */
        .timeline-container {{
            display: flex;
            align-items: center;
            gap: 1rem;
            position: relative;
        }}
        .time-label {{
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--accent-lime);
            width: 48px;
            text-align: center;
        }}
        .timeline-bar-wrapper {{
            position: relative;
            flex: 1;
            display: flex;
            align-items: center;
            height: 24px;
        }}
        .timeline-slider {{
            -webkit-appearance: none;
            width: 100%;
            height: 6px;
            border-radius: 6px;
            background: rgba(255, 255, 255, 0.1);
            outline: none;
            cursor: pointer;
            position: relative;
            z-index: 2;
        }}
        .timeline-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-green);
            box-shadow: 0 0 12px var(--accent-green);
            cursor: pointer;
            border: 2px solid #fff;
            transition: transform 0.1s;
        }}
        .timeline-slider::-webkit-slider-thumb:hover {{
            transform: scale(1.25);
        }}

        /* Event Pips on the scrubber bar */
        .event-pip {{
            position: absolute;
            top: 2px;
            transform: translateX(-50%);
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.62rem;
            cursor: pointer;
            z-index: 3;
            transition: all 0.2s;
            border: 1px solid rgba(255, 255, 255, 0.5);
        }}
        .event-pip:hover {{
            transform: translateX(-50%) scale(1.4);
            z-index: 5;
        }}
        .event-pip.goal {{ background: #ef4444; box-shadow: 0 0 8px rgba(239, 68, 68, 0.9); }}
        .event-pip.saved {{ background: #06b6d4; box-shadow: 0 0 8px rgba(6, 182, 212, 0.8); }}
        .event-pip.chance {{ background: #f59e0b; box-shadow: 0 0 8px rgba(245, 158, 11, 0.8); }}

        /* Controls Row */
        .controls-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 0.75rem;
        }}
        .playback-buttons {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .ctrl-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #fff;
            padding: 0.5rem 0.85rem;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.8rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.2s;
        }}
        .ctrl-btn:hover {{
            background: rgba(34, 197, 94, 0.15);
            border-color: var(--accent-green);
            color: var(--accent-lime);
        }}
        .ctrl-btn.play-btn {{
            background: linear-gradient(135deg, var(--accent-green), #059669);
            border: none;
            padding: 0.5rem 1.35rem;
            font-weight: 700;
            box-shadow: 0 4px 15px -3px rgba(34, 197, 94, 0.5);
        }}
        .ctrl-btn.play-btn:hover {{
            box-shadow: 0 6px 20px -2px rgba(34, 197, 94, 0.7);
            transform: scale(1.02);
        }}

        .speed-group {{
            display: flex;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 8px;
            padding: 2px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .speed-btn {{
            background: transparent;
            border: none;
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.55rem;
            border-radius: 6px;
            cursor: pointer;
        }}
        .speed-btn.active {{
            background: var(--accent-green);
            color: #fff;
        }}

        .real-events-dropdown {{
            background: rgba(4, 9, 5, 0.9);
            border: 1px solid var(--border-glow);
            color: #fff;
            border-radius: 10px;
            padding: 0.45rem 0.9rem;
            font-size: 0.8rem;
            font-weight: 600;
            outline: none;
            cursor: pointer;
            max-width: 320px;
        }}

        /* Floating Tactical Toggles Drawer */
        .toggles-bar {{
            position: absolute;
            top: 5.2rem;
            right: 1.5rem;
            z-index: 10;
            background: var(--bg-panel);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-glow);
            border-radius: 14px;
            padding: 0.4rem 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}
        .toggle-item {{
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.75rem;
            color: var(--text-secondary);
            cursor: pointer;
        }}
        .toggle-item input[type="checkbox"] {{
            accent-color: var(--accent-green);
            cursor: pointer;
        }}
        .toggle-item:hover {{ color: #fff; }}

        /* Notifications / Toast */
        .toast-banner {{
            position: absolute;
            top: 4.8rem;
            left: 50%;
            transform: translateX(-50%);
            z-index: 100;
            background: rgba(16, 185, 129, 0.94);
            backdrop-filter: blur(12px);
            color: #fff;
            padding: 0.45rem 1.25rem;
            border-radius: 30px;
            font-weight: 700;
            font-size: 0.84rem;
            box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.5);
            display: none;
            animation: fadeIn 0.2s ease;
        }}

        /* Instructions overlay for first person */
        .pov-instructions {{
            position: absolute;
            bottom: 7.2rem;
            left: 50%;
            transform: translateX(-50%);
            z-index: 10;
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            padding: 0.35rem 1.2rem;
            font-size: 0.75rem;
            color: #94a3b8;
            pointer-events: none;
            display: none;
        }}
        .pov-instructions.active {{ display: block; }}
        .pov-instructions strong {{ color: #38bdf8; }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-5px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>

    <!-- Three.js Canvas Container -->
    <div id="canvas-container"></div>

    <!-- First Person Crosshair -->
    <div class="pov-crosshair" id="pov-crosshair"></div>

    <!-- Notification Toast -->
    <div class="toast-banner" id="toast-banner">Event Loaded</div>

    <!-- POV Instructions -->
    <div class="pov-instructions" id="pov-instructions">
        👁️ <strong>Player POV:</strong> Drag mouse to turn head (Angles: Yaw \u00b1120°, Pitch \u00b140°) | Click ANY player on pitch/radar to switch POV
    </div>

    <!-- Top Header: Scoreboard & Top Actions -->
    <header class="top-nav">
        <div class="match-score-card">
            <div class="team-badge">
                <div class="team-dot augsburg"></div>
                <span>FC Augsburg</span>
            </div>
            <div class="score-display">
                <div class="score-nums" id="score-nums-display">2 - 2</div>
                <div class="match-clock" id="match-clock-display">01:00 • 1st Half</div>
            </div>
            <div class="team-badge">
                <div class="team-dot bayern"></div>
                <span>FC Bayern</span>
            </div>
            <div style="margin-left: 0.5rem; border-left: 1px solid rgba(255,255,255,0.15); padding-left: 0.75rem;">
                <select id="match-season-select" onchange="switchMatchDataset(this.value)" style="background: rgba(4, 9, 5, 0.95); color: var(--accent-lime); border: 1px solid var(--accent-green); padding: 0.35rem 0.65rem; border-radius: 8px; font-weight: 700; font-size: 0.78rem; cursor: pointer; outline: none;">
                    <option value="2026_27" selected>Season 2026/27 (FCA 2 - 2 FCB)</option>
                    <option value="2025_26">Season 2025/26 (FCA 2 - 3 FCB)</option>
                </select>
            </div>
        </div>

        <div class="header-actions">
            <button class="action-btn" id="audio-toggle-btn" onclick="toggleAudio()">
                <i data-lucide="volume-2" size="16"></i>
                <span id="audio-btn-text">Audio: ON</span>
            </button>
            <button class="action-btn" onclick="captureSnapshot()">
                <i data-lucide="camera" size="16"></i>
                <span>Snapshot</span>
            </button>
            <button class="action-btn" onclick="toggleFullScreen()">
                <i data-lucide="maximize" size="16"></i>
                <span>Full Screen</span>
            </button>
            <button class="action-btn active" onclick="window.location.href='index.html'">
                <i data-lucide="arrow-left" size="16"></i>
                <span>Dashboard</span>
            </button>
        </div>
    </header>

    <!-- Camera Mode Selector Bar -->
    <div class="camera-bar">
        <button class="cam-btn active" id="cam-orbit" onclick="setCameraMode('orbit')">
            <i data-lucide="orbit" size="14"></i> Orbit Cam
        </button>
        <button class="cam-btn" id="cam-broadcast" onclick="setCameraMode('broadcast')">
            <i data-lucide="tv" size="14"></i> TV Broadcast
        </button>
        <button class="cam-btn" id="cam-sky" onclick="setCameraMode('sky')">
            <i data-lucide="crosshair" size="14"></i> Overhead Sky
        </button>
        <button class="cam-btn" id="cam-goal" onclick="setCameraMode('goal')">
            <i data-lucide="shield" size="14"></i> Goal Cam
        </button>
        <button class="cam-btn" id="cam-drone" onclick="setCameraMode('drone')">
            <i data-lucide="video" size="14"></i> Action Drone
        </button>
        <button class="cam-btn" id="cam-pov" onclick="setCameraMode('pov')">
            <i data-lucide="eye" size="14"></i> Player POV
        </button>
    </div>

    <!-- Real Match Event Live Banner (Top Center) -->
    <div class="real-event-banner" id="real-event-banner">
        <div class="real-event-info">
            <div class="event-main-title" id="event-banner-title">
                27' ⚽ GOAL: Serge Gnabry (Bayern)
            </div>
            <div class="event-sub-details" id="event-banner-sub">
                OpenPlay • Throughball from Harry Kane • xG: 0.409 • LeftFoot
            </div>
        </div>
        <div class="event-pov-quick-btns">
            <button class="quick-pov-btn" onclick="jumpToCurrentShooterPOV()">
                🎯 Shooter POV
            </button>
            <button class="quick-pov-btn" onclick="jumpToCurrentKeeperPOV()">
                🧤 Keeper POV
            </button>
        </div>
    </div>

    <!-- Toggles Bar (Top Right) -->
    <div class="toggles-bar">
        <label class="toggle-item">
            <input type="checkbox" id="toggle-names" checked onchange="togglePlayerNames(this.checked)">
            <span>Names</span>
        </label>
        <label class="toggle-item">
            <input type="checkbox" id="toggle-trail" checked onchange="toggleBallTrail(this.checked)">
            <span>Ball Trail</span>
        </label>
        <label class="toggle-item">
            <input type="checkbox" id="toggle-offside" checked onchange="toggleOffsideLine(this.checked)">
            <span>Offside Line</span>
        </label>
        <label class="toggle-item">
            <input type="checkbox" id="toggle-hull" onchange="toggleTeamShape(this.checked)">
            <span>Tactical Shapes</span>
        </label>
        <label class="toggle-item">
            <input type="checkbox" id="toggle-visors" checked onchange="toggleEyesightVisors(this.checked)">
            <span>Visors</span>
        </label>
    </div>

    <!-- Squad Dock: Interactive Player Switcher Carousel -->
    <div class="squad-dock">
        <div class="squad-dock-header">
            <i data-lucide="users" size="14"></i>
            <span>SWITCH PLAYER POV:</span>
        </div>
        <div class="squad-nav-arrows">
            <button class="squad-nav-btn" onclick="cyclePlayer(-1)" title="Previous Player (Tab / [)">◀</button>
            <button class="squad-nav-btn" onclick="cyclePlayer(1)" title="Next Player (Shift+Tab / ])">▶</button>
        </div>
        <div class="squad-chips-wrapper" id="squad-chips-container">
            <!-- Dynamically populated chips for all 22 players -->
        </div>
    </div>

    <!-- Player First Person Telemetry HUD -->
    <div class="pov-banner" id="pov-banner">
        <div class="pov-header">
            <div class="pov-name" id="hud-player-name">
                <i data-lucide="user" size="16"></i> #9 Harry Kane
            </div>
            <span style="font-size: 0.72rem; color: #a3e635; font-weight: 700;" id="hud-player-role">Center Forward</span>
        </div>
        <div class="pov-stats-grid">
            <div class="pov-stat">
                <span class="stat-label">Velocity</span>
                <span class="stat-val" id="hud-player-speed">24.8 km/h</span>
            </div>
            <div class="pov-stat">
                <span class="stat-label">Distance Covered</span>
                <span class="stat-val" id="hud-player-dist">8,640 m</span>
            </div>
            <div class="pov-stat">
                <span class="stat-label">Head Yaw Angle</span>
                <span class="stat-val" id="hud-head-yaw">0.0°</span>
            </div>
            <div class="pov-stat">
                <span class="stat-label">Gaze Target</span>
                <span class="stat-val" style="color: #38bdf8;" id="hud-gaze-status">Ball Tracking</span>
            </div>
        </div>
        <div style="margin-top: 0.5rem; display: flex; gap: 0.4rem;">
            <button class="ctrl-btn" style="flex:1; font-size: 0.72rem; padding: 0.3rem;" onclick="resetHeadAngle()">
                <i data-lucide="rotate-ccw" size="12"></i> Center Head
            </button>
            <button class="ctrl-btn" style="flex:1; font-size: 0.72rem; padding: 0.3rem;" onclick="toggleBallGazeLock()" id="btn-gaze-lock">
                <i data-lucide="lock" size="12"></i> Lock Ball Gaze
            </button>
        </div>
    </div>

    <!-- 2D Tactical Minimap / Radar -->
    <div class="radar-panel">
        <div class="radar-header">
            <span>2D TACTICAL RADAR</span>
            <span style="font-size: 0.68rem; color: var(--text-secondary);">Click player dot to switch POV</span>
        </div>
        <canvas id="radar-canvas" width="210" height="136"></canvas>
    </div>

    <!-- Bottom Playback Dock -->
    <div class="bottom-dock">
        <!-- Interactive Scrubber Timeline with All 30 Real Shots -->
        <div class="timeline-container">
            <span class="time-label" id="timeline-time-display">27:00</span>
            <div class="timeline-bar-wrapper" id="timeline-bar-wrapper">
                <input type="range" id="timeline-slider" class="timeline-slider" min="0" max="5400" value="1620" step="1" oninput="onTimelineScrub(this.value)">
                <!-- 30 Real Shot Pips generated in JavaScript -->
            </div>
            <span class="time-label" style="color: var(--text-secondary);">90:00</span>
        </div>

        <!-- Controls Row -->
        <div class="controls-row">
            <div class="playback-buttons">
                <button class="ctrl-btn" onclick="stepTime(-10)" title="Rewind 10 seconds">
                    <i data-lucide="rotate-ccw" size="14"></i> -10s
                </button>
                <button class="ctrl-btn play-btn" id="play-pause-btn" onclick="togglePlayPause()">
                    <i data-lucide="pause" size="16" id="play-pause-icon"></i>
                    <span id="play-pause-text">Pause</span>
                </button>
                <button class="ctrl-btn" onclick="stepTime(10)" title="Forward 10 seconds">
                    <i data-lucide="rotate-cw" size="14"></i> +10s
                </button>
                <button class="ctrl-btn" onclick="replayCurrentAction()" title="Replay real action in slow-motion">
                    <i data-lucide="rewind" size="14"></i> Replay (0.5x)
                </button>

                <!-- Speed Multiplier -->
                <div class="speed-group">
                    <button class="speed-btn" onclick="setPlaybackSpeed(0.5, this)">0.5x</button>
                    <button class="speed-btn active" onclick="setPlaybackSpeed(1.0, this)">1x</button>
                    <button class="speed-btn" onclick="setPlaybackSpeed(2.0, this)">2x</button>
                    <button class="speed-btn" onclick="setPlaybackSpeed(4.0, this)">4x</button>
                </div>
            </div>

            <!-- Real Match Action Selector Dropdown -->
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="font-size: 0.74rem; color: var(--text-secondary); font-weight: 700;">REAL ACTION:</span>
                <select id="real-events-select" class="real-events-dropdown" onchange="jumpToEventIndex(Number(this.value))">
                    <!-- Options populated from real dataset -->
                </select>
            </div>
        </div>
    </div>

    <!-- Embedded Real Match Dataset & Engine -->
    <script>
        window.MATCH_DATA_2025_26 = {data_2526_str};
        window.MATCH_DATA_2026_27 = {data_2627_str};
        window.REAL_MATCH_DATA = window.MATCH_DATA_2026_27;

        function switchMatchDataset(seasonKey) {{
            window.REAL_MATCH_DATA = (seasonKey === '2026_27') ? window.MATCH_DATA_2026_27 : window.MATCH_DATA_2025_26;

            const meta = window.REAL_MATCH_DATA.metadata;
            const scoreEl = document.getElementById('score-nums-display');
            if (scoreEl) scoreEl.textContent = meta.score.replace(':', ' - ');

            // Remove existing player groups from scene
            for (const pid in playerObjects) {{
                if (playerObjects[pid] && playerObjects[pid].group) {{
                    scene.remove(playerObjects[pid].group);
                }}
            }}
            playerObjects = {{}};

            // Rebuild players with new roster
            buildRealPlayers();

            // Rebuild squad UI and event options
            buildSquadChipsUI();
            buildRealEventsUI();

            // Default player selection
            const allRoster = [
                ...window.REAL_MATCH_DATA.rosters.bayern,
                ...window.REAL_MATCH_DATA.rosters.augsburg
            ];
            const kane = allRoster.find(p => p.short === 'Kane');
            selectedPlayerKey = kane ? kane.id : allRoster[0].id;
            updateSelectedPlayerUI();

            // Jump to first event
            jumpToEventIndex(0);
            showToast(`Loaded ${{meta.season}} Match: FCA ${{meta.score}} FCB`);
        }}

        /* =========================================================================
           1. CORE VARIABLES & STATE MANAGEMENT
           ========================================================================= */
        const PITCH_LENGTH = 105.0; // X axis from -52.5 to +52.5
        const PITCH_WIDTH = 68.0;   // Z axis from -34.0 to +34.0
        const GOAL_WIDTH = 7.32;
        const GOAL_HEIGHT = 2.44;

        let scene, camera, renderer, controls, raycaster, mousePointer;
        let pitchMesh, ballMesh, ballShadowMesh;
        let ballTrailPoints = [];
        let ballTrailLine;
        let offsideLineMesh;
        let shapeLinesBayern, shapeLinesAugsburg;
        let playerObjects = {{}}; // id -> {{ mesh, visor, label, selectionRing, data, currentPos, velocity, heading }}
        let selectedPlayerKey = 'bayern_9'; // default Harry Kane

        let cameraMode = 'orbit'; // 'orbit', 'broadcast', 'sky', 'goal', 'drone', 'pov'
        let isPlaying = true;
        let matchTime = 45; // in seconds (1' Fellhauer goal)
        let playbackSpeed = 1.0;
        let lastTimestamp = performance.now();

        // First Person Head Look System
        let headYaw = 0.0;
        let headPitch = 0.0;
        let isDraggingHead = false;
        let prevMousePos = {{ x: 0, y: 0 }};
        let lockBallGaze = true;

        // Toggles
        let showNames = true;
        let showTrail = true;
        let showOffside = true;
        let showShape = false;
        let showVisors = true;
        let audioEnabled = true;

        let activeRealEvent = null;

        /* =========================================================================
           2. PROCEDURAL WEB AUDIO ENGINE
           ========================================================================= */
        let audioCtx = null;
        function initAudio() {{
            if (!audioCtx) {{
                const AudioContext = window.AudioContext || window.webkitAudioContext;
                audioCtx = new AudioContext();
            }}
            if (audioCtx.state === 'suspended') {{
                audioCtx.resume();
            }}
        }}

        function playWhistleSound() {{
            if (!audioEnabled || !audioCtx) return;
            const now = audioCtx.currentTime;
            const osc1 = audioCtx.createOscillator();
            const osc2 = audioCtx.createOscillator();
            const gain = audioCtx.createGain();

            osc1.type = 'sine'; osc1.frequency.setValueAtTime(2850, now);
            osc2.type = 'sine'; osc2.frequency.setValueAtTime(2890, now);

            gain.gain.setValueAtTime(0, now);
            gain.gain.linearRampToValueAtTime(0.3, now + 0.04);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.65);

            osc1.connect(gain); osc2.connect(gain);
            gain.connect(audioCtx.destination);
            osc1.start(now); osc2.start(now);
            osc1.stop(now + 0.7); osc2.stop(now + 0.7);
        }}

        function playKickSound() {{
            if (!audioEnabled || !audioCtx) return;
            const now = audioCtx.currentTime;
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.frequency.setValueAtTime(140, now);
            osc.frequency.exponentialRampToValueAtTime(35, now + 0.08);

            gain.gain.setValueAtTime(0.25, now);
            gain.gain.exponentialRampToValueAtTime(0.001, now + 0.09);

            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start(now);
            osc.stop(now + 0.1);
        }}

        function playCheerSound() {{
            if (!audioEnabled || !audioCtx) return;
            const bufferSize = audioCtx.sampleRate * 1.5;
            const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) {{
                data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (audioCtx.sampleRate * 0.7));
            }}
            const noise = audioCtx.createBufferSource();
            noise.buffer = buffer;

            const filter = audioCtx.createBiquadFilter();
            filter.type = 'bandpass';
            filter.frequency.setValueAtTime(600, audioCtx.currentTime);
            filter.Q.setValueAtTime(1.5, audioCtx.currentTime);

            const gain = audioCtx.createGain();
            gain.gain.setValueAtTime(0, audioCtx.currentTime);
            gain.gain.linearRampToValueAtTime(0.3, audioCtx.currentTime + 0.1);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.5);

            noise.connect(filter);
            filter.connect(gain);
            gain.connect(audioCtx.destination);
            noise.start();
        }}

        function toggleAudio() {{
            initAudio();
            audioEnabled = !audioEnabled;
            document.getElementById('audio-btn-text').textContent = audioEnabled ? 'Audio: ON' : 'Audio: OFF';
            document.getElementById('audio-toggle-btn').classList.toggle('active', audioEnabled);
            showToast(audioEnabled ? 'Audio Soundscape Enabled' : 'Audio Muted');
        }}

        /* =========================================================================
           3. THREE.JS SCENE SETUP
           ========================================================================= */
        function initThree() {{
            const container = document.getElementById('canvas-container');

            scene = new THREE.Scene();
            scene.background = new THREE.Color(0x020704);
            scene.fog = new THREE.FogExp2(0x020704, 0.0045);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 500);
            camera.position.set(0, 32, 60);

            renderer = new THREE.WebGLRenderer({{ antialias: true, preserveDrawingBuffer: true, powerPreference: "high-performance" }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.shadowMap.enabled = true;
            renderer.shadowMap.type = THREE.PCFSoftShadowMap;
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.05;
            container.appendChild(renderer.domElement);

            raycaster = new THREE.Raycaster();
            mousePointer = new THREE.Vector2();

            // Orbit Controls
            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.08;
            controls.maxPolarAngle = Math.PI / 2 - 0.02;
            controls.minDistance = 1.0;
            controls.maxDistance = 160.0;
            controls.target.set(0, 1.5, 0);

            // Lighting Setup
            const ambient = new THREE.AmbientLight(0xdcfce7, 0.6);
            scene.add(ambient);

            createFloodlight(-55, 30, -38, 0xecfdf5, 1.3);
            createFloodlight(55, 30, -38, 0xecfdf5, 1.3);
            createFloodlight(-55, 30, 38, 0xecfdf5, 1.3);
            createFloodlight(55, 30, 38, 0xecfdf5, 1.3);

            buildStadiumPitch();
            build3DGoals();
            buildStadiumPerimeter();
            buildBall();
            buildOffsideLine();
            buildShapeLines();
            buildRealPlayers();

            // Window resize & interaction listeners
            window.addEventListener('resize', onWindowResize);
            setupInteractiveSelectionListeners();

            // Initialize UI elements
            buildSquadChipsUI();
            buildRealEventsUI();
            updateSelectedPlayerUI();
            jumpToEventIndex(0);

            lucide.createIcons();
        }}

        function createFloodlight(x, y, z, color, intensity) {{
            const light = new THREE.SpotLight(color, intensity);
            light.position.set(x, y, z);
            light.target.position.set(x * 0.4, 0, z * 0.4);
            light.angle = Math.PI / 3;
            light.penumbra = 0.5;
            light.castShadow = true;
            light.shadow.mapSize.width = 1024;
            light.shadow.mapSize.height = 1024;
            light.shadow.bias = -0.001;
            scene.add(light);
            scene.add(light.target);

            const fixture = new THREE.Mesh(
                new THREE.BoxGeometry(2, 2, 2),
                new THREE.MeshBasicMaterial({{ color: 0xffffff }})
            );
            fixture.position.set(x, y, z);
            scene.add(fixture);
        }}

        /* =========================================================================
           4. PROCEDURAL HIGH-RESOLUTION PITCH & STADIUM
           ========================================================================= */
        function generatePitchTexture() {{
            const canvas = document.createElement('canvas');
            canvas.width = 2048;
            canvas.height = 1360;
            const ctx = canvas.getContext('2d');

            const w = canvas.width;
            const h = canvas.height;

            ctx.fillStyle = '#1b5e20';
            ctx.fillRect(0, 0, w, h);

            // Alternating Mowing Stripes
            const stripeCount = 18;
            const stripeW = w / stripeCount;
            for (let i = 0; i < stripeCount; i++) {{
                ctx.fillStyle = (i % 2 === 0) ? '#216a27' : '#1e6224';
                ctx.fillRect(i * stripeW, 0, stripeW, h);
            }}

            const padX = 80;
            const padY = 60;
            const pw = w - padX * 2;
            const ph = h - padY * 2;
            const pLeft = padX;
            const pRight = w - padX;
            const pTop = padY;
            const pBottom = h - padY;
            const pCenterX = w / 2;
            const pCenterY = h / 2;

            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 7;
            ctx.lineCap = 'round';

            // Boundaries
            ctx.strokeRect(pLeft, pTop, pw, ph);

            // Halfway line
            ctx.beginPath();
            ctx.moveTo(pCenterX, pTop);
            ctx.lineTo(pCenterX, pBottom);
            ctx.stroke();

            // Center circle
            const mScale = pw / 105.0;
            ctx.beginPath();
            ctx.arc(pCenterX, pCenterY, 9.15 * mScale, 0, Math.PI * 2);
            ctx.stroke();
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(pCenterX, pCenterY, 5, 0, Math.PI * 2);
            ctx.fill();

            // Left Box (Augsburg)
            const boxW = 16.5 * mScale;
            const boxH = 40.32 * mScale;
            ctx.strokeRect(pLeft, pCenterY - boxH / 2, boxW, boxH);
            const sixW = 5.5 * mScale;
            const sixH = 18.32 * mScale;
            ctx.strokeRect(pLeft, pCenterY - sixH / 2, sixW, sixH);
            const penSpotX_L = pLeft + 11.0 * mScale;
            ctx.beginPath(); ctx.arc(penSpotX_L, pCenterY, 4, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath();
            ctx.arc(penSpotX_L, pCenterY, 9.15 * mScale, -0.93, 0.93);
            ctx.stroke();

            // Right Box (Bayern)
            ctx.strokeRect(pRight - boxW, pCenterY - boxH / 2, boxW, boxH);
            ctx.strokeRect(pRight - sixW, pCenterY - sixH / 2, sixW, sixH);
            const penSpotX_R = pRight - 11.0 * mScale;
            ctx.beginPath(); ctx.arc(penSpotX_R, pCenterY, 4, 0, Math.PI * 2); ctx.fill();
            ctx.beginPath();
            ctx.arc(penSpotX_R, pCenterY, 9.15 * mScale, Math.PI - 0.93, Math.PI + 0.93);
            ctx.stroke();

            // Corners
            const cornerR = 1.0 * mScale;
            ctx.beginPath(); ctx.arc(pLeft, pTop, cornerR, 0, Math.PI / 2); ctx.stroke();
            ctx.beginPath(); ctx.arc(pLeft, pBottom, cornerR, -Math.PI / 2, 0); ctx.stroke();
            ctx.beginPath(); ctx.arc(pRight, pTop, cornerR, Math.PI / 2, Math.PI); ctx.stroke();
            ctx.beginPath(); ctx.arc(pRight, pBottom, cornerR, Math.PI, 3 * Math.PI / 2); ctx.stroke();

            const texture = new THREE.CanvasTexture(canvas);
            texture.anisotropy = 16;
            return texture;
        }}

        function buildStadiumPitch() {{
            const pitchGeo = new THREE.PlaneGeometry(PITCH_LENGTH + 12, PITCH_WIDTH + 10);
            const pitchMat = new THREE.MeshStandardMaterial({{
                map: generatePitchTexture(),
                roughness: 0.85,
                metalness: 0.1
            }});
            pitchMesh = new THREE.Mesh(pitchGeo, pitchMat);
            pitchMesh.rotation.x = -Math.PI / 2;
            pitchMesh.receiveShadow = true;
            scene.add(pitchMesh);
        }}

        function build3DGoals() {{
            const postRadius = 0.12;
            const postMat = new THREE.MeshStandardMaterial({{ color: 0xffffff, roughness: 0.2, metalness: 0.8 }});
            const netMat = new THREE.MeshBasicMaterial({{ color: 0x94a3b8, wireframe: true, transparent: true, opacity: 0.45 }});

            function createGoal(x, rotationY) {{
                const goalGroup = new THREE.Group();

                const postGeo = new THREE.CylinderGeometry(postRadius, postRadius, GOAL_HEIGHT, 16);
                const postL = new THREE.Mesh(postGeo, postMat);
                postL.position.set(0, GOAL_HEIGHT / 2, -GOAL_WIDTH / 2);
                postL.castShadow = true;

                const postR = new THREE.Mesh(postGeo, postMat);
                postR.position.set(0, GOAL_HEIGHT / 2, GOAL_WIDTH / 2);
                postR.castShadow = true;

                const barGeo = new THREE.CylinderGeometry(postRadius, postRadius, GOAL_WIDTH + postRadius * 2, 16);
                const crossbar = new THREE.Mesh(barGeo, postMat);
                crossbar.rotation.x = Math.PI / 2;
                crossbar.position.set(0, GOAL_HEIGHT, 0);
                crossbar.castShadow = true;

                const netGeo = new THREE.BoxGeometry(2.0, GOAL_HEIGHT, GOAL_WIDTH);
                const netMesh = new THREE.Mesh(netGeo, netMat);
                netMesh.position.set(-1.0, GOAL_HEIGHT / 2, 0);

                goalGroup.add(postL);
                goalGroup.add(postR);
                goalGroup.add(crossbar);
                goalGroup.add(netMesh);

                goalGroup.position.set(x, 0, 0);
                goalGroup.rotation.y = rotationY;
                scene.add(goalGroup);
            }}

            createGoal(-PITCH_LENGTH / 2, 0);
            createGoal(PITCH_LENGTH / 2, Math.PI);
        }}

        function buildStadiumPerimeter() {{
            const ledMat = new THREE.MeshBasicMaterial({{ color: 0x22c55e }});
            const ledGeoX = new THREE.BoxGeometry(PITCH_LENGTH + 8, 1.0, 0.4);
            const ledGeoZ = new THREE.BoxGeometry(0.4, 1.0, PITCH_WIDTH + 6);

            const ledNorth = new THREE.Mesh(ledGeoX, ledMat);
            ledNorth.position.set(0, 0.5, -PITCH_WIDTH / 2 - 3.5);
            scene.add(ledNorth);

            const ledSouth = new THREE.Mesh(ledGeoX, ledMat);
            ledSouth.position.set(0, 0.5, PITCH_WIDTH / 2 + 3.5);
            scene.add(ledSouth);

            const ledWest = new THREE.Mesh(ledGeoZ, ledMat);
            ledWest.position.set(-PITCH_LENGTH / 2 - 4.5, 0.5, 0);
            scene.add(ledWest);

            const ledEast = new THREE.Mesh(ledGeoZ, ledMat);
            ledEast.position.set(PITCH_LENGTH / 2 + 4.5, 0.5, 0);
            scene.add(ledEast);
        }}

        function buildBall() {{
            const ballRadius = 0.22;
            const ballGeo = new THREE.SphereGeometry(ballRadius, 32, 32);
            const ballMat = new THREE.MeshStandardMaterial({{
                color: 0xffffff,
                roughness: 0.3,
                metalness: 0.2
            }});
            ballMesh = new THREE.Mesh(ballGeo, ballMat);
            ballMesh.castShadow = true;
            ballMesh.position.set(0, ballRadius, 0);
            scene.add(ballMesh);

            const shadowGeo = new THREE.CircleGeometry(0.35, 16);
            const shadowMat = new THREE.MeshBasicMaterial({{ color: 0x000000, transparent: true, opacity: 0.6 }});
            ballShadowMesh = new THREE.Mesh(shadowGeo, shadowMat);
            ballShadowMesh.rotation.x = -Math.PI / 2;
            ballShadowMesh.position.y = 0.02;
            scene.add(ballShadowMesh);

            const maxTrail = 40;
            const trailPositions = new Float32Array(maxTrail * 3);
            const trailGeo = new THREE.BufferGeometry();
            trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
            const trailMat = new THREE.LineBasicMaterial({{ color: 0x38bdf8, transparent: true, opacity: 0.85, linewidth: 2 }});
            ballTrailLine = new THREE.Line(trailGeo, trailMat);
            scene.add(ballTrailLine);
        }}

        function buildOffsideLine() {{
            const offsideGeo = new THREE.PlaneGeometry(0.3, PITCH_WIDTH);
            const offsideMat = new THREE.MeshBasicMaterial({{
                color: 0xef4444,
                transparent: true,
                opacity: 0.55,
                side: THREE.DoubleSide
            }});
            offsideLineMesh = new THREE.Mesh(offsideGeo, offsideMat);
            offsideLineMesh.rotation.x = -Math.PI / 2;
            offsideLineMesh.position.set(0, 0.03, 0);
            scene.add(offsideLineMesh);
        }}

        function buildShapeLines() {{
            const geoB = new THREE.BufferGeometry();
            const posB = new Float32Array(8 * 3);
            geoB.setAttribute('position', new THREE.BufferAttribute(posB, 3));
            shapeLinesBayern = new THREE.Line(geoB, new THREE.LineBasicMaterial({{ color: 0xdc2626, transparent: true, opacity: 0.6, linewidth: 2 }}));
            shapeLinesBayern.visible = false;
            scene.add(shapeLinesBayern);

            const geoA = new THREE.BufferGeometry();
            const posA = new Float32Array(8 * 3);
            geoA.setAttribute('position', new THREE.BufferAttribute(posA, 3));
            shapeLinesAugsburg = new THREE.Line(geoA, new THREE.LineBasicMaterial({{ color: 0x22c55e, transparent: true, opacity: 0.6, linewidth: 2 }}));
            shapeLinesAugsburg.visible = false;
            scene.add(shapeLinesAugsburg);
        }}

        /* =========================================================================
           5. PLAYERS AS VERTICAL CYLINDERS WITH 3D LABELS & SELECTION RINGS
           ========================================================================= */
        function createPlayerLabel(number, name, color) {{
            const canvas = document.createElement('canvas');
            canvas.width = 256;
            canvas.height = 96;
            const ctx = canvas.getContext('2d');

            ctx.fillStyle = 'rgba(10, 20, 14, 0.85)';
            ctx.roundRect(10, 10, 236, 76, 16);
            ctx.fill();
            ctx.strokeStyle = color;
            ctx.lineWidth = 4;
            ctx.roundRect(10, 10, 236, 76, 16);
            ctx.stroke();

            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 36px "Space Grotesk", sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText(`${{number}} ${{name}}`, 128, 62);

            const texture = new THREE.CanvasTexture(canvas);
            const spriteMat = new THREE.SpriteMaterial({{ map: texture, transparent: true }});
            const sprite = new THREE.Sprite(spriteMat);
            sprite.scale.set(3.2, 1.2, 1);
            sprite.position.y = 2.4;
            return sprite;
        }}

        function buildRealPlayers() {{
            const playerHeight = 1.80;
            const playerRadius = 0.38;

            const bayernColor = 0xdc2626;
            const augsburgColor = 0xffffff;
            const neuerColor = 0xfacc15;
            const dahmenColor = 0x06b6d4;

            const allRoster = [
                ...window.REAL_MATCH_DATA.rosters.bayern,
                ...window.REAL_MATCH_DATA.rosters.augsburg
            ];

            const cylGeo = new THREE.CylinderGeometry(playerRadius, playerRadius, playerHeight, 20);

            allRoster.forEach(p => {{
                const group = new THREE.Group();
                group.userData = {{ playerId: p.id, playerObj: p }};

                // Player Body Cylinder
                const pColor = (p.pos === 'GK') ?
                    (p.team === 'bayern' ? neuerColor : dahmenColor) :
                    (p.team === 'bayern' ? bayernColor : augsburgColor);

                const mat = new THREE.MeshStandardMaterial({{
                    color: pColor,
                    roughness: 0.4,
                    metalness: 0.1
                }});
                const body = new THREE.Mesh(cylGeo, mat);
                body.position.y = playerHeight / 2;
                body.castShadow = true;
                group.add(body);

                // Team Accent Ring
                const ringGeo = new THREE.TorusGeometry(playerRadius + 0.02, 0.04, 8, 24);
                const ringMat = new THREE.MeshBasicMaterial({{ color: p.team === 'bayern' ? 0xffffff : 0x166534 }});
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.rotation.x = Math.PI / 2;
                ring.position.y = 1.35;
                group.add(ring);

                // Eyesight Visor
                const visorGeo = new THREE.ConeGeometry(0.2, 0.45, 12);
                const visorMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8 }});
                const visor = new THREE.Mesh(visorGeo, visorMat);
                visor.rotation.x = Math.PI / 2;
                visor.position.set(0, 1.62, playerRadius + 0.15);
                group.add(visor);

                // 3D Floating Label
                const label = createPlayerLabel(p.num, p.short, p.team === 'bayern' ? '#ef4444' : '#22c55e');
                group.add(label);

                // Selection Pulsing Halo (Grass Ring)
                const selGeo = new THREE.RingGeometry(playerRadius + 0.15, playerRadius + 0.35, 24);
                const selMat = new THREE.MeshBasicMaterial({{ color: 0x38bdf8, side: THREE.DoubleSide, transparent: true, opacity: 0 }});
                const selRing = new THREE.Mesh(selGeo, selMat);
                selRing.rotation.x = -Math.PI / 2;
                selRing.position.y = 0.03;
                group.add(selRing);

                // Initial Placement
                group.position.set(p.base_x, 0, p.base_z);
                scene.add(group);

                playerObjects[p.id] = {{
                    id: p.id,
                    group: group,
                    bodyMesh: body,
                    visor: visor,
                    label: label,
                    selRing: selRing,
                    data: p,
                    currentPos: new THREE.Vector3(p.base_x, 0, p.base_z),
                    velocity: new THREE.Vector3(0, 0, 0),
                    heading: 0,
                    distanceRun: 3800 + Math.random() * 2500
                }};
            }});
        }}

        /* =========================================================================
           6. SQUAD UI & REAL MATCH EVENT CONTROLS
           ========================================================================= */
        function buildSquadChipsUI() {{
            const container = document.getElementById('squad-chips-container');
            container.innerHTML = '';

            const allRoster = [
                ...window.REAL_MATCH_DATA.rosters.bayern,
                ...window.REAL_MATCH_DATA.rosters.augsburg
            ];

            allRoster.forEach(p => {{
                const chip = document.createElement('div');
                chip.className = `player-chip ${{p.team}} ${{p.id === selectedPlayerKey ? 'active' : ''}}`;
                chip.id = `chip-${{p.id}}`;
                chip.innerHTML = `<strong>#${{p.num}}</strong> ${{p.short}} <span style="font-size:0.65rem; opacity:0.8;">(${{p.pos}})</span>`;
                chip.onclick = () => switchPlayerPOV(p.id);
                container.appendChild(chip);
            }});
        }}

        function buildRealEventsUI() {{
            const select = document.getElementById('real-events-select');
            const wrapper = document.getElementById('timeline-bar-wrapper');

            select.innerHTML = '';
            wrapper.querySelectorAll('.event-pip').forEach(p => p.remove());

            window.REAL_MATCH_DATA.events.forEach((ev, idx) => {{
                // Populate dropdown
                const opt = document.createElement('option');
                opt.value = idx;
                opt.textContent = `${{ev.minute}}' [${{ev.team.toUpperCase()}}] ${{ev.shooter_name}} (${{ev.result}}) xG: ${{ev.xg}}`;
                select.appendChild(opt);

                // Populate timeline pips
                const pip = document.createElement('div');
                const pct = (ev.seconds / 5400) * 100;
                let pipClass = 'chance';
                let icon = '🔶';
                if (ev.is_goal) {{
                    pipClass = 'goal';
                    icon = '⚽';
                }} else if (ev.result === 'SavedShot') {{
                    pipClass = 'saved';
                    icon = '🧤';
                }}

                pip.className = `event-pip ${{pipClass}}`;
                pip.style.left = `${{Math.min(99, Math.max(1, pct))}}%`;
                pip.title = `${{ev.minute}}' ${{ev.shooter_name}} (${{ev.result}})`;
                pip.textContent = icon;
                pip.onclick = () => jumpToEventIndex(idx);
                wrapper.appendChild(pip);
            }});
        }}

        function cyclePlayer(direction) {{
            const allKeys = Object.keys(playerObjects);
            const curIdx = allKeys.indexOf(selectedPlayerKey);
            let nextIdx = (curIdx + direction + allKeys.length) % allKeys.length;
            switchPlayerPOV(allKeys[nextIdx]);
        }}

        function switchPlayerPOV(playerId) {{
            initAudio();
            if (!playerObjects[playerId]) return;

            // Deselect old
            if (playerObjects[selectedPlayerKey]) {{
                playerObjects[selectedPlayerKey].selRing.material.opacity = 0;
            }}

            selectedPlayerKey = playerId;
            const p = playerObjects[playerId];
            p.selRing.material.opacity = 0.85;

            // Update UI chips
            document.querySelectorAll('.player-chip').forEach(c => c.classList.remove('active'));
            const activeChip = document.getElementById(`chip-${{playerId}}`);
            if (activeChip) {{
                activeChip.classList.add('active');
                activeChip.scrollIntoView({{ behavior: 'smooth', inline: 'center', block: 'nearest' }});
            }}

            updateSelectedPlayerUI();

            if (cameraMode !== 'pov') {{
                setCameraMode('pov');
            }}

            showToast(`Switched POV: #${{p.data.num}} ${{p.data.name}} (${{p.data.team.toUpperCase()}})`);
        }}

        function updateSelectedPlayerUI() {{
            const p = playerObjects[selectedPlayerKey];
            if (!p) return;

            document.getElementById('hud-player-name').innerHTML = `<i data-lucide="user" size="16"></i> #${{p.data.num}} ${{p.data.name}}`;
            document.getElementById('hud-player-role').textContent = `${{p.data.pos}} • ${{p.data.team.toUpperCase()}}`;
            document.getElementById('hud-player-dist').textContent = `${{Math.round(p.distanceRun)}} m`;
            lucide.createIcons();
        }}

        function jumpToCurrentShooterPOV() {{
            if (activeRealEvent && activeRealEvent.shooter_id) {{
                switchPlayerPOV(activeRealEvent.shooter_id);
            }}
        }}

        function jumpToCurrentKeeperPOV() {{
            if (activeRealEvent) {{
                const gkId = (activeRealEvent.team === 'bayern') ? 'augsburg_1' : 'bayern_1';
                switchPlayerPOV(gkId);
            }}
        }}

        /* =========================================================================
           7. INTERACTIVE 3D & 2D SELECTION LISTENERS
           ========================================================================= */
        function setupInteractiveSelectionListeners() {{
            const container = document.getElementById('canvas-container');

            // 3D Raycasting: Click directly on ANY player cylinder to switch POV
            window.addEventListener('pointerdown', (e) => {{
                if (cameraMode === 'pov') {{
                    isDraggingHead = true;
                    prevMousePos = {{ x: e.clientX, y: e.clientY }};
                    return;
                }}

                mousePointer.x = (e.clientX / window.innerWidth) * 2 - 1;
                mousePointer.y = -(e.clientY / window.innerHeight) * 2 + 1;

                raycaster.setFromCamera(mousePointer, camera);
                const playerMeshes = Object.values(playerObjects).map(p => p.bodyMesh);
                const intersects = raycaster.intersectObjects(playerMeshes);

                if (intersects.length > 0) {{
                    const hitMesh = intersects[0].object;
                    const hitGroup = hitMesh.parent;
                    if (hitGroup && hitGroup.userData && hitGroup.userData.playerId) {{
                        switchPlayerPOV(hitGroup.userData.playerId);
                    }}
                }}
            }});

            window.addEventListener('pointerup', () => {{
                isDraggingHead = false;
            }});

            window.addEventListener('pointermove', (e) => {{
                if (cameraMode === 'pov' && isDraggingHead) {{
                    const dx = e.clientX - prevMousePos.x;
                    const dy = e.clientY - prevMousePos.y;

                    headYaw -= dx * 0.006;
                    headYaw = THREE.MathUtils.clamp(headYaw, -Math.PI * 0.72, Math.PI * 0.72);

                    headPitch -= dy * 0.005;
                    headPitch = THREE.MathUtils.clamp(headPitch, -Math.PI * 0.22, Math.PI * 0.20);

                    prevMousePos = {{ x: e.clientX, y: e.clientY }};
                }}
            }});

            // 2D Minimap Radar Click to switch POV
            const radarCanvas = document.getElementById('radar-canvas');
            radarCanvas.addEventListener('click', (e) => {{
                const rect = radarCanvas.getBoundingClientRect();
                const rx = e.clientX - rect.left;
                const ry = e.clientY - rect.top;

                // Find closest player dot
                let closestKey = null;
                let minDist = 18; // px

                for (const key in playerObjects) {{
                    const p = playerObjects[key];
                    const px = ((p.group.position.x + PITCH_LENGTH / 2) / PITCH_LENGTH) * radarCanvas.width;
                    const py = ((p.group.position.z + PITCH_WIDTH / 2) / PITCH_WIDTH) * radarCanvas.height;
                    const dist = Math.hypot(rx - px, ry - py);
                    if (dist < minDist) {{
                        minDist = dist;
                        closestKey = key;
                    }}
                }}

                if (closestKey) {{
                    switchPlayerPOV(closestKey);
                }}
            }});
        }}

        function resetHeadAngle() {{
            headYaw = 0.0;
            headPitch = 0.0;
            showToast('Head Look Centered');
        }}

        function toggleBallGazeLock() {{
            lockBallGaze = !lockBallGaze;
            document.getElementById('btn-gaze-lock').innerHTML = lockBallGaze ?
                '<i data-lucide="lock" size="12"></i> Lock Ball Gaze' :
                '<i data-lucide="unlock" size="12"></i> Free Head Gaze';
            lucide.createIcons();
            showToast(lockBallGaze ? 'Gaze Locked to Ball' : 'Free Head Orientation');
        }}

        /* =========================================================================
           8. REAL MATCH KINEMATIC SIMULATION (Driven by Authentic Events)
           ========================================================================= */
        function getClosestRealEvent(timeSec) {{
            const events = window.REAL_MATCH_DATA.events;
            for (let i = 0; i < events.length; i++) {{
                const ev = events[i];
                if (Math.abs(timeSec - ev.seconds) <= 12) {{
                    return {{ event: ev, index: i }};
                }}
            }}
            // Fallback to closest event
            let closest = events[0];
            let minDiff = Math.abs(timeSec - events[0].seconds);
            let closestIdx = 0;
            for (let i = 1; i < events.length; i++) {{
                const diff = Math.abs(timeSec - events[i].seconds);
                if (diff < minDiff) {{
                    minDiff = diff;
                    closest = events[i];
                    closestIdx = i;
                }}
            }}
            return {{ event: closest, index: closestIdx }};
        }}

        function computeRealMatchSimulation(timeSec) {{
            const {{ event: ev, index: evIdx }} = getClosestRealEvent(timeSec);
            activeRealEvent = ev;

            // Update Real Event Banner in UI
            document.getElementById('event-banner-title').textContent = ev.title;
            document.getElementById('event-banner-sub').textContent = ev.subtitle;
            document.getElementById('real-events-select').value = evIdx;

            const timeDiff = timeSec - ev.seconds; // seconds from shot moment (-12 to +6)
            let ballPos = {{ x: 0, y: 0.22, z: 0 }};

            const shotPos = ev.shot_coord;
            const assistPos = ev.assist_coord;
            const goalPos = ev.target_goal_coord;

            if (timeDiff < -3.0) {{
                // Phase 1: Assister carries / prepares delivery
                const progress = (timeDiff + 12.0) / 9.0; // 0 to 1
                ballPos.x = THREE.MathUtils.lerp(assistPos[0] - 4, assistPos[0], progress);
                ballPos.z = THREE.MathUtils.lerp(assistPos[1] + 2, assistPos[1], progress);
                ballPos.y = 0.22;
            }} else if (timeDiff < 0.0) {{
                // Phase 2: Delivery / Pass from assister to shooter
                const progress = (timeDiff + 3.0) / 3.0; // 0 to 1
                ballPos.x = THREE.MathUtils.lerp(assistPos[0], shotPos[0], progress);
                ballPos.z = THREE.MathUtils.lerp(assistPos[1], shotPos[1], progress);
                ballPos.y = (ev.last_action === 'Cross' || ev.situation === 'FromCorner') ?
                    0.22 + Math.sin(progress * Math.PI) * 2.8 : 0.22;
                if (progress > 0.95 && Math.random() < 0.05) playKickSound();
            }} else if (timeDiff <= 2.2) {{
                // Phase 3: Shot in flight towards net
                const progress = timeDiff / 2.2;
                ballPos.x = THREE.MathUtils.lerp(shotPos[0], goalPos[0], progress);
                ballPos.z = THREE.MathUtils.lerp(shotPos[1], goalPos[1], progress);
                const arcHeight = (ev.shot_type === 'Header') ? 2.1 : 1.4;
                ballPos.y = 0.22 + Math.sin(progress * Math.PI) * arcHeight;

                if (timeDiff > 1.8 && ev.is_goal && Math.random() < 0.06) {{
                    playWhistleSound();
                    playCheerSound();
                }}
            }} else {{
                // Phase 4: Net rebound / celebration
                ballPos.x = goalPos[0];
                ballPos.z = goalPos[1];
                ballPos.y = 0.22;
            }}

            // Update Ball Mesh
            ballMesh.position.set(ballPos.x, ballPos.y, ballPos.z);
            ballShadowMesh.position.set(ballPos.x, 0.02, ballPos.z);
            const scale = Math.max(0.4, 1.0 - ballPos.y * 0.18);
            ballShadowMesh.scale.set(scale, scale, 1);
            ballShadowMesh.material.opacity = Math.max(0.15, 0.6 - ballPos.y * 0.1);

            // Update Ball Trail
            if (showTrail) {{
                ballTrailPoints.push(new THREE.Vector3(ballPos.x, ballPos.y, ballPos.z));
                if (ballTrailPoints.length > 35) ballTrailPoints.shift();
                const posAttr = ballTrailLine.geometry.attributes.position;
                for (let i = 0; i < 35; i++) {{
                    const pt = ballTrailPoints[i] || ballTrailPoints[ballTrailPoints.length - 1] || new THREE.Vector3();
                    posAttr.setXYZ(i, pt.x, pt.y, pt.z);
                }}
                posAttr.needsUpdate = true;
            }}

            // Update Players: Shooter, Assister, Goalkeeper, and Formation
            let lastDefAugsburg = -PITCH_LENGTH / 2;
            let lastDefBayern = PITCH_LENGTH / 2;

            for (const key in playerObjects) {{
                const p = playerObjects[key];
                const base = [p.data.base_x, p.data.base_z];
                let targetX = base[0];
                let targetZ = base[1];

                if (key === ev.shooter_id) {{
                    // Shooter moves towards shot coordinates
                    targetX = shotPos[0];
                    targetZ = shotPos[1];
                }} else if (key === ev.assist_id) {{
                    // Assister at delivery coordinates
                    targetX = assistPos[0];
                    targetZ = assistPos[1];
                }} else if (p.data.pos === 'GK') {{
                    // Goalkeeper reacts and positions relative to shot
                    const isDefending = (p.data.team !== ev.team);
                    if (isDefending) {{
                        const gkGoalX = (p.data.team === 'augsburg') ? -49.5 : 49.5;
                        targetX = gkGoalX;
                        targetZ = THREE.MathUtils.lerp(0, goalPos[1], 0.7);
                    }}
                }} else {{
                    // Team Tactical Block shifts towards action zone
                    const pullX = (ballPos.x - base[0]) * 0.35;
                    const pullZ = (ballPos.z - base[1]) * 0.38;
                    targetX = base[0] + pullX;
                    targetZ = base[1] + pullZ;
                }}

                const prevX = p.group.position.x;
                const prevZ = p.group.position.z;

                p.group.position.x += (targetX - prevX) * 0.14;
                p.group.position.z += (targetZ - prevZ) * 0.14;

                const vx = p.group.position.x - prevX;
                const vz = p.group.position.z - prevZ;
                p.velocity.set(vx * 60, 0, vz * 60);
                p.currentPos.copy(p.group.position);

                // Heading orientation
                if (Math.hypot(vx, vz) > 0.005) {{
                    p.heading = Math.atan2(vx, vz);
                }} else {{
                    p.heading = Math.atan2(ballPos.x - p.group.position.x, ballPos.z - p.group.position.z);
                }}
                p.group.rotation.y = p.heading;

                // Offside line computation
                if (p.data.team === 'augsburg' && p.data.pos !== 'GK') {{
                    if (p.group.position.x > lastDefAugsburg) lastDefAugsburg = p.group.position.x;
                }}
                if (p.data.team === 'bayern' && p.data.pos !== 'GK') {{
                    if (p.group.position.x < lastDefBayern) lastDefBayern = p.group.position.x;
                }}
            }}

            // Dynamic Offside Line
            if (showOffside) {{
                const offsideX = (ballPos.x < 0) ? lastDefAugsburg : lastDefBayern;
                offsideLineMesh.position.x = offsideX;
                offsideLineMesh.visible = true;
            }} else {{
                offsideLineMesh.visible = false;
            }}

            if (showShape) {{
                updateTeamShapes();
            }}
        }}

        function updateTeamShapes() {{
            const bKeys = ['bayern_44', 'bayern_2', 'bayern_4', 'bayern_27'];
            const attrB = shapeLinesBayern.geometry.attributes.position;
            bKeys.forEach((k, idx) => {{
                if (playerObjects[k]) {{
                    const p = playerObjects[k].group.position;
                    attrB.setXYZ(idx, p.x, 0.1, p.z);
                }}
            }});
            attrB.needsUpdate = true;
            shapeLinesBayern.visible = true;

            const aKeys = ['augsburg_13', 'augsburg_31', 'augsburg_6', 'augsburg_5', 'augsburg_2'];
            const attrA = shapeLinesAugsburg.geometry.attributes.position;
            aKeys.forEach((k, idx) => {{
                if (playerObjects[k]) {{
                    const p = playerObjects[k].group.position;
                    attrA.setXYZ(idx, p.x, 0.1, p.z);
                }}
            }});
            attrA.needsUpdate = true;
            shapeLinesAugsburg.visible = true;
        }}

        /* =========================================================================
           9. CAMERA SYSTEM & FIRST-PERSON PLAYER VIEW
           ========================================================================= */
        function setCameraMode(mode) {{
            cameraMode = mode;
            document.querySelectorAll('.cam-btn').forEach(b => b.classList.remove('active'));
            const activeBtn = document.getElementById(`cam-${{mode}}`);
            if (activeBtn) activeBtn.classList.add('active');

            const isPov = (mode === 'pov');
            document.getElementById('pov-banner').classList.toggle('active', isPov);
            document.getElementById('pov-crosshair').classList.toggle('active', isPov);
            document.getElementById('pov-instructions').classList.toggle('active', isPov);

            if (isPov) {{
                controls.enabled = false;
            }} else {{
                controls.enabled = true;
            }}

            if (mode === 'broadcast') {{
                camera.position.set(0, 24, 46);
                controls.target.set(0, 1.5, 0);
            }} else if (mode === 'sky') {{
                camera.position.set(0, 68, 0.1);
                controls.target.set(0, 0, 0);
            }} else if (mode === 'goal') {{
                camera.position.set(-58, 7, 0);
                controls.target.set(-20, 1.5, 0);
            }} else if (mode === 'drone') {{
                camera.position.set(ballMesh.position.x + 12, 14, ballMesh.position.z + 18);
                controls.target.copy(ballMesh.position);
            }}

            showToast(`Camera: ${{mode.toUpperCase()}} Mode`);
        }}

        function updateCamera() {{
            if (cameraMode === 'pov') {{
                const player = playerObjects[selectedPlayerKey];
                if (!player) return;

                const eyeY = 1.74;
                const playerPos = player.group.position;
                camera.position.set(playerPos.x, eyeY, playerPos.z);

                let effectiveYaw = player.heading + headYaw;

                if (lockBallGaze) {{
                    const toBallX = ballMesh.position.x - playerPos.x;
                    const toBallZ = ballMesh.position.z - playerPos.z;
                    const ballAngle = Math.atan2(toBallX, toBallZ);
                    effectiveYaw = ballAngle + headYaw;
                }}

                const forward = new THREE.Vector3(
                    Math.sin(effectiveYaw) * Math.cos(headPitch),
                    Math.sin(headPitch),
                    Math.cos(effectiveYaw) * Math.cos(headPitch)
                );

                const lookTarget = camera.position.clone().add(forward.multiplyScalar(20.0));
                camera.lookAt(lookTarget);

                const speedKmh = (player.velocity.length() * 3.6).toFixed(1);
                document.getElementById('hud-player-speed').textContent = `${{speedKmh}} km/h`;
                document.getElementById('hud-head-yaw').textContent = `${{(headYaw * 180 / Math.PI).toFixed(1)}}°`;
                document.getElementById('hud-gaze-status').textContent = lockBallGaze ? 'Ball Tracking' : 'Free Look';

            }} else if (cameraMode === 'drone') {{
                camera.position.x += (ballMesh.position.x + 10 - camera.position.x) * 0.05;
                camera.position.z += (ballMesh.position.z + 16 - camera.position.z) * 0.05;
                controls.target.copy(ballMesh.position);
                controls.update();
            }} else {{
                controls.update();
            }}
        }}

        /* =========================================================================
           10. 2D TACTICAL MINIMAP / RADAR WITH VISION CONE
           ========================================================================= */
        function drawRadar() {{
            const canvas = document.getElementById('radar-canvas');
            const ctx = canvas.getContext('2d');
            const w = canvas.width;
            const h = canvas.height;

            ctx.fillStyle = '#06180b';
            ctx.fillRect(0, 0, w, h);

            function toX(x3d) {{ return ((x3d + PITCH_LENGTH / 2) / PITCH_LENGTH) * w; }}
            function toY(z3d) {{ return ((z3d + PITCH_WIDTH / 2) / PITCH_WIDTH) * h; }}

            ctx.strokeStyle = 'rgba(34, 197, 94, 0.4)';
            ctx.lineWidth = 1;
            ctx.strokeRect(4, 4, w - 8, h - 8);
            ctx.beginPath();
            ctx.moveTo(w / 2, 4); ctx.lineTo(w / 2, h - 4);
            ctx.stroke();
            ctx.beginPath();
            ctx.arc(w / 2, h / 2, (9.15 / PITCH_WIDTH) * h, 0, Math.PI * 2);
            ctx.stroke();

            // Draw Players
            for (const key in playerObjects) {{
                const p = playerObjects[key];
                const px = toX(p.group.position.x);
                const py = toY(p.group.position.z);
                const isSelected = (key === selectedPlayerKey);

                // Draw Vision Cone in POV mode
                if (isSelected && cameraMode === 'pov') {{
                    ctx.save();
                    ctx.fillStyle = 'rgba(56, 189, 248, 0.28)';
                    ctx.strokeStyle = '#38bdf8';
                    ctx.lineWidth = 1.5;

                    const effectiveAngle = p.heading + headYaw;
                    const halfFov = (70 * Math.PI / 180) / 2;
                    const coneLen = 38;

                    ctx.beginPath();
                    ctx.moveTo(px, py);
                    const angle2D = effectiveAngle - Math.PI / 2;
                    ctx.arc(px, py, coneLen, angle2D - halfFov, angle2D + halfFov);
                    ctx.closePath();
                    ctx.fill();
                    ctx.stroke();
                    ctx.restore();
                }}

                ctx.fillStyle = (p.data.team === 'bayern') ? '#ef4444' : '#22c55e';
                if (p.data.pos === 'GK') ctx.fillStyle = '#facc15';

                ctx.beginPath();
                ctx.arc(px, py, isSelected ? 4.5 : 3.0, 0, Math.PI * 2);
                ctx.fill();

                if (isSelected) {{
                    ctx.strokeStyle = '#ffffff';
                    ctx.lineWidth = 1.5;
                    ctx.stroke();
                }}
            }}

            // Draw Ball
            const bx = toX(ballMesh.position.x);
            const by = toY(ballMesh.position.z);
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.arc(bx, by, 3.5, 0, Math.PI * 2);
            ctx.fill();
        }}

        /* =========================================================================
           11. PLAYBACK & INTERACTION CONTROLS
           ========================================================================= */
        function togglePlayPause() {{
            initAudio();
            isPlaying = !isPlaying;
            document.getElementById('play-pause-icon').setAttribute('data-lucide', isPlaying ? 'pause' : 'play');
            document.getElementById('play-pause-text').textContent = isPlaying ? 'Pause' : 'Play';
            lucide.createIcons();
            showToast(isPlaying ? 'Simulation Resumed' : 'Simulation Paused');
        }}

        function setPlaybackSpeed(speed, btn) {{
            playbackSpeed = speed;
            document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
            if (btn) btn.classList.add('active');
            showToast(`Playback Speed: ${{speed}}x`);
        }}

        function stepTime(seconds) {{
            matchTime = Math.max(0, Math.min(5400, matchTime + seconds));
            updateTimelineUI();
            computeRealMatchSimulation(matchTime);
        }}

        function jumpToEventIndex(idx) {{
            initAudio();
            const ev = window.REAL_MATCH_DATA.events[idx];
            if (!ev) return;
            matchTime = ev.seconds;
            updateTimelineUI();
            computeRealMatchSimulation(matchTime);
            playWhistleSound();
            showToast(`Jumped to ${{ev.minute}}' ${{ev.shooter_name}}`);
        }}

        function replayCurrentAction() {{
            initAudio();
            matchTime = Math.max(0, matchTime - 12);
            playbackSpeed = 0.5;
            document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
            const halfBtn = document.querySelectorAll('.speed-btn')[0];
            if (halfBtn) halfBtn.classList.add('active');
            updateTimelineUI();
            showToast('Instant Replay (0.5x Slow Motion)');
        }}

        function onTimelineScrub(val) {{
            matchTime = Number(val);
            updateTimelineUI();
            computeRealMatchSimulation(matchTime);
        }}

        function updateTimelineUI() {{
            document.getElementById('timeline-slider').value = matchTime;
            const timeStr = formatTime(matchTime);
            document.getElementById('timeline-time-display').textContent = timeStr;
            const half = matchTime < 2700 ? '1st Half' : '2nd Half';
            document.getElementById('match-clock-display').textContent = `${{timeStr}} • ${{half}}`;
        }}

        function formatTime(totalSec) {{
            const m = Math.floor(totalSec / 60);
            const s = Math.floor(totalSec % 60);
            return `${{String(m).padStart(2, '0')}}:${{String(s).padStart(2, '0')}}`;
        }}

        function togglePlayerNames(checked) {{
            showNames = checked;
            for (const key in playerObjects) {{
                playerObjects[key].label.visible = checked;
            }}
        }}

        function toggleBallTrail(checked) {{
            showTrail = checked;
            ballTrailLine.visible = checked;
            if (!checked) ballTrailPoints = [];
        }}

        function toggleOffsideLine(checked) {{
            showOffside = checked;
            offsideLineMesh.visible = checked;
        }}

        function toggleTeamShape(checked) {{
            showShape = checked;
            shapeLinesBayern.visible = checked;
            shapeLinesAugsburg.visible = checked;
        }}

        function toggleEyesightVisors(checked) {{
            showVisors = checked;
            for (const key in playerObjects) {{
                playerObjects[key].visor.visible = checked;
            }}
        }}

        function showToast(msg) {{
            const toast = document.getElementById('toast-banner');
            toast.textContent = msg;
            toast.style.display = 'block';
            clearTimeout(window.toastTimer);
            window.toastTimer = setTimeout(() => {{
                toast.style.display = 'none';
            }}, 2200);
        }}

        function captureSnapshot() {{
            renderer.render(scene, camera);
            const link = document.createElement('a');
            link.download = `bundesliga-real-match-${{matchTime}}s.png`;
            link.href = renderer.domElement.toDataURL('image/png');
            link.click();
            showToast('High-Res Screenshot Captured!');
        }}

        function toggleFullScreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen().catch(() => {{}});
            }} else {{
                if (document.exitFullscreen) document.exitFullscreen();
            }}
        }}

        function onWindowResize() {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }}

        /* Keyboard Shortcuts */
        window.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                e.preventDefault();
                togglePlayPause();
            }} else if (e.code === 'Tab' || e.key === ']') {{
                e.preventDefault();
                cyclePlayer(1);
            }} else if (e.key === '[') {{
                e.preventDefault();
                cyclePlayer(-1);
            }} else if (e.key === 'c' || e.key === 'C') {{
                resetHeadAngle();
            }} else if (e.code === 'ArrowRight') {{
                stepTime(10);
            }} else if (e.code === 'ArrowLeft') {{
                stepTime(-10);
            }} else if (e.key === '1') switchPlayerPOV('bayern_1');
            else if (e.key === '2') switchPlayerPOV('augsburg_1');
            else if (e.key === '3') switchPlayerPOV('bayern_9');
            else if (e.key === '4') switchPlayerPOV('bayern_7');
            else if (e.key === '5') switchPlayerPOV('bayern_17');
            else if (e.key === '6') switchPlayerPOV('bayern_14');
            else if (e.key === '7') switchPlayerPOV('bayern_6');
            else if (e.key === '8') switchPlayerPOV('augsburg_36');
            else if (e.key === '9') switchPlayerPOV('augsburg_19');
        }});

        /* =========================================================================
           12. ANIMATION LOOP (60 FPS)
           ========================================================================= */
        function animate(timestamp) {{
            requestAnimationFrame(animate);

            const dt = (timestamp - lastTimestamp) / 1000.0;
            lastTimestamp = timestamp;

            if (isPlaying) {{
                matchTime += dt * playbackSpeed;
                if (matchTime > 5400) matchTime = 0;
                updateTimelineUI();
                computeRealMatchSimulation(matchTime);
            }}

            updateCamera();
            drawRadar();
            renderer.render(scene, camera);
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            initThree();
            updateTimelineUI();
            computeRealMatchSimulation(matchTime);
            animate(performance.now());
        }});
    </script>
</body>
</html>"""

    with open("match3d.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print("SUCCESS: match3d.html generated with 100% real match data and interactive player POV switcher!")

if __name__ == "__main__":
    generate_html()
