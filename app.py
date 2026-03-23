import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

# 2. Data Loading Logic (Simplified for brevity)
@st.cache_data
def load_data():
    if not os.path.exists(FN): return None, {}, {}
    df = pd.read_csv(FN, header=None).fillna("")
    matches, team_colors, db = [], {}, {}
    day = "Day 1"
    blocks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
    for idx, row in df.iterrows():
        txt = " ".join([str(x) for x in row]).upper()
        if "DAY 2" in txt: day = "Day 2"
        elif "DAY 1" in txt: day = "Day 1"
        for c in blocks:
            try:
                t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                if "|" not in t1: continue
                color = str(row[c[1]]).strip().upper()
                matches.append({"Day": day, "T1": t1, "T2": t2, "L": color, "Emoji": EMOJIS.get(color, "🏸")})
                team_colors[t1] = team_colors[t2] = color
            except: continue
    return pd.DataFrame(matches), team_colors

# 3. Custom CSS for Score Inputs
st.markdown("""
<style>
    .finals-header { background-color: #000; color: #fff; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; }
    .match-card { border: 1px solid #ddd; padding: 15px; border-radius: 10px; background-color: #f9f9f9; margin-bottom: 20px; }
    .team-row { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
    .score-box { width: 50px !important; }
    .sets-won { font-weight: bold; color: #d32f2f; background: #ffebee; padding: 5px 10px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

sch, clrs = load_data()

if sch is None:
    st.warning("Data not found.")
else:
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals"])

    with tab4:
        st.markdown('<div class="finals-header">⚫ BLACK BRACKET FINALS</div>', unsafe_allow_html=True)
        
        # Get list of teams in Black Bracket for dropdowns
        black_teams = sorted([t for t, c in clrs.items() if c == "BLACK"])
        if not black_teams: black_teams = ["Select Team..."]

        def render_match_input(label, key_suffix):
            st.subheader(label)
            with st.container():
                col_t, col_s1, col_s2, col_s3, col_sw = st.columns([3, 1, 1, 1, 1.5])
                
                with col_t:
                    t1 = st.selectbox(f"Team 1", black_teams, key=f"t1_{key_suffix}")
                    t2 = st.selectbox(f"Team 2", black_teams, key=f"t2_{key_suffix}")
                
                with col_s1:
                    s1a = st.number_input("S1", 0, 30, key=f"s1a_{key_suffix}", label_visibility="collapsed")
                    s1b = st.number_input("S1", 0, 30, key=f"s1b_{key_suffix}", label_visibility="collapsed")
                with col_s2:
                    s2a = st.number_input("S2", 0, 30, key=f"s2a_{key_suffix}", label_visibility="collapsed")
                    s2b = st.number_input("S2", 0, 30, key=f"s2b_{key_suffix}", label_visibility="collapsed")
                with col_s3:
                    s3a = st.number_input("S3", 0, 30, key=f"s3a_{key_suffix}", label_visibility="collapsed")
                    s3b = st.number_input("S3", 0, 30, key=f"s3b_{key_suffix}", label_visibility="collapsed")
                
                with col_sw:
                    # Logic: Calculate Sets Won based on higher scores
                    sw1 = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0) + (1 if s3a > s3b else 0)
                    sw2 = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0) + (1 if s3b > s3a else 0)
                    st.markdown(f"<br><div class='sets-won'>{sw1} Sets</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sets-won'>{sw2} Sets</div>", unsafe_allow_html=True)
            st.divider()

        render_match_input("Semi-Final 1 (#1 vs #4)", "sf1")
        render_match_input("Semi-Final 2 (#2 vs #3)", "sf2")
        render_match_input("🏆 Championship Final", "final")

    # Day 1/2 and Standings remain as they were...
    with tab1: st.write("Standings view...")
    with tab2: st.write("Day 1 view...")
    with tab3: st.write("Day 2 view...")
