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

# 2. Global Styling (Be Vietnam Pro)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;600;800&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, table, h1, h2, h3 {
        font-family: 'Be Vietnam Pro', sans-serif !important;
    }

    .m-table { width: 100%; border-collapse: collapse; margin-bottom: 25px; border-radius: 8px; overflow: hidden; }
    .m-table th { background-color: #f8f9fa; text-align: center !important; padding: 14px; border: 1px solid #dee2e6; font-weight: 800; color: #333; }
    .m-table td { text-align: center !important; padding: 12px; border: 1px solid #dee2e6; vertical-align: middle; }
    
    .high-stakes { background-color: #fffde7 !important; border: 2px solid #fbc02d !important; }
    
    .badge-semis { background: #eceff1; color: #455a64; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: 800; border: 1px solid #b0bec5; margin-right: 8px; display: inline-block; }
    .badge-finals { background: #fff9c4; color: #000; padding: 4px 10px; border-radius: 20px; font-size: 0.75em; font-weight: 800; border: 2px solid #fbc02d; margin-right: 8px; display: inline-block; }
    
    .status-pending { color: #adb5bd; font-style: italic; font-size: 0.85em; font-weight: 400; }

    .trademark { position: fixed; bottom: 12px; left: 50%; transform: translateX(-50%); font-size: 11px; color: #bbb; letter-spacing: 3px; z-index: 1000; text-align: center; width: 100%; font-weight: 300; }
</style>
<div class="trademark">POWERED BY J1</div>
""", unsafe_allow_html=True)

# 3. Fail-Safe Data Loading
@st.cache_data
def load_data(mtime):
    if not os.path.exists(FN): return None, {}, {}
    try:
        df = pd.read_csv(FN, header=None).fillna("")
        matches, team_colors, db = [], {}, {}
        day_context = "Day 1"
        
        # Block Mapping: [Time, Bracket, T1, T2, S1T1, S2T1, S1T2, S2T2]
        blocks = [[0,1,2,7,3,4,8,9], [13,14,15,20,16,17,21,22]]
        
        for idx, row in df.iterrows():
            row_str = " ".join([str(x) for x in row]).upper()
            if "DAY 2" in row_str: day_context = "Day 2"
            elif "DAY 1" in row_str: day_context = "Day 1"
            
            for c in blocks:
                try:
                    t1, t2 = str(row[c[2]]).strip(), str(row[c[3]]).strip()
                    bracket_raw = str(row[c[1]]).strip().upper()
                    if not bracket_raw: continue
                    
                    is_semis = "SEMIS" in bracket_raw
                    is_finals = "FINALS" in bracket_raw
                    
                    if not (is_semis or is_finals) and ("|" not in t1 or "|" not in t2):
                        continue
                    if t1 == "" or t2 == "": continue
                        
                    base_color = "WHITE"
                    for color_key in EMOJIS.keys():
                        if color_key in bracket_raw:
                            base_color = color_key
                            break
                    
                    court_val = "Court ?"
                    for r_scan in range(idx, -1, -1):
                        scan_text = str(df.iloc[r_scan, c[2]]).upper()
                        if "COURT" in scan_text:
                            court_val = scan_text.strip()
                            break
                    
                    m_id = f"{day_context[0]}{idx}{c[0]}"
                    matches.append({
                        "ID": m_id, "Day": day_context, "T": str(row[c[0]]).strip(), 
                        "T1": t1, "T2": t2, "P1": t1.replace("|", " AND "), "P2": t2.replace("|", " AND "),
                        "Bracket": bracket_raw, "Emoji": EMOJIS.get(base_color, "🏸"), 
                        "Court": court_val, "IsSemis": is_semis, "IsFinals": is_finals
                    })
                    
                    if "|" in t1: team_colors[t1] = base_color
                    if "|" in t2: team_colors[t2] = base_color
                    
                    scores = []
                    for col_idx in [c[4], c[5], c[6], c[7]]:
                        val = str(row[col_idx]).strip()
                        try:
                            scores.append(int(float(val)))
                        except:
                            scores.append(0)
                    
                    started = any(s > 0 for s in scores)
                    w1 = (scores[0] > scores[2]) + (scores[1] > scores[3])
                    w2 = (scores[2] > scores[0]) + (scores[3] > scores[1])
                    
                    db[m_id] = {
                        "s1": scores[0], "s2": scores[1], "s3": scores[2], "s4": scores[3],
                        "w1": w1, "w2": w2, "p1": scores[0]+scores[1], "p2": scores[2]+scores[3],
                        "started": started, "t1": t1, "t2": t2
                    }
                except: continue
        return pd.DataFrame(matches), team_colors, db
    except:
        return None, {}, {}

# 4. App UI Logic
st.title("🏸 GCCP SMASH S1 2026")
mtime = os.path.getmtime(FN) if os.path.exists(FN) else 0
sch, clrs, csv_db = load_data(mtime)

def get_rank_str(i):
    if i == 1: return "🥇 <b>1st</b>"
    if i == 2: return "🥈 <b>2nd</b>"
    if i == 3: return "🥉 <b>3rd</b>"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(i % 10, "th") if not 10 <= i % 100 <= 20 else "th"
    return f"{i}{suffix}"

if sch is None or sch.empty:
    st.error("Error loading CSV. Please check the file.")
else:
    st.session_state.db = csv_db
    tabs = st.tabs(["📊 Standings", "📅 Day 1", "📅 Day 2", "🏆 Finals", "⚙️ Admin"])

    def render_matches(df_slice, key):
        search = st.text_input(f"🔍 Search Matches", key=key).lower()
        rows = []
        for _, r in df_slice.iterrows():
            if search in r['T1'].lower() or search in r['T2'].lower() or search in r['Bracket'].lower():
                d = csv_db.get(r["ID"])
                badge, row_cls = "", ""
                if r['IsSemis']:
                    badge, row_cls = '<span class="badge-semis">🏆 SEMIS</span>', 'class="high-stakes"'
                elif r['IsFinals']:
                    badge, row_cls = '<span class="badge-finals">🥇 FINALS</span>', 'class="high-stakes"'
                
                if d and d['started']:
                    s1, s2 = f"{d['s1']}-{d['s3']}", f"{d['s2']}-{d['s4']}"
                else:
                    s1 = s2 = '<span class="status-pending">🕒 UPCOMING / IN PROGRESS</span>'
                
                rows.append(f"<tr {row_cls}><td>{r['Court']}</td><td>{r['T']}</td><td>{r['Emoji']} {r['Bracket']}</td><td>{badge}{r['P1']} <b>vs</b> {r['P2']}</td><td>{s1}</td><td>{s2}</td></tr>")
        
        if rows:
            st.write(f"<table class='m-table'><thead><tr><th>Court</th><th>Time</th><th>Bracket</th><th>Match</th><th>Set 1</th><th>Set 2</th></tr></thead><tbody>{''.join(rows)}</tbody></table>", unsafe_allow_html=True)

    with tabs[0]: # Standings
        df_stand = pd.DataFrame([{"Team":t, "B":c, "GP":0, "SW":0, "SL":0, "Pts":0} for t,c in clrs.items()])
        for v in st.session_state.db.values():
            for team_key, win_key, lose_key, pt_key in [('t1','w1','w2','p1'), ('t2','w2','w1','p2')]:
                if v.get(team_key) in clrs:
                    idx = df_stand.index[df_stand['Team']==v[team_key]][0]
                    df_stand.at[idx, 'GP'] += 1
                    df_stand.at[idx, 'SW'] += v[win_key]
                    df_stand.at[idx, 'SL'] += v[lose_key]
                    df_stand.at[idx, 'Pts'] += v[pt_key]
        
        for color in sorted(list(set(clrs.values()))):
            st.subheader(f"{color} Bracket")
            sdf = df_stand[df_stand["B"]==color].sort_values(["SW", "Pts"], ascending=False).reset_index(drop=True)
            sdf.insert(0, "Rank", [get_rank_str(i+1) for i in range(len(sdf))])
            st.write(sdf.drop(columns=["B"]).to_html(escape=False, index=False, classes="m-table"), unsafe_allow_html=True)

    with tabs[1]: render_matches(sch[sch["Day"] == "Day 1"].sort_values(["Court", "T"]), "q1")
    with tabs[2]: render_matches(sch[sch["Day"] == "Day 2"].sort_values(["Court", "T"]), "q2")
    with tabs[3]: st.info("Finals Bracket Management")
    with tabs[4]: 
        if st.text_input("Admin", type="password") == ADMIN_PW:
            if st.button("Reload Data"):
                st.cache_data.clear()
                st.rerun()
