import streamlit as st
import pandas as pd
import os

# 1. Setup
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th") if not 10 <= i % 100 <= 20 else "th"
    return f"{i}{suffix}"

# 2. Data Loader
@st.cache_data
def load_data():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    matches, colors, db, day = [], {}, {}, "Day 1"
    blks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
    
    for idx, row in df.iterrows():
        r_txt = " ".join(map(str, row)).upper()
        if "DAY 2" in r_txt: day = "Day 2"
        elif "DAY 1" in r_txt: day = "Day 1"
        for c in blks:
            t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
            if "|" not in t1 or "|" not in t2: continue
            L = str(row[c[1]]).strip().upper()
            tm, e = str(row[c[0]]).strip(), EMOJIS.get(L, "🏸")
            ct = "Court ?"
            for r_ptr in range(idx, -1, -1):
                vals = [str(v).upper() for v in df.iloc[r_ptr]]
                found = [v for v in vals if "COURT" in v]
                if found: 
                    ct = found[0].strip()
                    break
            p1, p2 = t1.replace("|", " AND "), t2.replace("|", " AND ")
            mid = f"{ct}|{L}|{tm}|{p1}vs{p2}"
            
            m_d = {"ID": mid, "Day": day, "T": tm, "P1": p1, "P2": p2, "T1": t1, "T2": t2, "L": L, "Emoji": e, "Court": ct}
            matches.append(m_d)
            colors[t1] = colors[t2] = L
            
            # FIXED SCORE LOGIC: Process each cell individually as an integer
            sc = []
            for col in [c[4],c[5],c[6],c[7]]:
                raw = str(row[col]).strip()
                # Remove anything that isn't a digit (like extra spaces or symbols)
                clean = "".join(filter(str.isdigit, raw))
                sc.append(int(clean) if clean else 0)
            
            w1 = (sc[0] > sc[2]) + (sc[1] > sc[3])
            w2 = (sc[2] > sc[0]) + (sc[3] > sc[1])
            res = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2}
            res["p1"], res["p2"], res["w1"], res["w2"] = sc[0]+sc[1], sc[2]+sc[3], w1, w2
            db[mid] = res
            
    return pd.DataFrame(matches), colors, db

# 3. Styling
st.markdown("""<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
    .m-table th { background-color: #f0f2f6; text-align: center; padding: 10px; border: 1px solid #ddd; }
    .m-table td { text-align: center; padding: 8px; border: 1px solid #ddd; }
    .winner { background-color: #e8f5e9; color: #2e7d32; font-weight: bold; padding: 2px 5px; border-radius: 3px; }
    .forfeit { color: #d32f2f; font-weight: bold; }
</style>""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Check your CSV file on GitHub.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    t1, t2 = st.tabs(["📊 Standings", "📅 Schedule"])
    with t1:
        stats = {t:{"Bracket":clrs.get(t,"?"),"Sets Won":0,"Sets Lost":0,"Total Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            for i in [1,2]:
                tm = v[f't{i}']
                if tm in stats:
                    stats[tm]["Sets Won"] += v[f'w{i}']
                    stats[tm]["Sets Lost"] += v[f'w{3-i}']
                    stats[tm]["Total Pts"] += v[f'p{i}']
        df_r = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Team'})
        df_r["Team"] = df_r["Team"].str.replace("|", " AND ", regex=False)
        for b in sorted(df_r["Bracket"].unique()):
            st.subheader(f"{EMOJIS.get(b.upper(), '🏆')} {b} Bracket")
            sdf = df_r[df_r["Bracket"]==b].sort_values(["Sets Won","Total Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["Bracket"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)
    with t2:
        day_sel = st.radio("Day:", ["Day 1", "Day 2"], horizontal=True)
        search = st.text_input("🔍 Search Team").lower()
        rows = []
        for _, r in sch[sch["Day"] == day_sel].iterrows():
            if search not in r['T1'].lower() and search not in r['T2'].lower(): continue
            d = st.session_state.db.get(r["ID"])
            if not d: continue
            is_ff = (d['s1']==0 and d['s2']==0 and d['s3']==0 and d['s4']==0)
            s1 = '<span class="forfeit">FF</span>' if is_ff else f"{d['s1']}-{d['s3']}"
            s2 = '<span class="forfeit">FF</span>' if is_ff else f"{d['s2']}-{d['s4']}"
            p1 = f'<span class="winner">{r["P1"]}</span>' if d['w1'] == 2 else r["P1"]
            p2 = f'<span class="winner">{r["P2"]}</span>' if d['w2'] == 2 else r["P2"]
            rows.append({"Time":r["T"],"Court":r["Court"],"Match":f"{p1} vs {p2}","Set 1":s1,"Set 2":s2,"Result":f"{d['w1']}-{d['w2']}"})
        if rows: st.write(pd.DataFrame(rows).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)
