"""Hash Analyzer — text/file hashing, magic bytes, entropy."""
import requests, streamlit as st, pandas as pd

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Hash Analyzer · ForenShield", page_icon="🔐", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
</style>""", unsafe_allow_html=True)

st.markdown("## 🔐 Hash Analyzer")
st.caption("Cryptographic verification · File integrity · Entropy analysis")

tab1, tab2, tab3 = st.tabs(["📄 File Hash (Server)", "📝 Text Hash", "⚖️ Compare Hashes"])

algos = ["md5", "sha1", "sha256", "sha512"]

# ── Tab 1: File Hash (Server-side) ──────────────────────────────────────────────
with tab1:
    h_path = st.text_input("Absolute path to file", placeholder=r"C:\Users\user\Downloads\suspect.exe")
    h_algos = st.multiselect("Algorithms", algos, default=["md5", "sha1", "sha256"])
    
    if st.button("Compute Hashes") and h_path:
        with st.spinner(f"Hashing {h_path}..."):
            try:
                r = requests.get(f"{API}/hash/file-path", 
                                 params={"path": h_path, "algorithms": ",".join(h_algos)}, 
                                 timeout=60)
                if r.status_code != 200:
                    st.error(r.json().get("detail", "Error")); st.stop()
                d = r.json()
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Size", f"{d.get('size_mb',0):.2f} MB")
                c2.metric("Entropy", f"{d.get('entropy',0):.4f}", 
                          "Packed likely" if d.get('packed_likely') else "Normal")
                c3.metric("Magic", d.get("magic") or "Unknown")
                
                st.markdown("**Hashes:**")
                hashes = d.get("hashes", {})
                for a, h in hashes.items():
                    st.code(f"{a.upper():8} : {h}")
            except Exception as ex:
                st.error(str(ex))

# ── Tab 2: Text Hash ────────────────────────────────────────────────────────────
with tab2:
    txt = st.text_area("Text string to hash", height=150)
    t_algos = st.multiselect("Algorithms for text", algos, default=["md5", "sha256"])
    if st.button("Hash Text") and txt:
        try:
            r = requests.post(f"{API}/hash/text", json={"text": txt, "algorithms": t_algos}, timeout=5)
            d = r.json()
            st.success(f"Text length: {d.get('text_length', 0)} chars")
            hashes = d.get("hashes", {})
            for a, h in hashes.items():
                st.code(f"{a.upper():8} : {h}")
        except Exception as ex:
            st.error(str(ex))

# ── Tab 3: Compare Hashes ───────────────────────────────────────────────────────
with tab3:
    c_a = st.text_input("Hash A")
    c_b = st.text_input("Hash B")
    if st.button("Compare"):
        if c_a and c_b:
            try:
                r = requests.get(f"{API}/hash/compare", params={"hash_a": c_a, "hash_b": c_b}, timeout=5)
                d = r.json()
                if d.get("match"):
                    st.success(f"✅ Hashes match! (Detected as {d.get('algorithm_guess')})")
                else:
                    st.error("❌ Hashes do not match!")
            except Exception as ex:
                st.error(str(ex))
        else:
            st.warning("Please provide both hashes.")
