"""Disk Analyzer — partitions, I/O stats, directory tree, large file finder."""
import requests, streamlit as st, pandas as pd

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Disk Analyzer · ForenShield", page_icon="💽", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
</style>""", unsafe_allow_html=True)

st.markdown("## 💽 Disk Analyzer")
st.caption("Partitions · I/O counters · Directory tree scanner · Large file finder")

tab1, tab2, tab3 = st.tabs(["📊 Partitions", "🌳 Directory Scanner", "🔎 Large File Finder"])

# ── Tab 1: Partitions ───────────────────────────────────────────────────────────
with tab1:
    if st.button("🔄 Load Partitions"):
        with st.spinner("Reading disk info..."):
            try:
                r    = requests.get(f"{API}/disk/partitions", timeout=6)
                data = r.json()
                parts = data.get("partitions", [])
                io    = data.get("io", {})

                ioc1, ioc2, ioc3, ioc4 = st.columns(4)
                ioc1.metric("Disk Read",   f"{io.get('read_mb',0):,.1f} MB")
                ioc2.metric("Disk Write",  f"{io.get('write_mb',0):,.1f} MB")
                ioc3.metric("Read Ops",    f"{io.get('read_ops',0):,}")
                ioc4.metric("Write Ops",   f"{io.get('write_ops',0):,}")

                st.divider()
                for p in parts:
                    pct = p.get("usedPct", 0)
                    c = "🟢" if pct < 70 else ("🟡" if pct < 90 else "🔴")
                    with st.expander(f"{c} {p['name']} ({p['fs']}) — {p['mount']}"):
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total", f"{p.get('total_gb',0):.2f} GB")
                        col2.metric("Used",  f"{p.get('used_gb',0):.2f} GB")
                        col3.metric("Free",  f"{p.get('free_gb',0):.2f} GB")
                        st.progress(int(pct), text=f"Used: {pct:.1f}%")
                        st.caption(f"Options: {p.get('opts','?')}")
            except Exception as ex:
                st.error(str(ex))

# ── Tab 2: Directory Tree ───────────────────────────────────────────────────────
with tab2:
    scan_path  = st.text_input("Directory to scan", value="C:\\", key="scan_path")
    scan_depth = st.slider("Depth", 1, 5, 2)
    if st.button("🌳 Scan Directory"):
        with st.spinner(f"Scanning {scan_path}..."):
            try:
                r    = requests.get(f"{API}/disk/scan",
                                    params={"path": scan_path, "depth": scan_depth}, timeout=30)
                tree = r.json()
                if "detail" in tree:
                    st.error(tree["detail"]); st.stop()

                def _render(node, level=0):
                    prefix = "  " * level
                    icon   = "📁" if node.get("children") else "📄"
                    sz     = f"{node.get('size_mb', node.get('size',0)/1024**2):.1f} MB"
                    st.markdown(f"`{prefix}{icon} {node['name']}`  —  {sz}  ({node.get('files',0)} files)")
                    for child in node.get("children", [])[:20]:
                        _render(child, level + 1)

                st.markdown(f"**Root:** `{tree.get('path', scan_path)}` — {tree.get('files',0)} files — {tree.get('size_mb', 0):.1f} MB")
                for child in tree.get("children", []):
                    _render(child)
            except Exception as ex:
                st.error(str(ex))

# ── Tab 3: Large File Finder ────────────────────────────────────────────────────
with tab3:
    lf_path   = st.text_input("Search root", value="C:\\", key="lf_path")
    lf_top    = st.slider("Max results", 10, 100, 50)
    lf_min_mb = st.number_input("Min file size (MB)", min_value=1.0, value=10.0, step=1.0)

    if st.button("🔎 Find Large Files"):
        with st.spinner("Scanning for large files..."):
            try:
                r = requests.get(f"{API}/disk/large-files",
                                 params={"path": lf_path, "top": lf_top, "min_mb": lf_min_mb},
                                 timeout=60)
                files = r.json().get("files", [])
                if not files:
                    st.info("No files found above the size threshold.")
                else:
                    st.success(f"Found {len(files)} files")
                    df = pd.DataFrame(files)[["name","path","size_mb","mtime"]]
                    df.columns = ["Name","Path","Size (MB)","Modified"]
                    st.dataframe(df, use_container_width=True, hide_index=True)
            except Exception as ex:
                st.error(str(ex))
