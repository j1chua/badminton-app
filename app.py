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
    df = pd.read_csv(FN, header=None).fillna(0)
    m, clrs, init_db = [], {}, {}
    curr_day = "Day 1"
    
    blocks = [("Left", [0,1,2,7,3,4,8,9]), ("Right", [13,14,15,20,16,17,21,22])]

    for row_idx in range(len(df)):
        row_str = " ".join(df.iloc[row_idx].astype(str)).upper()
        if "DAY 2" in row_str: curr_day = "Day 2"
        elif "DAY 1" in row_str: curr_day = "Day 1"
        
        for side, c in blocks:
            try:
                t1, t2 = str(df.iloc[row_idx, c[2]]).strip(), str(df.iloc[row_idx, c[3]]).strip()
                if "|" in t1 and "|" in t2:
                    l = str(df.iloc[row_idx, c[1]]).strip().upper()
                    t = str(df.iloc[row_idx, c[0]]).strip()
                    e = EMOJIS.get(l, "🏸")
                    # Label for the dropdown menu
                    mid = f"{e} {l} | {t} | {t1} vs {t2}"
                    m.append({"ID":mid,"Day":curr_day,"T":t,"T1":t1,"T2":t2,"L":l,"Emoji":e})
                    clrs[t1] = clrs[t2] = l
                    
                    try:
                        vals = [float(df.iloc[row_idx, col]) for col in [c[4], c[5], c[6], c[7]]]
                        s1, s2, s3, s4 = [int(v) for v in vals]
                        if sum(vals) > 0:
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
            sel = st.selectbox("Search/Select Match (by Color)", m_filt)
            if sel:
                d = sch[sch["ID"]==sel].iloc[0]
                c1, c2 = st.columns(2)
                s1, s2 = c1.number_input(f"S1 {d['T1']}",0,21,key=f"a{sel}"), c1.number_input(f"S2 {d['T1']}",0,21,key=f"b{sel}")
                s3, s4 = c2.number_input(f"S1 {d['T2']}",0,21,key=f"c{sel}"), c2.number_input(f"S2 {d['T2']}",0,21,key=f"d{sel}")
                if st.button("Save Score", type="primary", use_container_width=True):
                    w1, w2 = (s1>s3)+(s2>s4), (s3>s1)+(s4>s2)
                    st.session_state.db[sel] = {"sc":f"{s1}-{s3}, {s2}-{s4}","t1":d['T1'],"t2":d['T2'],"p1":s1+s2,"p2":s3+s4,"w1":w1,"l1":w2,"w2":w2,"l2":w1}
                    st.success(f"Score saved for {d['T1']} vs {d['T2']}!")
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
        L = [{"Time":r["T"], "Bracket":f"{r['Emoji']} {r['L']}", "Match":f"{r['T1']} vs {r['T2']}", "Result":st.session_state.db.get(r["ID"],{}).get("sc","--")} for _,r in sch[sch["Day"] == v_day].iterrows() if q in r['T1'].lower() or q in r['T2'].lower()]
        if L: st.table(L)
