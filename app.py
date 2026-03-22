import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026 Score Tracker", layout="wide")

@st.cache_data
def load_and_clean_schedule():
    file_path = "SMASH 2026 - Score Tracker.csv"
    if not os.path.exists(file_path):
        return None
    raw_df = pd.read_csv(file_path)
    matches = []
    configs = [
        {"name": "Court 1", "rows": (1, 10), "cols": (1, 6)},
        {"name": "Court 2", "rows": (1, 10), "cols": (13, 18)},
        {"name": "Court 3", "rows": (13, 22), "cols": (1, 6)},
        {"name": "Court 4", "rows": (13, 22), "cols": (13, 18)},
        {"name": "Court 5", "rows": (25, 34), "cols": (1, 6)},
        {"name": "Court 6", "rows": (25, 34), "cols": (13, 18)},
        {"name": "Court 7", "rows": (37, 46), "cols": (1, 6)},
        {"name": "Court 8", "rows": (37, 46), "cols": (13, 18)},
    ]
    for config in configs:
        r_start, r_end = config["rows"]
        c1, c2 = config["cols"]
        for i in range(r_start, r_end):
            try:
                t1, t2 = str(raw_df.iloc[i, c1]).strip(), str(raw_df.iloc[i, c2]).strip()
                time_col = 0 if config["cols"][0] == 1 else 12
                time_slot = str(raw_df.iloc[i, time_col]).strip()
                if "|" in t1 and "|" in t2:
                    matches.append({"ID": f"{config['name']} | {time_slot} | {t1} vs {t2}", "Court": config["name"], "Team 1": t1, "Team 2": t2})
            except: continue
    return pd.DataFrame(matches)

BRACKETS = {
    "PURPLE": ["WENDY | WYNETTE", "DAVID | JOSZEF", "ALLAN | AALIYAH", "KIM | BEVERLY", "MATTHEW | LANCE", "ZBIGNIEF | DELFZIJL", "WYATT | MACKINZIE"],
    "PINK": ["KYLE | ABIGAIL", "BENEDICK | ROBENSON", "DANNY | ANDREA", "BRYCE | MATTHEW", "JETHRO | IVAN", "Szczeinfjord | DARRYL", "KAELYN | GENEVIEVE"],
    "ORANGE": ["JERICHO | JOHN", "ENZO | SETH", "MAR
