"""Settings — configure forensic tools and preferences."""
import requests, streamlit as st

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Settings · ForenShield", page_icon="⚙️", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
</style>""", unsafe_allow_html=True)

st.markdown("## ⚙️ Settings")
st.caption("Configure ForenShield platform preferences")

def fetch_settings():
    try:
        return requests.get(f"{API}/settings", timeout=3).json()
    except:
        return {}

cfg = fetch_settings()

if not cfg:
    st.error("Could not load settings from backend.")
    st.stop()

with st.form("settings_form"):
    st.subheader("Examiner Profile")
    ex_name = st.text_input("Examiner Name", value=cfg.get("examiner_name", ""))
    agency = st.text_input("Agency / Organization", value=cfg.get("agency", ""))
    case = st.text_input("Default Case Number", value=cfg.get("case_number", ""))
    
    st.subheader("Global Preferences")
    theme = st.selectbox("Theme", ["dark", "light"], index=0 if cfg.get("theme") == "dark" else 1)
    auto_v = st.checkbox("Auto-verify evidence on add", value=cfg.get("auto_verify", True))
    telemetry = st.checkbox("Enable anonymous telemetry", value=cfg.get("enable_telemetry", False))
    
    st.subheader("Analysis Limits")
    pcap_max = st.number_input("Max PCAP Packets (Scapy)", value=cfg.get("pcap_max_packets", 500))
    hex_bpr = st.number_input("Hex Viewer Bytes Per Row", value=cfg.get("hex_bytes_per_row", 16))
    
    col1, col2 = st.columns(2)
    with col1:
        submit = st.form_submit_button("💾 Save Settings")
    with col2:
        reset = st.form_submit_button("⚠️ Reset to Defaults")

if submit:
    payload = {
        "examiner_name": ex_name,
        "agency": agency,
        "case_number": case,
        "theme": theme,
        "auto_verify": auto_v,
        "enable_telemetry": telemetry,
        "pcap_max_packets": pcap_max,
        "hex_bytes_per_row": hex_bpr
    }
    try:
        r = requests.put(f"{API}/settings", json=payload, timeout=5)
        if r.status_code == 200:
            st.success("Settings saved successfully!")
            st.session_state["settings"] = r.json().get("settings")
            st.rerun()
    except Exception as ex:
        st.error(str(ex))

if reset:
    try:
        r = requests.post(f"{API}/settings/reset", timeout=5)
        if r.status_code == 200:
            st.success("Reset to defaults.")
            st.rerun()
    except Exception as ex:
        st.error(str(ex))
