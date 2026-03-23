import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"

EMOJIS = {
    "BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", 
    "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"
}

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    suffix = "th"
    if 10 <= i % 100 <= 20: suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th")
    return f"{i}{suffix}"

@st.cache_data
def load():
    if not os.path.exists(FN): return None, {}, {}
    try:
        df = pd.read_csv(FN, header=None).fillna("")
        m, clrs, init_db = [], {}, {}
        curr_day = "Day 1"
        blocks = [("Left", [0,1,2,7,3,4,8,9]), ("Right", [13,14,15,20,16,17,21,22])]

        for row_idx in range(len(df)):
            row_str = " ".join([str(x) for x in df.iloc[row_idx]]).upper()
            if "DAY 2" in row_str: curr_day = "Day 2"
            elif "DAY 1" in row_str: curr_day = "Day 1"
            
            for side, c in blocks:
                try:
                    t1, t2 = str(df.iloc[row_idx, c[2]]).strip(), str(df.iloc[row_idx, c[3]]).strip()
                    if "|" in t1 and "|" in t2:
                        l = str(df.iloc[row_idx, c[1]]).strip().upper()
                        t = str(df.iloc[row_idx, c[0]]).strip()
                        e = EMOJIS.get(l, "🏸")
                        
                        court_label = "Court ?"
                        found = False
                        for r_search in range(row_idx, -1, -1):
                            row_vals = df.iloc[r_search].astype(str).tolist()
                            for
