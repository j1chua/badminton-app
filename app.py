import streamlit as st
import pandas as pd
import os

st.title("🏸 SMASH 2026")
FN = "SMASH 2026 - Score Tracker.csv"

@st.cache_data
def ld():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    m, cl, db, dy = [], {}, {}, "Day 1"
    bk = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
    for idx, r in df.iterrows():
        ts = " ".join(map(str, r)).upper()
        if "DAY 2" in ts: dy = "Day 2"
        elif "DAY 1" in ts: dy = "Day 1"
        for c in bk:
            t1, t2 = str(r[c[2]]).strip(), str(r[c[3]]).strip()
            if "|" not in t1: continue
            tm = str(r[c[0]]).strip()
            p1, p2 = t1.replace("|"," & "), t2.replace("|"," & ")
            id = f"{dy}{tm}{p1}"
            m.append({"ID":id,"Dy":dy,"T":tm,"P1":p1,"P2":p2,"T1":t1,"T2":t2})
            cl[t1] = cl[t2] = str(r[c[1]]).strip().upper()
            s = []
            for col in [c[4],c[5],c[6],c[7]]:
                v = "".join(filter(str.isdigit, str(r[col])))
                s.append(int(v) if v else 0)
            w1 = (s[0]>s[2])+(s[1]>s[3])
            w2 = (s[2]>s[0])+(s[3]>s[1])
            db[id] = {"s1":s[0],"s2":s[1],"s3":s[2],"s4":s[3],"t1":t1,"t2":t2,"w1":w1,"w2":w2}
    return pd.DataFrame(m), cl, db

data, clrs, d_b = ld()

if data is not None:
    t1, t2 = st.tabs(["📊 Standings", "📅 Schedule"])
    with t1:
        st.write("Standings Loading...")
        res = {t:{"Bracket":clrs[t],"Wins":0} for t in clrs}
        for v in d_b.values():
            if v['t1'] in res: res[v['t1']]["Wins"] += v['w1']
            if v['t2'] in res: res[v['t2']]["Wins"] += v['w2']
        st.table(pd.DataFrame.from_dict(res, "index"))
    with t2:
        day = st.radio("Day", ["Day 1", "Day 2"])
        for _, r in data[data["Dy"]==day].iterrows():
            d = d_b.get(r["ID"])
            if d:
                st.write(f"**{r['T']}**: {r['P
