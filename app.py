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
                m_id = f"{day}{court}{time}{p1_d}" # Shorter ID to prevent clipping
                
                matches.append({"ID": m_id, "Day": day, "T": time, "T1": t1, "T2": t2, "P1": p1_d, "P2": p2_d, "L": color, "Emoji": emoji, "Court": court})
                team_colors[t1] = team_colors[t2] = color
                
                # FIXED SCORE PARSING (Prevents 210-160 glitch)
                sc = []
                for col in [c[4], c[5], c[6], c[7]]:
                    v = "".join(filter(str.isdigit, str(row[col])))
                    sc.append(int(v) if v else 0)
                
                w1, w2 = (sc[0]>sc[2])+(sc[1]>sc[3]), (sc[2]>sc[0])+(sc[3]>sc[1])
                db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "p1":sc[0]+sc[1], "p2":sc[2]+sc[3], "w1":w1, "w2":w2}
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 3. Main App Execution
st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

st.markdown("""<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .m-table th { background-color: #f0f2f6; text-align: center; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center; padding: 10px; border: 1px solid #ddd; }
    .forfeit { color: #d32f2f; font-weight: bold; }
</style>""", unsafe_allow_html=True)

if sch is not None and not sch.empty:
    t1, t2 = st.tabs(["📊 Standings", "📅 Schedule"])
    with t1:
        stats = {t:{"Bracket":clrs.get(t,"?"),"Sets Won":0,"Total Pts":0} for t in clrs}
        for v in csv_db.values():
            for i in [1,2]:
                tm = v[f't{i}']
                if tm in stats:
                    stats[tm]["Sets Won"] += v[f'w{i}']
                    stats[tm]["Total Pts"] += v[f'p{i}']
        df_r = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Team'})
        for color in sorted(df_r["Bracket"].unique()):
            st.subheader(f"{EMOJIS.get(color.upper(), '🏆')} {color} Bracket")
            sdf = df_r[df_r["Bracket"]==color].sort_values(["Sets Won","Total Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["Bracket"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)
    with t2:
        day_pick = st.radio("Select Day:", ["Day 1", "Day 2"], horizontal=True)
        q = st.text_input("🔍 Search Team").lower()
        rows = []
        for _, r in sch[sch["Day"] == day_pick].iterrows():
            if q in r['T1'].lower() or q in r['P1'].lower() or q in r['P2'].lower():
                d = csv_db.get(r["ID"])
                s1, s2 = "--", "--"
                if d:
                    s1, s2 = f"{d['s1']} - {d['s3']}", f"{d['s2']} - {d['s4']}"
                rows.append({"Time": r["T"], "Court": r["Court"], "Match": f"{r['P1']} vs {r['P2']}", "Set 1": s1, "Set 2": s2})
        if rows: st.write(pd.DataFrame(rows).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)
else:
    st.warning("CSV file not found or empty.")
