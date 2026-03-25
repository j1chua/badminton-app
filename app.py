import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="GCCP SMASH S1 2026", layout="wide")

# Constants
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
ADMIN_PW = "pogisiJordan"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
COLOR_MAP = {
    "BLACK": "#000000", "RED": "#d32f2f", "GREEN": "#2e7d32", 
    "PURPLE": "#7b1fa2", "WHITE": "#9e9e9e", "YELLOW": "#fbc02d"
}
IGNORE_TEAMS = ["TBD", "1ST", "2ND", "3RD", "4TH", "5TH", "TBA"]

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
    return f"{i}th"

# 3. Global Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;600;800&display=swap');
    
    /* Global Font & Consistency */
    html, body, [class*="css"], .stMarkdown, p, div, table, h1, h2, h3 {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    /* Force consistent width for all tabs */
    .block-container {
        max-width: 1000px;
        padding-top: 2rem;
        padding-bottom: 5rem;
        margin: auto;
    }

    /* Modern Table: No vertical lines */
    .m-table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-bottom: 30px; 
    }
    .m-table th { 
        background-color: #ffffff; 
        text-align: center !important; 
        padding: 16px; 
        border-bottom: 2px solid #333; /* Thick header separator */
        font-weight: 800; 
        color: #111;
        text-transform: uppercase;
        font-size: 0.9em;
        letter-spacing: 1px;
    }
    .m-table td { 
        text-align: center !important; 
        padding: 14px; 
        border-bottom: 1px solid #eee; /* Light horizontal only */
        vertical-align: middle; 
    }
    
    /* Row effects */
    .m-table tr:hover { background-color: #fafafa; }
    
    .bracket-header { color: #fff; padding: 12px; border-radius: 4px; text-align: center; margin: 15px 0; font-weight: bold; font-size: 1.2em;}
    .score-badge { background: #f0f2f6; padding: 4px 10px; border-radius: 5px; font-weight: bold; margin-right: 5px; border: 1px solid #ccc; }
    .winner-banner { background: #e8f5e9; color: #2e7d32; padding: 6px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #2e7d32; display: inline-block; font-size: 0.85em; }
    .high-stakes { background-color: #fffde7 !important; }
    .winner-text { font-weight: 800; color: #2e7d32; }
    .status-pending { color: #adb5bd; font-style: italic; font-size: 0.85em; }
    
    .trademark { position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%); font-size: 11px; color: #bbb; letter-spacing: 3px; z-index: 1000; text-align: center; width: 100%; font-weight: 300; }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

# 4. Data Loading
@st.cache_data
def load_data(mtime):
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
                    bracket_raw = str(row[c[1]]).strip().upper()
                    if not bracket_raw or "BRACKET" in bracket_raw or "COLOR" in bracket_raw: continue
                    if t1 == "" or t2 == "" or "RESULTS" in t1 or "RESULTS" in t2: continue
                    
                    is_high_stakes = "SEMIS" in bracket_raw or "FINALS" in bracket_raw
                    base_color = "WHITE"
                    for k in EMOJIS:
                        if k in bracket_raw: base_color = k; break
                    
                    court = "Court ?"
                    for r_idx in range(idx, -1, -1):
                        if "COURT" in str(df.iloc[r_idx, c[2]]).upper():
                            court = str(df.iloc[r_idx, c[2]]).strip(); break
                    
                    m_id = f"{day[:1]}{idx}{c[0]}"
                    matches.append({"ID":m_id, "Day":day, "T":str(row[c[0]]).strip(), "T1":t1, "T2":t2, 
                                   "P1":t1.replace("|"," AND "), "P2":t2.replace("|"," AND "),
                                   "Bracket":bracket_raw, "Emoji":EMOJIS.get(base_color,"🏸"), 
                                   "Court":court, "HighStakes":is_high_stakes, "L": base_color})
                    
                    if not any(p in t1.upper() for p in IGNORE_TEAMS): team_colors[t1] = base_color
                    if not any(p in t2.upper() for p in IGNORE_TEAMS): team_colors[t2] = base_color
                    
                    sc = [int(float(str(row[col]).strip())) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7]]]
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, 
                               "p1":sc[0]+sc[1], "p2":sc[2]+sc[3], 
                               "w1":(sc[0]>sc[2])+(sc[1]>sc[3]), "w2":(sc[2]>sc[0])+(sc[3]>sc[1]),
                               "l1":(sc[0]<sc[2])+(sc[1]<sc[3]), "l2":(sc[2]<sc[0])+(sc[3]<sc[1]),
                               "started": any(s > 0 for s in sc)}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 5. UI Logic
st.title("🏸 GCCP SMASH S1 2026")
mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(mtime)

if sch is not None:
    if 'finals' not in st.session_state: st.session_state.finals = load_finals()
    if 'reset_versions' not in st.session_state: st.session_state.reset_versions = {}
    all_brackets = sorted(list(set(clrs.values())))
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    with tabs[0]: # STANDINGS
        df_stand = pd.DataFrame([{"Team":t, "B":c, "GP":0, "SW":0, "SL":0, "Pts":0} for t,c in clrs.items()])
        for v in csv_db.values():
            if not v.get('started'): continue 
            for tk, wk, lk, pk in [('t1','w1','l1','p1'),('t2','w2','l2','p2')]:
                if v.get(tk) in clrs:
                    i_list = df_stand.index[df_stand['Team']==v[tk]].tolist()
                    if i_list:
                        i = i_list[0]
                        df_stand.at[i,'GP']+=1; df_stand.at[i,'SW']+=v[wk]
                        df_stand.at[i,'SL']+=v[lk]; df_stand.at[i,'Pts']+=v[pk]
        for col in all_brackets:
            st.subheader(f"{EMOJIS.get(col,'')} {col} Bracket")
            sdf = df_stand[df_stand["B"]==col].sort_values(["SW","Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["B"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    def render_matches(df_slice, key, day_label):
        search = st.text_input(f"🔍 Search Matches", key=key).lower()
        rows = []
        for _, r in df_slice.iterrows():
            if search in r['T1'].lower() or search in r['T2'].lower() or search in r['Bracket'].lower():
                d = csv_db.get(r["ID"])
                p1_disp, p2_disp = r['P1'], r['P2']
                row_cls = 'class="high-stakes"' if r['HighStakes'] else ""
                if d and d['started']:
                    if d['w1']>d['w2']: p1_disp = f"🏆 <span class='winner-text'>{r['P1']}</span>"
                    elif d['w2']>d['w1']: p2_disp = f"🏆 <span class='winner-text'>{r['P2']}</span>"
                    s1, s2 = f"{d['s1']}-{d['s3']}", f"{d['s2']}-{d['s4']}"
                else: 
                    status_text = "🕒 UPCOMING MATCH" if day_label == "Day 2" else "🕒 MATCH IN PROGRESS"
                    s1 = s2 = f'<span class="status-pending">{status_text}</span>'
                rows.append(f"<tr {row_cls}><td>{r['Court']}</td><td>{r['T']}</td><td>{r['Emoji']} {r['Bracket']}</td><td>{p1_disp} <b>vs</b> {p2_disp}</td><td>{s1}</td><td>{s2}</td></tr>")
        if rows: st.write(f"<table class='m-table'><thead><tr><th>Court</th><th>Time</th><th>Bracket</th><th>Match</th><th>Set 1</th><th>Set 2</th></tr></thead><tbody>{''.join(rows)}</tbody></table>", unsafe_allow_html=True)

    with tabs[1]: render_matches(sch[sch["Day"] == "Day 1"].sort_values(["Court", "T"]), "q1", "Day 1")
    with tabs[2]: render_matches(sch[sch["Day"] == "Day 2"].sort_values(["Court", "T"]), "q2", "Day 2")

    with tabs[3]: # FINALS VIEW
        sel_v = st.radio("Select Bracket:", all_brackets, horizontal=True, key="view_sel")
        st.markdown(f'<div class="bracket-header" style="background-color: {COLOR_MAP.get(sel_v, "#000")}">🏆 {sel_v} BRACKET - FINALS</div>', unsafe_allow_html=True)
        def v_m(label, suffix):
            k = f"{sel_v}_{suffix}"
            d = st.session_state.finals.get(k, {"t1":"TBD", "t2":"TBD", "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "sw1":0, "sw2":0, "use_s3":False})
            st.markdown(f"#### {label}")
            c1, c2, c3 = st.columns([3, 4, 2])
            with c1: st.write(f"**{d['t1']}**"); st.write(f"**{d['t2']}**")
            with c2:
                h = f"<span class='score-badge'>{d['s1a']}-{d['s1b']}</span> <span class='score-badge'>{d['s2a']}-{d['s2b']}</span>"
                if d.get('use_s3'): h += f" <span class='score-badge'>{d['s3a']}-{d['s3b']}</span>"
                st.markdown(h, unsafe_allow_html=True)
            with c3:
                if d['sw1'] >= 2: st.markdown(f"<div class='winner-banner'>🏆 WINNER: {d['t1']}</div>", unsafe_allow_html=True)
                elif d['sw2'] >= 2: st.markdown(f"<div class='winner-banner'>🏆 WINNER: {d['t2']}</div>", unsafe_allow_html=True)
            st.divider()
        v_m("Semi-Final 1 (#1 vs #4)", "sf1"); v_m("Semi-Final 2 (#2 vs #3)", "sf2"); v_m("🏆 Championship Final", "fin")

    with tabs[4]: # ADMIN
        if st.text_input("Enter Admin Password", type="password") == ADMIN_PW:
            if st.button("🔄 Force Refresh Data"):
                st.cache_data.clear(); st.rerun()
            if mtime > 0:
                st.caption(f"📅 Data Last Updated: {datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')}")
            sel_a = st.selectbox("Select Bracket:", all_brackets, key="admin_sel")
            bg_color = COLOR_MAP.get(sel_a, "#000")
            teams = sorted([t.replace("|", " AND ") for t, c in clrs.items() if c == sel_a])
            st.markdown(f'<div class="bracket-header" style="background-color: {bg_color}">⚙️ ADMIN CONTROL - {sel_a}</div>', unsafe_allow_html=True)

            def a_m(label, suffix):
                match_id = f"{sel_a}_{suffix}"
                v = st.session_state.reset_versions.get(match_id, 0)
                d = st.session_state.finals.get(match_id, {"t1":"TBD", "t2":"TBD", "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "use_s3":False})
                c_title, c_reset = st.columns([5, 1])
                with c_title: st.write(f"### {label}")
                with c_reset:
                    if st.button(f"🗑️ Reset", key=f"reset_{match_id}_{v}"):
                        if match_id in st.session_state.finals: del st.session_state.finals[match_id]
                        st.session_state.reset_versions[match_id] = v + 1
                        save_finals(st.session_state.finals); st.rerun()
                c1, c2, c3, c4 = st.columns([2, 1, 1, 1], vertical_alignment="bottom")
                with c1:
                    t_opts = ["TBD"] + teams
                    t1 = st.selectbox(f"T1", t_opts, index=t_opts.index(d['t1']) if d['t1'] in t_opts else 0, key=f"t1_{match_id}_{v}")
                    t2 = st.selectbox(f"T2", t_opts, index=t_opts.index(d['t2']) if d['t2'] in t_opts else 0, key=f"t2_{match_id}_{v}")
                with c2: 
                    s1a = st.number_input("S1 T1", 0, 31, int(d['s1a']), key=f"s1a_{match_id}_{v}")
                    s1b = st.number_input("S1 T2", 0, 31, int(d['s1b']), key=f"s1b_{match_id}_{v}")
                with c3: 
                    s2a = st.number_input("S2 T1", 0, 31, int(d['s2a']), key=f"s2a_{match_id}_{v}")
                    s2b = st.number_input("S2 T2", 0, 31, int(d['s2b']), key=f"s2b_{match_id}_{v}")
                w1_temp = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0)
                w2_temp = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0)
                is_tie = (w1_temp == 1 and w2_temp == 1)
                with c4:
                    use_s3 = st.toggle("Set 3?", value=d.get('use_s3', False) if is_tie else False, key=f"s3tgl_{match_id}_{v}", disabled=not is_tie)
                    s3a = st.number_input("S3 T1", 0, 31, int(d['s3a']), key=f"s3a_{match_id}_{v}", disabled=not use_s3)
                    s3b = st.number_input("S3 T2", 0, 31, int(d['s3b']), key=f"s3b_{match_id}_{v}", disabled=not use_s3)
                if st.button(f"Save {label}", key=f"save_{match_id}_{v}"):
                    sw1 = w1_temp + (1 if use_s3 and s3a > s3b else 0)
                    sw2 = w2_temp + (1 if use_s3 and s3b > s3a else 0)
                    st.session_state.finals[match_id] = {
                        "t1":t1, "t2":t2, "s1a":s1a, "s1b":s1b, "s2a":s2a, "s2b":s2b, 
                        "s3a":s3a if use_s3 else 0, "s3b":s3b if use_s3 else 0, 
                        "sw1":sw1, "sw2":sw2, "use_s3":use_s3
                    }
                    save_finals(st.session_state.finals); st.success("Saved!"); st.rerun()
                st.divider()
            a_m("SEMI-FINAL 1", "sf1"); a_m("SEMI-FINAL 2", "sf2"); a_m("🏆 CHAMPIONSHIP", "fin")
