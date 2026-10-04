"""Network Forensics — live connections, NIC interfaces, PCAP analysis."""
import requests, streamlit as st, pandas as pd

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Network Forensics · ForenShield", page_icon="🌐", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
.pill-error{background:#450a0a;color:#f87171;border-radius:999px;padding:2px 10px;font-size:0.8rem}
.pill-ok{background:#064e3b;color:#34d399;border-radius:999px;padding:2px 10px;font-size:0.8rem}
</style>""", unsafe_allow_html=True)

st.markdown("## 🌐 Network Forensics")
st.caption("Live connections · C2 detection · NIC interfaces · PCAP analysis")

tab1, tab2, tab3 = st.tabs(["🔌 Live Connections", "📡 Interfaces", "📦 PCAP Analysis"])

# ── Tab 1: Connections ──────────────────────────────────────────────────────────
with tab1:
    kind    = st.selectbox("Protocol family", ["inet", "tcp", "udp"], index=0)
    c_refresh = st.button("🔄 Refresh Connections")

    @st.cache_data(ttl=5)
    def get_conns(k):
        r = requests.get(f"{API}/network/connections", params={"kind": k}, timeout=6)
        return r.json()

    try:
        data  = get_conns(kind)
    except Exception as e:
        st.error(f"Backend error: {e}"); st.stop()

    if c_refresh:
        st.cache_data.clear()
        data = get_conns(kind)

    m1, m2 = st.columns(2)
    m1.metric("Total Connections",  data.get("count", 0))
    m2.metric("⚠️ Suspicious",      data.get("suspicious_count", 0))

    conns = data.get("connections", [])
    if not conns:
        st.info("No connections found.")
    else:
        susp_filter = st.checkbox("Show suspicious only")
        if susp_filter:
            conns = [c for c in conns if c.get("suspicious")]

        search = st.text_input("Filter by IP / process / port", key="net_search")
        if search:
            conns = [c for c in conns if search in c.get("remote","") or search in c.get("proc","") or search in c.get("local","")]

        rows = []
        for c in conns:
            rows.append({
                "⚠️":     "🔴" if c.get("suspicious") else "🟢",
                "PID":    c.get("pid","?"),
                "Process":c.get("proc","?"),
                "Proto":  c.get("proto","?"),
                "Local":  c.get("local","?"),
                "Remote": c.get("remote","?"),
                "State":  c.get("state","?"),
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                     column_config={"⚠️": st.column_config.TextColumn("", width="small")})

# ── Tab 2: Interfaces ───────────────────────────────────────────────────────────
with tab2:
    if st.button("Load Interfaces"):
        with st.spinner("Loading NIC data..."):
            try:
                r    = requests.get(f"{API}/network/interfaces", timeout=6)
                ifaces = r.json().get("interfaces", [])
                for iface in ifaces:
                    up = iface.get("is_up", False)
                    colour = "normal" if up else "off"
                    with st.expander(f"{'🟢' if up else '🔴'} {iface['name']} — {'UP' if up else 'DOWN'} — {iface.get('speed_mbps',0)} Mbps"):
                        ic1, ic2 = st.columns(2)
                        with ic1:
                            st.markdown(f"**MTU:** `{iface.get('mtu','?')}`")
                            st.markdown(f"**Sent:** `{iface.get('bytes_sent_mb',0):.2f} MB`")
                            st.markdown(f"**Recv:** `{iface.get('bytes_recv_mb',0):.2f} MB`")
                        with ic2:
                            st.markdown(f"**Packets Sent:** `{iface.get('packets_sent',0):,}`")
                            st.markdown(f"**Packets Recv:** `{iface.get('packets_recv',0):,}`")
                            st.markdown(f"**Errors In/Out:** `{iface.get('errin',0)} / {iface.get('errout',0)}`")
                        addrs = iface.get("addresses", [])
                        if addrs:
                            st.dataframe(pd.DataFrame(addrs), use_container_width=True, hide_index=True)
            except Exception as ex:
                st.error(str(ex))

# ── Tab 3: PCAP Analysis ────────────────────────────────────────────────────────
with tab3:
    st.markdown("**Analyze a PCAP file from disk**")
    pcap_path = st.text_input("Absolute path to .pcap file",
                               placeholder=r"C:\captures\traffic.pcap")
    max_pkts  = st.slider("Max packets to parse", 100, 2000, 500, step=100)

    if st.button("🔍 Analyze PCAP") and pcap_path:
        with st.spinner("Parsing PCAP (requires Scapy)..."):
            try:
                r = requests.get(f"{API}/network/pcap",
                                 params={"path": pcap_path, "max_packets": max_pkts}, timeout=30)
                if r.status_code != 200:
                    st.error(r.json().get("detail", "Error")); st.stop()
                p = r.json()

                pm1, pm2, pm3, pm4 = st.columns(4)
                pm1.metric("Total Packets",    p.get("total_packets", 0))
                pm2.metric("⚠️ Suspicious",    p.get("suspicious_count", 0))
                pm3.metric("Total Bytes",      f"{p.get('total_bytes',0):,}")
                pm4.metric("Unique IPs",       p.get("unique_ips", 0))

                # Protocol distribution
                proto_dist = p.get("protocol_distribution", [])
                if proto_dist:
                    st.markdown("**Protocol Distribution:**")
                    pdf = pd.DataFrame(proto_dist)
                    st.bar_chart(pdf.set_index("proto")["count"])

                # IP Stats
                ip_stats = p.get("ip_stats", [])[:20]
                if ip_stats:
                    st.markdown("**Top IP Addresses:**")
                    st.dataframe(pd.DataFrame(ip_stats), use_container_width=True, hide_index=True)

                # Packet table
                packets = p.get("packets", [])
                if packets:
                    st.markdown(f"**Packet List ({len(packets)}):**")
                    susp_pkt = st.checkbox("Show suspicious packets only", key="pcap_susp")
                    if susp_pkt:
                        packets = [pk for pk in packets if pk.get("suspicious")]
                    rows = []
                    for pk in packets:
                        rows.append({
                            "⚠️":    "🔴" if pk.get("suspicious") else "",
                            "#":    pk.get("id",""),
                            "Time": pk.get("time",""),
                            "Src":  pk.get("src",""),
                            "Dst":  pk.get("dst",""),
                            "Proto":pk.get("proto",""),
                            "Port": pk.get("port",""),
                            "Size": pk.get("size",""),
                            "Info": pk.get("info","")[:60],
                        })
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            except Exception as ex:
                st.error(str(ex))
