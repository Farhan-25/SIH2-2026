"""Hex Viewer — server-side paginated hex dump and pattern search."""
import requests, streamlit as st

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Hex Viewer · ForenShield", page_icon="🔬", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
.hex-byte { color: #e2e8f0; font-family: monospace; margin: 0 4px; }
.hex-ascii { color: #94a3b8; font-family: monospace; white-space: pre; }
.hex-offset { color: #6366f1; font-family: monospace; margin-right: 16px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

st.markdown("## 🔬 Hex Viewer")
st.caption("Paginated hex dump · Magic detection · Pattern search")

tab1, tab2 = st.tabs(["📄 Hex Dump", "🔍 Search"])

# ── Tab 1: Hex Dump ─────────────────────────────────────────────────────────────
with tab1:
    h_path   = st.text_input("File path", placeholder=r"C:\Windows\System32\cmd.exe", key="h_path")
    
    col1, col2 = st.columns(2)
    with col1:
        offset = st.number_input("Offset (bytes)", min_value=0, value=0, step=4096)
    with col2:
        length = st.number_input("Bytes to read", min_value=16, max_value=65536, value=4096, step=4096)
        
    if st.button("Read Hex Dump") and h_path:
        with st.spinner("Reading file..."):
            try:
                r = requests.get(f"{API}/hex/read", 
                                 params={"path": h_path, "offset": offset, "length": length}, 
                                 timeout=10)
                if r.status_code != 200:
                    st.error(r.json().get("detail", "Error")); st.stop()
                d = r.json()
                
                m1, m2, m3 = st.columns(3)
                m1.metric("File Size", f"{d.get('file_size',0):,} bytes")
                m2.metric("Magic", d.get("magic") or "N/A")
                m3.metric("Entropy", f"{d.get('entropy',0):.4f}" if d.get("entropy") else "N/A")
                
                st.divider()
                html = "<div style='background:#12141c; padding:16px; border-radius:8px; overflow-x:auto;'>"
                for row in d.get("rows", []):
                    bytes_str = " ".join([f"<span class='hex-byte'>{b}</span>" for b in row["bytes"]])
                    # Pad bytes if less than 16
                    if len(row["bytes"]) < 16:
                        bytes_str += " " * (3 * (16 - len(row["bytes"])))
                    ascii_str = "".join(row["ascii"]).replace("<", "&lt;").replace(">", "&gt;")
                    html += f"<div><span class='hex-offset'>{row['offset']}</span> {bytes_str} &nbsp;&nbsp;&nbsp; <span class='hex-ascii'>{ascii_str}</span></div>"
                html += "</div>"
                
                st.markdown(html, unsafe_allow_html=True)
            except Exception as ex:
                st.error(str(ex))

# ── Tab 2: Pattern Search ───────────────────────────────────────────────────────
with tab2:
    s_path = st.text_input("File path", placeholder=r"C:\Windows\System32\cmd.exe", key="s_path")
    c1, c2, c3 = st.columns(3)
    with c1:
        s_pattern = st.text_input("Pattern")
    with c2:
        s_mode = st.selectbox("Mode", ["hex", "ascii"])
    with c3:
        s_limit = st.number_input("Max matches", min_value=1, value=50)
        
    if st.button("Search") and s_path and s_pattern:
        with st.spinner("Searching file..."):
            try:
                r = requests.get(f"{API}/hex/search", 
                                 params={"path": s_path, "pattern": s_pattern, "mode": s_mode, "limit": s_limit}, 
                                 timeout=30)
                if r.status_code != 200:
                    st.error(r.json().get("detail", "Error")); st.stop()
                d = r.json()
                
                matches = d.get("matches", [])
                st.success(f"Found {len(matches)} matches")
                if matches:
                    st.code("\n".join(matches))
            except Exception as ex:
                st.error(str(ex))
