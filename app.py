import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"

@st.cache_data
def load():
    if not os.path.exists(FN): return None, {}
    # Use header=None to handle the complex layout manually
    df = pd.read_csv(FN, header=None).fillna(0)
    m, clrs, init_db = [], {}, {}
    
    # Left Side Courts (1, 3, 5, 7) | Right Side Courts (2, 4, 6, 8)
    # Mapping: (Name, RowRange, ColIndices[Time, Color, T1, T2, T1_S1, T1_S2, T2_S1, T2_S2])
    cf = [
        ("C1",(2,11),(0,1,2,7,3,4,8,9)),   ("C2",(2,11),(13,14,15,20,16,17,21,22)),
        ("C3",(14,23),(0,1,2,7,3,4,8,9)),  ("C4",(14,23),(13,14,15,20,16,17,21,22)),
        ("C5",(26,35),(0,1,2,7,3,4,8,9)),  ("C6",(26,35),(13,14,15,20,16,17,21,22)),
        ("C7",(38,47),(0,1,2,7,3,4,8,9)),  ("C8",(38,47),(13,14,15,20,16,17,21,22))
    ]

    for n, r, c in cf:
        for i in range(r[0], r[1]):
            try:
                t1, t2 = str(df.iloc[i,c[2]]).strip(), str(df.iloc[i,c[3]]).strip()
                l, t = str(df.iloc[i,c[1]]).strip().upper(), str(df.iloc[i,c[0]]).strip()
                if "|" in t1 and "|" in t2:
                    mid = f"{n}|{t}|{t1}v{t2}"
                    m.append({"ID":mid,"C":n,"T":t,"T1":t1,"T2":t2,"L":l})
                    clrs[t1] = clrs[t2] = l
                    
                    # AUTO-LOAD SCORES FROM CSV
                    try:
                        s1, s2 = int(float(df.iloc[i,c[4]])), int(float(df.iloc[i,c[5]]))
                        s3, s4 = int(float(df.iloc[i,c[6]])), int(float(df.iloc[i,c[7]]))
                        if (s1+s2+s3+s4) > 0:
                            w1, w2 = (s1>s3)+(s2>s4), (s3>s1)+(s4>s2)
                            init_db[mid] = {"sc":f"{s1}-{s3}, {s2}-{s4}","t1":t1,"t2":t2,"p1":s1+s2,"p2":s3+s4,"w1":w1,"l1":w2,"w2":w2,"l2":w1}
                    except: pass
            except: continue
    return pd.DataFrame(m), clrs, init_db

st.title("🏸 SMASH 2026 Tournament Central")
sch, clrs, csv_scores = load()

if sch is None: st.error("CSV Missing")
else:
    # Merge CSV scores with session state (Session state takes priority)
    if 'db' not in st.session_state: st.session_state.db = csv_scores
    
    t1, t2, t3 = st.tabs(["📊 Standings", "📅 Schedule", "🔐 Entry"])

    with t3:
        pw = st.text_input("Admin Password", type="password")
        if pw == "pogisiJordan":
            sel = st.selectbox("Match", sch["ID"].tolist())
            d = sch[sch["ID"]==sel].iloc[0]
            c1, c2 = st.columns(2)
            s1, s2 = c1.number_input(f"S1 {d['T1']}",0,21,key=f"a{sel}"), c1.number_input(f"S2 {d['T1']}",0,21,key=f"b{sel}")
            s3, s4 = c2.number_input(f"S1 {d['T2']}",0,21,key=f"c{sel}"), c2.number_input(f"S2 {d['T2']}",0,21,key=f"d{sel}")
            if st.button("Save", type="primary", use_container_width=True):
                w1, w2 = (s1>s3)+(s2>s4), (s3>s1)+(s4>s2)
                st.session_state.db[sel] = {"sc":f"{s1}-{s3}, {s2}-{s4}","t1":d['T1'],"t2":d['T2'],"p1":s1+s2,"p2":s3+s4,"w1":w1,"l1":w2,"w2":w2,"l2":w1}
                st.success("Saved")
            if st.button("Reset", use_container_width=True):
                if sel in st.session_state.db: del st.session_state.db[sel]
                st.rerun()
        elif pw != "": st.error("Access Denied")

    with t1:
        res = {t:{"Brk":clrs.get(t,"?"),"W":0,"L":0,"Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            for i in [1,2]:
                res[v[f't{i}']]["W"]+=v[f'w{i}']; res[v[f't{i}']]["L"]+=v[f'l{i}']; res[v[f't{i}']]["Pts"]+=v[f'p{i}']
        df_r = pd.DataFrame.from_dict(res, orient='index').reset_index().rename(columns={'index':'Team'})
        for c in sorted(df_r["Brk"].unique()):
            st.subheader(f"🏆 {c} Bracket")
            st.table(df_r[df_r["Brk"]==c].sort_values(["W","Pts"], ascending=False))

    with t2:
        q = st.text_input("🔍 Search Team").lower()
        for ct in sorted(sch["C"].unique()):
            with st.expander(f"📍 {ct}", expanded=True):
                L = [{"Time":r["T"],"Brk":r["L"],"Match":f"{r['T1']} vs {r['T2']}","Res":st.session_state.db.get(r["ID"],{}).get("sc","--")} for _,r in sch[sch["C"]==ct].iterrows() if q in r['T1'].lower() or q in r['T2'].lower()]
                if L: st.table(L)
