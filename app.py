import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"

@st.cache_data
def load_data():
    if not os.path.exists(FN): return None, {}
    df = pd.read_csv(FN)
    m, colors = [], {}
    cfgs = [
        {"n":"C1","r":(1,10),"c":(0,1,2,7)}, {"n":"C3","r":(13,22),"c":(12,1,2,7)},
        {"n":"C5","r":(25,34),"c":(24,1,2,7)}, {"n":"C7","r":(37,46),"c":(36,1,2,7)},
        {"n":"C2","r":(1,10),"c":(13,14,15,20)}, {"n":"C4","r":(13,22),"c":(12,14,15,20)},
        {"n":"C6","r":(25,34),"c":(24,14,15,20)}, {"n":"C8","r":(37,46),"c":(36,14,15,20)}
    ]
    for c in cfgs:
        for i in range(c["r"][0], c["r"][1]):
            try:
                t1, t2 = str(df.iloc[i,c["c"][2]]).strip(), str(df.iloc[i,c["c"][3]]).strip()
                clr, tm = str(df.iloc[i,c["c"][1]]).strip().upper(), str(df.iloc[i,c["c"][0]]).strip()
                if "|" in t1:
                    m.append({"ID":f"{c['n']} | {tm} | {t1} vs {t2}","C":c["n"],"T":tm,"T1":t1,"T2":t2,"Clr":clr})
                    colors[t1] = colors[t2] = clr
            except: continue
    return pd.DataFrame(m), colors

st.title("🏸 SMASH 2026 Tournament Central")
sch, clrs = load_data()

if sch is None: st.error(f"Missing: {FN}")
else:
    if 'db' not in st.session_state: st.session_
