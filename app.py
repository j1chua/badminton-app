import streamlit as st
import pandas as pd
import os

st.title("🏸 SMASH 2026")
F = "SMASH 2026 - Score Tracker.csv"

@st.cache_data
def ld():
    if not os.path.exists(F):
        return None,{},{}
    df = pd.read_csv(F,header=None)
    df = df.fillna("")
    m,cl,db,dy = [],{},{},"Day 1"
    bk = [[0,1,2,7,3,4,8,9],
          [13,14,15,20,16,17,21,22]]
    for i,r in df.iterrows():
        s_r = " ".join(map(str,r))
        s_r = s_r.upper()
        if "DAY 2" in s_r: dy="Day 2"
        if "DAY 1" in s_r: dy="Day 1"
        for c in bk:
            v1 = str(r[c[2]])
            t1 = v1.strip()
            v2 = str(r[c[3]])
            t2 = v2.strip()
            if "|" not in t1:
                continue
            tm = str(r[c[0]])
            p1 = t1.replace("|","&")
            p2 = t2.replace("|","&")
            id = f"{dy}{tm}{p1}"
            d = {"ID":id,"Dy":dy}
            d["T"],d["P1"] = tm,p1
            d["P2"],d["T1"] = p2,t1
            d["T2"] = t2
            m.append(d)
            v_l = str(r[c[1]])
            cl[t1] = v_l.strip()
            cl[t2] = v_l.strip()
            sc = []
            for k in [4,5,6,7]:
                v = str(r[c[k]])
                cln = ""
                for ch in v:
                    if ch.isdigit():
                        cln += ch
                num = 0
                if cln: num = int(cln)
                sc.append(num)
            w1 = (sc[0]>sc[2])
            w1 += (sc[1]>sc[3])
            w2 = (sc[2]>sc[0])
            w2 += (sc[3]>sc[1])
            res = {"s1":sc[0],"s2":sc[1]}
            res["s3"] = sc[2]
            res["s4"] = sc[3]
            res["t1"],res["t2"] = t1,t2
            res["w1"],res["w2"] = w1,w2
            db[id] = res
    return pd.DataFrame(m),cl,db

dt,cls,db = ld()

if dt is not None:
    t_a,t_b = st.tabs(["List","Rank"])
    with t_b:
        st.write("Standings")
        st.table(pd.Series(cls))
    with t_a:
        d_s = st.radio("D",["Day 1","Day 2"])
        f = dt[dt["Dy"]==d_s]
        for _,r in f.iterrows():
            st.write("---")
            st.write(r["T"])
            st.write(r["P1"])
            st.write("vs")
            st.write(r["P2"])
            d = db.get(r["ID"])
            if d:
                s1,s2 = d["s1"],d["s2"]
                s3,s4 = d["s3"],d["s4"]
                st.write(f"S1: {s1}-{s3}")
                st.write(f"S2: {s2}-{s4}")
