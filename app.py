import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"

# Emoji Mapping
EMOJIS = {
    "BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", 
    "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"
}

# Helper for Ranking strings
def get_rank_str(i):
    if i == 1: return "<b>🥇 1st</b>"
    if i == 2: return "<b>🥈 2nd</b>"
    if i == 3: return "<b>🥉 3rd</b>"
    suffix = "th"
    if 10 <= i % 100 <= 20: suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th")
    return f"{i}{suffix}"

@st.cache_data
def load():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    m, clrs, init_db = [], {}, {}
    curr_day = "Day 1"
    
    blocks = [
        ("Left", [0,1,2,7,3,4,8,9]),
        ("Right", [13,14,15,20,16,17,21,22])
    ]

    for row_idx in range(len(df)):
        row_str = " ".join([str(x) for x in df.iloc[row_idx]]).upper()
        if "DAY 2" in row_str: curr_day = "Day 2"
        elif "DAY 1" in row_str: curr_day = "Day 1"
        
        for side, c in blocks:
            try:
                t1, t2 = str(df.iloc[row_idx, c[2]]).strip(), str(df.iloc[row_idx, c[3]]).strip()
                if "|" in t1 and "|" in t2:
                    l = str(df.iloc[row_idx, c[1]]).strip().upper()
                    t = str(df.iloc[row_idx, c[0]]).strip()
                    e = EMOJIS.get(l, "🏸")
                    
                    # Universal Court Finder
                    court_label = "Court ?"
                    found = False
                    for r_search in range(row_idx, -1, -1):
                        row_values = df.iloc[r_search].astype(str).tolist()
                        for val in row_values:
                            if "COURT" in val.upper():
                                court_label = val.strip()
                                found = True
                                break
                        if found: break
                    
                    p1, p2 = t1.replace("|", " AND "), t2.replace("|", " AND ")
                    mid = f"{court_label} | {e} {l} | {t} | {p1} vs {p2}"
                    
                    m.append({"ID":mid,"Day":curr_day,"T":t,"T1":t1,"T2":t2,"P1":p1,"P2":p2,"L":l,"Emoji":e, "Court": court_label})
                    clrs[t1] = clrs[t2] = l
                    
                    try:
                        v = [df.iloc[row_idx, col] for col in [c[4], c[5], c[6], c[7]]]
                        s1, s2, s3, s4 = [int(float(x)) if str(x).strip() != "" else 0 for x in v]
                        w1, w2 = (s1>s3)+(s2>s4), (s3>s1)+(s4>s2)
                        init_db[mid] = {
                            "s1":s1, "s2":s2, "s3":s3, "s4":s4,
                            "t1":t1,"t2":t2,"p1":s1+s2,"p2":s3+s4,"w1":w1,"l1":w2,"w2":w2,"l2":w1
                        }
                    except: pass
            except: continue
    return pd.DataFrame(m), clrs, init_db

# Custom CSS for middle alignment and pretty tables
st.markdown("""
<style>
    table { width: 100%; border-collapse: collapse; }
    th { background-color: #f0f2f6; text-align: center !important; font-weight: bold; padding: 12px; border: 1px solid #ddd; }
    td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    tr:nth-child(even) { background-color: #f9f9f9; }
</style>
""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_scores = load()

if sch is None: st.error("CSV Missing")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_scores
    t1, t2 = st.tabs(["📊 Standings", "📅 Schedule"])

    with t1:
        res = {t:{"Bracket":clrs.get(t,"?"),"Sets Won":0,"Sets Lost":0,"Total Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            for i in [1,2]:
                if v[f't{i}'] in res:
                    res[v[f't{i}']]["Sets Won"]+=v[f'w{i}']; res[v[f't{i}']]["Sets Lost"]+=v[f'l{i}']; res[v[f't{i}']]["Total Pts"]+=v[f'p{i}']
        
        df_r = pd.DataFrame.from_dict(res, orient='index').reset_index().rename(columns={'index':'Team'})
        df_r["Team"] = df_r["Team"].str.replace("|", " AND ", regex=False)
        
        for c in sorted(df_r["Bracket"].unique()):
            e = EMOJIS.get(c.upper(), "🏆")
            st.subheader(f"{e} {c} Bracket")
            
            # Ranking Logic
            sub_df = df_r[df_r["Bracket"]==c].sort_values(["Sets Won","Total Pts"], ascending=False).reset_index(drop=True)
            sub_df.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sub_df))])
            
            # Display centered HTML table
            disp_df = sub_df.drop(columns=["Bracket"])
            st.write(disp_df.to_html(escape=False, index=False), unsafe_allow_html=True)
            st.write("")

    with t2:
        v_day = st.radio("View Day:", ["Day 1", "Day 2"], horizontal=True)
        q = st.text_input("🔍 Search Team").lower()
        
        rows = []
        for _, r in sch[sch["Day"] == v_day].iterrows():
            if q in r['T1'].lower() or q in r['T2'].lower():
                score_data = st.session_state.db.get(r["ID"])
                s1_disp, s2_disp = "--", "--"
                
                if score_data:
                    s1, s2, s3, s4 = score_data['s1'], score_data['s2'], score_data['s3'], score_data['s4']
                    # Forfeit Logic: If score is 0-0 for both sets
                    if (s1 == 0 and s2 == 0) and (s3 == 0 and s4 == 0):
                        s1_disp = s2_disp = "<b style='color:#d32f2f;'>FORFEIT</b>"
                    else:
                        s1_disp = f"{s1} - {s3}"
                        s2_disp = f"{s2} - {s4}"
                
                rows.append({
                    "Time": r["T"], "Court": r["Court"], "Bracket": f"{r['Emoji']} {r['L']}",
                    "Match": f"{r['P1']} vs {r['P2']}", "Set 1": s1_disp, "Set 2": s2_disp
                })
        
        if rows:
            sched_df = pd.DataFrame(rows)
            st.write(sched_df.to_html(escape=False, index=False), unsafe_allow_html=True)
