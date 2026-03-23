import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

# 2. Score Repair Function (Fixes the 210-160 bug)
def clean_score(val):
    v = "".join(filter(str.isdigit, str(val)))
    return int(v) if v else 0

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    return f"{i}th"

# 3. Data Loading Logic
@st.cache_data
def load_data():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    matches, team_colors, db = [], {}, {}
    day, blocks = "Day 1", [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]

    for idx, row in df.iterrows():
        txt = " ".join([str(x) for x in row]).upper()
        if "DAY 2" in txt: day = "Day 2"
        elif "DAY 1" in txt: day = "Day 1"
        
        for c in blocks:
            t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
            if "|" not in t1: continue
            
            color = str(row[c[1]]).strip().upper()
            time, emoji = str(row[c[0]]).strip(), EMOJIS.get(color, "🏸")
            
            court = "Court ?"
            for r_idx in range(idx, -1, -1):
                sv = [str(v).upper() for v in df.iloc[r_idx]]
                if any("COURT" in v for v in sv):
                    court = next(v.strip() for v in sv if "COURT" in v)
                    break

            p1_d, p2_d = t1.replace("|", " & "), t2.replace("|", " & ")
            m_id = f"{day}{court}{time}{p1_d}" # Short ID to prevent wrap
            
            matches.append({"ID": m_id, "Day": day, "T": time, "T1": t1, "T2": t2, "P1": p1_d, "P2": p2_d, "L": color, "Emoji": emoji, "Court": court})
            team_colors[t1] = team_colors[t2] = color
            
            # THE SCORE FIX
            s = [clean_score(row[col]) for col in [c[4], c[5], c[6], c[7]]]
            w1, w2 = (s[0]>s[2])+(s[1]>s[3]), (s[2]>s[0])+(s[3]>s[1])
            db[m_id] = {"s1":s[0], "s2":s[1], "s3":s[2], "s4":s[3], "t1":t1, "t2":t2, "w1":w1, "w2":w2}
    return pd.DataFrame(matches), team_colors, db

# 4. Start App Immediately (Prevents NameError: load_)
st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

st.markdown("""<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .m-table th { background-color: #f0f2f6; text-align: center; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center; padding: 10px; border: 1px solid #ddd; }
</style>""", unsafe_allow_html=True)

if sch is not None and not sch.empty:
    t1, t2 = st.tabs(["📊 Standings", "📅 Schedule"])
    with t1:
        stats = {t:{"Bracket":clrs.get(t,"?"),"Sets Won":0} for t in clrs}
        for v in csv_db.values():
            if v['t1'] in stats: stats[v['t1']]["Sets Won"] += v['w1']
            if v['t2'] in stats: stats[v['t2']]["Sets Won"] += v['w2']
        df_r = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Team'})
        for color in sorted(df_r["Bracket"].unique()):
            st.subheader(f"{EMOJIS.get(color.upper(), '🏆')} {color} Bracket
