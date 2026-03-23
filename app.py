import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"

# Emoji Mapping
EMOJIS = {
    "BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", 
    "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"
}

@st.cache_data
def load():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    m, clrs, init_db = [], {}, {}
    curr_day = "Day 1"
    
    # [Time, Color, T1, T2, T1S1, T1S2, T2S1, T2S2]
    blocks = [
        ("Left", [0,1,2,7,3,4,8,9], 2),
        ("Right", [13,14,15,20,16,17,21,22], 15)
    ]

    for row_idx in range(len(df)):
        row_str = " ".join([str(x) for x in df.iloc[row_idx]]).upper()
        if "DAY 2" in row_str: curr_day = "Day 2"
        elif "DAY 1" in row_str: curr_day = "Day 1"
        
        for side, c, c_name_col in blocks:
            try:
                t1, t2 = str(df.iloc[row_idx, c[2]]).strip(), str(df.iloc[row_idx, c[3]]).strip()
                if "|" in t1 and "|" in t2:
                    l = str(df.iloc[row_idx, c[1]]).strip().upper()
                    t = str(df.iloc[row_idx, c[0]]).strip()
                    e = EMOJIS.get(l, "🏸")
                    
                    # WIDER Court Finder: Searches 3 columns left/right and up to 10 rows up
                    court_label = "Court ?"
                    found = False
                    for r_search in range(row_idx, -1, -1):
                        for col_off in range(-3, 4):
                            check_col = c_name_col + col_off
                            if 0 <= check_col < len(df.columns):
                                val = str(df.iloc[r_search, check_col]).strip()
                                if "COURT" in val.upper():
                                    court_label = val
                                    found = True
                                    break
                        if found: break
                    
                    p1, p2 = t1.replace("|", " AND "), t2.replace("|", " AND ")
                    
                    # FORMAT: Court 1 | 🔴 RED | 2:30 | NAME AND NAME vs NAME AND NAME
                    mid = f"{court_label} | {e} {l} | {t} | {p1} vs {p2}"
                    
                    m.append({"ID":mid,"Day":curr_day,"T":t,"T1":t1,"T2":t2,"P1":p1,"P2":p2,"L":l,"Emoji":e, "Court": court_label})
                    clrs[t1] = clrs[t2] = l
                    
                    try:
                        v = [df.iloc[row_idx, col] for col in [c[4], c[5], c[6], c[7]]]
                        s1, s2, s3, s4 =
