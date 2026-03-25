import streamlit as st
import pandas as pd
import os
import json

# 1. Page Configuration
st.set_page_config(page_title="GCCP SMASH S1 2026", layout="wide")

# File Constants
FN = "SMASH 2026 - Score Tracker.csv"
SAVE_FN = "finals_data.json"
ADMIN_PW = "pogisiJordan"

# UI Constants
EMOJIS = {"BLACK": "⚫", "RED": "🔴", "GREEN": "🟢", "PURPLE": "🟣", "WHITE": "⚪", "YELLOW": "🟡"}
COLOR_MAP = {
    "BLACK": "#000000", "RED": "#d32f2f", "GREEN": "#2e7d32", 
    "PURPLE": "#7b1fa2", "WHITE": "#9e9e9e", "YELLOW": "#fbc02d"
}

# 2. Helper Functions
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

# 3. Enhanced Data Loading
@st.cache_data
def load_data(mtime):
    if not os.path.exists(FN): return None, {}, {}
    try:
        df = pd.read_csv(FN, header=None).fillna("")
        matches, team_colors, db = [], {}, {}
        day_context = "Day 1"
        
        # Block definitions based on your CSV layout
        # c[0]:Time, c[1]:Bracket, c[2]:T1, c[3]:T2, c[4]:S1T1, c[5]:S2T1, c[6]:S1T2, c[7]:S2T2
        blocks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
        
        for idx, row in df.iterrows():
            row_str = " ".join([str(x) for x in row]).upper()
            if "DAY 2" in row_str: day_context = "Day 2"
            elif "DAY 1" in row_str: day_context = "Day 1"
            
            for c in blocks:
                try:
                    t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                    bracket_raw = str(row[c[1]]).strip().upper()
                    
                    # Logic: Accept if it's a paired match (|) OR a special bracket (SEMIS/FINALS)
                    is_special = any(word in bracket_raw for word in ["SEMIS", "FINALS"])
                    if not is_special and ("|" not in t1 or "|" not in t2):
                        continue
                    if t1 == "" or t2 == "": continue
                        
                    # Map base color for styling
                    base_color = "WHITE"
                    for color_key in EMOJIS.keys():
                        if color_key in bracket_raw:
                            base_color = color_key
                            break
                    
                    time_val = str(row[c[0]]).strip()
                    emoji = EMOJIS.get(base_color, "🏸")
                    
                    # Court Detection (Scan upwards for "Court X" label)
                    court_val = "Court ?"
                    for r_scan in range(idx, -1, -1):
                        scan_text = str(df.iloc[r_scan, c[2]]).upper()
                        if "COURT" in scan_text:
                            court_val = scan_text.strip()
                            break
                    
                    p1_display = t1.replace("|", " AND ")
                    p2_display = t2.replace("|", " AND ")
                    m_id = f"{day_context[0]}{idx}{c[0]}"
                    
                    matches.append({
                        "ID": m_id, "Day": day_context, "T": time_val, "T1": t1, "T2": t2, 
                        "P1": p1_display, "P2": p2_display, "Bracket": bracket_raw, 
                        "BaseColor": base_color, "Emoji": emoji, "Court": court_val,
                        "IsSpecial": is_special
                    })
                    
                    # Track colors for standings (only for real teams)
                    if "|" in t1: team_colors[t1] = base_color
                    if "|" in t2: team_colors[t2] = base_color
                    
                    # Score Parsing
                    sc = [int(float(row[col])) if str(row[col]).strip().replace('.','',1).isdigit() else 0 for col in [c[4], c[5], c[6], c[7]]]
                    w1 = (sc[0] > sc[2]) + (sc[1] > sc[3])
                    w2 = (sc[2] > sc[0]) + (sc[3] > sc[1])
                    db[m_id] = {"s1":sc[0], "s2":sc[1], "s3":sc[2], "s4":sc[3], "t1":t1, "t2":t2, "w1":w1, "w2":w2, "p1":sc[0]+sc[1], "p2":sc[2]+sc[3]}
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except Exception as e:
        return None, {}, {}

# 4. Styling & Custom Components
st.markdown("""
<style>
    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; font-family: sans-serif; }
    .m-table th { background-color: #f0f2f6; text-align: center !important; padding: 12px; border: 1px solid #ddd; }
    .m-table td { text-align: center !important; padding: 10px; border: 1px solid #ddd; }
    
    .high-stakes { background-color: #fffde7 !important; border: 2px solid #fbc02d !important; font-weight: bold; }
    .badge-special { background: #fbc02d; color: #000; padding: 2px 8px; border-radius: 12px; font-size: 0.7em; font-weight: 800; border: 1px solid #000; margin-right: 5px; }
    
    .trademark { position: fixed; bottom: 10px; left: 50%; transform: translateX(-50%); font-size: 10px; color: #999; letter-spacing: 2px; z-index: 1000; text-align: center; width: 100%; }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

st.title("🏸 GCCP SMASH S1 2026")

# 5. Main Execution
mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(mtime)

if sch is None or sch.empty:
    st.error("Could not load schedule. Check if the CSV file is in the folder.")
else:
    st.session_state.db = csv_db
    if 'finals' not in st.session_state: st.session_state.finals = load_finals()
    
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    # --- STANDINGS ---
    with tabs[0]:
        stats = {t:{"Bracket":clrs.get(t,"?"), "GP":0, "SW":0, "SL":0, "Pts":0} for t in sorted(clrs.keys())}
        for v in st.session_state.db.values():
            if v['t1'] in stats:
                stats[v['t1']]["GP"]+=1; stats[v['t1']]["SW"]+=v['w1']; stats[v['t1']]["SL"]+=v['w2']; stats[v['t1']]["Pts"]+=v['p1']
            if v['t2'] in stats:
                stats[v['t2']]["GP"]+=1; stats[v['t2']]["SW"]+=v['w2']; stats[v['t2']]["SL"]+=v['w1']; stats[v['t2']]["Pts"]+=v['p2']
        
        df_stand = pd.DataFrame.from_dict(stats, orient='index').reset_index().rename(columns={'index':'Team'})
        for color in sorted(list(set(clrs.values()))):
            st.subheader(f"{EMOJIS.get(color, '🏆')} {color} Bracket")
            sdf = df_stand[df_stand["Bracket"]==color].sort_values(["SW", "Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["Bracket"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    # --- DAY 1 ---
    with tabs[1]:
        q1 = st.text_input("🔍 Search Day 1", key="q1").lower()
        d1_df = sch[sch["Day"] == "Day 1"].copy().sort_values(by=["Court", "T"])
        rows1 = []
        for _, r in d1_df.iterrows():
            if q1 in r['T1'].lower() or q1 in r['T2'].lower():
                d = csv_db.get(r["ID"])
                s1, s2 = (f"{d['s1']}-{d['s3']}", f"{d['s2']}-{d['s4']}") if d else ("--", "--")
                rows1.append(f"<tr><td>{r['Court']}</td><td>{r['T']}</td><td>{r['Emoji']} {r['Bracket']}</td><td>{r['P1']} vs {r['P2']}</td><td>{s1}</td><td>{s2}</td></tr>")
        st.write(f"<table class='m-table'><thead><tr><th>Court</th><th>Time</th><th>Bracket</th><th>Match</th><th>Set 1</th><th>Set 2</th></tr></thead><tbody>{''.join(rows1)}</tbody></table>", unsafe_allow_html=True)

    # --- DAY 2 ---
    with tabs[2]:
        q2 = st.text_input("🔍 Search Day 2", key="q2").lower()
        d2_df = sch[sch["Day"] == "Day 2"].copy().sort_values(by=["Court", "T"])
        rows2 = []
        for _, r in d2_df.iterrows():
            if q2 in r['T1'].lower() or q2 in r['T2'].lower() or q2 in r['Bracket'].lower():
                row_cls = 'class="high-stakes"' if r['IsSpecial'] else ""
                badge = '<span class="badge-special">🏆 ELIMINATION</span>' if r['IsSpecial'] else ""
                d = csv_db.get(r["ID"])
                s1, s2 = (f"{d['s1']}-{d['s3']}", f"{d['s2']}-{d['s4']}") if d else ("--", "--")
                rows2.append(f"<tr {row_cls}><td>{r['Court']}</td><td>{r['T']}</td><td>{r['Emoji']} {r['Bracket']}</td><td>{badge} {r['P1']} vs {r['P2']}</td><td>{s1}</td><td>{s2}</td></tr>")
        st.write(f"<table class='m-table'><thead><tr><th>Court</th><th>Time</th><th>Bracket</th><th>Match</th><th>Set 1</th><th>Set 2</th></tr></thead><tbody>{''.join(rows2)}</tbody></table>", unsafe_allow_html=True)

    # --- FINALS (Admin/Manual Input View) ---
    with tabs[3]:
        st.info("Manual Finals Tracker - Select a bracket to view elimination status.")
        # Logic for the custom tournament tree/manual input can be expanded here...

    # --- ADMIN ---
    with tabs[4]:
        if st.text_input("Admin Access", type="password") == ADMIN_PW:
            if st.button("Clear Cache & Reload CSV"):
                st.cache_data.clear()
                st.rerun()
