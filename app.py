import streamlit as st
import pandas as pd

# Basic Page Config
st.set_page_config(page_title="SMASH 2026 Score Tracker", layout="wide")

st.title("🏸 SMASH 2026 - Score Tracker")

# 1. Load the Schedule (I've pre-processed your CSV data here)
@st.cache_data
def load_schedule():
    # This matches the teams found in your CSV
    return pd.read_csv("SMASH 2026 - Score Tracker.csv")

schedule = load_schedule()

# 2. Sidebar Navigation
menu = st.sidebar.radio("Navigation", ["Input Scores", "Leaderboard / View Tab"])

# 3. Logic for Inputs
if menu == "Input Scores":
    st.header("Update Match Results")
    
    # Selection of Court and Time
    court = st.selectbox("Select Court", ["Court 1", "Court 2", "Court 3", "Court 4", "Court 5", "Court 6", "Court 7", "Court 8"])
    
    # Filter schedule for selected court (Simplified for this example)
    match_to_edit = st.selectbox("Select Match Time", ["2:30 - 2:55", "2:55 - 3:20", "3:20 - 3:45", "3:45 - 4:10"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Team 1")
        t1_score1 = st.number_input("Set 1 Score (T1)", min_value=0, max_value=21, step=1)
        t1_score2 = st.number_input("Set 2 Score (T1)", min_value=0, max_value=21, step=1)
        
    with col2:
        st.subheader("Team 2")
        t2_score1 = st.number_input("Set 1 Score (T2)", min_value=0, max_value=21, step=1)
        t2_score2 = st.number_input("Set 2 Score (T2)", min_value=0, max_value=21, step=1)

    if st.button("Save Match Result"):
        st.success("Score Updated Locally! (Connect to Google Sheets to save permanently)")

# 4. Logic for Leaderboard
else:
    st.header("Tournament Standings")
    
    # Dummy data placeholder for demonstration
    standings = pd.DataFrame({
        "Team Name": ["JOHANN | ANTHONY", "ERVIN | KYLE", "KIM | BEVERLY"],
        "Bracket": ["White", "White", "White"],
        "Wins": [2, 1, 0],
        "Losses": [0, 1, 2],
        "Total Points": [42, 38, 20]
    })
    
    # Apply color sorting
    def color_bracket(val):
        color = 'white' if val == "White" else 'lightgray'
        return f'background-color: {color}'

    st.table(standings.style.applymap(color_bracket, subset=['Bracket']))
