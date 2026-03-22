import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026 Score Tracker", layout="wide")

# Ensure this matches the EXACT name of the file you uploaded to GitHub
FILE_NAME = "SMASH 2026 - Score Tracker.csv"

@st.cache_data
def load_tournament_data():
    if not os.path.exists(FILE_NAME):
        return None, {}
    
    df = pd.read_csv(FILE_NAME)
    matches = []
    team_color_map = {}

    # Define the coordinates for each of the 8 courts in your CSV grid
    configs = [
        {"name": "Court 1", "rows": (1, 10), "cols": (0, 1, 2, 7)},
        {"name": "Court 3", "rows": (13, 22), "cols": (12, 1, 2, 7)},
        {"name": "Court 5", "rows": (25, 34), "cols": (24, 1, 2, 7)},
        {"name": "Court 7", "rows": (37, 46), "cols": (36, 1, 2, 7)},
        {"name": "Court 2", "rows": (1, 10), "cols": (13, 14, 15, 20)},
        {"name": "Court 4", "rows": (13, 22), "cols": (12, 14, 15, 20)},
        {"name": "Court 6", "rows": (25, 34), "cols": (24, 14, 15, 20)},
        {"name": "Court 8", "rows": (37, 46), "cols": (36, 14, 15, 20)},
    ]

    for c in configs:
        r_start, r_end = c["rows"]
        idx_time, idx_color, idx_t1, idx_t2 = c["cols"]
        for i in range(r_start, r_end):
            try:
                t1 = str(df.iloc[i, idx_t1]).strip()
                t2 = str(df.iloc[i, idx_t2]).strip()
                color = str(df.iloc[i, idx_color]).strip().upper()
                time_slot = str(df.iloc[i, idx_time]).strip()

                if "|" in t1 and "|" in t2:
                    match_id = f"{c['name']} | {time_slot} | {t1} vs {t2}"
                    matches.append({
                        "ID": match_id, "Court": c["name"], "Time": time_slot,
