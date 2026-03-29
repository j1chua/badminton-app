import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="GCCP SMASH S1 2026", layout="wide")

# Constants
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
ADMIN_PW = "pogisiJordan"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "VIOLET": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
COLOR_MAP = {
    "BLACK": "#000000", "RED": "#d32f2f", "GREEN": "#2e7d32", 
    "VIOLET": "#7b1fa2", "WHITE": "#9e9e9e", "YELLOW": "#fbc02d"
}
IGNORE_TEAMS = ["TBD", "1ST", "2ND", "3RD", "4TH", "5TH", "TBA"]

# 2. Persistence Logic
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

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    return f"<b>{i}th</b>"

def nz(value):
    try:
        val = float(value)
        return val if pd.notnull(val) else 0
    except: return 0

@st.cache_data
def load_raw_data():
    if os.path.exists(FN):
        return pd.read_csv(FN, header=None).fillna("")
    return pd.DataFrame()

df = load_raw_data()

# 3. Calculation Logic for Standings
def get_detailed_standings(df):
    all_teams = []
    # Extract unique teams from Team 1 and Team 2 columns across both courts
    for col in [2, 7, 15, 20]:
        all_teams.extend(df[col].astype(str).tolist())
    
    unique_teams = sorted(list(set([
        t.strip() for t in all_teams 
        if t.strip() and "|" in t and not any(p in t for p in IGNORE_TEAMS)
    ])))

    stats_list = []
    for team in unique_teams:
        gp, sw, sl, pts = 0, 0, 0, 0
        # Column mapping for Court 1 and Court 2
        courts = [(2, 3, 4, 5, 7, 8, 9, 10), (15, 16, 17, 18, 20, 21, 22, 23)]
        
        for c in courts:
            # Check matches where the team is Team 1 or Team 2
            for t_col, s_start, o_t_col, o_s_start in [(c[0], c[1], c[4], c[5]), (c[4], c[5], c[0], c[1])]:
                m = df[df[t_col] == team]
                for _, row in m.iterrows():
                    s_scores = [nz(row[s_start]), nz(row[s_start+1]), nz(row[s_start+2])]
                    o_scores = [nz(o_s_start), nz(o_s_start+1), nz(o_s_start+2)]
                    
                    if sum(s_scores) + sum(o_scores) > 0:
                        gp += 1
                        for i in range(3):
                            if s_scores[i] > o_scores[i]: sw += 1
                            elif o_scores[i] > s_scores[i]: sl += 1
                        pts += sum(s_scores)
        
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
# Only Day 1, Day 2, and Standings are active
tab_day1, tab_day2, tab_standings = st.tabs(["📅 Day 1", "📅 Day 2", "📊 Standings"])

with tab_day1:
    st.header("Day 1 - Match Logs")
    if not df.empty:
        st.dataframe(df.iloc[1:24], use_container_width=True, hide_index=True)

with tab_day2:
    st.header("Day 2 - Match Logs")
    if not df.empty:
        st.dataframe(df.iloc[26:], use_container_width=True, hide_index=True)

with tab_standings:
    st.header("Tournament Standings & Playoffs")
    
    # Leaderboard Section
    st.subheader("Leaderboard")
    leaderboard = get_detailed_standings(df)
    st.table(leaderboard)
    
    st.divider()
    
    # Playoff Brackets Section
    st.subheader("🏆 Championship Brackets (Semis & Finals)")
    playoff_rows = []
    if not df.empty:
        for idx, row in df.iterrows():
            # Court 1 (1, 2, 7) and Court 2 (14, 15, 20)
            for c_lbl, t1_idx, t2_idx, s1_rng, s2_rng in [(1, 2, 7, [3,4,5], [8,9,10]), (14, 15, 20, [16,17,18], [21,22,23])]:
                label = str(row[c_lbl]).upper()
                if any(x in label for x in ["SEMIS", "FINALS"]):
                    t1, t2 = str(row[t1_idx]), str(row[t2_idx])
                    if "|" in t1:
                        # Format scores: only show sets that have scores
                        sc1 = " | ".join([str(row[i]) for i in s1_rng if str(row[i]).strip() and str(row[i]) not in ["0", "0.0", ""]])
                        sc2 = " | ".join([str(row[i]) for i in s2_rng if str(row[i]).strip() and str(row[i]) not in ["0", "0.0", ""]])
                        playoff_rows.append({
                            "BRACKET": label, 
                            "TEAM 1": t1.replace("1ST ","").replace("2ND ","").replace("3RD ","").replace("4TH ",""), 
                            "SCORE TEAM 1": sc1 if sc1 else "0", 
                            "TEAM 2": t2.replace("1ST ","").replace("2ND ","").replace("3RD ","").replace("4TH ",""), 
                            "SCORE TEAM 2": sc2 if sc2 else "0"
                        })
    
    if playoff_rows:
        st.dataframe(pd.DataFrame(playoff_rows), use_container_width=True, hide_index=True)
    else:
        st.info("Playoff matches are being processed.")

# ==============================================================================
# HIDDEN CODE SECTIONS (RETAINED FOR FUTURE USE)
# ==============================================================================
"""
# To reactivate these, add "tab_finals" and "tab_admin" to the st.tabs list above.

with tab_finals:
    st.header("🏆 Finals View")
    f_data = load_finals()
    # Logic for rendering podiums and winner brackets
    for v in ["VIOLET", "RED", "YELLOW", "BLACK", "GREEN", "WHITE"]:
        d = f_data.get(v, {})
        st.markdown(f"### {EMOJIS.get(v, '')} {v} BRACKET")
        # [Render code for podiums and sets]

with tab_admin:
    st.header("⚙️ Admin Management")
    auth = st.text_input("Admin Password", type="password")
    if auth == ADMIN_PW:
        st.success("Authenticated")
        # Score update forms and save_finals() logic
        # [Form code for Semi 1, Semi 2, and Finals]
"""
