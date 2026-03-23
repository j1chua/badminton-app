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
    # Read raw CSV
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
                    
                    # Find Court Name
                    court_label = "Court ?"
                    found = False
                    for r_search in range(row_idx, -1, -1):
                        for col_off in range(-2, 3):
                            check_col = c_name_col + col_off
                            if 0 <=
