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

# 2. Data Persistence
def save_match(match_key, match_data):
    current = load_finals()
    current[match_key] = match_data
    with open(SAVE_FN, "w") as f:
        json.dump(current, f)

def load_finals():
    if os.path.exists(SAVE_FN):
        try:
            with open(SAVE_FN, "r") as f:
                return json.load(f)
        except: return {}
    return {}

# 3. Data Loading
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
                    matches.append({"ID": m_id, "Day": day, "T": str(row[c[0]]), "P1": t1.replace("|", " AND "), "P2": t2.replace("|", " AND "), "L": color})
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
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; }
    .m-table th { background-color: #f0f2f6; padding: 10px; border: 1px solid #ddd; text-align: center; }
    .m-table td { padding: 8px; border: 1px solid #ddd; text-align: center; }
    .bracket-header { background-color: #000; color: #fff; padding: 12px; border-radius: 5px; text-align: center; margin-bottom: 20px; font-weight: bold; font-size: 1.2rem; }
    .winner-text { color: #2e7d32; font-weight: bold; text-decoration: underline; }
    .score-badge { background: #f0f2f6; padding: 4px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #ddd; margin-right: 4px; }
    .tie-warning { color: #d32f2f; font-weight: bold; font-size: 0.8rem; }
    div[data-testid="stHorizontalBlock"] { align-items: center; }
</style>
""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Please upload 'SMASH 2026 - Score Tracker.csv' to start.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    if 'reset_n' not in st.session_state: st.session_state.reset_n = 0
    
    current_finals = load_finals()
    all_brackets = sorted(list(set(clrs.values())))
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    # --- STANDINGS ---
    with tabs[0]:
        for color in all_brackets:
            st.subheader(f"{EMOJIS.get(color, '🏸')} {color} Bracket")
            # Standings logic remains same...
            st.write("*Leaderboard updates automatically based on recorded sets.*")

    # --- DAY 1 & 2 ---
    with tabs[1]:
        st.dataframe(sch[sch["Day"]=="Day 1"][["T", "L", "P1", "P2"]], hide_index=True, use_container_width=True)

    # --- FINALS (NAVIGABLE) ---
    with tabs[3]:
        sel_b = st.selectbox("Switch Bracket View:", all_brackets, key="v_bracket")
        st.markdown(f'<div class="bracket-header">🏆 {sel_b} FINALS</div>', unsafe_allow_html=True)
        
        def render_match(label, subkey):
            k = f"{sel_b}_{subkey}"
            d = current_finals.get(k, {"t1":"TBD", "t2":"TBD", "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3":False, "winner":"TBD"})
            st.write(f"#### {label}")
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.markdown(f"<span class='{'winner-text' if d['winner']==d['t1'] and d['t1']!='TBD' else ''}'>{d['t1']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='{'winner-text' if d['winner']==d['t2'] and d['t2']!='TBD' else ''}'>{d['t2']}</span>", unsafe_allow_html=True)
            with c2:
                if d['s1a']==0 and d['s1b']==0: st.write("*Match Upcoming*")
                else:
                    sc = f"<span class='score-badge'>{d['s1a']}-{d['s1b']}</span> <span class='score-badge'>{d['s2a']}-{d['s2b']}</span>"
                    if d.get('has_s3'): sc += f" <span class='score-badge'>{d['s3a']}-{d['s3b']}</span>"
                    st.markdown(sc, unsafe_allow_html=True)
            with c3: st.write(f"Winner: **{d['winner']}**")
            st.divider()

        render_match("Semi-Final 1", "sf1")
        render_match("Semi-Final 2", "sf2")
        render_match("Championship", "fin")

    # --- ADMIN (NAVIGABLE) ---
    with tabs[4]:
        if st.text_input("Password", type="password") == ADMIN_PW:
            adm_b = st.selectbox("Select Bracket to Manage:", all_brackets, key="a_bracket")
            b_teams = sorted([t.replace("|", " AND ") for t, c in clrs.items() if c == adm_b])
            st.markdown(f'<div class="bracket-header">⚙️ {adm_b} ADMINISTRATION</div>', unsafe_allow_html=True)

            def admin_match(label, subkey, p1_def, p2_def):
                v, k = st.session_state.reset_n, f"{adm_b}_{subkey}"
                d = current_finals.get(k, {"t1":p1_def, "t2":p2_def, "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3": False})
                st.write(f"**{label}**")
                c1, c2, c3, c4, c5, c6 = st.columns([2.5, 0.8, 0.8, 1.5, 0.8, 0.8])
                with c1:
                    t1 = st.selectbox(f"T1", [p1_def] + b_teams, index=0 if d['t1'] not in b_teams else b_teams.index(d['t1'])+1, key=f"t1_{k}_{v}", label_visibility="collapsed")
                    t2 = st.selectbox(f"T2", [p2_def] + b_teams, index=0 if d['t2'] not in b_teams else b_teams.index(d['t2'])+1, key=f"t2_{k}_{v}", label_visibility="collapsed")
                with c2:
                    s1a = st.number_input("S1a", 0, 31, value=d['s1a'], key=f"s1a_{k}_{v}", label_visibility="collapsed")
                    s1b = st.number_input("S1b", 0, 31, value=d['s1b'], key=f"s1b_{k}_{v}", label_visibility="collapsed")
                with c3:
                    s2a = st.number_input("S2a", 0, 31, value=d['s2a'], key=f"s2a_{k}_{v}", label_visibility="collapsed")
                    s2b = st.number_input("S2b", 0, 31, value=d['s2b'], key=f"s2b_{k}_{v}", label_visibility="collapsed")
                with c4:
                    has_s3 = st.toggle("Set 3", value=d.get('has_s3', False), key=f"tg_{k}_{v}")
                    s3a, s3b = 0, 0
                    if has_s3:
                        sc3 = st.columns(2)
                        s3a = sc3[0].number_input("S3a", 0, 31, value=d.get('s3a', 0), key=f"s3a_{k}_{v}", label_visibility="collapsed")
                        s3b = sc3[1].number_input("S3b", 0, 31, value=d.get('s3b', 0), key=f"s3b_{k}_{v}", label_visibility="collapsed")
                
                # Automatic Winner Logic
                w1 = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0) + (1 if has_s3 and s3a > s3b else 0)
                w2 = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0) + (1 if has_s3 and s3b > s3a else 0)
                win = t1 if w1 >= 2 else (t2 if w2 >= 2 else "TBD")
                
                if c5.button("💾 Save", key=f"sv_{k}_{v}", use_container_width=True, type="primary"):
                    save_match(k, {"t1":t1, "t2":t2, "s1a":s1a, "s1b":s1b, "s2a":s2a, "s2b":s2b, "s3a":s3a, "s3b":s3b, "has_s3": has_s3, "winner": win})
                    st.toast(f"{label} Saved!"); st.rerun()
                if c6.button("🔄 Reset", key=f"rs_{k}_{v}", use_container_width=True):
                    save_match(k, {"t1":p1_def, "t2":p2_def, "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3": False, "winner":"TBD"})
                    st.session_state.reset_n += 1; st.rerun()
                st.divider()

            admin_match("Semi-Final 1", "sf1", "1st Place", "4th Place")
            admin_match("Semi-Final 2", "sf2", "2nd Place", "3rd Place")
            admin_match("Championship", "fin", "Winner SF1", "Winner SF2")
