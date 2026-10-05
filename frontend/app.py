"""
ForenShield — Streamlit Frontend
Main dashboard / home page.
Run: streamlit run frontend/app.py
"""

import time
import requests
import streamlit as st
import pandas as pd

API = "http://127.0.0.1:8000/api"

st.set_page_config(
    page_title="ForenShield",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Hide default hamburger & footer */
  #MainMenu, footer { visibility: hidden; }

  /* Metric card styling */
  [data-testid="metric-container"] {
      background: #12141c;
      border: 1px solid #1e2035;
      border-radius: 12px;
      padding: 16px 20px;
  }
  [data-testid="metric-container"] label {
      color: #94a3b8 !important;
      font-size: 0.75rem !important;
      letter-spacing: 0.08em;
      text-transform: uppercase;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
      font-size: 1.6rem !important;
      color: #e2e8f0 !important;
  }

  /* Sidebar brand */
  [data-testid="stSidebarNav"]::before {
      content: "🛡️ ForenShield";
      display: block;
      padding: 1rem 1.2rem 0.5rem;
      font-size: 1.1rem;
      font-weight: 700;
      color: #6366f1;
      letter-spacing: 0.02em;
  }

  /* Alert / status pills */
  .pill-ok    { background:#064e3b; color:#34d399; border-radius:999px; padding:2px 10px; font-size:0.8rem; }
  .pill-warn  { background:#451a03; color:#fbbf24; border-radius:999px; padding:2px 10px; font-size:0.8rem; }
  .pill-error { background:#450a0a; color:#f87171; border-radius:999px; padding:2px 10px; font-size:0.8rem; }
  .section-title { color:#6366f1; font-size:0.7rem; letter-spacing:0.12em; text-transform:uppercase; margin-bottom:4px; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.caption("SIH 2026 · Digital Forensics")
    st.divider()
    st.markdown("**Navigation**")
    st.page_link("app.py",                              label="📊 Dashboard",          )
    st.page_link("pages/Memory_Forensics.py",         label="🧠 Memory Forensics"    )
    st.page_link("pages/Network_Forensics.py",        label="🌐 Network Forensics"   )
    st.page_link("pages/Disk_Analyzer.py",            label="💽 Disk Analyzer"       )
    st.page_link("pages/Timeline.py",                 label="⏱️ Timeline / MAC"      )
    st.page_link("pages/Hash_Analyzer.py",            label="🔐 Hash Analyzer"       )
    st.page_link("pages/Hex_Viewer.py",               label="🔬 Hex Viewer"          )
    st.page_link("pages/File_Recovery.py",            label="📂 File Recovery"       )
    st.page_link("pages/Drive_Eraser.py",             label="🗑️ Drive Eraser"        )
    st.page_link("pages/Evidence_Locker.py",          label="🔒 Evidence Locker"     )
    st.page_link("pages/Reports.py",                 label="📋 Reports"             )
    st.page_link("pages/AI_Models.py",               label="🤖 AI Models"           )
    st.page_link("pages/Settings.py",                label="⚙️ Settings"            )
    st.divider()
    if st.button("🔄 Refresh Dashboard", use_container_width=True):
        st.rerun()

# ── Header ──────────────────────────────────────────────────────────────────────
st.markdown("## 🛡️ ForenShield — System Dashboard")
st.caption("Integrated Digital Forensics & Secure Data Erasure Platform · SIH 2026")

# ── Fetch health ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=5)
def fetch_health():
    try:
        r = requests.get(f"{API}/health", timeout=4)
        return r.json()
    except Exception:
        return None

@st.cache_data(ttl=5)
def fetch_processes():
    try:
        r = requests.get(f"{API}/memory/processes", timeout=4)
        return r.json()
    except Exception:
        return None

@st.cache_data(ttl=5)
def fetch_connections():
    try:
        r = requests.get(f"{API}/network/connections", timeout=4)
        return r.json()
    except Exception:
        return None

@st.cache_data(ttl=5)
def fetch_partitions():
    try:
        r = requests.get(f"{API}/disk/partitions", timeout=4)
        return r.json()
    except Exception:
        return None

health = fetch_health()

# ── Backend Status Banner ───────────────────────────────────────────────────────
if health is None:
    st.error("⚠️  Backend offline — make sure `python backend.py` is running on port 8000")
    st.code("python backend.py", language="bash")
    st.stop()
else:
    st.success(f"Backend online · {health.get('hostname', '?')} · {health.get('platform', '?')[:40]}")

st.divider()

# ── Top Metrics Row ─────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("CPU Usage",    f"{health.get('cpu_percent', 0):.1f}%",
          f"{health.get('cpu_count_logical', '?')} logical cores")
c2.metric("RAM Used",     f"{health.get('ram_used_gb', 0):.1f} GB",
          f"of {health.get('ram_total_gb', 0):.1f} GB ({health.get('ram_percent', 0):.0f}%)")
c3.metric("Net Sent",     f"{health.get('net_sent_mb', 0):.1f} MB",  "↑ total")
c4.metric("Net Recv",     f"{health.get('net_recv_mb', 0):.1f} MB",  "↓ total")
c5.metric("Uptime",       health.get('uptime', '--'),                 health.get('boot_time', '')[:10])

st.divider()

# ── Second Row: Process + Network snapshot ──────────────────────────────────────
left, right = st.columns(2)

with left:
    st.markdown("##### 🧠 Live Processes")
    pdata = fetch_processes()
    if pdata:
        total = pdata.get("count", 0)
        susp  = pdata.get("suspicious_count", 0)
        sc1, sc2 = st.columns(2)
        sc1.metric("Total Processes",    total)
        sc2.metric("⚠️ Suspicious",     susp, delta=None)
        procs = pdata.get("processes", [])
        susp_procs = [p for p in procs if p.get("suspicious")]
        if susp_procs:
            st.markdown("**Flagged processes:**")
            for p in susp_procs[:5]:
                st.markdown(
                    f'<span class="pill-error">⚠ PID {p["pid"]}</span> &nbsp; '
                    f'`{p["name"]}` — {p["user"]} — CPU {p["cpu"]}%',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<span class="pill-ok">✓ No suspicious processes detected</span>', unsafe_allow_html=True)
    else:
        st.warning("Could not load process data")

with right:
    st.markdown("##### 🌐 Network Connections")
    ndata = fetch_connections()
    if ndata:
        total_n = ndata.get("count", 0)
        susp_n  = ndata.get("suspicious_count", 0)
        nc1, nc2 = st.columns(2)
        nc1.metric("Active Connections", total_n)
        nc2.metric("⚠️ Suspicious",      susp_n)
        susp_conns = [c for c in ndata.get("connections", []) if c.get("suspicious")]
        if susp_conns:
            st.markdown("**Flagged connections:**")
            for c in susp_conns[:5]:
                st.markdown(
                    f'<span class="pill-error">⚠ {c["proto"]}</span> &nbsp; '
                    f'`{c["remote"]}` ← `{c["proc"]}`',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<span class="pill-ok">✓ No suspicious connections detected</span>', unsafe_allow_html=True)
    else:
        st.warning("Could not load network data")

st.divider()

# ── Disk Row ────────────────────────────────────────────────────────────────────
st.markdown("##### 💽 Disk Partitions")
ddata = fetch_partitions()
if ddata and ddata.get("partitions"):
    parts = ddata["partitions"]
    rows = []
    for p in parts:
        rows.append({
            "Drive":     p.get("name", "?"),
            "Mount":     p.get("mount", "?"),
            "FS":        p.get("fs", "?"),
            "Total GB":  p.get("total_gb", 0),
            "Used GB":   p.get("used_gb", 0),
            "Free GB":   p.get("free_gb", 0),
            "Used %":    p.get("usedPct", 0),
        })
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Progress bars for each partition
    for p in parts:
        pct = p.get("usedPct", 0)
        col = "normal" if pct < 80 else "inverse"
        st.progress(int(pct), text=f"{p['name']} — {pct:.0f}% used ({p['used_gb']:.1f}/{p['total_gb']:.1f} GB)")
else:
    st.warning("Could not load disk data")

st.divider()

# ── System Info ─────────────────────────────────────────────────────────────────
st.markdown("##### 🖥️ System Information")
sic1, sic2, sic3 = st.columns(3)
with sic1:
    st.markdown(f"**Hostname:** `{health.get('hostname', '?')}`")
    st.markdown(f"**Platform:** `{health.get('platform', '?')}`")
    st.markdown(f"**Python:** `{health.get('python', '?')}`")
with sic2:
    st.markdown(f"**CPU Cores:** `{health.get('cpu_count_physical', '?')}P / {health.get('cpu_count_logical', '?')}L`")
    st.markdown(f"**CPU Freq:** `{health.get('cpu_freq_mhz', '?')} MHz`")
    st.markdown(f"**Swap Used:** `{health.get('swap_used_pct', 0):.1f}%`")
with sic3:
    st.markdown(f"**Boot:** `{health.get('boot_time', '?')[:19]}`")
    scapy_ok = health.get("scapy_available", False)
    win32_ok = health.get("win32_setctime", False)
    st.markdown(f"**Scapy:** {'<span class=\"pill-ok\">✓ available</span>' if scapy_ok else '<span class=\"pill-warn\">✗ not installed</span>'}", unsafe_allow_html=True)
    st.markdown(f"**win32_setctime:** {'<span class=\"pill-ok\">✓ available</span>' if win32_ok else '<span class=\"pill-warn\">✗ not installed</span>'}", unsafe_allow_html=True)

st.caption(f"Last refreshed at {time.strftime('%H:%M:%S')} · Auto-refresh: use the Refresh button in sidebar")
