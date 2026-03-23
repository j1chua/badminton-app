import streamlit as st
import pandas as pd
import os

# 1. Page Config
st.set_page_config(page_title="SMASH 2026", layout="wide")
F = "SMASH 2026 - Score Tracker.csv"
EMO = {"BLACK":"⚫","RED":"🔴","GREEN":"🟢","PURPLE":"🟣","WHITE":"⚪","YELLOW":"🟡"}

# 2. Data Engine
@st.cache_data
def ld():
    if not os.path.exists(F): return None,{},{}
    df = pd.read_csv(F,header=None).fillna("")
    m,cl,db,dy = [],{},{},"Day 1"
    bk = [[0,1,2,7,3,4,8,9],[13,14,15,20,16,17,21,22]]
    for i,r in df.iterrows():
        sr = " ".join(map(str,r)).upper()
        if "DAY 2" in sr: dy="Day 2"
        elif "DAY 1" in sr: dy="Day 1"
        for c in bk:
            t1,t2 = str(r[c[2]]).strip(),str(r[c[3]]).strip()
            if "|" not in t1: continue
            tm,L = str(r[c[0]]).strip(),str(r[c[1]]).strip().upper()
            p1,p2 = t1.replace("|"," & "),t2.replace("|"," & ")
            # Court Finder
            ct = "Court ?"
            for p in range(i,-1,-1):
                v = [str(x).upper() for x in df.iloc[p]]
                f = [x for x in v if "COURT" in x]
                if f: ct=f[0]; break
            # Match Data
            id = f"{dy}{ct}{tm}{p1}"
            d = {"ID":id,"Dy":dy,"T":tm,"P1":p1,"P2":p2,"T1":t1,"T2":t2,"L":L,"C":ct}
            m.append(d)
            cl[t1]=cl[t2]=L
            # Score Logic (Fixed 210 issue)
            sc = []
            for k in [4,5,6,7]:
                v = "".join(filter(str.isdigit,str(r[c[k]])))
                sc.append(int(v) if v else 0)
            w1,w2 = (sc[0]>sc[2])+(sc[1]>sc[3]),(sc[2]>sc[0])+(sc[3]>sc[1])
            db[id] = {"s1":sc[0],"s2":sc[1],"s3":sc[2],"s4":sc[3],"t1":t1,"t2":t2,"w1":w1,"w2":w2}
    return pd.DataFrame(m),cl,db

# 3. UI Styling
st.markdown("""<style>
    .m-t{width:100%;border-collapse:collapse;}
    .m-t th,.m-t td{text-align:center;padding:8px;border:1px solid #ddd;}
    .win{background:#e8f5e9;color:#2e7d32;font-weight:bold;border-radius:3px;}
</style>""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
dt,cls,db = ld()

if dt is not None:
    t1,t2 = st.tabs(["📊 Standings","📅 Schedule"])
    with t1:
        st.subheader("Leaderboard")
        res = {t:{"Bracket":cls[t],"Sets Won":0} for t in cls}
        for v in db.values():
            if v['t1'] in res: res[v['t1']]["Sets Won"] += v['w1']
            if v['t2'] in res: res[v['t2']]["Sets Won"] += v['w2']
        df_s = pd.DataFrame.from_dict(res,"index").reset_index()
        for b in sorted(df_s["Bracket"].unique()):
            st.write(f"### {EMO.get(b,'🏆')} {b} Bracket")
            sdf = df_s[df_s["Bracket"]==b].sort_values("Sets Won",ascending=False)
            st.table(sdf.drop(columns=["Bracket"]))
    with t2:
        colA,colB = st.columns([1,2])
        d_s = colA.radio("Select Day",["Day 1","Day 2"],horizontal=True)
        sh = colB.text_input("🔍 Search Team").lower()
        rows = []
        for _,r in dt[dt["Dy"]==d_s].iterrows():
            if sh and sh not in r["P1"].lower() and sh not in r["P2"].lower(): continue
            d = db.get(r["ID"])
            if d:
                p1 = f"**{r['P1']}**" if d['w1']==2 else r['P1']
                p2 = f"**{r['P2']}**" if d['w2']==2 else r['P2']
                rows.append({"Time":r["T"],"Court":r["C"],"Match":f"{p1} vs {p2}","S1":f"{d['s1']}-{d['s3']}","S2":f"{d['s2']}-{d['s4']}","Res":f"{d['w1']}-{d['w2']}"})
        if rows: st.write(pd.DataFrame(rows).to_html(escape=False,index=False,classes="m-t"),unsafe_allow_html=True)
