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
COLOR_MAP = {
    "BLACK": "#000000", "RED": "#d32f2f", "GREEN": "#2e7d32", 
    "PURPLE": "#7b1fa2", "WHITE": "#9e9e9e", "YELLOW": "#fbc02d"
}

# 2. Styling & Custom Typography (Be Vietnam Pro)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@100;300;400;600;800&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, table {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .m-table th { background-color: #f0f2f6; text-align: center !important; padding: 12px; border: 1px solid #ddd; font-weight: 800; }
    .m-table td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    
    .high-stakes { background-color: #fffde7 !important; border: 2px solid #fbc02d !important; font-weight: 600; }
    
    /* Dynamic Badges */
    .badge-semis { background: #e0e0e0; color: #424242; padding: 2px 8px; border-radius: 12px; font-size: 0.7em; font-weight: 800; border: 1px solid #9e9e9e; margin-right: 5px; }
    .badge-finals { background: #fbc02d; color: #000; padding: 2px 8px; border-radius: 12px; font-size: 0.7em; font-weight: 800; border: 1px solid #000; margin-right: 5px; }
    
    .status-pending { color: #9e9e9e; font-style: italic; font-size: 0.85em; }

    .trademark { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); font-size: 10px; color: #999; letter-spacing: 2px; z-index: 1000; text-align: center; width: 100%; }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

# 3. Helper Functions
def save_finals(data):
    with open(SAVE_FN, "w") as f:
        json.dump(data, f)

def load_finals():
    if os.path.exists(SAVE_FN):
        try:
            with open(SAVE_FN, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th") if not 10 <= i % 100 <= 20 else "th"
    return f"{i}{suffix}"

# 4. Data Loading Logic
@st.cache_data
def load_data(mtime):
    if not os.path.exists(FN): return None, {}, {}
    try:
        df = pd.read_csv(FN, header=None).fillna("")
        matches, team_colors, db = [], {}, {}
        day_context = "Day 1"
        blocks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
        
        for idx, row in df.iterrows():
            row_str = " ".join([str(x) for x in row]).upper()
            if "DAY 2" in row_str: day_context = "Day 2"
            elif "DAY 1" in row_str: day_context = "Day 1"
            
            for c in blocks:
                try:
                    t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                    bracket_raw = str(row[c[1]]).strip().upper()
                    
                    is_semis = "SEMIS" in bracket_raw
                    is_finals = "FINALS" in bracket_raw
                    
                    if not (is_semis or is_finals) and ("|" not in t1 or "|" not in t2):
                        continue
                    if t1 == "" or t2 == "": continue
                        
                    base_color = "WHITE"
                    for color_key in EMOJIS.keys():
                        if color_key in bracket_raw:
                            base_color = color_key
                            break
                    
                    time_val = str(row[c[0]]).strip()
                    emoji = EMOJIS.get(base_color, "🏸")
                    
                    court_val = "Court ?"
                    for r_scan in range(idx, -1, -1):
                        scan_text = str(df.iloc[r_scan, c[2]]).upper()
                        if "COURT" in scan_text:
                            court_val = scan_text.strip()
                            break
                    
                    p1_display = t1.replace("|", " AND ")
                    p2_display = t2.replace("|", " AND ")
                    m_id = f"{day_context[0]}{idx}{c[0]}"
                    
                    matches.append({
                        "ID": m_id, "Day": day_context, "T": time_val, "T1": t1, "T2": t2, 
                        "P1": p1_display, "P2": p2_display, "Bracket": bracket_raw, 
                        "Emoji": emoji, "Court": court_val,
                        "IsSemis": is_semis, "IsFinals": is_finals
                    })
                    
                    if "|" in t1: team_colors[t1] = base_color
                    if "|" in t2: team_colors[t2] = base_color
                    
                    # Score Processing
                    raw_sc = [str(row[col]).strip() for col in [c[4], c[5], c[6], c[7]]]
                    sc = [int(float(x)) if x.replace('.','',1).isdigit() else 0 for x in raw_sc]
                    
                    # Check if match is started (any score > 0)
                    is_started = any(s > 0 for s in sc)
                    
                    w1 = (sc[0] > sc[2]) + (sc[1] > sc[3])
                    w2 = (sc[2] > sc[0]) + (sc[3] > sc[1])
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "w1":w1, "w2":w2, "p1":sc[0]+sc[1], "p2":sc[2]+sc[3], "started": is_started}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 5. App UI
st.title("🏸 GCCP SMASH S1 2026")
mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(mtime)

if sch is None or sch.empty:
    st.error("CSV Data missing or unreadable.")
else:
    st.session_state.db = csv_db
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    # --- REUSABLE TABLE RENDERER ---
    def render_schedule(df_slice, search_key):
        rows = []
        for _, r in df_slice.iterrows():
            if search_key in r['T1'].lower() or search_key in r['T2'].lower() or search_key in r['Bracket'].lower():
                d = csv_db.get(r["ID"])
                
                # Badge Logic
                badge = ""
                row_cls = ""
                if r['IsSemis']:
                    badge = '<span class="badge-semis">🏆 SEMIS</span>'
                    row_cls = 'class="high-stakes"'
                elif r['IsFinals']:
                    badge = '<span class="badge-finals">🥇 FINALS</span>'
                    row_cls = 'class="high-stakes"'
                
                # Status/Score Logic
                if d and d['started']:
                    s1, s2 = f"{d['s1']}-{d['s3']}", f"{d['s2']}-{d['s4']}"
                else:
                    s1 = s2 = '<span class="status-pending">🕒 UPCOMING / IN PROGRESS</span>'
                
                rows.append(f"""
                <tr {row_cls}>
                    <td>{r['Court']}</td>
                    <td>{r['T']}</td>
                    <td>{r['Emoji']} {r['Bracket']}</td>
                    <td>{badge}{r['P1']} <b>vs</b> {r['P2']}</td>
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

    with tabs[0]: # Standings
        df_stand = pd.DataFrame([{"Team":t, "B":c, "GP":0, "SW":0, "SL":0, "Pts":0} for t,c in clrs.items()])
        for v in st.session_state.db.values():
            for t_key, w_key, l_key, p_key in [('t1','w1','w2','p1'), ('t2','w2','w1','p2')]:
                if v[t_key] in clrs:
                    row_idx = df_stand.index[df_stand['Team']==v[t_key]][0]
                    df_stand.at[row_idx, 'GP'] += 1
                    df_stand.at[row_idx, 'SW'] += v[w_key]
                    df_stand.at[row_idx, 'SL'] += v[l_key]
                    df_stand.at[row_idx, 'Pts'] += v[p_key]
        
        for color in sorted(list(set(clrs.values()))):
            st.subheader(f"{EMOJIS.get(color, '🏆')} {color} Bracket")
            sdf = df_stand[df_stand["B"]==color].sort_values(["SW", "Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["B"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    with tabs[1]: # Day 1
        render_schedule(sch[sch["Day"] == "Day 1"].sort_values(by=["Court", "T"]), st.text_input("🔍 Search Day 1", key="q1").lower())

    with tabs[2]: # Day 2
        render_schedule(sch[sch["Day"] == "Day 2"].sort_values(by=["Court", "T"]), st.text_input("🔍 Search Day 2", key="q2").lower())

    with tabs[3]: # Finals (Manual)
        st.info("The Finals tab is manually managed for the Championship Bracket.")

    with tabs[4]: # Admin
        if st.text_input("Admin Access", type="password") == ADMIN_PW:
            if st.button("Force Refresh Data"):
                st.cache_data.clear()
                st.rerun()
