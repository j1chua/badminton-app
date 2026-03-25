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
    .m-table th { background-color: #f8f9fa; text-align: center !important; padding: 14px; border: 1px solid #dee2e6; font-weight: 800; }
    .m-table td { text-align: center !important; padding: 12px; border: 1px solid #dee2e6; }
    .status-pending { color: #adb5bd; font-style: italic; font-size: 0.85em; }
    .trademark { position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%); font-size: 11px; color: #bbb; letter-spacing: 3px; z-index: 1000; text-align: center; width: 100%; }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

# 3. Persistence Logic
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
                    if "|" not in t1 or "|" not in t2: continue
                    bracket = str(row[c[1]]).strip().upper()
                    base_col = "WHITE"
                    for k in EMOJIS:
                        if k in bracket: base_col = k; break
                    m_id = f"{day_context[0]}{idx}{c[0]}"
                    matches.append({"ID":m_id,"Day":day_context,"T":str(row[c[0]]),"T1":t1,"T2":t2,"Bracket":bracket,"Emoji":EMOJIS.get(base_col,"🏸"),"Court":"Court 1"})
                    team_colors[t1] = base_col
                    team_colors[t2] = base_col
                    scores = []
                    for ci in [c[4],c[5],c[6],c[7]]:
                        try: scores.append(int(float(str(row[ci]))))
                        except: scores.append(0)
                    db[m_id] = {"s1":scores[0],"s2":scores[1],"s3":scores[2],"s4":scores[3],"started":any(s>0 for s in scores),"t1":t1,"t2":t2}
                    db[m_id]["w1"] = (scores[0]>scores[2])+(scores[1]>scores[3])
                    db[m_id]["w2"] = (scores[2]>scores[0])+(scores[3]>scores[1])
                    db[m_id]["p1"] = scores[0]+scores[1]
                    db[m_id]["p2"] = scores[2]+scores[3]
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 5. UI
st.title("🏸 GCCP SMASH S1 2026")
mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(mtime)

if 'finals' not in st.session_state:
    st.session_state.finals = load_finals()

if sch is not None:
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    with tabs[0]: # Standings
        df_stand = pd.DataFrame([{"Team":t, "B":c, "GP":0, "SW":0, "Pts":0} for t,c in clrs.items()])
        for v in csv_db.values():
            for tk, wk, pk in [('t1','w1','p1'),('t2','w2','p2')]:
                if v[tk] in clrs:
                    i = df_stand.index[df_stand['Team']==v[tk]][0]
                    df_stand.at[i,'GP']+=1; df_stand.at[i,'SW']+=v[wk]; df_stand.at[i,'Pts']+=v[pk]
        for col in sorted(list(set(clrs.values()))):
            st.subheader(f"{col} Bracket")
            sdf = df_stand[df_stand["B"]==col].sort_values(["SW","Pts"], ascending=False)
            st.write(sdf.drop(columns=["B"]).to_html(index=False, classes="m-table"), unsafe_allow_html=True)

    with tabs[1]: # Day 1
        d1 = sch[sch["Day"]=="Day 1"]
        rows = []
        for _, r in d1.iterrows():
            d = csv_db.get(r["ID"])
            s = f"{d['s1']}-{d['s3']} | {d['s2']}-{d['s4']}" if d['started'] else "PENDING"
            rows.append(f"<tr><td>{r['T']}</td><td>{r['Emoji']} {r['Bracket']}</td><td>{r['T1']} vs {r['T2']}</td><td>{s}</td></tr>")
        st.write(f"<table class='m-table'><tr><th>Time</th><th>Bracket</th><th>Match</th><th>Score</th></tr>{''.join(rows)}</table>", unsafe_allow_html=True)

    with tabs[2]: st.write("Day 2 Schedule Loading...")

    with tabs[3]: # Finals Tab
        f = st.session_state.finals
        st.subheader("🏆 Tournament Finals")
        for b in ["RED", "BLACK", "GREEN", "PURPLE", "YELLOW", "WHITE"]:
            if f.get(f"{b}_t1"):
                st.info(f"**{b} BRACKET FINALS**")
                col1, col2 = st.columns(2)
                col1.metric(f.get(f"{b}_t1"), f.get(f"{b}_s1", "0"))
                col2.metric(f.get(f"{b}_t2"), f.get(f"{b}_s2", "0"))

    with tabs[4]: # Admin
        pw = st.text_input("Admin", type="password")
        if pw == ADMIN_PW:
            st.success("Admin Mode")
            with st.expander("Update Finals Scoreboard"):
                target_b = st.selectbox("Select Bracket", ["RED", "BLACK", "GREEN", "PURPLE", "YELLOW", "WHITE"])
                st.session_state.finals[f"{target_b}_t1"] = st.text_input("Team 1 Name", st.session_state.finals.get(f"{target_b}_t1", ""))
                st.session_state.finals[f"{target_b}_t2"] = st.text_input("Team 2 Name", st.session_state.finals.get(f"{target_b}_t2", ""))
                st.session_state.finals[f"{target_b}_s1"] = st.text_input("Team 1 Score", st.session_state.finals.get(f"{target_b}_s1", "0"))
                st.session_state.finals[f"{target_b}_s2"] = st.text_input("Team 2 Score", st.session_state.finals.get(f"{target_b}_s2", "0"))
                if st.button("Save Finals Data"):
                    save_finals(st.session_state.finals)
                    st.toast("Saved!")
