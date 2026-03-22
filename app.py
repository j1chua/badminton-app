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

    # Mapping based on your 8-court grid layout from the CSV
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
                # Determine time column (Day 1 info is in Col 0 or Col 12)
                time_col = 0 if config["cols"][0] == 1 else 12
                time_slot = str(raw_df.iloc[i, time_col]).strip()
                
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

# --- 2. COLOR MAPPING ---
BRACKETS = {
    "PURPLE": ["WENDY | WYNETTE", "DAVID | JOSZEF", "ALLAN | AALIYAH", "KIM | BEVERLY", "MATTHEW | LANCE", "ZBIGNIEF | DELFZIJL", "WYATT | MACKINZIE"],
    "PINK": ["KYLE | ABIGAIL", "BENEDICK | ROBENSON", "DANNY | ANDREA", "BRYCE | MATTHEW", "JETHRO | IVAN", "Szczeinfjord | DARRYL", "KAELYN | GENEVIEVE"],
    "ORANGE": ["JERICHO | JOHN", "ENZO | SETH", "MARSTON | MARCUS", "JULIO | STEVE", "SETH | ENZO", "JOHANN | ANTHONY", "ERVIN | KYLE", "SPENCER | LUCAS", "JANELLE | BEA"],
    "BLUE": ["RAINIER | MICHAEL", "SHAWN | NATHAN", "VICTOR | CHARLES", "CELINE | CARLSON", "APOL | TRISTEN", "TIMOTHY | JORDAN", "KATE | JEAN", "KELLY | COLLIN"],
    "YELLOW": ["JOANNA | KELWIN", "RIANA | RINAN", "HANS | JARED", "JOHNSEN | ELISHA", "WILBERT | KRISTIN", "JUSTIN | BRANSON", "HARVEY | GAB"],
    "GREEN": ["BRENT | JEEVAN", "JYRELL | SEAN", "KATHERINE | GINA", "HART | CHANTELLE", "CHRISTIAN | JOHN", "MATTHEW | KALVIN", "JOHN | CHARLENE", "LAURENCE | JAQUELINE"]
}

def get_bracket_color(team_name):
    clean_name = str(team_name).strip().upper()
    for color, teams in BRACKETS.items():
        if any(clean_name == t.strip().upper() for t in teams):
            return color
    return "WHITE"

# --- 3. UI LOGIC ---
st.title("🏸 SMASH 2026 Score Tracker")

schedule_df = load_and_clean_schedule()

if schedule_df is None:
    st.error("Error: 'SMASH 2026 - Score Tracker.csv' not found. Please upload it to your GitHub repo.")
else:
    # Initialize Score DB in memory
    if 'db' not in st.session_state:
        st.session_state.db = {}

    tab1, tab2 = st.tabs(["📊 Leaderboard", "📝 Admin Score Entry"])

    with tab2:
        st.header("Input Match Results")
        court_filter = st.selectbox("Select Court", ["All"] + sorted(schedule_df["Court"].unique().tolist()))
        filtered_df = schedule_df if court_filter == "All" else schedule_df[schedule_df["Court"] == court_filter]
        
        match_choice = st.selectbox("Select Matchup", filtered_df["ID"].tolist())
        match_data = schedule_df[schedule_df["ID"] == match_choice].iloc[0]
        
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"Team 1: {match_data['Team 1']}")
            t1_s1 = st.number_input("Set 1 Points (T1)", 0, 21, key="t1s1")
            t1_s2 = st.number_input("Set 2 Points (T1)", 0, 21, key="t1s2")
        with col2:
            st.subheader(f"Team 2: {match_data['Team 2']}")
            t2_s1 = st.number_input("Set 1 Points (T2)", 0, 21, key="t2s1")
            t2_s2 =
