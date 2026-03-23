import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    return f"{i}th"

# 2. Data Loading Logic
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
                t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                if "|" not in t1 or "|" not in t2: continue
                
                color = str(row[c[1]]).strip().upper()
                time, emoji = str(row[c[0]]).strip(), EMOJIS.get(color, "🏸")
                
                court = "Court ?"
                for r_idx in range(idx, -1, -1):
                    search_vals = [str(v).upper() for v in df.iloc[r_idx]]
                    if any("COURT" in v for v in search_vals):
                        court = next(v.strip() for v in search_vals if "COURT" in v)
                        break

                p1_d, p2_d = t1.replace("|", " & "), t2.replace("|", " & ")
                # Shortened ID to prevent web editor clipping/SyntaxErrors
                m_id = f"{day[:1]}{idx}{c[0]}" 
                
                matches.append({"ID": m_id, "Day": day, "T": time, "T1": t1, "T2": t2, "P1": p1_d, "P2": p2_d, "L": color, "Emoji": emoji, "Court": court})
                team_colors[t1] = team_colors[t2] = color
                
                # Fixed Score Cleaning (Fixes the 210-160 glitch)
                sc = []
                for col in [c[4], c[5], c[6], c[7]]:
                    val = "".join(filter(str.isdigit, str(row[col])))
                    sc.append(int(val) if val else 0)
                
                w1, w2 = (sc[0]>sc[2])+(sc[1]>sc[3]), (sc[2]>sc[0])+(sc[3]>sc[1])
                db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "w1":w1, "w2":w2}
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 3. App Execution
st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

st.markdown("""<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .m-table th { background-color: #f0f2f6; text-align: center; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center; padding: 10px; border: 1px solid #ddd; }
</style>""", unsafe_allow_html=True)

if sch is not None and not sch.empty:
    tab1, tab2 = st.tabs(["📊 Standings", "📅 Schedule"])
    with tab1:
        stats = {t:{"Bracket":clrs.get(t,"?"),"Sets Won":0} for t in clrs}
        for v in csv_db.values():
            if v['t1'] in
