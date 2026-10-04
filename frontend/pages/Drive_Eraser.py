"""Drive Eraser — secure file erasure and free-space wiping."""
import requests, streamlit as st

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Drive Eraser · ForenShield", page_icon="🗑️", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
</style>""", unsafe_allow_html=True)

st.markdown("## 🗑️ Drive Eraser")
st.caption("Secure file erasure · Free-space wiping · DoD / Gutmann algorithms")

tab1, tab2, tab3 = st.tabs(["📄 Secure File Erase", "💽 Wipe Free Space", "☠️ Physical Drive Wipe"])

# ── Tab 1: File Eraser ──────────────────────────────────────────────────────────
with tab1:
    st.error("⚠️ **WARNING:** Files erased using these methods cannot be recovered.")
    
    e_path = st.text_input("Absolute path to file", placeholder=r"C:\Users\user\sensitive.docx")
    
    col1, col2 = st.columns(2)
    with col1:
        e_method = st.selectbox("Erasure Algorithm", 
                                ["dod", "gutmann", "random", "zeros"], 
                                format_func=lambda x: {
                                    "dod": "DoD 5220.22-M (Random)",
                                    "gutmann": "Gutmann (35-pass)",
                                    "random": "CSPRNG Random",
                                    "zeros": "Zero-fill"
                                }[x])
    with col2:
        e_passes = st.number_input("Number of passes", min_value=1, max_value=35, value=3)
        if e_method == "gutmann":
            st.info("Gutmann method overrides pass count to 35 internally.")
            
    if st.button("🔥 Permanently Erase File"):
        if e_path:
            with st.spinner(f"Securely erasing {e_path}..."):
                try:
                    r = requests.post(f"{API}/eraser/file", 
                                      json={"path": e_path, "method": e_method, "passes": e_passes}, 
                                      timeout=120)
                    if r.status_code == 200:
                        d = r.json()
                        st.success(f"Successfully erased: {e_path}")
                        st.json({
                            "size_bytes": d.get("size_bytes"),
                            "method": d.get("method"),
                            "passes": d.get("passes"),
                            "timestamp": d.get("timestamp")
                        })
                    else:
                        st.error(r.json().get("detail", "Error"))
                except Exception as ex:
                    st.error(str(ex))
        else:
            st.warning("Please provide a file path.")

# ── Tab 2: Free Space Wipe ──────────────────────────────────────────────────────
with tab2:
    st.info("Wiping free space prevents recovery of previously deleted files by overwriting unallocated sectors.")
    st.warning("⚠️ **CAUTION:** This operation will temporarily fill your drive to 100% capacity before deleting the temporary files. This can cause OS instability if performed on your primary C: drive.")
    
    w_drive = st.text_input("Drive or Mount Point", value="", placeholder="Z:\\ or /mnt/usb")
    w_passes = st.slider("Wipe Passes", 1, 3, 1)
    
    confirm_wipe = st.checkbox("I understand the risks and want to proceed")
    
    if st.button("🧹 Start Free Space Wipe"):
        if not confirm_wipe:
            st.error("You must check the confirmation box to proceed.")
        elif w_drive:
            try:
                r = requests.post(f"{API}/eraser/freespace", params={"drive": w_drive, "passes": w_passes}, timeout=5)
                if r.status_code == 200:
                    task_id = r.json().get("task_id")
                    st.success(f"Wipe task started! Task ID: `{task_id}`")
                    st.session_state["wipe_task_id"] = task_id
                else:
                    st.error(r.json().get("detail", "Error"))
            except Exception as ex:
                st.error(str(ex))
        else:
            st.warning("Please provide a drive.")
            
    st.divider()
    t_id = st.text_input("Monitor Task ID", value=st.session_state.get("wipe_task_id", ""))
    if t_id:
        try:
            r = requests.get(f"{API}/tasks/{t_id}", timeout=5)
            if r.status_code == 200:
                t = r.json()
                st.markdown(f"**Status:** `{t.get('status', 'unknown').upper()}`")
                prog = t.get('progress', 0)
                st.progress(prog, text=f"Progress: {prog}%")
            else:
                st.error("Task not found.")
        except Exception as ex:
            st.error(str(ex))

# ── Tab 3: Physical Drive Wipe ──────────────────────────────────────────────────
with tab3:
    st.error("🚨 **CRITICAL DANGER:** This module performs a raw block-level sector wipe on the physical drive. ALL partitions, file systems, and data will be IRRECOVERABLY DESTROYED.")
    st.markdown("> *Requires Administrator privileges on Windows (Raw Block Device Access).*")
    
    p_drive = st.text_input("Physical Block Device", value="", placeholder=r"\\.\PhysicalDrive1 or /dev/sdb")
    p_passes = st.slider("Raw Sectors Wipe Passes", 1, 3, 1)
    
    st.warning("Type 'DESTROY' below to confirm you want to obliterate this drive.")
    p_confirm = st.text_input("Confirmation")
    
    if st.button("☠️ OBLITERATE PHYSICAL DRIVE"):
        if p_confirm != "DESTROY":
            st.error("Confirmation string must match exactly: DESTROY")
        elif p_drive:
            try:
                r = requests.post(f"{API}/eraser/physical", params={"drive": p_drive, "passes": p_passes}, timeout=5)
                if r.status_code == 200:
                    task_id = r.json().get("task_id")
                    st.success(f"Physical Drive Wipe initiated! Task ID: `{task_id}`")
                    st.session_state["pwipe_task_id"] = task_id
                else:
                    st.error(r.json().get("detail", "Error"))
            except Exception as ex:
                st.error(str(ex))
        else:
            st.warning("Please provide a physical drive path.")
            
    st.divider()
    pt_id = st.text_input("Monitor Physical Wipe Task", value=st.session_state.get("pwipe_task_id", ""))
    if pt_id:
        try:
            r = requests.get(f"{API}/tasks/{pt_id}", timeout=5)
            if r.status_code == 200:
                t = r.json()
                st.markdown(f"**Status:** `{t.get('status', 'unknown').upper()}`")
                prog = t.get('progress', 0)
                st.progress(prog, text=f"Sector Overwrite Progress: {prog}%")
            else:
                st.error("Task not found.")
        except Exception as ex:
            st.error(str(ex))
