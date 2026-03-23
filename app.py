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

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th") if not 10 <= i % 100 <= 20 else "th"
    return f"{i}{suffix}"

# 3. Tournament Data Loading
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
                    time, emoji = str(row[c[0]]).strip(), EMOJIS.get(color, "🏸")
                    court = "Court ?"
                    for r_idx in range(idx, -1, -1):
                        val = str(df.iloc[r_idx, c[2]]).upper()
                        if "COURT" in val: court = val.strip(); break
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

# 4. Styling
st.markdown("""
<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-family: sans-serif; }
    .m-table th { background-color: #f0f2f6; text-align: center !important; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    .bracket-header { background-color: #000; color: #fff; padding: 8px; border-radius: 4px; text-align: center; margin: 15px 0; font-weight: bold;}
    .score-badge { background: #f0f2f6; padding: 4px 10px; border-radius: 5px; font-weight: bold; margin-right: 5px; border: 1px solid #ccc; font-family: monospace; }
    .winner-text { color: #2e7d32; font-weight: bold; text-decoration: underline; }
    .tie-warning { color: #d32f2f; font-weight: bold; font-size: 0.8em; }
</style>
""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Data not found. Please ensure the CSV is uploaded.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    tab1, tab2, tab3, tab_view, tab_admin = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    black_teams = sorted([t.replace("|", " AND ") for t, c in clrs.items() if c == "BLACK"])
    current_finals = load_finals()

    # --- ADMIN TAB ---
    with tab_admin:
        pw = st.text_input("Admin Password", type="password")
        if pw == ADMIN_PW:
            st.markdown('<div class="bracket-header">⚙️ ADMIN CONTROL - BLACK BRACKET</div>', unsafe_allow_html=True)
            
            def admin_match(label, k, p1_def, p2_def):
                st.write(f"**{label}**")
                d = current_finals.get(k, {"t1":p1_def, "t2":p2_def, "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3": False})
                
                c1, c2, c3, c4, c5 = st.columns([2.5, 1, 1, 1, 1])
                with c1:
                    t1 = st.selectbox(f"T1", [p1_def] + black_teams, index=0 if d['t1'] not in black_teams else black_teams.index(d['t1'])+1, key=f"t1_{k}")
                    t2 = st.selectbox(f"T2", [p2_def] + black_teams, index=0 if d['t2'] not in black_teams else black_teams.index(d['t2'])+1, key=f"t2_{k}")
                with c2:
                    s1a = st.number_input("S1a", 0, 30, value=d['s1a'], key=f"s1a_{k}", label_visibility="collapsed")
                    s1b = st.number_input("S1b", 0, 30, value=d['s1b'], key=f"s1b_{k}", label_visibility="collapsed")
                with c3:
                    s2a = st.number_input("S2a", 0, 30, value=d['s2a'], key=f"s2a_{k}", label_visibility="collapsed")
                    s2b = st.number_input("S2b", 0, 30, value=d['s2b'], key=f"s2b_{k}", label_visibility="collapsed")
                
                # Winner Logic for Sets 1 and 2
                sw1_base = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0)
                sw2_base = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0)
                is_tie = (sw1_base == 1 and sw2_base == 1)

                with c4:
                    if is_tie: st.markdown('<p class="tie-warning">1-1 TIE! ⬇️</p>', unsafe_allow_html=True)
                    has_s3 = st.toggle("Set 3", value=d.get('has_s3', False), key=f"tog_{k}")
                    s3a, s3b = 0, 0
                    if has_s3:
                        s3a = st.number_input("S3a", 0, 30, value=d.get('s3a', 0), key=f"s3a_{k}", label_visibility="collapsed")
                        s3b = st.number_input("S3b", 0, 30, value=d.get('s3b', 0), key=f"s3b_{k}", label_visibility="collapsed")
                
                with c5:
                    if st.button("Reset", key=f"reset_{k}"):
                        current_finals[k] = {"t1":p1_def, "t2":p2_def, "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3": False, "winner":"TBD"}
                        save_finals(current_finals)
                        st.rerun()

                # Final Winner Calculation
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
            if st.button("💾 Save All Changes"):
                save_finals(new_data)
                st.success("Results updated!")
                st.rerun()
        elif pw != "": st.error("Access Denied.")

    # --- VIEW-ONLY FINALS ---
    with tab_view:
        st.markdown('<div class="bracket-header">🏆 BLACK BRACKET - FINALS</div>', unsafe_allow_html=True)
        def render_view(label, key):
            d = current_finals.get(key, {"t1":"TBD", "t2":"TBD", "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3":False, "winner":"TBD"})
            st.markdown(f"#### {label}")
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                t1_s = f"<span class='winner-text'>{d['t1']}</span>" if d['winner']==d['t1'] and d['t1']!="TBD" else d['t1']
                t2_s = f"<span class='winner-text'>{d['t2']}</span>" if d['winner']==d['t2'] and d['t2']!="TBD" else d['t2']
                st.markdown(t1_s, unsafe_allow_html=True)
                st.markdown(t2_s, unsafe_allow_html=True)
            with c2:
                # Don't show scores if they are 0-0 (match hasn't started)
                if d['s1a'] == 0 and d['s1b'] == 0:
                    st.markdown("<span class='tbd-text'>Match Upcoming</span>", unsafe_allow_html=True)
                else:
                    scores = f"<span class='score-badge'>{d['s1a']}-{d['s1b']}</span><span class='score-badge'>{d['s2a']}-{d['s2b']}</span>"
                    if d.get('has_s3'):
                        scores += f"<span class='score-badge'>{d['s3a']}-{d['s3b']}</span>"
                    st.markdown(scores, unsafe_allow_html=True)
            with c3:
                win_label = f"<span class='winner-text'>{d['winner']}</span>" if d['winner']!="TBD" else "TBD"
                st.markdown(f"Winner: {win_label}", unsafe_allow_html=True)
            st.divider()

        render_view("Semi-Final 1 (#1 vs #4)", "sf1")
        render_view("Semi-Final 2 (#2 vs #3)", "sf2")
        render_view("🏆 Championship Final", "final")

    # --- STANDINGS (Simplified for this display) ---
    with tab1:
        st.info("🕒 Check rankings based on Day 1 & Day 2 scores.")
