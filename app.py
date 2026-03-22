import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="SMASH 2026", layout="wide")

@st.cache_data
def load_data():
    if not os.path.exists("SMASH 2026 - Score Tracker.csv"): return None
    df = pd.read_csv("SMASH 2026 - Score Tracker.csv")
    m = []
    cfgs = [{"n":"C1","r":(1,10),"c":1},{"n":"C2","r":(1,10),"c":13},{"n":"C3","r":(13,22),"c":1},{"n":"C4","r":(13,22),"c":13},{"n":"C5","r":(25,34),"c":1},{"n":"C6","r":(25,34),"c":13},{"n":"C7","r":(37,46),"c":1},{"n":"C8","r":(37,46),"c":13}]
    for c in cfgs:
        for i in range(c["r"][0], c["r"][1]):
            try:
                t1, t2 = str(df.iloc[i,c["c"]]).strip(), str(df.iloc[i,c["c"]+5]).strip()
                tm = str(df.iloc[i, 0 if c["c"]==1 else 12]).strip()
                if "|" in t1: m.append({"ID":f"{c['n']} | {tm} | {t1} vs {t2}","T1":t1,"T2":t2})
            except: continue
    return pd.DataFrame(m)

B = {
    "PURPLE": ["WENDY | WYNETTE","DAVID | JOSZEF","ALLAN | AALIYAH","KIM | BEVERLY","MATTHEW | LANCE","ZBIGNIEF | DELFZIJL","WYATT | MACKINZIE"],
    "PINK": ["KYLE | ABIGAIL","BENEDICK | ROBENSON","DANNY | ANDREA","BRYCE | MATTHEW","JETHRO | IVAN","Szczeinfjord | DARRYL","KAELYN | GENEVIEVE"],
    "ORANGE": ["JERICHO | JOHN","ENZO | SETH","MARSTON | MARCUS","JULIO | STEVE","SETH | ENZO","JOHANN | ANTHONY","ERVIN | KYLE","SPENCER | LUCAS","JANELLE | BEA"],
    "BLUE": ["RAINIER | MICHAEL","SHAWN | NATHAN","VICTOR | CHARLES","CELINE | CARLSON","APOL | TRISTEN","TIMOTHY | JORDAN","KATE | JEAN","KELLY | COLLIN"],
    "YELLOW": ["JOANNA | KELWIN","RIANA | RINAN","HANS | JARED","JOHNSEN | ELISHA","WILBERT | KRISTIN","JUSTIN | BRANSON","HARVEY | GAB"],
    "GREEN": ["BRENT | JEEVAN","JYRELL | SEAN","KATHERINE | GINA","HART | CHANTELLE","CHRISTIAN | JOHN","MATTHEW | KALVIN","JOHN | CHARLENE","LAURENCE | JAQUELINE"]
}

def get_c(n):
    n = str(n).strip().upper()
    for k,v in B.items():
        if any(n == x.strip().upper() for x in v): return k
    return "WHITE"

st.title("🏸 SMASH 2026 Score Tracker")
sch = load_data()

if sch is None: st.error("CSV Missing")
else:
    if 'db' not in st.session_state: st.session_state.db = {}
    tab1, tab2 = st.tabs(["📊 Leaderboard", "📝 Input"])
    with tab2:
        sel = st.selectbox("Match", sch["ID"].tolist())
        d = sch[sch["ID"]==sel].iloc[0]
        c1, c2 = st.columns(2)
        s1t1 = c1.number_input(f"S1 {d['T1']}", 0, 21)
        s2t1 = c1.number_input(f"S2 {d['T1']}", 0, 21)
        s1t2 = c2.number_input(f"S1 {d['T2']}", 0, 21)
        s2t2 = c2.number_input(f"S2 {d['T2']}", 0, 21)
        if st.button("Save"):
            w1, w2 = (1 if s1t1>s1t2 else 0)+(1 if s2t1>s2t2 else 0), (1 if s1t2>s1t1 else 0)+(1 if s2t2>s2t1 else 0)
            st.session_state.db[sel] = {"t1":d['T1'],"t2":d['T2'],"p1":s1t1+s2t1,"p2":s1t2+s2t2,"w1":w1,"l1":w2,"w2":w2,"l2":w1}
            st.success("Saved")
    with tab1:
        teams = sorted(list(set(sch["T1"]).union(set(sch["T2"]))))
        res = {t: {"Bracket":get_c(t), "Won":0, "Lost":0, "Pts":0} for t in teams}
        for v in st.session_state.db.values():
            for i in [1,2]:
                res[v[f't{i}']]["Won"]+=v[f'w{i}']; res[v[f't{i}']]["Lost"]+=v[f'l{i}']; res[v[f't{i}']]["Pts"]+=v[f'p{i}']
        df = pd.DataFrame.from_dict(res, orient='index').reset_index()
        df.columns = ["Team","Bracket","Won","Lost","Pts"]
        df = df.sort_values(["Bracket","Won","Pts"], ascending=[True,False,False])
        st.table(df.style.apply(lambda r: [f"background-color: {r['Bracket'].lower()}"]*5, axis=1))
