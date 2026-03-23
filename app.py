import streamlit as st
import pandas as pd
import os
import json

# 1. Page Configuration
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
ADMIN_PW = "pogisiJordan"

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

# 3. Tournament Data Loading (Day 1/2 Logic)
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
                    if "|" not in t1: continue
                    color = str(row[c[1]]).strip().upper()
                    m_id = f"{day[:1]}{idx}{c[0]}"
                    p1_d, p2_d = t1.replace("|", " AND "), t2.replace("|", " AND ")
                    matches.append({"ID": m_id, "Day": day, "P1": p1_d, "P2": p2_d, "L": color})
                    team_colors[t1] = team_colors[t2] = color
                    sc = [int(float(row[col])) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7]]]
                    w1, w2 = (sc[0]>sc[2])+(sc[1]>sc[3]), (sc[2]>sc[0])+(sc[3]>sc[1])
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "w1":w1, "w2":w2, "p1":sc[0]+sc[1], "p2":sc[2]+sc[3]}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 4. Styling
st.markdown("""
<style>
    .bracket-header { background-color: #000; color: #fff; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; font-weight: bold; }
    .winner-text { color: #2e7d32; font-weight: bold; text-decoration: underline; }
    .score-badge { background: #f0f2f6; padding: 4px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #ddd; margin-right: 4px; }
    .tie-warning { color: #d32f2f; font-weight: bold; font-size: 0.75rem; margin-top: -10px; display: block; }
    /* Fix alignment for number inputs and selectboxes */
    div[data-testid="stHorizontalBlock"] { align-items: center; }
</style>
""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Please ensure the CSV file is uploaded.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    current_finals = load_finals()
    tab1, tab2, tab3, tab_view, tab_admin = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    black_teams = sorted([t.replace("|", " AND ") for t, c in clrs.items() if c == "BLACK"])

    # --- ADMIN TAB (Aligned & Fixed) ---
    with tab_admin:
        pw = st.text_input("Admin Password", type="password")
        if pw == ADMIN_PW:
            st.markdown('<div class="bracket-header">⚙️ ADMIN CONTROL - BLACK BRACKET</div>', unsafe_allow_html=True)
            
            def admin_match(label, k, p1_def, p2_def):
                st.write(f"**{label}**")
                d = current_finals.get(k, {"t1":p1_def, "t2":p2_def, "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3": False})
                
                # Optimized column width ratios for a single row
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1.5, 0.8])
                
                with c1:
                    t1 = st.selectbox(f"T1", [p1_def] + black_teams, index=0 if d['t1'] not in black_teams else black_teams.index(d['t1'])+1, key=f"t1_{k}", label_visibility="collapsed")
                    t2 = st.selectbox(f"T2", [p2_def] + black_teams, index=0 if d['t2'] not in black_teams else black_teams.index(d['t2'])+1, key=f"t2_{k}", label_visibility="collapsed")
                
                with c2:
                    s1a = st.number_input("S1a", 0, 31, value=d['s1a'], key=f"s1a_{k}", label_visibility="collapsed")
                    s1b = st.number_input("S1b", 0, 31, value=d['s1b'], key=f"s1b_{k}", label_visibility="collapsed")
                
                with c3:
                    s2a = st.number_input("S2a", 0, 31, value=d['s2a'], key=f"s2a_{k}", label_visibility="collapsed")
                    s2b = st.number_input("S2b", 0, 31, value=d['s2b'], key=f"s2b_{k}", label_visibility="collapsed")
                
                # Winner logic for Set 3 requirement
                sw1_base = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0)
                sw2_base = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0)
                is_tie = (sw1_base == 1 and sw2_base == 1)

                with c4:
                    if is_tie: st.markdown('<span class="tie-warning">TIE (1-1) - ADD SET 3</span>', unsafe_allow_html=True)
                    has_s3 = st.toggle("Set 3", value=d.get('has_s3', False), key=f"tog_{k}")
                    s3a, s3b = 0, 0
                    if has_s3:
                        s3_cols = st.columns(2)
                        s3a = s3_cols[0].number_input("S3a", 0, 31, value=d.get('s3a', 0), key=f"s3a_{k}", label_visibility="collapsed")
                        s3b = s3_cols[1].number_input("S3b", 0, 31, value=d.get('s3b', 0), key=f"s3b_{k}", label_visibility="collapsed")
                
                with c5:
                    if st.button("Reset", key=f"reset_{k}", use_container_width=True):
                        current_finals[k] = {"t1":p1_def, "t2":p2_def, "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3": False, "winner":"TBD"}
                        save_finals(current_finals)
                        st.rerun()

                total_w1 = sw1_base + (1 if has_s3 and s3a > s3b else 0)
                total_w2 = sw2_base + (1 if has_s3 and s3b > s3a else 0)
                winner = "TBD"
                if total_w1 >= 2: winner = t1
                elif total_w2 >= 2: winner = t2
                
                st.divider()
                return {"t1":t1, "t2":t2, "s1a":s1a, "s1b":s1b, "s2a":s2a, "s2b":s2b, "s3a":s3a, "s3b":s3b, "has_s3": has_s3, "winner": winner}

            new_data = {
                'sf1': admin_match("SEMI-FINAL 1", "sf1", "1st Place", "4th Place"),
                'sf2': admin_match("SEMI-FINAL 2", "sf2", "2nd Place", "3rd Place"),
                'final': admin_match("🏆 CHAMPIONSHIP FINAL", "fin", "Winner SF1", "Winner SF2")
            }
            if st.button("💾 SAVE ALL RESULTS", use_container_width=True, type="primary"):
                save_finals(new_data)
                st.success("Scores saved successfully!")
                st.rerun()

    # --- VIEW-ONLY FINALS ---
    with tab_view:
        st.markdown('<div class="bracket-header">🏆 BLACK BRACKET - FINALS</div>', unsafe_allow_html=True)
        def render_view(label, key):
            d = current_finals.get(key, {"t1":"TBD", "t2":"TBD", "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3":False, "winner":"TBD"})
            st.markdown(f"#### {label}")
            v1, v2, v3 = st.columns([3, 2, 2])
            with v1:
                t1_s = f"<span class='winner-text'>{d['t1']}</span>" if d['winner']==d['t1'] and d['t1']!="TBD" else d['t1']
                t2_s = f"<span class='winner-text'>{d['t2']}</span>" if d['winner']==d['t2'] and d['t2']!="TBD" else d['t2']
                st.markdown(t1_s, unsafe_allow_html=True)
                st.markdown(t2_s, unsafe_allow_html=True)
            with v2:
                if d['s1a'] == 0 and d['s1b'] == 0: st.write("*Match Upcoming*")
                else:
                    scores = f"<span class='score-badge'>{d['s1a']}-{d['s1b']}</span> <span class='score-badge'>{d['s2a']}-{d['s2b']}</span>"
                    if d.get('has_s3'): scores += f" <span class='score-badge'>{d['s3a']}-{d['s3b']}</span>"
                    st.markdown(scores, unsafe_allow_html=True)
            with v3:
                win_label = f"<span class='winner-text'>{d['winner']}</span>" if d['winner']!="TBD" else "TBD"
                st.markdown(f"Winner: {win_label}", unsafe_allow_html=True)
            st.divider()

        render_view("Semi-Final 1 (#1 vs #4)", "sf1")
        render_view("Semi-Final 2 (#2 vs #3)", "sf2")
        render_view("🏆 Championship Final", "final")
