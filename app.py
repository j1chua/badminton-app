import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"

@st.cache_data
def load():
    if not os.path.exists(FN): return None, {}
    df, m, clrs = pd.read_csv(FN), [], {}
    cf = [
        ("C1",(1,10),(0,1,2,7)), ("C3",(13,22),(12,1,2,7)), ("C5",(25,34),(24,1,2,7)), ("C7",(37,46),(36,1,2,7)),
        ("C2",(1,10),(13,14,15,20)), ("C4",(13,22),(12,14,15,20)), ("C6",(25,34),(24,14,15,20)), ("C8",(37,46),(36,14,15,20))
    ]
    for n, r, c in cf:
        for i in range(r[0], r[1]):
            try:
                t1, t2 = str(df.iloc[i,c[2]]).strip(), str(df.iloc[i,c[3]]).strip()
                l, t = str(df.iloc[i,c[1]]).strip().upper(), str(df.iloc[i,c[0]]).strip()
                if "|" in t1:
                    m.append({"ID":f"{n}|{t}|{t1}v{t2}","C":n,"T":t,"T1":t1,"T2":t2,"L":l})
                    clrs[t1] = clrs[t2] = l
            except: continue
    return pd.DataFrame(m), clrs

st.title("🏸 SMASH 2026")
sch, clrs = load()

if sch is None: st.error("CSV Missing")
else:
    if 'db' not in st.session_state: st.session_state.db = {}
    t1, t2, t3 = st.tabs(["📊 Standings", "📅 Schedule", "🔐 Entry"])

    with t3:
        pw = st.text_input("Admin Password", type="password")
        if pw == "pogisiJordan":
            sel = st.selectbox("Match", sch["ID"].tolist())
            d = sch[sch["ID"]==sel].iloc[0]
            c1, c2 = st.columns(2)
            s1, s2 = c1.number_input(f"S1 {d['T1']}",0,21,key=f"a{sel}"), c1.number_input(f"S2 {d['T1']}",0,21,key=f"b{sel}")
            s3, s4 = c2.number_input(f"S1 {d['T2']}",0,21,key=f"c{sel}"), c2.number_input(f"S2 {d['T2']}",0,21,key=f"d{sel}")
            b1, b2 = st.columns(2)
            if b1.button("Save", type="primary", use_container_width=True):
                w1, w2 = (s1>s3)+(s2>s4), (s3>s1)+(s4>s2)
                st.session_state.db[sel] = {"sc":f"{s1}-{s3}, {s2}-{s4}","t1":d['T1'],"t2":d['T2'],"p1":s1+s2,"p2":s3+s4,"w1":w1,"l1":w2,"w2":w2,"l2":w1}
                st.success("Saved")
            if b2.button("Reset", use_container_width=True):
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
            st.subheader(f"🏆 {c}")
            st.table(df_r[df_r["Brk"]==c].sort_values(["W","Pts"], ascending=False))

    with t2:
        q = st.text_input("🔍 Search Team").lower()
        for ct in sorted(sch["C"].unique()):
            with st.expander(f"📍 {ct}", expanded=True):
                L = [{"Time":r["T"],"Brk":r["L"],"Match":f"{r['T1']} vs {r['T2']}","Res":st.session_state.db.get(r["ID"],{}).get("sc","--")} for _,r in sch[sch["C"]==ct].iterrows() if q in r['T1'].lower() or q in r['T2'].lower()]
                if L: st.table(L)
