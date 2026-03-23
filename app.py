import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMO = {"BLACK":"⚫","RED":"🔴","GREEN":"🟢","PURPLE":"🟣","WHITE":"⚪","YELLOW":"🟡"}

def rk(i):
    s = {1:"🥇 <b>1st</b>",2:"🥈 <b>2nd</b>",3:"🥉 <b>3rd</b>"}
    if i in s: return s[i]
    x = "th" if 10<=i%100<=20 else {1:"st",2:"nd",3:"rd"}.get(i%10,"th")
    return f"{i}{x}"

@st.cache_data
def ld():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    m, cl, db, dy = [], {}, {}, "Day 1"
    bk = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
    for idx, r in df.iterrows():
        txt = " ".join(map(str, r)).upper()
        if "DAY 2" in txt: dy = "Day 2"
        elif "DAY 1" in txt: dy = "Day 1"
        for c in bk:
            t1, t2 = str(r[c[2]]).strip(), str(r[c[3]]).strip()
            if "|" not in t1 or "|" not in t2: continue
            L = str(r[c[1]]).strip().upper()
            tm, e = str(r[c[0]]).strip(), EMO.get(L, "🏸")
            ct = "Court ?"
            for p in range(idx, -1, -1):
                v = [str(x).upper() for x in df.iloc[p]]
                f = [x for x in v if
