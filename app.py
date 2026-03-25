import streamlit as st
import pandas as pd
import os
import json

# 1. Page Configuration
st.set_page_config(page_title="GCCP SMASH S1 2026", layout="wide")

# Constants
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
ADMIN_PW = "pogisiJordan"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

# 2. Global Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;600;800&display=swap');
    html, body, [class*="css"], .stMarkdown, p, div, table, h1, h2, h3 {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; border-radius: 8px; overflow: hidden; }
    .m-table th { background-color: #f8f9fa; text-align: center !important; padding: 14px; border: 1px solid #dee2e6; font-weight: 800; color: #333; }
    .m-table td { text-align: center !important; padding: 12px; border: 1px solid #dee2e6; vertical-align: middle; }
    .high-stakes { background-color: #fffde7 !important; border: 2px solid #fbc02d !important; }
    .winner-text { font-weight: 800; color: #2e7d32; }
    .status-pending { color: #adb5bd; font-style: italic; font-size: 0.85em; }
    .trademark { position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%); font-size: 11px; color: #bbb; letter-spacing: 3px; z-index: 1000; text-align: center; width: 100%; font-weight: 300; }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

# 3. Persistence Logic (From your app.py)
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
    return f"{i}th"

# 4. Data Loading
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
                    if not bracket_raw or "BRACKET" in bracket_raw or "COLOR" in bracket_raw: continue
                    if t1 == "" or t2 == "" or "RESULTS" in t1 or "RESULTS" in t2: continue
                    
                    is_high_stakes = "SEMIS" in bracket_raw or "FINALS" in bracket_raw
                    base_color = "WHITE"
                    for k in EMOJIS:
                        if k in bracket_raw: base_color = k; break
                    
                    court_val = "Court ?"
                    for r_scan in range(idx, -1, -1):
                        if "COURT" in str(df.iloc[r_scan, c[2]]).upper():
                            court_val = str(df.iloc[r_scan, c[2]]).strip(); break
                    
                    m_id = f"{day_context[0]}{idx}{c[0]}"
                    matches.append({"ID":m_id, "Day":day_context, "T":str(row[c[0]]).strip(), "T1":t1, "T2":t2, 
                                   "P1":t1.replace("|"," AND "), "P2":t2.replace("|"," AND "),
                                   "Bracket":bracket_raw, "Emoji":EMOJIS.get(base_color,"🏸"), 
                                   "Court":court_val, "HighStakes":is_high_stakes})
                    
                    if "|" in t1: team_colors[t1] = base_color
                    if "|" in t2: team_colors[t2] = base_color
                    
                    scores = []
                    for ci in [c[4],c[5],c[6],c[7]]:
                        try: scores.append(int(float(str(row[ci]).strip())))
                        except: scores.append(0)
                    
                    db[m_id] = {"s1":scores[0],"s2":scores[1],"s3":scores[2],"s4":scores[3],
                               "w1":(scores[0]>scores[2])+(scores[1]>scores[3]),
                               "w2":(scores[2]>scores[0])+(scores[3]>scores[1]),
                               "l1":(scores[0]<scores[2])+(scores[1]<scores[3]),
                               "l2":(scores[2]<scores[0])+(scores[3]<scores[1]),
                               "p1":scores[0]+scores[1], "p2":scores[2]+scores[3],
                               "started":any(s>0 for s in scores), "t1":t1, "t2":t2}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 5. UI Execution
st.title("🏸 GCCP SMASH S1 2026")
mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(mtime)

if 'finals' not in st.session_state:
    st.session_state.finals = load_finals()

if sch is not None:
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    with tabs[0]: # STANDINGS
        df_stand = pd.DataFrame([{"Team":t, "B":c, "Games Played":0, "Sets Won":0, "Sets Lost":0, "Points":0} for t,c in clrs.items()])
        for v in csv_db.values():
            for tk, wk, lk, pk in [('t1','w1','l1','p1'),('t2','w2','l2','p2')]:
                if v.get(tk) in clrs:
                    i = df_stand.index[df_stand['Team']==v[tk]][0]
                    df_stand.at[i,'Games Played']+=1; df_stand.at[i,'Sets Won']+=v[wk]
                    df_stand.at[i,'Sets Lost']+=v[lk]; df_stand.at[i,'Points']+=v[pk]
        
        for col in sorted(list(set(clrs.values()))):
            st.subheader(f"{EMOJIS.get(col,'')} {col} Bracket")
            sdf = df_stand[df_stand["B"]==col].sort_values(["Sets Won","Points"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["B"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    def render_matches(df_slice, key):
        search = st.text_input(f"🔍 Search Matches", key=key).lower()
        rows = []
        for _, r in df_slice.iterrows():
            if search in r['T1'].lower() or search in r['T2'].lower() or search in r['Bracket'].lower():
                d = csv_db.get(r["ID"])
                p1_disp, p2_disp = r['P1'], r['P2']
                row_cls = 'class="high-stakes"' if r['HighStakes'] else ""
                if d and d['started']:
                    if d['w1']>d['w2']: p1_disp = f"🏆 <span class='winner-text'>{r['P1']}</span>"
                    elif d['w2']>d['w1']: p2_disp = f"🏆 <span class='winner-text'>{r['P2']}</span>"
                    s1, s2 = f"{d['s1']}-{d['s3']}", f"{d['s2']}-{d['s4']}"
                else: s1 = s2 = '<span class="status-pending">🕒 MATCH IN PROGRESS</span>'
                rows.append(f"<tr {row_cls}><td>{r['Court']}</td><td>{r['T']}</td><td>{r['Emoji']} {r['Bracket']}</td><td>{p1_disp} <b>vs</b> {p2_disp}</td><td>{s1}</td><td>{s2}</td></tr>")
        if rows: st.write(f"<table class='m-table'><thead><tr><th>Court</th><th>Time</th><th>Bracket</th><th>Match</th><th>Set 1</th><th>Set 2</th></tr></thead><tbody>{''.join(rows)}</tbody></table>", unsafe_allow_html=True)

    with tabs[1]: render_matches(sch[sch["Day"] == "Day 1"].sort_values(["Court", "T"]), "q1")
    with tabs[2]: render_matches(sch[sch["Day"] == "Day 2"].sort_values(["Court", "T"]), "q2")

    with tabs[3]: # FINALS (Restored logic from your app.py)
        f = st.session_state.finals
        st.subheader("🏆 Tournament Finals")
        for b in ["RED", "BLACK", "GREEN", "PURPLE", "YELLOW", "WHITE"]:
            if f.get(f"{b}_t1"):
                st.info(f"**{b} BRACKET FINALS**")
                c1, c2 = st.columns(2)
                c1.metric(f.get(f"{b}_t1"), f.get(f"{b}_s1", "0"))
                c2.metric(f.get(f"{b}_t2"), f.get(f"{b}_s2", "0"))

    with tabs[4]: # ADMIN (Restored exact manual management from your app.py)
        if st.text_input("Admin Password", type="password") == ADMIN_PW:
            st.success("Authorized")
            with st.expander("Manually Manage Finals"):
                bracket_list = ["RED", "BLACK", "GREEN", "PURPLE", "YELLOW", "WHITE"]
                v = st.selectbox("Select Bracket to Update", bracket_list)
                
                c1, c2 = st.columns(2)
                with c1:
                    st.session_state.finals[f"{v}_t1"] = st.text_input(f"{v} Team 1", st.session_state.finals.get(f"{v}_t1",""))
                    st.session_state.finals[f"{v}_s1"] = st.text_input(f"{v} Team 1 Score", st.session_state.finals.get(f"{v}_s1","0"))
                with c2:
                    st.session_state.finals[f"{v}_t2"] = st.text_input(f"{v} Team 2", st.session_state.finals.get(f"{v}_t2",""))
                    st.session_state.finals[f"{v}_s2"] = st.text_input(f"{v} Team 2 Score", st.session_state.finals.get(f"{v}_s2","0"))
                
                if st.button(f"Save {v} Finals Data"):
                    save_finals(st.session_state.finals)
                    st.toast(f"Updated {v} Bracket!")
                    st.rerun()
            
            if st.button("🔄 Force Refresh CSV Data"):
                st.cache_data.clear()
                st.rerun()
