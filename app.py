import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="GCCP SMASH S1 2026", layout="wide")

# Constants (RETAINED FROM BASE)
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
ADMIN_PW = "pogisiJordan"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "VIOLET": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
COLOR_MAP = {
    "BLACK": "#000000", "RED": "#d32f2f", "GREEN": "#2e7d32", 
    "VIOLET": "#7b1fa2", "WHITE": "#9e9e9e", "YELLOW": "#fbc02d"
}
IGNORE_TEAMS = ["TBD", "1ST", "2ND", "3RD", "4TH", "5TH", "TBA"]

# 2. Persistence & Helper Logic (RETAINED FROM BASE)
def save_finals(data):
    with open(SAVE_FN, "w") as f:
        json.dump(data, f)

def load_finals():
    if os.path.exists(SAVE_FN):
        try:
            with open(SAVE_FN, "r") as f:
                return json.load(f)
        except: return {}
    return {}

def nz(value):
    try:
        val = float(value)
        return val if pd.notnull(val) else 0
    except: return 0

@st.cache_data
def load_raw_data():
    if os.path.exists(FN):
        # We load without header because the CSV uses merged-cell style headers
        return pd.read_csv(FN, header=None).fillna("")
    return pd.DataFrame()

df = load_raw_data()

# 3. Standings Calculation
def get_detailed_standings(df):
    all_teams = []
    for col in [2, 7, 15, 20]:
        all_teams.extend(df[col].astype(str).tolist())
    
    unique_teams = sorted(list(set([
        t.strip() for t in all_teams 
        if t.strip() and "|" in t and not any(p in t for p in IGNORE_TEAMS)
    ])))

    stats_list = []
    for team in unique_teams:
        gp, sw, sl, pts = 0, 0, 0, 0
        # Court 1 (Cols 2-10) and Court 2 (Cols 15-23)
        courts = [(2, 3, 4, 5, 7, 8, 9, 10), (15, 16, 17, 18, 20, 21, 22, 23)]
        for c in courts:
            # Check Team 1 position and Team 2 position
            for t_col, s_start, o_col, os_start in [(c[0], c[1], c[4], c[5]), (c[4], c[5], c[0], c[1])]:
                m = df[df[t_col] == team]
                for _, row in m.iterrows():
                    s = [nz(row[s_start]), nz(row[s_start+1]), nz(row[s_start+2])]
                    o = [nz(os_start), nz(os_start+1), nz(os_start+2)]
                    if sum(s) + sum(o) > 0:
                        gp += 1
                        for i in range(3):
                            if s[i] > o[i]: sw += 1
                            elif o[i] > s[i]: sl += 1
                        pts += sum(s)
        
        stats_list.append({
            "TEAM": team, 
            "GAMES PLAYED": gp, 
            "SETS WON": sw, 
            "SETS LOST": sl, 
            "POINTS": int(pts)
        })
    
    res = pd.DataFrame(stats_list).sort_values(by=['SETS WON', 'POINTS'], ascending=False).reset_index(drop=True)
    res.index += 1
    res.index.name = "RANK"
    return res.reset_index()

# 4. Main UI Tabs
# Visible Tabs: Day 1, Day 2, Standings
tab_day1, tab_day2, tab_standings = st.tabs(["📅 Day 1", "📅 Day 2", "📊 Standings"])

with tab_day1:
    st.header("Day 1 - Match Logs")
    # Display the first chunk of the tracker (Day 1 section)
    st.dataframe(df.iloc[1:24], use_container_width=True, hide_index=True)

with tab_day2:
    st.header("Day 2 - Match Logs")
    # Display the second chunk of the tracker (Day 2 section)
    st.dataframe(df.iloc[26:], use_container_width=True, hide_index=True)

with tab_standings:
    st.header("Tournament Standings & Playoffs")
    
    # Leaderboard with full labels
    st.subheader("Leaderboard")
    st.table(get_detailed_standings(df))
    
    st.divider()
    
    # Integrated Brackets (Scanning CSV for SEMIS/FINALS)
    st.subheader("🏆 Championship Brackets (Semis & Finals)")
    playoff_rows = []
    for idx, row in df.iterrows():
        for col_label, t1_idx, t2_idx, s1_range, s2_range in [(1, 2, 7, [3,4,5], [8,9,10]), (14, 15, 20, [16,17,18], [21,22,23])]:
            label = str(row[col_label]).upper()
            if any(x in label for x in ["SEMIS", "FINALS"]):
                t1, t2 = str(row[t1_idx]), str(row[t2_idx])
                if "|" in t1:
                    sc1 = " | ".join([str(row[i]) for i in s1_range if str(row[i]).strip() and str(row[i]) not in ["0", "0.0", ""]])
                    sc2 = " | ".join([str(row[i]) for i in s2_range if str(row[i]).strip() and str(row[i]) not in ["0", "0.0", ""]])
                    playoff_rows.append({"BRACKET": label, "TEAM 1": t1, "SCORE 1": sc1, "TEAM 2": t2, "SCORE 2": sc2})
    
    if playoff_rows:
        st.dataframe(pd.DataFrame(playoff_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Playoff matches will appear here as they are recorded.")

# ==============================================================================
# HIDDEN PIECES OF CODE (Commented out for future use)
# This includes the original Finals rendering and the Admin data management.
# ==============================================================================
"""
# To restore these, add "tab_finals" and "tab_admin" to the st.tabs list above.

with tab_finals:
    st.header("🏆 Finals Summary")
    f_data = load_finals()
    # [Original base code for rendering winner podiums and color-coded brackets goes here]

with tab_admin:
    st.header("⚙️ Admin Management")
    auth = st.text_input("Admin Password", type="password")
    if auth == ADMIN_PW:
        st.success("Authenticated")
        # [Original base code for the interactive score input form, 
        #  the S3 Toggle logic, and save_finals() trigger goes here]
"""
