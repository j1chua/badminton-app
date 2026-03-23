import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}

# ... (Data Loading Logic remains the same, omitted for space)
@st.cache_data
def load_data():
    if not os.path.exists(FN): return None, {}, {}
    try:
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
                    if "|" not in t1 or "|" not in t2: continue
                    color = str(row[c[1]]).strip().upper()
                    time, emoji = str(row[c[0]]).strip(), EMOJIS.get(color, "🏸")
                    court = "Court ?"
                    for r_idx in range(idx, -1, -1):
                        val = str(df.iloc[r_idx, c[2]]).upper()
                        if "COURT" in val:
                            court = val.strip()
                            break
                    p1_d, p2_d = t1.replace("|", " AND "), t2.replace("|", " AND ")
                    m_id = f"{day[:1]}{idx}{c[0]}"
                    matches.append({"ID": m_id, "Day": day, "T": time, "T1": t1, "T2": t2, "P1": p1_d, "P2": p2_d, "L": color, "Emoji": emoji, "Court": court})
                    team_colors[t1] = team_colors[t2] = color
                    sc = [int(float(row[col])) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7]]]
                    w1, w2 = (sc[0]>sc[2])+(sc[1]>sc[3]), (sc[2]>sc[0])+(sc[3]>sc[1])
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "p1":sc[0]+sc[1], "p2":sc[2]+sc[3], "w1":w1, "w2":w2}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}
# ... (Styling remains the same, omitted for space)
st.markdown("""
<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-family: sans-serif; }
    .m-table th { background-color: #f0f2f6; text-align: center !important; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    .m-table tr:nth-child(even) { background-color: #f9f9f9; }
    .forfeit { color: #d32f2f; font-weight: bold; }
    .win-red { color: red; font-weight: bold; text-decoration: underline; }
    .win-green { color: green; font-weight: bold; text-decoration: underline; }
    .win-purple { color: purple; font-weight: bold; text-decoration: underline; }
    .win-yellow { color: #d4af37; font-weight: bold; text-decoration: underline; }
    .win-black { color: black; font-weight: bold; text-decoration: underline; }
    .win-white { color: gray; font-weight: bold; text-decoration: underline; }
    
    /* Finals Table styling */
    .finals-table { border-collapse: collapse; width: 100%; margin-top: 20px; font-family: sans-serif; }
    .finals-table td { border: 1px solid #eee; padding: 5px; vertical-align: middle; }
    .finals-header { background-color: #000; color: #fff; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; font-weight: bold;}
    .sets-won-result { font-weight: bold; color: #d32f2f; text-align: center; font-size: 1.1em; background-color: #ffebee; border-radius: 4px;}
</style>
""", unsafe_allow_html=True)

sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Data not found. Please check the CSV file.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals"])
    # (Standings, Day 1, Day 2 tabs remain the same...)

    with tab4:
        st.markdown('<div class="finals-header">🏆 KNOCKOUT STAGE — ⚫ BLACK BRACKET</div>', unsafe_allow_html=True)
        black_teams = sorted([t.replace("|", " AND ") for t, c in clrs.items() if c == "BLACK"])
        if not black_teams: black_teams = ["Select Team..."]

        def render_compact_match(match_label, key_suffix):
            with st.container():
                st.write(f"**{match_label}**")
                # Using columns for team selection, then scores
                c1, c2, c3, c4, c5, c6 = st.columns([3, 1, 1, 1, 1, 1])
                
                with c1:
                    t1 = st.selectbox(f"T1", black_teams, key=f"t1_{key_suffix}", label_visibility="collapsed")
                    t2 = st.selectbox(f"T2", black_teams, key=f"t2_{key_suffix}", label_visibility="collapsed")
                
                with c2:
                    s1a = st.number_input("S1", 0, 30, key=f"s1a_{key_suffix}", label_visibility="collapsed")
                    s1b = st.number_input("S1", 0, 30, key=f"s1b_{key_suffix}", label_visibility="collapsed")
                with c3:
                    s2a = st.number_input("S2", 0, 30, key=f"s2a_{key_suffix}", label_visibility="collapsed")
                    s2b = st.number_input("S2b", 0, 30, key=f"s2b_{key_suffix}", label_visibility="collapsed")
                with c4:
                    s3a = st.number_input("S3a", 0, 30, key=f"s3a_{key_suffix}", label_visibility="collapsed")
                    s3b = st.number_input("S3b", 0, 30, key=f"s3b_{key_suffix}", label_visibility="collapsed")
                
                with c5:
                    sw1 = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0) + (1 if s3a > s3b else 0)
                    sw2 = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0) + (1 if s3b > s3a else 0)
                    st.markdown(f"<div class='sets-won-result'>{sw1} Set</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sets-won-result'>{sw2} Set</div>", unsafe_allow_html=True)
                
                with c6:
                    st.write("") # Placeholder for potential 'TBD' or winner
            st.divider()

        render_compact_match("SEMI-FINAL 1 (#1 vs #4)", "sf1")
        render_compact_match("SEMI-FINAL 2 (#2 vs #3)", "sf2")
        render_compact_match("🏆 CHAMPIONSHIP FINAL", "final")
