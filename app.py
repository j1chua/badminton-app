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

# 2. Data Loader (Shortened lines to prevent cutoff)
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
            
            # BROKEN INTO SHORT LINES TO PREVENT SYNTAX ERRORS
            m_data = {"ID": mid, "Day": day, "T": tm}
            m_data["T1"] = t1
            m_data["T2"] = t2
            m_data["P1"] = p1
            m_data["P2"] = p2
            m_data["L"] = L
            m_data["Emoji"] = e
            m_data["Court"] = ct
            matches.append(m_data)
            
            colors[t1] = colors[t2] = L
            scores = []
            for col_idx in [c[4],c[5],c[6],c[7]]:
                val = str(row[col_idx]).strip().replace('.','',1)
                scores.append(int(float(val)) if val.isdigit() else 0)
            
            w1 = (scores[0] > scores[2]) + (scores[1] > scores[3])
            w2 = (scores[2] > scores[0]) + (scores[3] > scores[1])
            db[mid] = {"s1":scores[0],"s2":scores[1],"s3":scores[2],"s4":scores[3],"t1":t1,
                       "t2":t2,"p1":scores[0]+scores[1],"p2":scores[2]+scores[3],"w1":w1
