import streamlit as st
import pandas as pd
import os

# 1. Setup & Score Fix
st.set_page_config(
    page_title="SMASH 2026",
    layout="wide"
)
F = "SMASH 2026 - Score Tracker.csv"
EM = {
    "BLACK": "⚫", "RED": "🔴", 
    "GREEN": "🟢", "PURPLE": "🟣", 
    "WHITE": "⚪", "YELLOW": "🟡"
}

def cln(v):
    """Fixes the 210-160 glitch"""
    s = str(v)
    c = "".join(filter(str.isdigit, s))
    return int(c) if c else 0

def rk(i):
    if i == 1: return "🥇 1st"
    if i == 2: return "🥈 2nd"
    if i == 3: return "🥉 3rd"
    return f"{i}th"

# 2. Data Logic
@st.cache_data
def ld():
    if not os.path.exists(F): 
        return None, {}, {}
    df = pd.read_csv(F, header=None)
    df = df.fillna("")
    m, cl, db, dy = [], {}, {}, "Day 1"
    bk = [
        [0,1,2,7,3,4,8,9], 
        [13,14,15,20,16,17,21,22]
    ]

    for idx, r in df.iterrows():
        ts = " ".join(map(str, r))
        ts = ts.upper()
        if "DAY 2" in ts: dy = "Day 2"
        elif "DAY 1" in ts: dy = "Day 1"
        for c in bk:
            v1 = str(r[c[2]])
            t1 = v1.strip()
            v2 = str(r[c[3]])
            t2 = v2.strip()
            if "|" not in t1: continue
            L = str(r[c[1]]).upper()
            tm = str(r[c[0]])
            p1 = t1.replace("|","&")
            p2 = t2.replace("|","&")
            
            ct = "Court ?"
            for p in range(idx, -1, -1):
                v_s = df.iloc[p]
                f = False
                for x in v_s:
                    if "COURT" in str(x).upper():
                        ct = str(x).strip()
                        f = True; break
                if f: break

            id = f"{dy}{ct}{tm}{p1}"
            m.append({
                "ID":id, "Dy":dy, "T":tm, 
                "P1":p1, "P2":p2, "T1":t1, 
                "L":L, "C":ct
            })
            cl[t1] = cl[t2] = L
            
            # THE SCORE FIX
            s = []
            for k in [4,5,6,7]:
                s.append(cln(r[c[k]]))
            w1 = (s[0]>s[2])+(s[1]>s[3])
            w2 = (s[2]>s[0])+(s[3]>s[1])
            db[id] = {
                "s1":s[0], "s2":s[1], 
                "s3":s[2], "s4":s[3],
                "t1":t1, "t2":t2, 
                "w1":w1, "w2":w2
            }
    return pd.DataFrame(m), cl, db

# 3. Execution
st.title(
    "🏸 SMASH 2026"
)
dt, cls, d_b = ld()

st.markdown("""<style>
    .m-t { width: 100%; border-collapse: collapse; }
    .m-t td { text-align: center; border: 1px solid #ddd; }
</style>""", unsafe_allow_html=True)

if dt is not None:
    t_1, t_2 = st.tabs(["📊 Rank", "📅 List"])
    with t_1:
        st.write("### Standings")
        stat = {t:{"B":cls[t],"W":0} for t in cls}
        for v in d_b.values():
            if v['t1'] in stat: 
                stat[v['t1']]["W"] += v['w1']
            if v['t2'] in stat: 
                stat[v['t2']]["W"] += v['w2']
        df_r = pd.DataFrame.from_dict(stat, "index")
        df_r = df_r.reset_index()
        for b in sorted(df_r["B"].unique()):
            st.write(f"#### {EM.get(b,'🏆')} {b}")
            sdf = df_r[df_r["B"]==b]
            sdf = sdf.sort_values("W", ascending=False)
            st.table(sdf)
    with t_2:
        dy_p = st.radio("D", ["Day 1", "Day 2"])
        sh = st.text_input("🔍 Search").lower()
        rows = []
        for _, r in dt[dt["Dy"] == dy_p].iterrows():
            if sh and sh not in r['P1'].lower(): 
                continue
            d = d_b.get(r["ID"])
            s1 = f"{d['s1']}-{d['s3']}" if d else "--"
            s2 = f"{d['s2']}-{d['s4']}" if d else "--"
            rows.append({
                "Time": r["T"], "Match": r["P1"]+" vs "+r["P2"],
                "S1": s1, "S2": s2, "W": f"{d['w1']}-{d['w2']}"
            })
        if rows: st.write(pd.DataFrame(rows).to_html(
            escape=False, index=False, classes="m-t"
        ), unsafe_allow_html=True)
