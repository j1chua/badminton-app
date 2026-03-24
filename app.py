import streamlit as st
import pandas as pd
import os
import json
import time

# 1. Page Configuration
st.set_page_config(page_title="GCCP SMASH S1 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
COLOR_MAP = {
    "BLACK": "#000000", "RED": "#d32f2f", "GREEN": "#2e7d32", 
    "PURPLE": "#7b1fa2", "WHITE": "#9e9e9e", "YELLOW": "#fbc02d"
}
ADMIN_PW = "pogisiJordan"

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

# 2. Data Loading Logic
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
                    if "|" not in t1 or "|" not in t2: continue
                    color = str(row[c[1]]).strip().upper()
                    time_val, emoji = str(row[c[0]]).strip(), EMOJIS.get(color, "🏸")
                    court = "Court ?"
                    for r_idx in range(idx, -1, -1):
                        val = str(df.iloc[r_idx, c[2]]).upper()
                        if "COURT" in val: court = val.strip(); break
                    p1_d, p2_d = t1.replace("|", " AND "), t2.replace("|", " AND ")
                    m_id = f"{day[:1]}{idx}{c[0]}"
                    matches.append({"ID": m_id, "Day": day, "T": time_val, "T1": t1, "T2": t2, "P1": p1_d, "P2": p2_d, "L": color, "Emoji": emoji, "Court": court})
                    team_colors[t1] = team_colors[t2] = color
                    sc = [int(float(row[col])) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7]]]
                    w1, w2 = (sc[0]>sc[2])+(sc[1]>sc[3]), (sc[2]>sc[0])+(sc[3]>sc[1])
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "p1":sc[0]+sc[1], "p2":sc[2]+sc[3], "w1":w1, "w2":w2}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except: return None, {}, {}

# 3. Styling & Trademark
st.markdown("""
<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-family: sans-serif; }
    .m-table th { background-color: #f0f2f6; text-align: center !important; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    .bracket-header { color: #fff; padding: 12px; border-radius: 4px; text-align: center; margin: 15px 0; font-weight: bold; font-size: 1.2em;}
    .score-badge { background: #f0f2f6; padding: 4px 10px; border-radius: 5px; font-weight: bold; margin-right: 5px; border: 1px solid #ccc; }
    .winner-banner { background: #e8f5e9; color: #2e7d32; padding: 6px 12px; border-radius: 4px; font-weight: bold; border: 1px solid #2e7d32; display: inline-block; font-size: 0.85em; }
    [class^="win-"] { font-weight: bold; text-decoration: underline; }
    .win-black { color: black; } .win-red { color: red; } .win-green { color: green; }
    .win-purple { color: purple; } .win-white { color: grey; } .win-yellow { color: #fbc02d; }
    .ongoing-box { background-color: #fff9c4; border: 2px dashed #fbc02d; padding: 30px; border-radius: 10px; text-align: center; font-size: 1.5em; color: #827717; font-weight: bold; }
    
    .trademark {
        position: fixed;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 10px;
        color: #999;
        font-family: sans-serif;
        letter-spacing: 2px;
        z-index: 1000;
        text-align: center;
        width: 100%;
    }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

st.title("🏸 GCCP SMASH S1 2026")

# 4. App Logic
file_mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(file_mtime)

if sch is None or sch.empty:
    st.warning("Data not found.")
else:
    st.session_state.db = csv_db
    if 'finals' not in st.session_state: st.session_state.finals = load_finals()
    if 'reset_versions' not in st.session_state: st.session_state.reset_versions = {}
    
    all_brackets = sorted(list(set(clrs.values())))
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    # --- STANDINGS ---
    with tabs[0]:
        stats = {t:{"Bracket":clrs.get(t,"?"), "Games Played":0, "Sets Won":0, "Sets Lost":0, "Total Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            if v['t1'] in stats:
                stats[v['t1']]["Games Played"] += 1; stats[v['t1']]["Sets Won"] += v['w1']; stats[v['t1']]["Sets Lost"] += v['w2']; stats[v['t1']]["Total Pts"] += v['p1']
            if v['t2'] in stats:
                stats[v['t2']]["Games Played"] += 1; stats[v['t2']]["Sets Won"] += v['w2']; stats[v['t2']]["Sets Lost"] += v['w1']; stats[v['t2']]["Total Pts"] += v['p2']
        df_r = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Team'})
        df_r["Team"] = df_r["Team"].str.replace("|", " AND ", regex=False)
        for color in all_brackets:
            st.subheader(f"{EMOJIS.get(color, '🏆')} {color} Bracket")
            sdf = df_r[df_r["Bracket"]==color].sort_values(["Sets Won", "Total Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["Bracket"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    # --- DAY 1 ---
    with tabs[1]:
        q = st.text_input("🔍 Search Team Name", key="q1").lower()
        rows = []
        day1_df = sch[sch["Day"] == "Day 1"].copy().sort_values(by="Court")
        for _, r in day1_df.iterrows():
            if q in r['T1'].lower() or q in r['T2'].lower():
                d = st.session_state.db.get(r["ID"])
                s1, s2 = "--", "--"
                p1_tag, p2_tag = r["P1"], r["P2"]
                if d:
                    s1, s2 = f"{d['s1']} - {d['s3']}", f"{d['s2']} - {d['s4']}"
                    win_cls = f"win-{r['L'].lower()}"
                    if d['w1'] == 2: p1_tag = f'<span class="{win_cls}">{r["P1"]}</span>'
                    if d['w2'] == 2: p2_tag = f'<span class="{win_cls}">{r["P2"]}</span>'
                rows.append({"Court": r["Court"], "Time": r["T"], "Bracket": r["Emoji"], "Match": f"{p1_tag} vs {p2_tag}", "Set 1": s1, "Set 2": s2})
        if rows: st.write(pd.DataFrame(rows).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    # --- DAY 2 ---
    with tabs[2]:
        st.write("")
        st.markdown('<div class="ongoing-box">🕒 Day 2 Schedule is still ongoing...</div>', unsafe_allow_html=True)

    # --- FINALS VIEW ---
    with tabs[3]:
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

    # --- ADMIN ---
    with tabs[4]:
        if st.text_input("Enter Admin Password", type="password") == ADMIN_PW:
            if st.button("🔄 Force Refresh Data"):
                st.cache_data.clear(); st.rerun()
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
                    save_finals(st.session_state.finals); st.success("Saved!")
                st.divider()
            a_m("SEMI-FINAL 1", "sf1"); a_m("SEMI-FINAL 2", "sf2"); a_m("🏆 CHAMPIONSHIP", "fin")
