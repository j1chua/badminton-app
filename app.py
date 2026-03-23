import streamlit as st
import pandas as pd
import os

# 1. Setup & Constants
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th") if not 10 <= i % 100 <= 20 else "th"
    return f"{i}{suffix}"

# 2. Optimized Data Loader
@st.cache_data
def load_data():
    if not os.path.exists(FN): return None, {}, {}
    try:
        df = pd.read_csv(FN, header=None).fillna("")
        matches, colors, db, day = [], {}, {}, "Day 1"
        # Column blocks for matches
        blks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
        
        for idx, row in df.iterrows():
            r_txt = " ".join(map(str, row)).upper()
            if "DAY 2" in r_txt: day = "Day 2"
            elif "DAY 1" in r_txt: day = "Day 1"
            
            for c in blks:
                t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                if "|" not in t1 or "|" not in t2: continue
                
                # Metadata
                L = str(row[c[1]]).strip().upper()
                tm, e = str(row[c[0]]).strip(), EMOJIS.get(L, "🏸")
                
                # Quick Court Search
                ct = "Court ?"
                for r_ptr in range(idx, -1, -1):
                    vals = [str(v).upper() for v in df.iloc[r_ptr]]
                    found = [v for v in vals if "COURT" in v]
                    if found: 
                        ct = found[0].strip()
                        break
                
                p1, p2 = t1.replace("|", " AND "), t2.replace("|", " AND ")
                mid = f"{ct}|{L}|{tm}|{p1}vs{p2}"
                matches.append({"ID":mid,"Day":day,"T":tm,"T1":t1,"T2":t2,"P1":p1,"P2":p2,"L":L,"Emoji":e,"Court":ct})
                colors[t1] = colors[t2] = L
                
                # Scores (2 sets, sudden death at 21)
                v = [int(float(row[x])) if str(row[x]).strip().replace('.','',1).isdigit() else 0 for x in [c[4],c[5],c[6],c[7]]]
                w1, w2 = (v[0]>v[2])+(v[1]>v[3]), (v[2]>v[0])+(v[3]>v[1])
                db[mid] = {"s1":v[0],"s2":v[1],"s3":v[2],"s4":v[3],"t1":t1,"t2":t2,"p1":v[0]+v[1],"p2":v[2]+v[3],"w1":w1,"w2":w2}
        return pd.DataFrame(matches), colors, db
    except: return None, {}, {}

# 3. UI & Styling
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
    st.warning("Ensure the CSV file is uploaded to GitHub.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    t1, t2 = st.tabs(["📊 Standings", "📅 Schedule"])
    
    with t1: # Leaderboard logic
        res = {t:{"Bracket":clrs.get(t,"?"),"Sets Won":0,"Sets Lost":0,"Total Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            for i in [1,2]:
                tm = v[f't{i}']
                if tm in res:
                    res[tm]["Sets Won"] += v[f'w{i}']; res[tm]["Sets Lost"] += v[f'w{3-i}']; res[tm]["Total Pts"] += v[f'p{i}']
        df_r = pd.DataFrame.from_dict(res, orient='index').reset_index().rename(columns={'index':'Team'})
        df_r["Team"] = df_r["Team"].str.replace("|", " AND ", regex=False)
        for b in sorted(df_r["Bracket"].unique()):
            st.subheader(f"{EMOJIS.get(b.upper(), '🏆')} {b} Bracket")
            sdf = df_r[df_r["Bracket"]==b].sort_values(["Sets Won","Total Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["Bracket"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    with t2: # Schedule logic
        day_sel = st.radio("Day:", ["Day 1", "Day 2"], horizontal=True)
        search = st.text_input("🔍 Search Team").lower()
        rows = []
        for _, r in sch[sch["Day"] == day_sel].iterrows():
            if search in r['T1'].lower() or search in r['T2'].lower():
                d = st.session_state.db.get(r["ID"])
                s1, s2, res_str, m_disp = "--", "--", "--", f"{r['P1']} vs {r['P2']}"
                if d:
                    if (d['s1']==0 and d['s2']==0) and (d['s3']==0 and d['s4']==0):
