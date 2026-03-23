import streamlit as st
import pd as pd
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
def save_single_match(match_key, match_data):
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

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    return f"<b>{i}th</b>"

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
    .bracket-header { background-color: #000; color: #fff; padding: 10px; border-radius: 5px; text-align: center; margin-bottom: 20px; font-weight: bold; }
    .winner-text { color: #2e7d32; font-weight: bold; text-decoration: underline; }
    .score-badge { background: #f0f2f6; padding: 4px 8px; border-radius: 4px; font-weight: bold; border: 1px solid #ddd; margin-right: 4px; }
    .tie-warning { color: #d32f2f; font-weight: bold; font-size: 0.75rem; display: block; }
    div[data-testid="stHorizontalBlock"] { align-items: center; }
</style>
""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Please upload the CSV file to begin.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    if 'reset_n' not in st.session_state: st.session_state.reset_n = 0
    
    current_finals = load_finals()
    main_tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])
    all_brackets = sorted(list(set(clrs.values())))

    # --- STANDINGS ---
    with main_tabs[0]:
        stats = {t:{"Bracket":clrs.get(t,"?"), "Sets Won":0, "Total Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            if v['t1'] in stats: stats[v['t1']]["Sets Won"] += v['w1']; stats[v['t1']]["Total Pts"] += v['p1']
            if v['t2'] in stats: stats[v['t2']]["Sets Won"] += v['w2']; stats[v['t2']]["Total Pts"] += v['p2']
        
        df_r = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Team'})
        for color in all_brackets:
            st.subheader(f"{EMOJIS.get(color, '🏸')} {color} Bracket")
            sdf = df_r[df_r["Bracket"]==color].sort_values(["Sets Won", "Total Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    # --- DAY 1 ---
    with main_tabs[1]:
        q = st.text_input("🔍 Search Team", key="q1").lower()
        d1_matches = sch[sch["Day"] == "Day 1"]
        rows = []
        for _, r in d1_matches.iterrows():
            if q in r['T1'].lower() or q in r['T2'].lower():
                d = st.session_state.db.get(r["ID"])
                s1, s2 = f"{d['s1']}-{d['s3']}", f"{d['s2']}-{d['s4']}" if d else ("--","--")
                rows.append({"Time": r["T"], "Court": r["Court"], "Bracket": r["Emoji"], "Match": f"{r['P1']} vs {r['P2']}", "Set 1": s1, "Set 2": s2})
        st.write(pd.DataFrame(rows).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    # --- DAY 2 ---
    with main_tabs[2]:
        st.info("Day 2 Schedule Ongoing...")

    # --- FINALS (View Only) ---
    with main_tabs[3]:
        sel_bracket = st.radio("Select Bracket", all_brackets, horizontal=True, key="view_bracket")
        st.markdown(f'<div class="bracket-header">🏆 {sel_bracket} BRACKET - FINALS</div>', unsafe_allow_html=True)
        
        def render_view(label, key_suffix):
            key = f"{sel_bracket}_{key_suffix}"
            d = current_finals.get(key, {"t1":"TBD", "t2":"TBD", "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3":False, "winner":"TBD"})
            st.markdown(f"#### {label}")
            v1, v2, v3 = st.columns([3, 2, 2])
            with v1:
                st.markdown(f"<span class='{'winner-text' if d['winner']==d['t1'] and d['t1']!='TBD' else ''}'>{d['t1']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='{'winner-text' if d['winner']==d['t2'] and d['t2']!='TBD' else ''}'>{d['t2']}</span>", unsafe_allow_html=True)
            with v2:
                if d['s1a'] == 0 and d['s1b'] == 0: st.write("*Upcoming*")
                else:
                    sc = f"<span class='score-badge'>{d['s1a']}-{d['s1b']}</span> <span class='score-badge'>{d['s2a']}-{d['s2b']}</span>"
                    if d.get('has_s3'): sc += f" <span class='score-badge'>{d['s3a']}-{d['s3b']}</span>"
                    st.markdown(sc, unsafe_allow_html=True)
            with v3: st.write(f"Winner: **{d['winner']}**")
            st.divider()

        render_view("Semi-Final 1", "sf1")
        render_view("Semi-Final 2", "sf2")
        render_view("🏆 Championship", "fin")

    # --- ADMIN (Manage All Brackets) ---
    with main_tabs[4]:
        if st.text_input("Password", type="password") == ADMIN_PW:
            adm_bracket = st.selectbox("Manage Bracket:", all_brackets)
            bracket_teams = sorted([t.replace("|", " AND ") for t, c in clrs.items() if c == adm_bracket])
            st.markdown(f'<div class="bracket-header">⚙️ {adm_bracket} SETTINGS</div>', unsafe_allow_html=True)

            def admin_match(label, key_suffix, p1_def, p2_def):
                v, k = st.session_state.reset_n, f"{adm_bracket}_{key_suffix}"
                d = current_finals.get(k, {"t1":p1_def, "t2":p2_def, "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3": False})
                st.write(f"**{label}**")
                c1, c2, c3, c4, c5, c6 = st.columns([2.5, 0.8, 0.8, 1.5, 0.8, 0.8])
                with c1:
                    t1 = st.selectbox(f"T1", [p1_def] + bracket_teams, index=0 if d['t1'] not in bracket_teams else bracket_teams.index(d['t1'])+1, key=f"t1_{k}_{v}", label_visibility="collapsed")
                    t2 = st.selectbox(f"T2", [p2_def] + bracket_teams, index=0 if d['t2'] not in bracket_teams else bracket_teams.index(d['t2'])+1, key=f"t2_{k}_{v}", label_visibility="collapsed")
                with c2:
                    s1a = st.number_input("S1a", 0, 31, value=d['s1a'], key=f"s1a_{k}_{v}", label_visibility="collapsed")
                    s1b = st.number_input("S1b", 0, 31, value=d['s1b'], key=f"s1b_{k}_{v}", label_visibility="collapsed")
                with c3:
                    s2a = st.number_input("S2a", 0, 31, value=d['s2a'], key=f"s2a_{k}_{v}", label_visibility="collapsed")
                    s2b = st.number_input("S2b", 0, 31, value=d['s2b'], key=f"s2b_{k}_{v}", label_visibility="collapsed")
                with c4:
                    has_s3 = st.toggle("Set 3", value=d.get('has_s3', False), key=f"tg_{k}_{v}")
                    s3a, s3b = (st.columns(2)[0].number_input("S3a", 0, 31, value=d.get('s3a', 0), key=f"s3a_{k}_{v}", label_visibility="collapsed"), 
                               st.columns(2)[1].number_input("S3b", 0, 31, value=d.get('s3b', 0), key=f"s3b_{k}_{v}", label_visibility="collapsed")) if has_s3 else (0,0)
                
                win = t1 if ((s1a>s1b)+(s2a>s2b)+(1 if has_s3 and s3a>s3b else 0)) >= 2 else (t2 if ((s1b>s1a)+(s2b>s2a)+(1 if has_s3 and s3b>s3a else 0)) >= 2 else "TBD")
                m_data = {"t1":t1, "t2":t2, "s1a":s1a, "s1b":s1b, "s2a":s2a, "s2b":s2b, "s3a":s3a, "s3b":s3b, "has_s3": has_s3, "winner": win}
                
                if c5.button("💾 Save", key=f"sv_{k}_{v}", use_container_width=True, type="primary"):
                    save_single_match(k, m_data); st.toast(f"{label} Saved!"); st.rerun()
                if c6.button("🔄 Reset", key=f"rs_{k}_{v}", use_container_width=True):
                    save_single_match(k, {"t1":p1_def, "t2":p2_def, "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "has_s3": False, "winner":"TBD"})
                    st.session_state.reset_n += 1; st.rerun()
                st.divider()

            admin_match("Semi-Final 1", "sf1", "1st Place", "4th Place")
            admin_match("Semi-Final 2", "sf2", "2nd Place", "3rd Place")
            admin_match("🏆 Championship", "fin", "Winner SF1", "Winner SF2")
