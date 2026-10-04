"""File Recovery — trigger background carving and view progress."""
import time
import requests, streamlit as st, pandas as pd

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="File Recovery · ForenShield", page_icon="📂", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
</style>""", unsafe_allow_html=True)

st.markdown("## 📂 File Recovery / Carving")
st.caption("Forensic file carving · Signature-based recovery")

@st.cache_data
def get_signatures():
    try:
        return requests.get(f"{API}/recovery/signatures", timeout=5).json().get("signatures", [])
    except:
        return []

sigs = get_signatures()
sig_exts = [s["ext"] for s in sigs] if sigs else ["jpg", "png", "pdf", "zip", "exe"]

tab1, tab2 = st.tabs(["🛠️ Start Carving", "📈 Active Tasks"])

# ── Tab 1: Start Carving ────────────────────────────────────────────────────────
with tab1:
    c_src = st.text_input("Source Path (Disk Image or Partition)", placeholder=r"C:\image.dd")
    c_out = st.text_input("Output Directory", placeholder=r"C:\RecoveredFiles")
    c_ext = st.multiselect("File types to recover (leave empty for all)", sig_exts)
    
    st.markdown("### Advanced Options")
    c_adv = st.checkbox("🧩 Enable Advanced Fragmented File Reconstruction (Slower but higher recovery rate)")
    
    if st.button("🚀 Start Carving Job"):
        if c_src and c_out:
            try:
                r = requests.post(f"{API}/recovery/carve", 
                                  json={"source_path": c_src, "output_dir": c_out, "file_types": c_ext, "advanced": c_adv}, 
                                  timeout=5)
                if r.status_code == 200:
                    task_id = r.json().get("task_id")
                    st.success(f"Carving started! Task ID: `{task_id}`")
                    st.session_state["carve_task_id"] = task_id
                else:
                    st.error(r.json().get("detail", "Error"))
            except Exception as ex:
                st.error(str(ex))
        else:
            st.warning("Please provide source and output paths.")

    if sigs:
        with st.expander("View supported signatures"):
            st.dataframe(pd.DataFrame(sigs), hide_index=True)

# ── Tab 2: Active Tasks ─────────────────────────────────────────────────────────
with tab2:
    t_id = st.text_input("Task ID to monitor", value=st.session_state.get("carve_task_id", ""))
    auto_poll = st.checkbox("🔄 Auto-poll (2s)")
    
    if t_id:
        try:
            r = requests.get(f"{API}/recovery/carve/{t_id}", timeout=5)
            if r.status_code == 200:
                t = r.json()
                
                st.markdown(f"**Status:** `{t.get('status', 'unknown').upper()}`")
                prog = t.get('progress', 0)
                st.progress(prog, text=f"Progress: {prog}%")
                
                c1, c2 = st.columns(2)
                c1.metric("Sectors Scanned", f"{t.get('sectors_scanned',0):,}")
                
                found = t.get("found", [])
                c2.metric("Files Recovered", len(found))
                
                if found:
                    st.markdown("**Recovered Files:**")
                    st.dataframe(pd.DataFrame(found)[["name", "type", "ext", "size_fmt", "sector", "confidence"]], 
                                 use_container_width=True, hide_index=True)
                
                log = t.get("log", [])
                if log:
                    st.markdown("**Log:**")
                    log_text = "\n".join([f"[{l['time']}] {l['type'].upper()} - {l['msg']}" for l in log[-10:]])
                    st.code(log_text)
                    
            else:
                st.error("Task not found or error")
        except Exception as ex:
            st.error(str(ex))
            
    if auto_poll and t_id:
        time.sleep(2)
        st.rerun()
