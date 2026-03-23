import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMO = {"BLACK":"⚫","RED":"🔴","GREEN":"🟢","PURPLE":"🟣","WHITE":"⚪","YELLOW":"🟡"}

def rk(i):
    s = {1:"🥇 1st", 2:"🥈 2nd", 3:"🥉 3rd"}
    if i in s: return f"<b>{s[i]}</b>"
    return f"{i}th"

@st.cache_data
def ld():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    m, cl, db, dy = [], {}, {}, "Day 1"
    bk = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
    for idx, r in df.iterrows():
        t_str = " ".join(map(str, r)).upper()
        if "DAY 2" in t_str: dy = "Day 2"
        elif "DAY 1" in t_str: dy = "Day 1"
        for c in bk:
            t1, t2 = str(r[c[2]]).strip(), str(r[c[3]]).strip()
            if "|" not in t1 or "|" not in t2: continue
            L = str(r[c[1]]).strip().upper()
            tm, e = str(r[c[0]]).strip(), EMO.get(L, "🏸")
            ct = "Court ?"
            for p in range(idx, -1, -1):
                found = False
                for val in df.iloc[p]:
                    if "COURT" in str(val).upper():
                        ct = str(val).strip()
                        found = True; break
                if found: break
            p1, p2 = t1.replace("|", " AND "), t2.replace("|", " AND ")
            id = f"{ct}{L}{tm}{p1}"
            m.append({"ID":id,"Dy":dy,"T":tm,"P1":p1,"P2":p2,"T1":t1,"T2":t
