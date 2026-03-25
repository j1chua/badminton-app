import streamlit as st
import pandas as pd
import os
import json

# 1. Page Configuration
st.set_page_config(page_title="GCCP SMASH S1 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
COLOR_MAP = {
    "BLACK": "#000000", "RED": "#d32f2f", "GREEN": "#2e7d32", 
    "PURPLE": "#7b1fa2", "WHITE": "#9e9e9e", "YELLOW": "#fbc02d"
}
ADMIN_PW = "pogisiJordan"

# 2. Styling including High-Stakes highlighting
st.markdown("""
<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-family: sans-serif; }
    .m-table th { background-color: #f0f2f6; text-align: center !important; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    
    /* High Stakes Special Match Styling */
    .high-stakes { 
        background-color: #fffde7 !important; 
        border: 2px solid #fbc02d !important; 
        font-weight: bold;
    }
    .badge-special {
        background: #fbc02d; color: #000; padding: 2px 8px; 
        border-radius: 12px; font-size: 0.7em; margin-right: 8px;
        font-weight: 800; border: 1px solid #000;
    }

    .trademark {
        position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%);
        font-size: 10px; color: #999; font-family: sans-serif;
        letter-spacing: 2px; z-index: 1000; text-align: center; width: 100%;
    }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

# 3. Enhanced Data Loading Logic
@st.cache_data
def load_data(mtime):
    if not os.path.exists(FN): return None, {}, {}
    try:
        df = pd.read_csv(FN, header=None).fillna("")
        matches, team_colors, db = [], {}, {}
        day = "Day 1"
        blocks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
        for idx, row in df.iterrows():
            txt = " ".join([str(x) for x in row]).upper()
            if "DAY 2" in txt: day = "Day 2"
            elif "DAY 1" in txt: day = "Day 1"
            
            for c in blocks:
                try:
                    t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                    bracket_str = str(row[c[1]]).strip().upper()
                    
                    # VALIDATION: Accept if it's a team name (contains |) OR a special match (SEMIS/FINALS)
                    is_special_bracket = "SEMIS" in bracket_str or "FINALS" in bracket_str
                    if not is_special_bracket and ("|" not in t1 or "|" not in t2):
                        continue
                    if t1 == "" or t2 == "": continue
                        
                    # Find base color for mapping
                    base_color = "WHITE"
                    for color in EMOJIS.keys():
                        if color in bracket_str: base_color = color; break
                    
                    time_val, emoji = str(row[c[0]]).strip(), EMOJIS.get(base_color, "🏸")
                    
                    # Court detection logic
                    court = "Court ?"
                    for r_idx in range(idx, -1, -1):
                        val = str(df.iloc[r_idx, c[2]]).upper()
                        if "COURT" in val: court = val.strip(); break
                    
                    p1_d, p2_d = t1.replace("|", " AND "), t2.replace("|", " AND ")
                    m_id = f"{day[:1]}{idx}{c[0]}"
                    
                    matches.append({
                        "ID": m_id, "Day": day, "T": time_val, "T1": t1, "T2": t2, 
                        "P1": p1_d, "P2": p2_d, "Bracket": bracket_str, 
                        "BaseColor": base_color, "Emoji": emoji, "Court": court
                    })
                    if "|" in t1: team_colors[t1] = base_color
                    if "|" in t2: team_colors[t2] = base_color
                    
                    sc = [int(float(row[col])) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7]]]
                    w1, w2 = (sc[0]>sc[2])+(sc[1]>sc[3]), (sc[2]>sc[0])+(sc[3]>sc[1])
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "w1":w1, "w2":w2}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# App Logic
st.title("🏸 GCCP SMASH S1 2026")
file_mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(file_mtime)

if sch is not None and not sch.empty:
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])
    
    # Standings & Day 1 logic remain standard...
    # (Omitted for brevity, but same as previous version)

    # --- DAY 2 TAB ---
    with tabs[2]:
        q2 = st.text_input("🔍 Search Day 2 Matches", key="q2").lower()
        rows = []
        day2_df = sch[sch["Day"] == "Day 2"].copy().sort_values(by=["Court", "T"])
        
        for _, r in day2_df.iterrows():
            if q2 in r['T1'].lower() or q2 in r['T2'].lower() or q2 in r['Bracket'].lower():
                is_special = "SEMIS" in r['Bracket'] or "FINALS" in r['Bracket']
                row_style = 'class="high-stakes"' if is_special else ""
                badge = '<span class="badge-special">🏆 ELIMINATION</span>' if is_special else ""
                
                d = csv_db.get(r["ID"])
                s1, s2 = "--", "--"
                if d: s1, s2 = f"{d['s1']} - {d['s3']}", f"{d['s2']} - {d['s4']}"
                
                rows.append(f"""
                <tr {row_style}>
                    <td>{r['Court']}</td>
                    <td>{r['T']}</td>
                    <td>{r['Emoji']} {r['Bracket']}</td>
                    <td>{badge} {r['P1']} <b>vs</b> {r['P2']}</td>
                    <td>{s1}</td>
                    <td>{s2}</td>
                </tr>
                """)
        
        if rows:
            st.write(f"""
            <table class="m-table">
                <thead><tr><th>Court</th><th>Time</th><th>Bracket</th><th>Match</th><th>Set 1</th><th>Set 2</th></tr></thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
            """, unsafe_allow_html=True)
        else:
            st.info("No matches found for Day 2.")

    # (Admin & Finals logic remains same as previous version)
