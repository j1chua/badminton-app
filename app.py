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
    df = pd.read_csv(FN, header=None).fillna(0)
    m, clrs, init_db = [], {}, {}
    curr_day = "Day 1"
    
    # Blocks: [Time, Color, Team1, Team2, T1S1, T1S2, T2S1, T2S2]
    blocks = [
        ("Left", [0,1,2,7,3,4,8,9], 2),
        ("Right", [13,14,15,20,16,17,21,22], 15)
    ]

    for row_idx in range(len(df)):
        row_str = " ".join(df.iloc[row_idx].astype(str)).upper()
        if "DAY 2" in row_str: curr_day = "Day 2"
        elif "DAY 1" in row_str: curr_day = "Day 1"
        
        for side, c, c_name_col in blocks:
            try:
                t1, t2 = str(df.iloc[row_idx, c[2]]).strip(), str(df.iloc[row_idx, c[3]]).strip()
                if "|" in t1 and "|" in t2:
                    l = str(df.iloc[row_idx, c[1]]).strip().upper()
                    t = str(df.iloc[row_idx, c[0]]).strip()
                    e = EMOJIS.get(l, "🏸")
                    
                    # Find Court Name
                    court_label = "Unknown Court"
                    for search_up in range(row_idx, -1, -1):
                        potential_court = str(df.iloc[search_up, c_name_col]).strip()
                        if "COURT" in potential_court.upper():
                            court_label = potential_court
                            break
                    
                    # REFORMATTED ID: Court | Emoji Color | | Time | Match
                    mid = f"{court_label} | {e} {l} | | {t} | {t1} vs {t2}"
                    
                    m.append({"ID":mid,"Day":curr_day,"T":t,"T1":t1,"T2":t2,"L":l,"Emoji":e, "Court": court_label})
                    clrs[t1] = clrs[t2] = l
                    
                    try:
                        vals = [float(df
