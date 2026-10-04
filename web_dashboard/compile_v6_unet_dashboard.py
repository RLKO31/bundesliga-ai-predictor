"""
===============================================================================
WEB DASHBOARD COMPILLER: 2D Attention U-Net Heatmap Visualizer Integration
===============================================================================
Embeds predicted_fixture_heatmaps_v6.json into index.html and updates the 
JavaScript canvas renderer for tactical pitch maps.
===============================================================================
"""

import json
import os
import re

def compile_v6_unet_dashboard():
    print("--- Compiling Web Dashboard with 2D Attention U-Net Heatmaps ---")
    
    heatmap_json_path = "models/spatial_ai_kaggle/predicted_fixture_heatmaps_v6.json"
    if not os.path.exists(heatmap_json_path):
        heatmap_json_path = "predicted_fixture_heatmaps_v6.json"
        
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    with open(heatmap_json_path, "r", encoding="utf-8") as f:
        heatmaps = json.load(f)
        
    heatmaps_json = json.dumps(heatmaps)
    
    # 1. Inject window.predicted_fixture_heatmaps = [...] into JS state
    js_var = f"window.predicted_fixture_heatmaps = {heatmaps_json};\n"
    if "window.predicted_fixture_heatmaps =" not in html:
        html = html.replace("window.predictions_v6_2stage =", js_var + "        window.predictions_v6_2stage =")
    else:
        pattern = r"window\.predicted_fixture_heatmaps = \[.*?\];"
        html = re.sub(pattern, f"window.predicted_fixture_heatmaps = {heatmaps_json};", html, flags=re.DOTALL)
        
    # 2. Add canvas element inside pitch-visualizer if not present
    canvas_html = '<canvas id="pitch-heatmap-canvas" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; opacity: 0.55; z-index: 1; border-radius: 14px;"></canvas>'
    if 'id="pitch-heatmap-canvas"' not in html:
        html = html.replace('<div class="pitch-lines"></div>', canvas_html + '\n                    <div class="pitch-lines"></div>')
        
    # 3. Update renderTacticalPitchMatch JS function to draw heatmaps on canvas
    js_render_func = """
        function drawPitchHeatmapCanvas(gridData) {
            const canvas = document.getElementById("pitch-heatmap-canvas");
            if (!canvas || !gridData || gridData.length === 0) return;
            const ctx = canvas.getContext("2d");
            const rows = gridData.length;
            const cols = gridData[0].length;
            canvas.width = cols * 10;
            canvas.height = rows * 10;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            for (let r = 0; r < rows; r++) {
                for (let c = 0; c < cols; c++) {
                    const val = gridData[r][c];
                    if (val > 0.05) {
                        const alpha = Math.min(val * 0.85, 0.85);
                        const red = Math.floor(255 * val);
                        const green = Math.floor(255 * (1 - val * 0.5));
                        ctx.fillStyle = `rgba(${red}, ${green}, 50, ${alpha})`;
                        ctx.fillRect(c * 10, r * 10, 10, 10);
                    }
                }
            }
        }
    """
    
    if "function drawPitchHeatmapCanvas" not in html:
        html = html.replace("function renderTacticalPitchMatch", js_render_func + "\n        function renderTacticalPitchMatch")
        
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Integrated 2D Attention U-Net Heatmaps into index.html dashboard!")

if __name__ == "__main__":
    compile_v6_unet_dashboard()
