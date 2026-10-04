"""Timeline / MAC Times — read, modify, and reconstruct file event timelines."""
import requests, streamlit as st, pandas as pd
from datetime import datetime

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Timeline · ForenShield", page_icon="⏱️", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
</style>""", unsafe_allow_html=True)

st.markdown("## ⏱️ Timeline & MAC Time Analyzer")
st.caption("Read/modify file timestamps · Directory timeline reconstruction · Timestomping")

tab1, tab2, tab3 = st.tabs(["🕐 Read MAC Times", "✏️ Modify Timestamps", "📅 Timeline Scan"])

# ── Tab 1: Read MAC ─────────────────────────────────────────────────────────────
with tab1:
    mac_path = st.text_input("File path", placeholder=r"C:\Windows\System32\cmd.exe")
    if st.button("Read MAC Times") and mac_path:
        try:
            r = requests.get(f"{API}/timeline/mac", params={"path": mac_path}, timeout=6)
            if r.status_code != 200:
                st.error(r.json().get("detail", "Error")); st.stop()
            d = r.json()
            c1, c2, c3 = st.columns(3)
            c1.metric("Modified (M)", d.get("mtime_iso","?")[:19])
            c2.metric("Accessed (A)", d.get("atime_iso","?")[:19])
            c3.metric("Created (C)",  d.get("ctime_iso","?")[:19])
            st.metric("File Size", f"{d.get('size',0):,} bytes")
        except Exception as ex:
            st.error(str(ex))

# ── Tab 2: Modify Timestamps ────────────────────────────────────────────────────
with tab2:
    st.warning("⚠️ Modifying timestamps is for forensic testing and research purposes only.")
    mod_path = st.text_input("Target file path", key="mod_path")
    col1, col2, col3 = st.columns(3)
    with col1:
        use_m = st.checkbox("Set Modified time")
        mtime_dt = st.date_input("M-date", key="mdt")
        mtime_tm = st.time_input("M-time", key="mtt")
    with col2:
        use_a = st.checkbox("Set Accessed time")
        atime_dt = st.date_input("A-date", key="adt")
        atime_tm = st.time_input("A-time", key="att")
    with col3:
        use_c = st.checkbox("Set Created time (Windows only)")
        ctime_dt = st.date_input("C-date", key="cdt")
        ctime_tm = st.time_input("C-time", key="ctt")

    if st.button("Apply Timestamps") and mod_path:
        payload = {"path": mod_path}
        if use_m:
            payload["mtime"] = datetime.combine(mtime_dt, mtime_tm).timestamp()
        if use_a:
            payload["atime"] = datetime.combine(atime_dt, atime_tm).timestamp()
        if use_c:
            payload["ctime"] = datetime.combine(ctime_dt, ctime_tm).timestamp()
        try:
            r = requests.post(f"{API}/timeline/mac", json=payload, timeout=6)
            if r.status_code == 200:
                d = r.json()
                st.success("Timestamps updated successfully!")
                st.json({"new_mtime": d.get("new_mtime"), "new_atime": d.get("new_atime"), "new_ctime": d.get("new_ctime")})
            else:
                st.error(r.json().get("detail","Error"))
        except Exception as ex:
            st.error(str(ex))

# ── Tab 3: Timeline Scan ────────────────────────────────────────────────────────
with tab3:
    scan_path = st.text_input("Directory to scan", value="C:\\Users", key="tl_path")
    col_a, col_b = st.columns(2)
    with col_a:
        start_dt = st.date_input("Start date (optional)", value=None, key="tl_start")
    with col_b:
        end_dt   = st.date_input("End date (optional)",   value=None, key="tl_end")
    tl_limit  = st.slider("Max events", 100, 5000, 1000, step=100)
    mac_filter = st.multiselect("MAC type", ["M","A","C"], default=["M","A","C"])

    if st.button("🔍 Build Timeline"):
        with st.spinner("Scanning directory timestamps..."):
            try:
                params = {"path": scan_path, "limit": tl_limit}
                if start_dt:
                    params["start"] = datetime.combine(start_dt, datetime.min.time()).timestamp()
                if end_dt:
                    params["end"]   = datetime.combine(end_dt,   datetime.max.time()).timestamp()
                r = requests.get(f"{API}/timeline/scan", params=params, timeout=60)
                if r.status_code != 200:
                    st.error(r.json().get("detail","Error")); st.stop()
                data = r.json()
                events = [e for e in data.get("events", []) if e.get("mac") in mac_filter]
                st.success(f"{data.get('total',0)} events found · showing {len(events)} after MAC filter")
                if events:
                    df = pd.DataFrame([{
                        "Time":  e.get("time",""),
                        "MAC":   e.get("mac",""),
                        "Type":  e.get("type",""),
                        "Name":  e.get("name",""),
                        "Size":  e.get("size",0),
                        "Path":  e.get("path",""),
                    } for e in events])
                    st.dataframe(df, use_container_width=True, hide_index=True,
                                 column_config={"MAC": st.column_config.TextColumn("", width="small")})
            except Exception as ex:
                st.error(str(ex))
