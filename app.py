import streamlit as st
import pandas as pd
import os

# 1. Setup
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th") if not 10 <= i % 100 <= 20 else "th"
    return f"{i}{suffix}"

# 2. Data Loader (Flattened to avoid Syntax Errors)
@st.cache_data
def load_data():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    matches, colors, db, day = [], {}, {}, "Day 1"
    blks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
    
    for idx, row in df.iterrows():
        r_txt = " ".join(map(str, row)).upper()
        if "DAY 2" in r_txt: day = "Day 2"
        elif "DAY 1" in r_txt: day = "Day 1"
        
        for c in blks:
            t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
            if "|" not in t1 or "|" not in t2: continue
            
            L = str(row[c[1]]).strip().upper()
            tm, e = str(row[c[0]]).strip(), EMOJIS.get(L, "🏸")
            ct = "Court ?"
            for r_ptr in range(idx, -1, -1):
                vals = [str(v).upper() for v in df.iloc[r_ptr]]
                found = [v for v in vals if "COURT" in v]
                if found: 
                    ct = found[0].strip()
                    break
            
            p1, p2 = t1.replace("|", " AND "), t2.replace("|", " AND ")
            mid = f"{ct}|{L}|{tm}|{p1}vs{p2}"
            matches.append({"ID":mid,"Day":day,"T":tm,"T1":t1,"T2":t2,"P1":p1,"P2":p2,"L":L,"Emoji
