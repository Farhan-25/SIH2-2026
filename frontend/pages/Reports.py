"""Reports — generate and export forensic audit reports."""
import requests, streamlit as st, pandas as pd

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Reports · ForenShield", page_icon="📋", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
</style>""", unsafe_allow_html=True)

st.markdown("## 📋 Reports & Audit Logs")
st.caption("Generate comprehensive forensic reports · Export to text")

tab1, tab2 = st.tabs(["📄 Generated Reports", "➕ Create New Report"])

def fetch_reports():
    try:
        return requests.get(f"{API}/reports", timeout=5).json().get("reports", [])
    except:
        return []

# ── Tab 1: View / Export ────────────────────────────────────────────────────────
with tab1:
    if st.button("🔄 Refresh Reports"):
        st.rerun()
        
    reports = fetch_reports()
    if not reports:
        st.info("No reports generated yet.")
    else:
        df = pd.DataFrame(reports)[["id", "title", "case_number", "examiner", "status", "generated"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("**Report Actions**")
        r_id = st.selectbox("Select Report ID", [r["id"] for r in reports])
        
        if r_id:
            c1, c2 = st.columns(2)
            with c1:
                # Export button
                try:
                    export_res = requests.get(f"{API}/reports/{r_id}/export", timeout=5)
                    if export_res.status_code == 200:
                        st.download_button(
                            label="⬇️ Download Text Report",
                            data=export_res.text,
                            file_name=f"{r_id}.txt",
                            mime="text/plain"
                        )
                except Exception as ex:
                    st.error("Could not fetch export data.")
            with c2:
                if st.button("🗑️ Delete Report"):
                    requests.delete(f"{API}/reports/{r_id}")
                    st.rerun()

# ── Tab 2: Create ───────────────────────────────────────────────────────────────
with tab2:
    with st.form("create_report"):
        r_title = st.text_input("Report Title*")
        r_case = st.text_input("Case Number")
        r_exam = st.text_input("Examiner Name", value=st.session_state.get("settings", {}).get("examiner_name", "Unknown Examiner"))
        r_type = st.selectbox("Type", ["general", "incident", "malware", "compliance"])
        r_secs = st.multiselect("Include Sections", ["System Health", "Memory", "Network", "Disk", "Timeline", "Hashes", "Carved Files"])
        
        # Try to fetch evidence IDs
        try:
            evs = requests.get(f"{API}/evidence", timeout=2).json().get("items", [])
            ev_opts = [e["id"] for e in evs]
        except:
            ev_opts = []
            
        r_evids = st.multiselect("Link Evidence IDs", ev_opts)
        r_notes = st.text_area("Examiner Notes")
        
        if st.form_submit_button("Generate Report"):
            if r_title:
                payload = {
                    "title": r_title,
                    "case_number": r_case,
                    "examiner": r_exam,
                    "type": r_type,
                    "sections": r_secs,
                    "evidence_ids": r_evids,
                    "notes": r_notes
                }
                try:
                    r = requests.post(f"{API}/reports", json=payload, timeout=10)
                    if r.status_code == 200:
                        st.success(f"Report generated! ID: {r.json().get('id')}")
                    else:
                        st.error(r.json().get("detail", "Error"))
                except Exception as ex:
                    st.error(str(ex))
            else:
                st.warning("Title is required.")
