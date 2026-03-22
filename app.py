import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026 Score Tracker", layout="wide")

FILE_NAME = "SMASH 2026 - Score Tracker.csv"

@st.cache_data
def load_tournament_data():
    if not os.path.exists(FILE_NAME):
        return None, {}
    
    df = pd.read_csv(FILE_NAME)
    matches = []
    team_color_map = {}

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
                    matches.append({"ID": match_id, "Court": c["name"], "Time": time_slot, "T1": t1, "T2": t2, "Color": color})
                    team_color_map[t1] = color
                    team_color_map[t2] = color
            except: continue
            
    return pd.DataFrame(matches), team_color_map

st.title("🏸 SMASH 2026 Tournament Central")
sch_df, color_map = load_tournament_data()

if sch_df is None:
    st.error(f"File '{FILE_NAME}' not found on GitHub!")
else:
    if 'db' not in st.session_state: st.session_state.db = {}
    
    tab1, tab2, tab3 = st.tabs(["📊 Standings", "📅 Match Schedule", "📝 Score Entry"])

    with tab3:
        st.header("Admin: Record Result")
        sel = st.selectbox("Select Matchup", sch_df["ID"].tolist())
        d = sch_df[sch_df["ID"] == sel].iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(d['T1'])
            s1t1 = st.number_input("Set 1 Pts", 0, 21, key=f"{sel}_s1t1")
            s2t1 = st.number_input("Set 2 Pts", 0, 21, key=f"{sel}_s2t1")
        with c2:
            st.subheader(d['T2'])
            s1t2 = st.number_input("Set 1 Pts ", 0, 21, key=f"{sel}_s1t2")
            s2t2 = st.number_input("Set 2 Pts ", 0, 21, key=f"{sel}_s2t2")

        if st.button("Save Score"):
            w1 = (1 if s1t1 > s1t2 else 0) + (1 if s2t1 > s2t2 else 0)
            w2 = (1 if s1t2 > s1t1 else 0) + (1 if s2t2 > s2t1 else 0)
            st.session_state.db[sel] = {
                "t1_score": f"{s1t1}-{s1t2}, {s2t1}-{s2t2}",
                "t1": d['T1'], "t2": d['T2'], "p1": s1t1+s2t1, "p2": s1t2+s2t2,
                "w1": w1, "l1": w2, "w2": w2, "l2": w1
            }
            st.success("Standings Updated!")

    with tab1:
        st.header("Leaderboard by Bracket")
        teams = sorted(list(color_map.keys()))
        res = {t: {"Bracket": color_map.get(t, "WHITE"), "Won": 0, "Lost": 0, "Pts": 0} for t in teams}
        for v in st.session_state.db.values():
            for i in [1, 2]:
                res[v[f't{i}']]["Won"] += v[f'w{i}']
                res[v[f't{i}']]["Lost"] += v[f'l{i}']
                res[v[f't{i}']]["Pts"] += v[f'p{i}']
        
        df_full = pd.DataFrame.from_dict(res, orient='index').reset_index()
        df_full.columns = ["Team", "Bracket", "Sets Won", "Sets Lost", "Total Pts"]
        
        # Display separate tables for each color
        for color in sorted(df_full["Bracket"].unique()):
            st.subheader(f"🏆 {color} Bracket")
            sub_df = df_full[df_full["Bracket"] == color].sort_values(["Sets Won", "Total Pts"], ascending=False)
            st.table(sub_df)

    with tab2:
        st.header("Court Schedule & Live Results")
        # Creating a grid view similar to the CSV
        courts = sorted(sch_df["Court"].unique())
        for court in courts:
            with st.expander(f"📍 {court}", expanded=True):
                c_matches = sch_df[sch_df["Court"] == court]
                display_data = []
                for _, row in c_matches.iterrows():
                    score = st.session_state.db.get(row["ID"], {}).get("t1_score", "Pending")
                    display_data.append({
                        "Time": row["Time"],
                        "Bracket": row["Color"],
                        "Matchup": f"{row['T1']} vs {row['T2']}",
                        "Result (S1, S2)": score
                    })
                st.dataframe(pd.DataFrame(display_data), use_container_width=True, hide_index=True)
