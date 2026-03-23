import streamlit as st
import pandas as pd
import os

# 1. Page Configuration
st.set_page_config(page_title="SMASH 2026", layout="wide")
FN = "SMASH 2026 - Score Tracker.csv"
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
ADMIN_PW = "pogisiJordan"

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th") if not 10 <= i % 100 <= 20 else "th"
    return f"{i}{suffix}"

# 2. Data Loading Logic
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

# 3. Styling
st.markdown("""
<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-family: sans-serif; }
    .m-table th { background-color: #f0f2f6; text-align: center !important; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    .m-table tr:nth-child(even) { background-color: #f9f9f9; }
    .bracket-header { background-color: #000; color: #fff; padding: 8px; border-radius: 4px; text-align: center; margin: 15px 0; font-weight: bold;}
    .sets-won-result { font-weight: bold; color: #d32f2f; text-align: center; font-size: 1.1em; background-color: #ffebee; border-radius: 4px; margin-bottom: 2px;}
    .score-badge { background: #f0f2f6; padding: 4px 10px; border-radius: 5px; font-weight: bold; margin-right: 5px; border: 1px solid #ccc; }
    .win-black { color: black; font-weight: bold; text-decoration: underline; }
</style>
""", unsafe_allow_html=True)

st.title("🏸 SMASH 2026")
sch, clrs, csv_db = load_data()

if sch is None or sch.empty:
    st.warning("Data not found.")
else:
    if 'db' not in st.session_state: st.session_state.db = csv_db
    
    # 4. Navigation Tabs
    tab1, tab2, tab3, tab_view, tab_admin = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    black_teams = sorted([t.replace("|", " AND ") for t, c in clrs.items() if c == "BLACK"])
    if not black_teams: black_teams = ["TBD"]

    # --- STANDINGS ---
    with tab1:
        st.info("🕒 **Current Standings**")
        stats = {t:{"Bracket":clrs.get(t,"?"), "Games Played":0, "Sets Won":0, "Sets Lost":0, "Total Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            if v['t1'] in stats:
                stats[v['t1']]["Games Played"] += 1; stats[v['t1']]["Sets Won"] += v['w1']; stats[v['t1']]["Sets Lost"] += v['w2']; stats[v['t1']]["Total Pts"] += v['p1']
            if v['t2'] in stats:
                stats[v['t2']]["Games Played"] += 1; stats[v['t2']]["Sets Won"] += v['w2']; stats[v['t2']]["Sets Lost"] += v['w1']; stats[v['t2']]["Total Pts"] += v['p2']
        df_r = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Team'})
        df_r["Team"] = df_r["Team"].str.replace("|", " AND ", regex=False)
        for color in sorted(df_r["Bracket"].unique()):
            st.subheader(f"{EMOJIS.get(color.upper(), '🏆')} {color} Bracket")
            sdf = df_r[df_r["Bracket"]==color].sort_values(["Sets Won", "Total Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["Bracket"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    # --- DAY 1 ---
    with tab2:
        q = st.text_input("🔍 Search Team Name", key="q1").lower()
        rows = []
        for _, r in sch[sch["Day"] == "Day 1"].iterrows():
            if q in r['T1'].lower() or q in r['T2'].lower():
                d = st.session_state.db.get(r["ID"])
                s1, s2 = "--", "--"
                match_display = f"{r['P1']} vs {r['P2']}"
                if d:
                    s1, s2 = f"{d['s1']} - {d['s3']}", f"{d['s2']} - {d['s4']}"
                    win_cls = f"win-{r['L'].lower()}"
                    p1_tag = f'<span class="{win_cls}">{r["P1"]}</span>' if d['w1'] == 2 else r["P1"]
                    p2_tag = f'<span class="{win_cls}">{r["P2"]}</span>' if d['w2'] == 2 else r["P2"]
                    match_display = f"{p1_tag} vs {p2_tag}"
                rows.append({"Time": r["T"], "Court": r["Court"], "Bracket": r["Emoji"], "Match": match_display, "Set 1": s1, "Set 2": s2})
        if rows:
            st.write(pd.DataFrame(rows).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    # --- DAY 2 ---
    with tab3:
        st.subheader("Day 2 Schedule")
        st.success("🔥 **Day 2 brackets are currently ongoing.**")

    # --- ADMIN TAB (Password Protected) ---
    with tab_admin:
        pw = st.text_input("Enter Admin Password", type="password")
        if pw == ADMIN_PW:
            st.markdown('<div class="bracket-header">⚙️ ADMIN CONTROL - BLACK BRACKET</div>', unsafe_allow_html=True)
            def admin_match(label, k):
                st.write(f"**{label}**")
                c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 1, 1.5])
                with c1:
                    t1 = st.selectbox(f"T1_{k}", black_teams, key=f"t1_{k}", label_visibility="collapsed")
                    t2 = st.selectbox(f"T2_{k}", black_teams, key=f"t2_{k}", label_visibility="collapsed")
                with c2:
                    s1a = st.number_input("S1a", 0, 30, key=f"s1a_{k}", label_visibility="collapsed")
                    s1b = st.number_input("S1b", 0, 30, key=f"s1b_{k}", label_visibility="collapsed")
                with c3:
                    s2a = st.number_input("S2a", 0, 30, key=f"s2a_{k}", label_visibility="collapsed")
                    s2b = st.number_input("S2b", 0, 30, key=f"s2b_{k}", label_visibility="collapsed")
                with c4:
                    s3a = st.number_input("S3a", 0, 30, key=f"s3a_{k}", label_visibility="collapsed")
                    s3b = st.number_input("S3b", 0, 30, key=f"s3b_{k}", label_visibility="collapsed")
                with c5:
                    sw1 = (1 if s1a > s1b else 0) + (1 if s2a > s2b else 0) + (1 if s3a > s3b else 0)
                    sw2 = (1 if s1b > s1a else 0) + (1 if s2b > s2a else 0) + (1 if s3b > s3a else 0)
                    st.markdown(f"<div class='sets-won-result'>{sw1} Set(s)</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='sets-won-result'>{sw2} Set(s)</div>", unsafe_allow_html=True)
                st.divider()
                return {"t1":t1, "t2":t2, "s1a":s1a, "s1b":s1b, "s2a":s2a, "s2b":s2b, "s3a":s3a, "s3b":s3b, "sw1":sw1, "sw2":sw2}

            st.session_state.sf1 = admin_match("SEMI-FINAL 1", "sf1")
            st.session_state.sf2 = admin_match("SEMI-FINAL 2", "sf2")
            st.session_state.final = admin_match("🏆 CHAMPIONSHIP FINAL", "fin")
        elif pw != "":
            st.error("Incorrect password.")

    # --- VIEW-ONLY FINALS ---
    with tab_view:
        st.markdown('<div class="bracket-header">🏆 BLACK BRACKET - FINALS</div>', unsafe_allow_html=True)
        def view_match(label, data_key):
            data = st.session_state.get(data_key, {"t1":"TBD", "t2":"TBD", "s1a":0, "s1b":0, "s2a":0, "s2b":0, "s3a":0, "s3b":0, "sw1":0, "sw2":0})
            st.markdown(f"#### {label}")
            c1, c2, c3 = st.columns([3, 2, 1])
            with c1:
                st.write(f"**{data['t1']}**")
                st.write(f"**{data['t2']}**")
            with c2:
                st.markdown(f"<span class='score-badge'>{data['s1a']}-{data['s1b']}</span> <span class='score-badge'>{data['s2a']}-{data['s2b']}</span> <span class='score-badge'>{data['s3a']}-{data['s3b']}</span>", unsafe_allow_html=True)
            with c3:
                st.markdown(f"<div class='sets-won-result'>{data['sw1']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='sets-won-result'>{data['sw2']}</div>", unsafe_allow_html=True)
            st.divider()

        view_match("Semi-Final 1 (#1 vs #4)", "sf1")
        view_match("Semi-Final 2 (#2 vs #3)", "sf2")
        view_match("🏆 Championship Final", "final")
