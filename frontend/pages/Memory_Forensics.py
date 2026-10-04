"""Memory Forensics — live process enumeration, suspicion scoring, string extraction."""
import requests, streamlit as st, pandas as pd

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Memory Forensics · ForenShield", page_icon="🧠", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
.pill-error{background:#450a0a;color:#f87171;border-radius:999px;padding:2px 10px;font-size:0.8rem}
.pill-ok{background:#064e3b;color:#34d399;border-radius:999px;padding:2px 10px;font-size:0.8rem}
.pill-warn{background:#451a03;color:#fbbf24;border-radius:999px;padding:2px 10px;font-size:0.8rem}
</style>""", unsafe_allow_html=True)

st.markdown("## 🧠 Memory Forensics")
st.caption("Live process enumeration · Suspicion scoring · String extraction · RAM snapshot")

tab1, tab2, tab3 = st.tabs(["🗂️ Process List", "🔍 Process Detail", "📸 RAM Snapshot"])

# ── Tab 1: Process List ─────────────────────────────────────────────────────────
with tab1:
    col_f, col_b = st.columns([3, 1])
    with col_f:
        search = st.text_input("🔍 Search processes", placeholder="name, user, PID...")
    with col_b:
        susp_only = st.checkbox("⚠️ Suspicious only", value=False)
        auto_ref  = st.checkbox("🔄 Auto-refresh (5s)")

    if auto_ref:
        import time; time.sleep(5); st.rerun()

    @st.cache_data(ttl=5)
    def get_procs(susp):
        r = requests.get(f"{API}/memory/processes", params={"filter_suspicious": str(susp).lower()}, timeout=8)
        return r.json()

    try:
        data  = get_procs(susp_only)
        procs = data.get("processes", [])
    except Exception as e:
        st.error(f"Backend error: {e}"); st.stop()

    # filter
    if search:
        s = search.lower()
        procs = [p for p in procs if s in p.get("name","").lower() or s in str(p.get("pid","")) or s in p.get("user","").lower()]

    m1, m2, m3 = st.columns(3)
    m1.metric("Total",     data.get("count", 0))
    m2.metric("Filtered",  len(procs))
    m3.metric("⚠️ Suspicious", data.get("suspicious_count", 0))

    if not procs:
        st.info("No processes match the filter.")
    else:
        rows = []
        for p in procs:
            rows.append({
                "⚠️":       "🔴" if p.get("suspicious") else "🟢",
                "PID":      p["pid"],
                "Name":     p["name"],
                "User":     p.get("user","?"),
                "CPU %":    p.get("cpu","0"),
                "Memory":   p.get("mem","--"),
                "Handles":  p.get("handles",0),
                "Status":   p.get("status","?"),
                "Created":  (p.get("created") or "")[:19],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True,
                     column_config={"⚠️": st.column_config.TextColumn("", width="small")})

        # String extractor
        st.divider()
        st.markdown("**Extract Strings from Process Executable**")
        pid_input = st.number_input("PID", min_value=0, value=procs[0]["pid"] if procs else 0, step=1)
        min_len   = st.slider("Min string length", 4, 20, 6)
        if st.button("Extract Strings"):
            with st.spinner(f"Extracting strings from PID {pid_input}..."):
                try:
                    r = requests.get(f"{API}/memory/process/{pid_input}/strings",
                                     params={"min_len": min_len}, timeout=15)
                    sdata = r.json()
                    strs  = sdata.get("strings", [])
                    s1, s2 = st.columns(2)
                    s1.metric("Strings found",       sdata.get("total",0))
                    s2.metric("⚠️ Suspicious strings", sdata.get("suspicious_count",0))
                    if strs:
                        sdf = pd.DataFrame([{
                            "⚠️":     "🔴" if s["suspicious"] else "",
                            "Offset": s["offset"],
                            "String": s["value"][:120],
                        } for s in strs])
                        st.dataframe(sdf, use_container_width=True, hide_index=True)
                except Exception as ex:
                    st.error(str(ex))

# ── Tab 2: Process Detail ───────────────────────────────────────────────────────
with tab2:
    pid2 = st.number_input("Enter PID", min_value=1, value=4, step=1, key="pid2")
    if st.button("Load Process Detail"):
        with st.spinner(f"Loading PID {pid2}..."):
            try:
                r    = requests.get(f"{API}/memory/process/{pid2}", timeout=6)
                d    = r.json()
                if "detail" in d:
                    st.error(d["detail"]); st.stop()
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Name:** `{d.get('name','?')}`")
                    st.markdown(f"**PID:** `{d.get('pid','?')}` &nbsp; **PPID:** `{d.get('ppid','?')}`")
                    st.markdown(f"**User:** `{d.get('username','?')}`")
                    st.markdown(f"**Status:** `{d.get('status','?')}`")
                    st.markdown(f"**Created:** `{d.get('created','?')}`")
                    susp = d.get("suspicious", False)
                    st.markdown(
                        '<span class="pill-error">⚠️ SUSPICIOUS</span>' if susp
                        else '<span class="pill-ok">✓ Clean</span>',
                        unsafe_allow_html=True
                    )
                with c2:
                    st.markdown(f"**CPU:** `{d.get('cpu_percent','?'):.1f}%`" if isinstance(d.get("cpu_percent"), float) else f"**CPU:** `{d.get('cpu_percent','?')}`")
                    st.markdown(f"**RAM RSS:** `{d.get('mem_rss_mb','?')} MB`")
                    st.markdown(f"**RAM VMS:** `{d.get('mem_vms_mb','?')} MB`")
                    st.markdown(f"**Threads:** `{d.get('threads','?')}`")
                    st.markdown(f"**Handles:** `{d.get('handles','?')}`")
                    st.markdown(f"**Exe:** `{d.get('exe','?')}`")

                st.markdown(f"**Cmdline:** `{d.get('cmdline','?')}`")

                # Connections
                conns = d.get("connections", [])
                if conns:
                    st.markdown("**Network Connections:**")
                    st.dataframe(pd.DataFrame(conns), use_container_width=True, hide_index=True)

                # Open files
                files = d.get("open_files", [])
                if files:
                    st.markdown(f"**Open Files ({len(files)}):**")
                    st.dataframe(pd.DataFrame({"path": files}), use_container_width=True, hide_index=True)
            except Exception as ex:
                st.error(str(ex))

# ── Tab 3: RAM Snapshot ─────────────────────────────────────────────────────────
with tab3:
    if st.button("Take RAM Snapshot"):
        with st.spinner("Capturing RAM snapshot..."):
            try:
                r = requests.get(f"{API}/memory/snapshot", timeout=6)
                s = r.json()
                mc1, mc2, mc3 = st.columns(3)
                mc1.metric("Total RAM",     f"{s.get('total_mb',0):,} MB")
                mc2.metric("Used",          f"{s.get('used_mb',0):,} MB")
                mc3.metric("Available",     f"{s.get('available_mb',0):,} MB")
                st.progress(int(s.get("percent", 0)), text=f"RAM Usage: {s.get('percent',0):.1f}%")
                st.markdown("**Top Memory Consumers:**")
                top = s.get("top_consumers", [])
                if top:
                    st.dataframe(pd.DataFrame(top), use_container_width=True, hide_index=True)
            except Exception as ex:
                st.error(str(ex))
