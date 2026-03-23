import streamlit as st
import pandas as pd
import os

# 1. Setup & Score Fix
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMO = {
    "BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", 
    "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"
}

def clean_sc(v):
    """Fixes the 210-160 score glitch"""
    c = "".join(filter(str.isdigit, str(v)))
    return int(c) if c else 0

def get_rk(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    return f"{i}th"

# 2. Data Logic
@st.cache_data
def ld():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    m, cl, db, dy = [], {}, {}, "Day 1"
    bk = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]

    for idx, r in df.iterrows():
        ts = " ".join([str(x) for x in r]).upper()
        if "DAY 2" in ts: dy = "Day 2"
        elif "DAY 1" in ts: dy = "Day 1"
        for c in bk:
            t1, t2 = str(r[c[2]]).strip(), str(r[c[3]]).strip()
            if "|" not in t1: continue
            L = str(r[c[1]]).strip().upper()
            tm = str(r[c[0]]).strip()
            p1, p2 = t1.replace("|","&"), t2.replace("|","&")
            
            # Court Search
            ct = "Court ?"
            for p_idx in range(idx, -1, -1):
                sv = [str(v).upper() for v in df.iloc[p_idx]]
                if any("COURT" in v for v in sv):
                    ct = next(v.strip() for v in sv if "COURT" in v)
                    break

            id = f"{dy}{ct}{tm}{p1}"
            m.append({
                "ID":id, "Dy":dy, "T":tm, 
                "P1":p1, "P2":p2, "T1":t1, 
                "T2":t2, "L":L, "C":ct
            })
            cl[t1] = cl[t2] = L
            
            # Apply Score Fix
            s = [clean_sc(r[col]) for col in [c[4],c[5],c[6],c[7]]]
            w1 = (s[0]>s[2])+(s[1]>s[3])
            w2 = (s[2]>s[0])+(s[3]>s[1])
            db[id] = {
                "s1":s[0], "s2":s[1], "s3":s[2], "s4":s[3],
                "t1":t1, "t2":t2, "w1":w1, "w2":w2
            }
    return pd.DataFrame(m), cl, db

# 3. Main App
st.title("
