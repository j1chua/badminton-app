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
    return f"<b>{i}th</b>"

def nz(value):
    try:
        val = float(value)
        return val if pd.notnull(val) else 0
    except: return 0

@st.cache_data
def load_raw_data():
    if os.path.exists(FN):
        return pd.read_csv(FN, header=None).fillna("")
    return pd.DataFrame()

df = load_raw_data()

# 3. Calculation Logic for Standings
def get_detailed_standings(df):
    all_teams = []
    for col in [2, 7, 15, 20]:
        all_teams.extend(df[col].astype(str).tolist())
    
    unique_teams = sorted(list(set([
        t.strip() for t in all_teams 
        if t.strip() and "|" in t and not any(p in t for p in IGNORE_TEAMS)
    ])))

    stats_list = []
    for team in unique_teams:
        gp, sw, sl, pts = 0, 0, 0, 0
        courts = [(2, 3, 4, 5, 7, 8, 9, 10), (15, 16, 17, 18, 20, 21, 22, 23)]
        for c in courts:
            for t_col, s_start, o_col, os_start in [(c[0], c[1], c[4], c[5]), (c[4], c[5], c[0], c[1])]:
                m = df[df[t_col] == team]
                for _, row in m.iterrows():
                    s = [nz(row[s_start]), nz(row[s_start+1]), nz(row[s_start+2])]
                    o = [nz(os_start), nz(os_start+1), nz(os_start+2)]
                    if sum(s) + sum(o) > 0:
                        gp += 1
                        for i in range(3):
                            if s[i] > o[i]: sw += 1
                            elif o[i] > s[i]: sl += 1
                        pts += sum(s)
        
        stats_list.append({
            "TEAM": team, 
            "GAMES PLAYED": gp, 
            "SETS WON": sw, 
            "SETS LOST": sl, 
            "POINTS": int(pts)
        })
    
    res = pd.DataFrame(stats_list).sort_values(by=['SETS WON', 'POINTS'], ascending=False).reset_index(drop=True)
    res.index += 1
    res.index.name = "RANK"
    return res.reset_index()

# 4. Main UI Tabs
t1, t2, t3, t4, t5 = st.tabs(["📅 Day 1", "📅 Day 2", "📊 Standings", "🏆 Finals", "⚙️ Admin"])

with t1:
    st.header("Day 1 - Match Logs")
    st.dataframe(df.iloc[1:24], use_container_width=True, hide_index=True)

with t2:
    st.header("Day 2 - Match Logs")
    st.dataframe(df.iloc[26:], use_container_width=True, hide_index=True)

with t3:
    st.header("Tournament Standings & Playoffs")
    # THE ONLY MODIFIED PART:
    st.table(get_detailed_standings(df))
    st.divider()
    st.subheader("🏆 Championship Brackets (Semis & Finals)")
    playoff_rows = []
    for idx, row in df.iterrows():
        for c_lbl, t1_idx, t2_idx, s1_rng, s2_rng in [(1, 2, 7, [3,4,5], [8,9,10]), (14, 15, 20, [16,17,18], [21,22,23])]:
            label = str(row[c_lbl]).upper()
            if any(x in label for x in ["SEMIS", "FINALS"]):
                tn1, tn2 = str(row[t1_idx]), str(row[t2_idx])
                if "|" in tn1:
                    sc1 = " | ".join([str(row[i]) for i in s1_rng if str(row[i]).strip() and str(row[i]) not in ["0", "0.0"]])
                    sc2 = " | ".join([str(row[i]) for i in s2_rng if str(row[i]).strip() and str(row[i]) not in ["0", "0.0"]])
                    playoff_rows.append({"BRACKET": label, "TEAM 1": tn1, "SCORE 1": sc1, "TEAM 2": tn2, "SCORE 2": sc2})
    if playoff_rows:
        st.dataframe(pd.DataFrame(playoff_rows), use_container_width=True, hide_index=True)

with t4:
    st.header("🏆 Finals Summary")
    finals_data = load_finals()
    for v in ["PURPLE", "RED", "YELLOW", "BLACK", "GREEN", "WHITE"]:
        d = finals_data.get(v, {"s1":{}, "s2":{}, "f":{}, "w":[]})
        st.markdown(f'<div style="background-color:{COLOR_MAP.get(v, "#333")}; color:white; padding:10px; border-radius:5px; margin-top:20px;">{EMOJIS.get(v, "")} {v} BRACKET</div>', unsafe_allow_html=True)
        
        winners = d.get('w', [])
        if winners:
            cols = st.columns(len(winners))
            for i, team in enumerate(winners):
                with cols[i]:
                    st.markdown(f'<div style="text-align:center; padding:10px; border:1px solid #ddd; border-radius:5px;">{get_rank_str(i+1)}<br>{team}</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        for col, m_key, label in zip([c1, c2, c3], ['s1', 's2', 'f'], ['Semi 1', 'Semi 2', 'Finals']):
            m = d.get(m_key, {})
            with col:
                st.write(f"**{label}**")
                st.write(f"{m.get('t1','TBD')} ({m.get('sw1',0)})")
                st.write(f"{m.get('t2','TBD')} ({m.get('sw2',0)})")

with t5:
    st.header("⚙️ Admin Management")
    if st.text_input("Password", type="password") == ADMIN_PW:
        finals_data = load_finals()
        v = st.selectbox("Select Bracket", list(COLOR_MAP.keys()))
        d = finals_data.setdefault(v, {"s1":{'t1':'','t2':'','s1a':0,'s1b':0,'s2a':0,'s2b':0,'s3a':0,'s3b':0,'use_s3':False,'sw1':0,'sw2':0},
                                       "s2":{'t1':'','t2':'','s1a':0,'s1b':0,'s2a':0,'s2b':0,'s3a':0,'s3b':0,'use_s3':False,'sw1':0,'sw2':0},
                                       "f":{'t1':'','t2':'','s1a':0,'s1b':0,'s2a':0,'s2b':0,'s3a':0,'s3b':0,'use_s3':False,'sw1':0,'sw2':0},
                                       "w":[]})
        
        for match_id, label in [("s1", "Semi 1"), ("s2", "Semi 2"), ("f", "Finals")]:
            st.subheader(label)
            m = d[match_id]
            c1, c2, c3, c4 = st.columns([2,1,1,1])
            with c1:
                m['t1'] = st.text_input("Team 1", m.get('t1',''), key=f"t1_{match_id}_{v}")
                m['t2'] = st.text_input("Team 2", m.get('t2',''), key=f"t2_{match_id}_{v}")
            with c2:
                m['s1a'] = st.number_input("S1 T1", 0, 31, int(m.get('s1a',0)), key=f"s1a_{match_id}_{v}")
                m['s1b'] = st.number_input("S1 T2", 0, 31, int(m.get('s1b',0)), key=f"s1b_{match_id}_{v}")
            with c3:
                m['s2a'] = st.number_input("S2 T1", 0, 31, int(m.get('s2a',0)), key=f"s2a_{match_id}_{v}")
                m['s2b'] = st.number_input("S2 T2", 0, 31, int(m.get('s2b',0)), key=f"s2b_{match_id}_{v}")
            
            w1_t = (1 if m['s1a'] > m['s1b'] else 0) + (1 if m['s2a'] > m['s2b'] else 0)
            w2_t = (1 if m['s1b'] > m['s1a'] else 0) + (1 if m['s2b'] > m['s2a'] else 0)
            is_tie = (w1_t == 1 and w2_t == 1)
            with c4:
                m['use_s3'] = st.toggle("Set 3?", value=m.get('use_s3', False) if is_tie else False, key=f"s3tgl_{match_id}_{v}", disabled=not is_tie)
                m['s3a'] = st.number_input("S3 T1", 0, 31, int(m.get('s3a',0)), key=f"s3a_{match_id}_{v}", disabled=not m['use_s3'])
                m['s3b'] = st.number_input("S3 T2", 0, 31, int(m.get('s3b',0)), key=f"s3b_{match_id}_{v}", disabled=not m['use_s3'])
            if st.button(f"Save {label}", key=f"save_{match_id}_{v}"):
                m['sw1'] = w1_t + (1 if m['use_s3'] and m['s3a'] > m['s3b'] else 0)
                m['sw2'] = w2_t + (1 if m['use_s3'] and m['s3b'] > m['s3a'] else 0)
                save_finals(finals_data)
                st.rerun()

        st.subheader("Podium Standings")
        w_in = st.text_input("Winners (comma separated)", ",".join(d.get('w',[])), key=f"win_{v}")
        if st.button("Save Podium", key=f"p_btn_{v}"):
            d['w'] = [x.strip() for x in w_in.split(",") if x.strip()]
            save_finals(finals_data)
            st.rerun()
