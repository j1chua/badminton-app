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
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th") if not 10 <= i % 100 <= 20 else "th"
    return f"{i}{suffix}"

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
                try:
                    t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                    if "|" not in t1 or "|" not in t2: continue
                    
                    color = str(row[c[1]]).strip().upper()
                    time, emoji = str(row[c[0]]).strip(), EMOJIS.get(color, "🏸")
                    
                    court = "Court ?"
                    for r_idx in range(idx, -1, -1):
                        val = str(df.iloc[r_idx, c[2]]).upper()
                        if "COURT" in val:
                            court = val.strip()
                            break

                    p1_d, p2_d = t1.replace("|", " AND "), t2.replace("|", " AND ")
                    m_id = f"{day[:1]}{idx}{c[0]}"
                    
                    matches.append({"ID": m_id, "Day": day, "T": time, "T1": t1, "T2": t2, "P1": p1_d, "P2": p2_d, "L": color, "Emoji": emoji, "Court": court})
                    team_colors[t1] = team_colors[t2] = color
                    
                    sc = [int(float(row[col])) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7]]]
                    w1, w2 = (sc[0]>sc[2])+(sc[1]>sc[3]), (sc[2]>sc[0])+(sc[3]>sc[1])
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "p1":sc[0]+sc[1], "p2":sc[2]+sc[3], "w1":w1, "w2":w2}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 3. Styling
st.markdown("""
<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-family: sans-serif; }
    .m-table th { background-color: #f0f2f6; text-align: center !important; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    .m-table tr:nth-child(even) { background-color: #f9f9f9; }
    .forfeit { color: #d32f2f; font-weight: bold; }
    .win-red { color: red; font-weight: bold; text-decoration: underline; }
    .win-green { color: green; font-weight: bold; text-decoration: underline; }
    .win-purple { color: purple; font-weight: bold; text-decoration: underline; }
    .win-yellow { color: #d4af37; font-weight: bold; text-decoration: underline; }
    .win-black { color: black; font-weight: bold; text-decoration: underline; }
    .win-white { color: gray; font-weight: bold; text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Data not found. Please check the CSV file.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    
    # 4. Main Navigation Tabs
    main_tab1, main_tab2, main_tab3 = st.tabs([
        "📊 Standings", 
        "📅 Day 1 Schedule", 
        "📅 Day 2 Schedule - COMING SOON"
    ])

    with main_tab1:
        st.info("🕒 **Current Standings** — *Results as of March 22, 2026 (Provisional)*")
        stats = {t:{"Bracket":clrs.get(t,"?"), "Games Played":0, "Sets Won":0, "Sets Lost":0, "Total Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            if v['t1'] in stats:
                stats[v['t1']]["Games Played"] += 1
                stats[v['t1']]["Sets Won"] += v['w1']; stats[v['t1']]["Sets Lost"] += v['w2']; stats[v['t1']]["Total Pts"] += v['p1']
            if v['t2'] in stats:
                stats[v['t2']]["Games Played"] += 1
                stats[v['t2']]["Sets Won"] += v['w2']; stats[v['t2']]["Sets Lost"] += v['w1']; stats[v['t2']]["Total Pts"] += v['p2']
        
        df_r = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Team'})
        df_r["Team"] = df_r["Team"].str.replace("|", " AND ", regex=False)
        
        for color in sorted(df_r["Bracket"].unique()):
            st.subheader(f"{EMOJIS.get(color.upper(), '🏆')} {color} Bracket")
            sdf = df_r[df_r["Bracket"]==color].sort_values(["Sets Won", "Total Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["Bracket"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    with main_tab2:
        q = st.text_input("🔍 Search Team Name", key="q1").lower()
        rows = []
        for _, r in sch[sch["Day"] == "Day 1"].iterrows():
            if q in r['T1'].lower() or q in r['T2'].lower() or q in r['P1'].lower() or
