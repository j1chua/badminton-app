import streamlit as st
import pandas as pd
import os
import json

# 1. Page Configuration
st.set_page_config(page_title="GCCP SMASH S1 2026", layout="wide")

# File Constants
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
ADMIN_PW = "pogisiJordan"

# UI Constants
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

# 2. Global Styling (Be Vietnam Pro)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;600;800&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, table, h1, h2, h3 {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; border-radius: 8px; overflow: hidden; }
    .m-table th { background-color: #f8f9fa; text-align: center !important; padding: 14px; border: 1px solid #dee2e6; font-weight: 800; color: #333; }
    .m-table td { text-align: center !important; padding: 12px; border: 1px solid #dee2e6; vertical-align: middle; }
    
    /* High Stakes Special Match Styling */
    .high-stakes { background-color: #fffde7 !important; border: 2px solid #fbc02d !important; }
    
    .badge-semis { background: #eceff1; color: #455a64; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: 800; border: 1px solid #b0bec5; margin-right: 8px; display: inline-block; }
    .badge-finals { background: #fff9c4; color: #fbc02d; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: 800; border: 2px solid #fbc02d; margin-right: 8px; display: inline-block; color: #000; }
    
    .status-pending { color: #adb5bd; font-style: italic; font-size: 0.85em; font-weight: 400; }

    .trademark { position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%); font-size: 11px; color: #bbb; letter-spacing: 3px; z-index: 1000; text-align: center; width: 100%; font-weight: 300; }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

# 3. Fail-Safe Data Loading
@st.cache_data
def load_data(mtime):
    if not os.path.exists(FN): return None, {}, {}
    try:
        df = pd.read_csv(FN, header=None).fillna("")
        matches, team_colors, db = [], {}, {}
        day_context = "Day 1"
        
        # Block Mapping: [Time, Bracket, T1, T2, S1T1, S2T1, S1T2, S2T2]
        blocks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
        
        for idx, row in df.iterrows():
            row_str = " ".join([str(x) for x in row]).upper()
            if "DAY 2" in row_str: day_context = "Day 2"
            elif "DAY 1" in row_str: day_context = "Day 1"
            
            for c in blocks:
                try:
                    # Basic Info
                    t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                    bracket_raw = str(row[c[1]]).strip().upper()
                    if not bracket_raw: continue
                    
                    is_semis = "SEMIS" in bracket_raw
                    is_finals = "FINALS" in bracket_raw
                    
                    # Accept if valid team names OR if it's a special stage placeholder
                    if not (is_semis or is_finals) and ("|" not in t1 or "|" not in t2):
                        continue
                    if t1 == "" or t2 == "": continue
                        
                    # Find color mapping
                    base_color = "WHITE"
                    for color_key in EMOJIS.keys():
                        if color_key in bracket_raw:
                            base_color = color_key
                            break
                    
                    # Court Detection
                    court_val = "Court ?"
                    for r_scan in range(idx, -1, -1):
                        scan_text = str(df.iloc[r_scan, c[2]]).upper()
                        if "COURT" in scan_text:
                            court_val = scan_text.strip()
                            break
                    
                    m_id = f"{day_context[0]}{idx}{c[0]}"
                    matches.append({
                        "ID": m_id, "Day": day_context, "T": str(row[c[0]]).strip(), 
                        "T1": t1, "T2": t2, "P1": t1.replace("|", " AND "), "P2": t2.replace("|", " AND "),
                        "Bracket": bracket_raw, "Emoji": EMOJIS.get(base_color, "🏸"), 
                        "Court": court_val, "IsSemis": is_semis, "IsFinals": is_finals
                    })
                    
                    if "|" in t1: team_colors[t1] = base_color
                    if "|" in t2: team_colors[t2] = base_color
                    
                    # Hardened Score Parsing (Fail-safe against non-numbers)
                    scores = []
                    for col_idx in [c[4], c[5], c[6], c[7]]:
                        val = str(row[col_idx]).strip()
                        try:
                            scores.append(int(float(val)))
