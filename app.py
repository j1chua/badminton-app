import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"

# Emoji Mapping for Brackets
EMOJIS = {
    "BLACK": "⚫",
    "RED": "🔴",
    "GREEN": "🟢",
    "PURPLE": "🟣",
    "WHITE": "⚪",
    "YELLOW": "🟡"
}

@st.cache_data
def load():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna(0)
    m, clrs, init_db = [], {}, {}
    curr_day = "Day 1"
    
    blocks = [("Left", [0,1,2,7,3,4,8,9]), ("Right", [13,14,15,20,16,17,21,22])]

    for row_idx in range(len(df)):
        row_str = " ".join(df.iloc[row_idx].astype(str)).upper()
        if "DAY 2" in row_str: curr_day = "Day 2"
        elif "DAY 1" in row_str: curr_day = "Day 1"
        
        for side, c in blocks:
            try:
                t1, t2 = str(df.iloc[row_idx, c[2]]).strip(), str(df.iloc[row_idx, c[3]]).strip()
                if "|" in t1 and "|" in t2:
                    l, t = str(df.iloc[row_idx, c[1]]).strip().upper(), str(df.iloc[row_idx, c[0]]).strip()
                    mid = f"{curr_day} | {t} | {t1} vs {t2}"
                    m.append({"ID":mid,"Day":curr_day,"T":t,"T1":t1,"T2":t2,"L":l})
                    clrs[t1] = clrs[t2] = l
                    
                    try:
                        vals = [float(df.iloc[row_idx, col]) for col in [c[4], c[5], c[6], c[7]]]
                        s1, s2, s3, s4 = [int(v) for v in vals]
                        if sum(vals) > 0:
                            w1, w2 = (s1>s3)+(s2>s
