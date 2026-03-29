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
    
    html, body, [class*="css"], .stMarkdown, p, div, table, h1, h2, h3 {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    .table-container {
        width: 95%;
        margin: 0 auto;
    }

    .m-table { 
        width: 100%; 
        border-collapse: collapse; 
        margin-bottom: 30px; 
    }
    .m-table th { 
        background-color: #ffffff; 
        text-align: center !important; 
        padding: 16px; 
        border-bottom: 2px solid #333; 
        font-weight: 800; 
        color: #111;
        text-transform: uppercase;
        font-size: 0.85em;
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .m-table td { 
        text-align: center !important; 
        padding: 14px; 
        border-bottom: 1px solid #eee; 
        vertical-align: middle; 
    }
    
    .m-table tr:hover { background-color: #fafafa; }
    
    .bracket-header { color: #fff; padding: 12px; border-radius: 4px; text-align: center; margin: 15px 0; font-weight: bold; font-size: 1.2em;}
    .score-badge { background: #f0f2f6; padding: 4px 10px; border-radius: 5px; font-weight: bold; margin-right: 5px; border: 1px solid #ccc; }
    .winner-banner { background: #e8f5e9; color: #2e7d32; padding: 6px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #2e7d32; display: inline-block; font-size: 0.85em; }
    .high-stakes { background-color: #fffde7 !important; }
    .winner-text { font-weight: 800; color: #2e7d32; }
    .status-pending { color: #adb5bd; font-style: italic; font-size: 0.85em; }
    .sync-text { font-size: 0.8em; color: #888; text-align: center; margin-top: 20px; font-style: italic; }
    
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
        blocks = [[0,1,2,7, 3,8, 4,9, 5,10], [13,14,15,20, 16,21, 17,22, 18,23]]
        
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
                    prio = 1 if "SEMIS" in bracket_raw else (2 if "FINALS" in bracket_raw else 3)
                    
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
                                   "Court":court, "HighStakes":is_high_stakes, "L": base_color, "Prio": prio})
                    
                    if not any(p in t1.upper() for p in IGNORE_TEAMS): team_colors[t1] = base_color
                    if not any(p in t2.upper() for p in IGNORE_TEAMS): team_colors[t2] = base_color
                    
                    sc = [int(float(str(row[col]).strip())) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7], c[8], c[9]]]
                    
                    w1 = (sc[0]>sc[1]) + (sc[2]>sc[3]) + (sc[4]>sc[5] if (sc[4]>0 or sc[5]>0) else 0)
                    w2 = (sc[1]>sc[0]) + (sc[3]>sc[2]) + (sc[5]>sc[4] if (sc[4]>0 or sc[5]>0) else 0)
                    
                    db[m_id] = {
                        "s1":sc[0], "s1b":sc[1], "s2":sc[2], "s2b":sc[3], "s3":sc[4], "s3b":sc[5],
                        "t1":t1, "t2":t2, 
                        "p1":sc[0]+sc[2]+sc[4], "p2":sc[1]+sc[3]+sc[5], 
                        "w1":w1, "w2":w2,
                        "started": any(s > 0 for s in sc)
                    }
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 5. UI Logic
st.title("🏸 GCCP SMASH S1 2026")
mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(mtime)

if sch is not None:
    if 'finals' not in st.session_state: st.session_state.finals = load_finals()
    all_brackets = sorted(list(set(clrs.values())))
    
    # Hiding Finals and Admin for now by removing them from tabs list
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2"])

    with tabs[0]: # STANDINGS
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        df_stand = pd.DataFrame([{"Team":t, "Bracket":c, "Games Played":0, "Sets Won":0, "Sets Lost":0, "Points":0} for t,c in clrs.items()])
        for v in csv_db.values():
            if not v.get('started'): continue 
            for tk, wk, lk, pk in [('t1','w1','w2','p1'),('t2','w2','w1','p2')]:
                if v.get(tk) in clrs:
                    i_list = df_stand.index[df_stand['Team']==v[tk]].tolist()
                    if i_list:
                        i = i_list[0]
                        df_stand.at[i,'Games Played']+=1; df_stand.at[i,'Sets Won']+=v[wk]
                        df_stand.at[i,'Sets Lost']+=v[lk]; df_stand.at[i,'Points']+=v[pk]
        
        for col in all_brackets:
            st.subheader(f"{EMOJIS.get(col,'')} {col} Bracket")
            sdf = df_stand[df_stand["Bracket"]==col].sort_values(["Sets Won","Points"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["Bracket"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)
            
            st.write(f"#### 🏆 {col} BRACKET PLAYOFF MATCHES")
            playoff_matches = sch[(sch["L"] == col) & (sch["HighStakes"] == True)].sort_values(["Prio", "T"])
            
            if not playoff_matches.empty:
                p_rows = []
                for _, r in playoff_matches.iterrows():
                    d = csv_db.get(r["ID"])
                    p1_disp, p2_disp = r['P1'], r['P2']
                    if d and d['started']:
                        if d['w1'] > d['w2']: p1_disp = f"🏆 <span class='winner-text'>{r['P1']}</span>"
                        elif d['w2'] > d['w1']: p2_disp = f"🏆 <span class='winner-text'>{r['P2']}</span>"
                        s1, s2 = f"{d['s1']}-{d['s1b']}", f"{d['s2']}-{d['s2b']}"
                        s3 = f"{d['s3']}-{d['s3b']}" if (d['s3']>0 or d['s3b']>0) else '<span class="status-pending">-</span>'
                    else:
                        s1 = s2 = s3 = '<span class="status-pending">TBD</span>'
                    
                    p_rows.append(f"<tr><td><b>{r['Bracket']}</b></td><td>{r['T']}</td><td>{p1_disp} <b>vs</b> {p2_disp}</td><td>{s1}</td><td>{s2}</td><td>{s3}</td></tr>")
                st.write(f"<table class='m-table'><thead><tr><th>Round</th><th>Time</th><th>Matchup</th><th>Set 1</th><th>Set 2</th><th>Set 3</th></tr></thead><tbody>{''.join(p_rows)}</tbody></table>", unsafe_allow_html=True)
            else:
                st.info(f"No playoff matches found for {col} bracket yet.")
        
        if mtime > 0:
            st.markdown(f'<div class="sync-text">Scores last synced: {datetime.fromtimestamp(mtime).strftime("%I:%M %p, %b %d")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def render_matches(df_slice, key, day_label):
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        search = st.text_input(f"🔍 Search Matches", key=key).lower()
        rows = []
        for _, r in df_slice.sort_values(["Court", "T"]).iterrows():
            if search in r['T1'].lower() or search in r['T2'].lower() or search in r['Bracket'].lower():
                d = csv_db.get(r["ID"])
                p1_disp, p2_disp = r['P1'], r['P2']
                row_cls = 'class="high-stakes"' if r['HighStakes'] else ""
                if d and d['started']:
                    if d['w1']>d['w2']: p1_disp = f"🏆 <span class='winner-text'>{r['P1']}</span>"
                    elif d['w2']>d['w1']: p2_disp = f"🏆 <span class='winner-text'>{r['P2']}</span>"
                    s1, s2 = f"{d['s1']}-{d['s1b']}", f"{d['s2']}-{d['s2b']}"
                    s3 = f"{d['s3']}-{d['s3b']}" if (d['s3']>0 or d['s3b']>0) else "-"
                else: 
                    status_text = "🕒 UPCOMING"
                    s1 = s2 = s3 = f'<span class="status-pending">{status_text}</span>'
                rows.append(f"<tr {row_cls}><td>{r['Court']}</td><td>{r['T']}</td><td>{r['Emoji']} {r['Bracket']}</td><td>{p1_disp} <b>vs</b> {p2_disp}</td><td>{s1}</td><td>{s2}</td><td>{s3}</td></tr>")
        if rows: st.write(f"<table class='m-table'><thead><tr><th>Court</th><th>Time</th><th>Bracket</th><th>Match</th><th>Set 1</th><th>Set 2</th><th>Set 3</th></tr></thead><tbody>{''.join(rows)}</tbody></table>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tabs[1]: render_matches(sch[sch["Day"] == "Day 1"], "q1", "Day 1")
    with tabs[2]: render_matches(sch[sch["Day"] == "Day 2"], "q2", "Day 2")

# --- Hidden Logic (Retained for future use) ---
def hidden_finals_tab():
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

def hidden_admin_tab():
    if st.text_input("Enter Admin Password", type="password") == ADMIN_PW:
        if st.button("🔄 Force Refresh Data"):
            st.cache_data.clear(); st.rerun()
