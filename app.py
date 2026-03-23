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

@st.cache_data
def load():
    if not os.path.exists(FN): return None, {}, {}
    # Read raw CSV
    df = pd.read_csv(FN, header=None).fillna("")
    m, clrs, init_db = [], {}, {}
    curr_day = "Day 1"
    
    # Define columns for Left and Right blocks
    # [Time, Color, T1, T2, T1S1, T1S2, T2S1, T2S2]
    blocks = [
        ("Left", [0,1,2,7,3,4,8,9], 2),
        ("Right", [13,14,15,20,16,17,21,22], 15)
    ]

    for row_idx in range(len(df)):
        row_str = " ".join([str(x) for x in df.iloc[row_idx]]).upper()
        if "DAY 2" in row_str: curr_day = "Day 2"
        elif "DAY 1" in row_str: curr_day = "Day 1"
        
        for side, c, c_name_col in blocks:
            try:
                t1, t2 = str(df.iloc[row_idx, c[2]]).strip(), str(df.iloc[row_idx, c[3]]).strip()
                # Check if it's a valid match row
                if "|" in t1 and "|" in t2:
                    l = str(df.iloc[row_idx, c[1]]).strip().upper()
                    t = str(df.iloc[row_idx, c[0]]).strip()
                    e = EMOJIS.get(l, "🏸")
                    
                    # Improved Court Finder: Checks the column and nearby columns for "Court"
                    court_label = "Court ?"
                    found = False
                    for r_search in range(row_idx, -1, -1):
                        for col_off in range(-2, 3): # Search slightly left/right of the team column
                            check_col = c_name_col + col_off
                            if 0 <= check_col < len(df.columns):
                                val = str(df.iloc[r_search, check_col]).strip()
                                if "COURT" in val.upper():
                                    court_label = val
                                    found = True
                                    break
                        if found: break
                    
                    # YOUR REQUESTED FORMAT: Court | Emoji Color | | Time | Match
                    mid = f"{court_label} | {e} {l} | | {t} | {t1} vs {t2}"
                    
                    m.append({"ID":mid,"Day":curr_day,"T":t,"T1":t1,"T2":t2,"L":l,"Emoji":e, "Court": court_label})
                    clrs[t1] = clrs[t2] = l
                    
                    # Scoring logic
                    try:
                        s1 = int(float(df.iloc[row_idx, c[4]])) if df.iloc[row_idx, c[4]] != "" else 0
                        s2 = int(float(df.iloc[row_idx, c[5]])) if df.iloc[row_idx, c[5]] != "" else 0
                        s3 = int(float(df.iloc[row_idx, c[6]])) if df.iloc[row_idx, c[6]] != "" else 0
                        s4 = int(float(df.iloc[row_idx, c[7]])) if df.iloc[row_idx, c[7]] != "" else 0
                        
                        if (s1+s2+s3+s4) > 0:
                            w1, w2 = (s1>s3)+(s2>s4), (s3>s1)+(s4>s2)
                            init_db[mid] = {"sc":f"{s1}-{s3}, {s2}-{s4}","t1":t1,"t2":t2,"p1":s1+s2,"p2":s3+s4,"w1":w1,"l1":w2,"w2":w2,"l2":w1}
                    except: pass
            except: continue
    return pd.DataFrame(m), clrs, init_db

st.title("🏸 SMASH 2026")
sch, clrs, csv_scores = load()

if sch is None: st.error("CSV Missing")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_scores
    t1, t2, t3 = st.tabs(["📊 Standings", "📅 Schedule", "🔐 Entry"])

    with t3:
        pw = st.text_input("Admin Password", type="password")
        if pw == "pogisiJordan":
            d_sel = st.radio("Select Day to Edit", ["Day 1", "Day 2"], horizontal=True)
            m_filt = sch[sch["Day"] == d_sel]["ID"].tolist()
            sel = st.selectbox("Search Match", [""] + m_filt)
            if sel:
                d = sch[sch["ID"]==sel].iloc[0]
                st.markdown(f"### 📍 {sel.split('|')[0]} - {sel.split('|')[1]}")
                c1, c2 = st.columns(2)
                s1, s2 = c1.number_input(f"Set 1: {d['T1']}", 0, 30, key=f"a{sel}") , c1.number_input(f"Set 2: {d['T1']}", 0, 30, key=f"b{sel}")
                s3, s4 = c2.number_input(f"Set 1: {d['T2']}", 0, 30, key=f"c{sel}") , c2.number_input(f"Set 2: {d['T2']}", 0, 30, key=f"d{sel}")
                if st.button("Save Score", type="primary", use_container_width=True):
                    w1, w2 = (s1>s3)+(s2>s4), (s3>s1)+(s4>s2)
                    st.session_state.db[sel] = {"sc":f"{s1}-{s3}, {s2}-{s4}","t1":d['T1'],"t2":d['T2'],"p1":s1+s2,"p2":s3+s4,"w1":w1,"l1":w2,"w2":w2,"l2":w1}
                    st.success("Score Updated!")
        elif pw != "": st.error("Access Denied")

    with t1:
        res = {t:{"Bracket":clrs.get(t,"?"),"Sets Won":0,"Sets Lost":0,"Total Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            for i in [1,2]:
                if v[f't{i}'] in res:
                    res[v[f't{i}']]["Sets Won"]+=v[f'w{i}']; res[v[f't{i}']]["Sets Lost"]+=v[f'l{i}']; res[v[f't{i}']]["Total Pts"]+=v[f'p{i}']
        df_r = pd.DataFrame.from_dict(res, orient='index').reset_index().rename(columns={'index':'Team'})
        for c in sorted(df_r["Bracket"].unique()):
            e = EMOJIS.get(c.upper(), "🏆")
            st.subheader(f"{e} {c} Bracket")
            st.table(df_r[df_r["Bracket"]==c].sort_values(["Sets Won","Total Pts"], ascending=False))

    with t2:
        v_day = st.radio("View Day:", ["Day 1", "Day 2"], horizontal=True)
        q = st.text_input("🔍 Search Team").lower()
        L = [{"Time":r["T"], "Court": r["Court"], "Bracket":f"{r['Emoji']} {r['L']}", "Match":f"{r['T1']} vs {r['T2']}", "Result":st.session_state.db.get(r["ID"],{}).get("sc","--")} for _,r in sch[sch["Day"] == v_day].iterrows() if q in r['T1'].lower() or q in r['T2'].lower()]
        if L: st.table(L)
