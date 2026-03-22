import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"

@st.cache_data
def load():
    if not os.path.exists(FN): return None, {}
    df = pd.read_csv(FN, header=None).fillna(0)
    m, clrs, init_db = [], {}, {}
    # Row/Col mapping for Courts 1-8
    cf = [
        ("C1",(2,11),(0,1,2,7,3,4,8,9)),   ("C2",(2,11),(13,14,15,20,16,17,21,22)),
        ("C3",(14,23),(0,1,2,7,3,4,8,9)),  ("C4",(14,23),(13,14,15,20,16,17,21,22)),
        ("C5",(26,35),(0,1,2,7,3,4,8,9)),  ("C6",(26,35),(13,14,15,20,16,17,21,22)),
        ("C7",(38,47),(0,1,2,7,3,4,8,9)),  ("C8",(38,47),(13,14,15,20,16,17,21,22))
    ]
    for n, r, c in cf:
        for i in range(r[0], r[1]):
            try:
                t1, t2 = str(df.iloc[i,c[2]]).strip(), str(df.iloc[i,c[3]]).strip()
                l, t = str(df.iloc[i,c[1]]).strip().upper(), str(df.iloc[i,c[0]]).strip()
                if "|" in t1:
                    mid = f"{n}|{t}|{t1}v{t2}"
                    m.append({"ID":mid,"C":n,"T":t,"T1":t1,"T2":t2,"L":l})
                    clrs[t1] = clrs[t2] = l
                    try:
                        s1, s2 = int(float(df.iloc[i,c[4]])), int(float(df.iloc[i,c[5]]))
                        s3, s4 = int(float(df.iloc[i,c[6]])), int(float(df.iloc[i,c[7]]))
                        if (s1+s2+s3+s4) > 0:
                            w1, w2 = (s1>s3)+(s2>s4), (s3>s1)+(s4>s2)
