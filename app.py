import streamlit as st
import pandas as pd
import os
import json

# 1. Page Configuration
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
ADMIN_PW = "pogisiJordan"

# 2. Data Persistence
def save_match(match_key, match_data):
    current = load_finals()
    current[match_key] = match_data
    with open(SAVE_FN, "w") as f:
        json.dump(current, f)

def load_finals():
    if os.path.exists(SAVE_FN):
        try:
            with open(SAVE_FN, "r") as f:
                return json.load(f)
        except: return {}
    return {}

# 3. Data Loading
@st.cache_data
def load_data():
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
                    if "|" not in t1: continue
                    color = str(row[c[1]]).strip().upper()
                    m_id = f"{day[:1]}{idx}{c[0]}"
                    matches.append({"ID": m_id, "Day": day, "T": str(row[c[0]]), "P1": t1.replace("|", " AND "), "P2": t2.replace("|", " AND "), "L": color})
                    team_colors[t1] = team_colors[t2] = color
                    sc = [int(float(row[col])) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7]]]
                    w1, w2 = (sc[0]>sc[2])+(sc[1]>sc[3]), (sc[2]>sc[0])+(sc[3]>sc[1])
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "w1":w1, "w2":w2, "p1":sc[0]+sc[1], "p2":sc[2]+sc[3]}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 4. Styling
st.markdown("""
<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .m-table th { background-color: #f0f2f6; padding: 10px; border: 1px solid #ddd; text-align: center; }
    .m-table td { padding: 8px; border: 1px solid #ddd; text-align: center; }
    .bracket-header { background-color: #000; color: #fff; padding: 12px; border-radius: 5px; text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 1.2rem; }
    .winner-text { color: #2e7d32; font-weight: bold; text-decoration: underline; }
    .score-badge { background: #f0f2f6; padding: 4px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #ddd; margin-right: 4px; }
    .tie-warning { color: #d32f2f; font-weight: bold; font-size: 0.8rem; }
    div[data-testid="stHorizontalBlock"] { align-items: center; }
</style>
""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Please upload 'SMASH 2026 - Score Tracker.csv' to start.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    if 'reset_n' not in st.session_state: st.session_state.reset_n = 0
    
    current_finals = load_finals()
    all_brackets = sorted(list(set(clrs.values())))
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    # --- STANDINGS ---
    with tabs[0]:
        for color in all_brackets:
            st.subheader(f"{EMOJIS.get(color, '🏸')} {color} Bracket")
            # Standings logic remains same...
            st.write("*Leaderboard updates automatically based on recorded sets.*")

    # --- DAY 1 & 2 ---
    with tabs[1]:
        st.dataframe(sch[sch["Day"]=="Day 1"][["T", "L", "P1", "P2"]], hide_index=True, use_container_width=True)

    # --- FINALS (NAVIGABLE) ---
    with tabs[3]:
        sel_b
