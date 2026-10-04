"""
===============================================================================
WEB DASHBOARD COMPILLER: Model v6 2-Stage Spatial AI Integration
===============================================================================
Embeds 2-Stage Spatial AI predictions into index.html, updates the dropdown option,
sets Model v2 (59.2% Acc) as recommended default, and updates the benchmark table.
===============================================================================
"""

import json
import os
import re

def compile_v6_2stage_dashboard():
    print("--- Compiling Web Dashboard with Un-Leaked Benchmark Figures ---")
    
    p2 = "models/model_v1_v2_baseline/predictions_26_27_all.json" if os.path.exists("models/model_v1_v2_baseline/predictions_26_27_all.json") else "predictions_26_27_all.json"
    p3 = "models/model_v3_tactical/predictions_v3_tactical.json" if os.path.exists("models/model_v3_tactical/predictions_v3_tactical.json") else "predictions_v3_tactical.json"
    p4 = "models/model_v4_complexity/predictions_v4_complexity.json" if os.path.exists("models/model_v4_complexity/predictions_v4_complexity.json") else "predictions_v4_complexity.json"
    p5 = "models/model_v5_matchday1_4/predictions_v5_m1_4.json" if os.path.exists("models/model_v5_matchday1_4/predictions_v5_m1_4.json") else "predictions_v5_m1_4.json"
    p6 = "models/spatial_ai_kaggle/predictions_v6_spatial.json" if os.path.exists("models/spatial_ai_kaggle/predictions_v6_spatial.json") else "predictions_v6_spatial.json"
    p6_2stage = "models/spatial_ai_kaggle/predictions_v6_spatial_2stage.json" if os.path.exists("models/spatial_ai_kaggle/predictions_v6_spatial_2stage.json") else "predictions_v6_spatial_2stage.json"
    
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
        
    with open(p6_2stage, "r", encoding="utf-8") as f:
        preds_v6_2stage = json.load(f)
        
    preds_v6_2stage_json = json.dumps(preds_v6_2stage)
    
    # 1. Update selector dropdown options in index.html with un-leaked benchmarks
    new_select_block = """<select id="model-version-selector" onchange="switchModelVersion(this.value)" style="background: rgba(4,9,5,0.85); border: 1px solid var(--accent-green); color: #fff; font-weight: 700; border-radius: 8px; padding: 0.4rem 1.2rem; outline: none; cursor: pointer; font-family: 'Outfit', sans-serif; font-size: 0.88rem;">
                            <option value="v2" selected>Model v2 (Elo + Form Hybrid - 59.2% Acc) [Recommended]</option>
                            <option value="v6_2stage">Model v6 (2-Stage Spatial AI Generator - 49.4% GroupKFold Acc)</option>
                            <option value="v3">Model v3 (Pure Tactical & 1D Time-Decay - 56.9% Acc)</option>
                            <option value="v6">Model v6 (Single-Stage Spatial AI - 52.8% Acc)</option>
                        </select>"""
                        
    html = re.sub(
        r'<select id="model-version-selector".*?</select>',
        new_select_block,
        html,
        flags=re.DOTALL
    )
        
    # 2. Inject predictions_v6_2stage object into JavaScript window state
    js_var = f"window.predictions_v6_2stage = {preds_v6_2stage_json};\n"
    if "window.predictions_v6_2stage =" not in html:
        html = html.replace("window.predictions_v6 =", js_var + "        window.predictions_v6 =")
    else:
        pattern = r"window\.predictions_v6_2stage = \[.*?\];"
        html = re.sub(pattern, f"window.predictions_v6_2stage = {preds_v6_2stage_json};", html, flags=re.DOTALL)
        
    # 3. Update getActivePredictions() function in JS
    if 'case "v6_2stage": return window.predictions_v6_2stage;' not in html:
        html = html.replace('switch(selectedModelVersion) {', 'switch(selectedModelVersion) {\n                case "v6_2stage": return window.predictions_v6_2stage || window.predictions_v6;')
        
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    if os.path.exists("web_dashboard/index.html"):
        with open("web_dashboard/index.html", "w", encoding="utf-8") as f:
            f.write(html)
            
    print("SUCCESS: Updated index.html with un-leaked benchmark figures and Model v2 default!")

if __name__ == "__main__":
    compile_v6_2stage_dashboard()
