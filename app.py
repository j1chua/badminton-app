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

    # Configs for reading the 8 courts
    # Courts 1,3,5,7 (Left Side) - Courts 2,4,6,8 (Right Side)
    configs = [
        {"name": "Court 1", "rows": (1, 10), "cols": (0, 1, 2, 7)},
        {"name": "Court 3", "rows": (13, 22), "cols": (0, 1, 2, 7)},
        {"name": "Court 5", "rows": (25, 34), "cols": (0, 1, 2, 7)},
        {"name": "Court 7", "rows": (37, 46), "cols": (0, 1, 2, 7)},
        {"name": "Court 2", "rows": (1, 10), "cols": (13, 14, 15, 20)},
        {"name": "Court 4", "rows": (13, 22), "cols": (13, 14, 15, 20)},
        {"name": "Court 6", "rows": (25, 34), "cols": (13, 14, 15, 20)},
        {"name": "Court 8", "rows": (37, 46), "cols": (13, 14, 15, 20)},
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
                    matches.append({"ID": match_id, "T1": t1, "T2": t2, "Color": color})
                    team_color_map[t1] = color
                    team_color_map[t2] = color
            except: continue
            
    return pd.DataFrame(matches), team_color_map

st.title("🏸 SMASH 2026 Score Tracker")
sch_df, color_map = load_tournament_data()

if sch_df is None:
    st.error(f"File '{FILE_NAME}' not found! Please check the filename on GitHub.")
else:
    if 'db' not in st.session_state: st.session_state.db = {}
    tab1, tab2 = st.tabs(["📊 Leaderboard", "📝 Admin Score Entry"])

    with tab2:
        st.header("Record Match Scores")
        sel = st.selectbox("Select Matchup", sch_df["ID"].tolist())
        d = sch_df[sch_df["ID"] == sel].iloc[0]
        
        st.info(f"Bracket: **{d['Color']}**")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(d['T1'])
            s1t1 = st.number_input("Set 1 Pts", 0, 21, key=f"{sel}_s1t1")
            s2t1 = st.number_input("Set 2 Pts", 0, 21, key=f"{sel}_s2t1")
        with c2:
            st.subheader(d['T2'])
            s1t2 = st.number_input("Set 1 Pts ", 0, 21, key=f"{sel}_s1t2")
            s2t2 = st.number_input("Set 2 Pts ", 0, 21, key=f"{sel}_s2t2")

        if st.button("Save Result", use_container_width=True):
            w1 = (1 if s1t1 > s1t2 else 0) + (1 if s2t1 > s2t2 else 0)
            w2 = (1 if s1t2 > s1t1 else 0) + (1 if s2t2 > s2t1 else 0)
            st.session_state.db[sel] = {
                "t1": d['T1'], "t2": d['T2'], "p1": s1t1+s2t1, "p2": s1t2+s2t2,
                "w1": w1, "l1": w2, "w2": w2, "l2": w1
            }
            st.success("Match Recorded!")

    with tab1:
        st.header("Tournament Standings")
        teams = sorted(list(color_map.keys()))
        res = {t: {"Bracket": color_map.get(t, "WHITE"), "Won": 0, "Lost": 0, "Total Pts": 0} for t in teams}
        for v in st.session_state.db.values():
            for i in [1, 2]:
                res[v[f't{i}']]["Won"] += v[f'w{i}']
                res[v[f't{i}']]["Lost"] += v[f'l{i}']
                res[v[f't{i}']]["Total Pts"] += v[f'p{i}']
        
        df_standings = pd.DataFrame.from_dict(res, orient='index').reset_index()
        df_standings.columns = ["Team", "Bracket", "Sets Won", "Sets Lost", "Total Pts"]
        df_standings = df_standings.sort_values(["Bracket", "Sets Won", "Total Pts"], ascending=[True, False, False])

        def color_style(row):
            c = str(row["Bracket"]).lower()
            bg, text = "#ffffff", "#000000"
            if c == "red": bg = "#ffcccc"
            elif c == "green": bg = "#ccffcc"
            elif c == "purple": bg = "#e6ccff"
            elif c == "yellow": bg = "#ffffcc"
            elif c == "black": bg = "#333333"; text = "#ffffff"
            elif c == "white": bg = "#f0f0f0"
            return [f"background-color: {bg}; color: {text}"] * len(row)

        st.table(df_standings.style.apply(color_style, axis=1))
