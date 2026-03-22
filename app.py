import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026 Score Tracker", layout="wide")

# --- 1. DATA LOADING & CLEANING ---
@st.cache_data
def load_and_clean_schedule():
    file_path = "SMASH 2026 - Score Tracker.csv"
    if not os.path.exists(file_path):
        return None
    
    raw_df = pd.read_csv(file_path)
    matches = []

    # Mapping based on your 8-court grid layout
    court_configs = [
        {"name": "Court 1", "rows": (1, 10), "cols": (1, 6)},
        {"name": "Court 2", "rows": (1, 10), "cols": (13, 18)},
        {"name": "Court 3", "rows": (13, 22), "cols": (1, 6)},
        {"name": "Court 4", "rows": (13, 22), "cols": (13, 18)},
        {"name": "Court 5", "rows": (25, 34), "cols": (1, 6)},
        {"name": "Court 6", "rows": (25, 34), "cols": (13, 18)},
        {"name": "Court 7", "rows": (37, 46), "cols": (1, 6)},
        {"name": "Court 8", "rows": (37, 46), "cols": (13, 18)},
    ]

    for config in court_configs:
        r_start, r_end = config["rows"]
        c1, c2 = config["cols"]
        for i in range(r_start, r_end):
            try:
                t1 = str(raw_df.iloc[i, c1]).strip()
                t2 = str(raw_df.iloc[i, c2]).strip()
                time_slot = str(raw_df.iloc[i, 0 if config["cols"][0] == 1 else 12]).strip()
                if "|" in t1 and "|" in t2:
                    matches.append({
                        "ID": f"{config['name']} | {time_slot} | {t1} vs {t2}",
                        "Court": config["name"],
                        "Time": time_slot,
                        "Team 1": t1,
                        "Team 2": t2
                    })
            except:
                continue
    return pd.DataFrame(matches)

# --- 2. COLOR MAPPING (Based on your Bracket Photos) ---
BRACKETS = {
    "PURPLE": ["WENDY | WYNETTE", "DAVID | JOSZEF", "ALLAN | AALIYAH", "KIM | BEVERLY", "MATTHEW | LANCE", "ZBIGNIEF | DELFZIJL", "WYATT | MACKINZIE"],
    "PINK": ["KYLE | ABIGAIL", "BENEDICK | ROBENSON", "DANNY | ANDREA", "BRYCE | MATTHEW", "JETHRO | IVAN", "Szczeinfjord | DARRYL", "KAELYN | GENEVIEVE"],
    "ORANGE": ["JERICHO | JOHN", "ENZO | SETH", "MARSTON | MARCUS", "JULIO | STEVE", "SETH | ENZO", "JOHANN | ANTHONY", "ERVIN | KYLE", "SPENCER | LUCAS", "JANELLE | BEA"],
    "BLUE": ["RAINIER | MICHAEL", "SHAWN | NATHAN", "VICTOR | CHARLES", "CELINE | CARLSON", "APOL | TRISTEN", "TIMOTHY | JORDAN", "KATE | JEAN", "KELLY | COLLIN"],
    "YELLOW": ["JOANNA | KELWIN", "RIANA | RINAN", "HANS | JARED", "JOHNSEN | ELISHA", "WILBERT | KRISTIN", "JUSTIN | BRANSON", "HARVEY | GAB"],
    "GREEN": ["BRENT | JEEVAN", "JYRELL | SEAN", "KATHERINE | GINA", "HART | CHANTELLE", "CHRISTIAN | JOHN", "MATTHEW | KALVIN", "JOHN | CHARLENE", "LAURENCE | JAQUELINE"]
}

def get_bracket_color(team_name):
    for color, teams in BRACKETS.items():
        if team_name in teams:
            return color
    return "WHITE"

# --- 3. UI LOGIC ---
st.title("🏸 SMASH 2026 Tournament Tracker")

schedule_df = load_and_clean_schedule()

if schedule_df is None:
    st.error("Please upload 'SMASH 2026 - Score Tracker.csv' to your GitHub repo.")
else:
    # Initialize Score DB in memory
    if 'db' not in st.session_state:
        st.session_state.db = {}

    tab1, tab2 = st.tabs(["📊 Leaderboard", "📝 Input Scores"])

    with tab2:
        st.header("Admin: Record Match Result")
        # Filter court first to make it easier
        court_filter = st.selectbox("Filter by Court", ["All"] + sorted(schedule_df["Court"].unique().tolist()))
        filtered_df = schedule_df if court_filter == "All" else schedule_df[schedule_df["Court"] == court_filter]
        
        match_choice = st.selectbox("Select Match", filtered_df["ID"].tolist())
        match_data = schedule_df[schedule_df["ID"] == match_choice].iloc[0]
        
        st.info(f"🏆 Match: {match_data['Team 1']} vs {match_data['Team 2']}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**{match_data['Team 1']}**")
            t1_s1 = st.number_input("Set 1 Points", 0, 21, key="t1s1", help="Max 21")
            t1_s2 = st.number_input("Set 2 Points", 0, 21, key="t1s2")
        with c2:
            st.markdown(f"**{match_data['Team 2']}**")
            t2_s1 = st.number_input("Set 1 Points ", 0, 21, key="t2s1")
            t2_s2 = st.number_input("Set 2 Points ", 0, 21, key="t2s2")

        if st.button("Submit Final Result"):
            # Calculate Wins for each set
            t1_wins = (1 if t1_s1 > t2_s1 else 0) + (1 if t1_s2 > t2_s2 else 0)
            t2_wins = (1 if t2_s1 > t1_s1 else 0) + (1 if t2_s2 > t1_s2 else 0)
            
            st.session_state.db[match_choice] = {
                "t1": match_data['Team 1'], "t2": match_data['Team 2'],
                "t1_pts": t1_s1 + t1_s2, "t2_pts": t2_s1 + t2_s2,
                "t1_sets_won": t1_wins, "t1_sets_lost": t2_wins,
                "t2_sets_won": t2_wins, "t2_sets_lost": t1_wins
            }
            st.success("✅ Match Recorded!")

    with tab1:
        st.header("Standings by Bracket")
        
        # Build Stats for all 46 teams
        all_teams = sorted(list(set(schedule_df["Team 1"]).union(set(schedule_df["Team 2"]))))
        stats = {team: {"Bracket": get_bracket_color(team), "Sets Won": 0, "Sets Lost": 0, "Total Pts": 0} for team in all_teams}
        
        # Apply recorded results
        for match_id, res in st.session_state.db.items():
            # Team 1
            stats[res["t1"]]["Sets Won"] += res["t1_sets_won"]
            stats[res["t1"]]["Sets Lost"] += res["t1_sets_lost"]
            stats[res["t1"]]["Total Pts"] += res["t1_pts"]
            # Team 2
            stats[res["t2"]]["Sets Won"] += res["t2_sets_won"]
            stats[res["t2"]]["Sets Lost"] += res["t2_sets_lost"]
            stats[res["t2"]]["Total Pts"] += res["t2_pts"]
            
        standings_df = pd.DataFrame.from_dict(stats, orient='index').reset_index()
        standings_df.columns = ["Team", "Bracket", "Sets Won", "Sets Lost", "Total Points"]
        
        # Sorting
        standings_df = standings_df.sort_values(by=["Bracket", "Sets Won", "Total Points"], ascending=[True, False, False])

        # Color Formatting
        def apply_bracket_colors(row):
            b = row["Bracket"].upper()
            colors = {
                "PURPLE": "background-color: #E1BEE7; color: black",
                "PINK": "background-color: #F8BBD0; color: black",
                "ORANGE": "background-color: #FFE0B2; color: black",
                "BLUE": "background-color: #BBDEFB; color: black",
                "YELLOW": "background-color: #FFF9C4; color: black",
                "GREEN": "background-color: #C8E6C9; color: black",
                "WHITE": "background-color: white; color: black"
            }
            return [colors.get(b, "")] * len(row)

        st.table(standings_df.style.apply(apply_bracket_colors, axis=1))
