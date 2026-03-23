import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026")
FN = "SMASH 2026 - Score Tracker.csv"
EMO = {
    "BLACK":"⚫","RED":"🔴","GREEN":"🟢",
    "PURPLE":"🟣","WHITE":"⚪","YELLOW":"🟡"
}

def rk(i):
    s = {1:"🥇 1st", 2:"🥈 2nd", 3:"🥉 3rd"}
    if i in s: return f"<b>{s[i]}</b>"
    return f"{i}th"

@st.cache_data
def ld():
    if not os.path.exists(FN): 
        return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    m, cl, db, dy = [], {}, {}, "Day 1"
    bk = [
        [0,1,2,7,3,4,8,9], 
        [13,14,15,20,16,17,21,22]
    ]
    for idx, r in df.iterrows():
        ts = " ".join(map(str, r)).upper()
        if "DAY 2" in ts: dy = "Day 2"
        elif "DAY 1" in ts: dy = "Day 1"
        for c in bk:
            t1 = str(r[c[2]]).strip()
            t2 = str(r[c[3]]).strip()
            if "|" not in t1 or "|" not in t2: 
                continue
            L = str(r[c[1]]).strip().upper()
            tm = str(r[c[0]]).strip()
            e = EMO.get(L, "🏸")
            ct = "Court ?"
            for p in range(idx, -1, -1):
                fnd = False
                for v in df.iloc[p]:
                    if "COURT" in str(v).upper():
                        ct = str(v).strip()
                        fnd = True
                        break
                if fnd: break
            p1 = t1.replace("|", " AND ")
            p2 = t2.replace("|", " AND ")
            id = f"{ct}{L}{tm}{p1}"
            
            # SPLIT INTO TINY LINES
            d = {"ID":id, "Dy":dy, "T":tm}
            d["P1"], d["P2"] = p1, p2
            d["T1"], d["T2"] = t1, t2
            d["L"], d["E"], d["C"] = L, e, ct
            m
