import json
import os
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

def build_tipps_excel():
    # 1. Load predictions dataset
    json_path = "models/model_v1_v2_baseline/predictions_26_27_all.json"
    if not os.path.exists(json_path):
        json_path = "predictions_26_27_all.json"
        
    with open(json_path, "r", encoding="utf-8") as f:
        matches_data = json.load(f)

    # Team code mapping
    team_codes = {
        "Bayern Munich": "bay",
        "VfB Stuttgart": "vfb",
        "RasenBallsport Leipzig": "rb",
        "Borussia M.Gladbach": "bmg",
        "Mainz 05": "mai",
        "Paderborn": "pad",
        "Union Berlin": "uni",
        "Eintracht Frankfurt": "fra",
        "FC Cologne": "fck",
        "Hoffenheim": "hoff",
        "Elversberg": "sve",
        "Bayer Leverkusen": "b04",
        "Borussia Dortmund": "bvb",
        "Hamburger SV": "hsv",
        "Freiburg": "scf",
        "Werder Bremen": "bre",
        "Augsburg": "fca",
        "Schalke 04": "s04"
    }

    # User's existing tips for Matchday 4
    md4_user_tips = {
        "bay - uni": "3:0",
        "bre - fca": "1:2",
        "fra - scf": "1:1",
        "bmg - mai": "0:2",
        "hsv - fck": "1:1",
        "vfb - bvb": "2:2",
        "b04 - rb": "2:1",
        "s04 - sve": "2:1",
        "pad - hoff": "0:1"
    }

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Tipps Saison 2026-27"
    ws.views.sheetView[0].showGridLines = True

    # Fonts & Styles
    title_font = Font(name="Calibri", size=16, bold=True, color="FFFFFF")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    md_header_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    bold_font = Font(name="Calibri", size=11, bold=True)
    normal_font = Font(name="Calibri", size=11)
    sub_font = Font(name="Calibri", size=10, italic=True, color="666666")

    title_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_fill = PatternFill(start_color="334155", end_color="334155", fill_type="solid")
    md_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    user_tip_fill = PatternFill(start_color="FEF08A", end_color="FEF08A", fill_type="solid") # Soft yellow for user tips
    model_tip_fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    accent_green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")

    thin_border_side = Side(border_style="thin", color="CBD5E1")
    thick_bottom_side = Side(border_style="medium", color="475569")
    cell_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
    md_border = Border(left=thin_border_side, right=thin_border_side, top=thick_bottom_side, bottom=thick_bottom_side)

    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    align_right = Alignment(horizontal="right", vertical="center")

    # Title Block
    ws.merge_cells("A1:H1")
    title_cell = ws["A1"]
    title_cell.value = "BUNDESLIGA SAISON 2026/2027 — TIPP-VERGLEICH (ICH VS. AI MODEL)"
    title_cell.font = title_font
    title_cell.fill = title_fill
    title_cell.alignment = align_center
    ws.row_dimensions[1].height = 40

    # Summary Panel Block (Rows 3-6)
    ws.merge_cells("A3:H3")
    summary_title = ws["A3"]
    summary_title.value = "SAISON-ÜBERSICHT & STAND (AUTOMATISCHE AUSWERTUNG)"
    summary_title.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    summary_title.fill = PatternFill(start_color="475569", end_color="475569", fill_type="solid")
    summary_title.alignment = align_center
    ws.row_dimensions[3].height = 22

    # Score Board Table in Rows 4-5
    ws["B4"] = "Gesamtpunkte Ich:"
    ws["B4"].font = bold_font
    ws["C4"] = "=SUM(G9:G450)"
    ws["C4"].font = Font(name="Calibri", size=12, bold=True, color="166534")
    ws["C4"].fill = accent_green_fill
    ws["C4"].alignment = align_center

    ws["E4"] = "Gesamtpunkte AI Model:"
    ws["E4"].font = bold_font
    ws["F4"] = "=SUM(H9:H450)"
    ws["F4"].font = Font(name="Calibri", size=12, bold=True, color="1E40AF")
    ws["F4"].fill = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")
    ws["F4"].alignment = align_center

    # Main Table Headers (Row 8)
    headers = [
        "Begegnung",
        "Mein Tipp",
        "Model Tipp",
        "Model Wahrscheinlichkeiten (H / D / A)",
        "Model Tendenz",
        "Reales Ergebnis",
        "Punkte (Ich)",
        "Punkte (Model)"
    ]
    
    ws.row_dimensions[8].height = 28
    for col_idx, text in enumerate(headers, 1):
        cell = ws.cell(row=8, column=col_idx)
        cell.value = text
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = align_center
        cell.border = cell_border

    current_row = 9

    # Group matches by matchday
    for md in range(1, 35):
        md_matches = [m for m in matches_data if m['matchday'] == md]
        
        # Matchday Section Header
        ws.merge_cells(start_row=current_row, start_column=1, end_row=current_row, end_column=8)
        md_cell = ws.cell(row=current_row, column=1)
        md_cell.value = f"--- {md}. Spieltag ---"
        md_cell.font = md_header_font
        md_cell.fill = md_fill
        md_cell.alignment = align_center
        ws.row_dimensions[current_row].height = 24
        
        for c in range(1, 9):
            ws.cell(row=current_row, column=c).border = md_border
            
        current_row += 1

        for m in md_matches:
            h_code = team_codes.get(m['home_clean'], m['home_clean'][:3].lower())
            a_code = team_codes.get(m['away_clean'], m['away_clean'][:3].lower())
            match_str = f"{h_code} - {a_code}"

            p_h = round(m['p_home'] * 100)
            p_d = round(m['p_draw'] * 100)
            p_a = round(m['p_away'] * 100)
            prob_str = f"{p_h}% / {p_d}% / {p_a}%"

            tendenz = "Heimsieg" if m['p_home'] > max(m['p_draw'], m['p_away']) else ("Auswärtssieg" if m['p_away'] > max(m['p_home'], m['p_draw']) else "Unentschieden")
            
            # User tip for Matchday 4
            user_tip = ""
            if md == 4 and match_str in md4_user_tips:
                user_tip = md4_user_tips[match_str]
            elif md == 4 and match_str.replace(" ", "") in md4_user_tips:
                user_tip = md4_user_tips[match_str.replace(" ", "")]

            ws.row_dimensions[current_row].height = 22

            # Col A: Match Code
            cell_a = ws.cell(row=current_row, column=1, value=match_str)
            cell_a.alignment = align_center
            cell_a.font = bold_font
            cell_a.border = cell_border

            # Col B: Mein Tipp
            cell_b = ws.cell(row=current_row, column=2, value=user_tip)
            cell_b.alignment = align_center
            cell_b.font = bold_font
            cell_b.fill = user_tip_fill
            cell_b.border = cell_border

            # Col C: Model Tipp
            cell_c = ws.cell(row=current_row, column=3, value=m['score'])
            cell_c.alignment = align_center
            cell_c.font = bold_font
            cell_c.fill = model_tip_fill
            cell_c.border = cell_border

            # Col D: Probabilities
            cell_d = ws.cell(row=current_row, column=4, value=prob_str)
            cell_d.alignment = align_center
            cell_d.font = normal_font
            cell_d.border = cell_border

            # Col E: Tendenz
            cell_e = ws.cell(row=current_row, column=5, value=tendenz)
            cell_e.alignment = align_center
            cell_e.font = normal_font
            cell_e.border = cell_border

            # Col F: Reales Ergebnis
            cell_f = ws.cell(row=current_row, column=6, value="")
            cell_f.alignment = align_center
            cell_f.font = bold_font
            cell_f.border = cell_border

            # Col G: Punkte (Ich) — Kicktipp formula (3 pts exact, 2 pts diff, 1 pt tendenz)
            r = current_row
            formula_ich = f'=IF(OR(B{r}="", F{r}=""), "", IF(B{r}=F{r}, 3, IF(OR(AND(VALUE(LEFT(B{r},FIND(":",B{r})-1))>VALUE(RIGHT(B{r},LEN(B{r})-FIND(":",B{r}))), VALUE(LEFT(F{r},FIND(":",F{r})-1))>VALUE(RIGHT(F{r},LEN(F{r})-FIND(":",F{r})))), AND(VALUE(LEFT(B{r},FIND(":",B{r})-1))<VALUE(RIGHT(B{r},LEN(B{r})-FIND(":",B{r}))), VALUE(LEFT(F{r},FIND(":",F{r})-1))<VALUE(RIGHT(F{r},LEN(F{r})-FIND(":",F{r})))), AND(VALUE(LEFT(B{r},FIND(":",B{r})-1))=VALUE(RIGHT(B{r},LEN(B{r})-FIND(":",B{r}))), VALUE(LEFT(F{r},FIND(":",F{r})-1))=VALUE(RIGHT(F{r},LEN(F{r})-FIND(":",F{r}))))), IF(VALUE(LEFT(B{r},FIND(":",B{r})-1))-VALUE(RIGHT(B{r},LEN(B{r})-FIND(":",B{r})))=VALUE(LEFT(F{r},FIND(":",F{r})-1))-VALUE(RIGHT(F{r},LEN(F{r})-FIND(":",F{r}))), 2, 1), 0)))'
            cell_g = ws.cell(row=current_row, column=7, value=formula_ich)
            cell_g.alignment = align_center
            cell_g.font = bold_font
            cell_g.border = cell_border

            # Col H: Punkte (Model)
            formula_model = f'=IF(OR(C{r}="", F{r}=""), "", IF(C{r}=F{r}, 3, IF(OR(AND(VALUE(LEFT(C{r},FIND(":",C{r})-1))>VALUE(RIGHT(C{r},LEN(C{r})-FIND(":",C{r}))), VALUE(LEFT(F{r},FIND(":",F{r})-1))>VALUE(RIGHT(F{r},LEN(F{r})-FIND(":",F{r})))), AND(VALUE(LEFT(C{r},FIND(":",C{r})-1))<VALUE(RIGHT(C{r},LEN(C{r})-FIND(":",C{r}))), VALUE(LEFT(F{r},FIND(":",F{r})-1))<VALUE(RIGHT(F{r},LEN(F{r})-FIND(":",F{r})))), AND(VALUE(LEFT(C{r},FIND(":",C{r})-1))=VALUE(RIGHT(C{r},LEN(C{r})-FIND(":",C{r}))), VALUE(LEFT(F{r},FIND(":",F{r})-1))=VALUE(RIGHT(F{r},LEN(F{r})-FIND(":",F{r}))))), IF(VALUE(LEFT(C{r},FIND(":",C{r})-1))-VALUE(RIGHT(C{r},LEN(C{r})-FIND(":",C{r})))=VALUE(LEFT(F{r},FIND(":",F{r})-1))-VALUE(RIGHT(F{r},LEN(F{r})-FIND(":",F{r}))), 2, 1), 0)))'
            cell_h = ws.cell(row=current_row, column=8, value=formula_model)
            cell_h.alignment = align_center
            cell_h.font = bold_font
            cell_h.border = cell_border

            current_row += 1

    # Auto-adjust Column Widths
    column_widths = {
        "A": 18,
        "B": 14,
        "C": 14,
        "D": 38,
        "E": 20,
        "F": 18,
        "G": 14,
        "H": 16
    }
    for col_letter, width in column_widths.items():
        ws.column_dimensions[col_letter].width = width

    target_file = "meineTipps.xlsx"
    wb.save(target_file)
    print(f"SUCCESS: Saved updated '{target_file}' with 34 matchdays ({current_row - 1} rows)!")

if __name__ == "__main__":
    build_tipps_excel()
