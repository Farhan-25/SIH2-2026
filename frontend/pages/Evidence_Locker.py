"""Evidence Locker — CRUD for evidence items and chain of custody."""
import requests, streamlit as st, pandas as pd

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="Evidence Locker · ForenShield", page_icon="🔒", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
</style>""", unsafe_allow_html=True)

st.markdown("## 🔒 Evidence Locker")
st.caption("Chain of custody · Evidence hashing · Verification")

tab1, tab2, tab3 = st.tabs(["📦 View Evidence", "➕ Add Evidence", "🔍 Verify & Custody"])

# ── Fetch Evidence ──────────────────────────────────────────────────────────────
def fetch_evidence():
    try:
        return requests.get(f"{API}/evidence", timeout=5).json().get("items", [])
    except:
        return []

# ── Tab 1: View ─────────────────────────────────────────────────────────────────
with tab1:
    if st.button("🔄 Refresh List"):
        st.rerun()
        
    items = fetch_evidence()
    if not items:
        st.info("No evidence registered.")
    else:
        df = pd.DataFrame(items)[["id", "name", "type", "status", "created"]]
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("**Evidence Details**")
        sel_id = st.selectbox("Select Evidence ID", [i["id"] for i in items])
        if sel_id:
            item = next((i for i in items if i["id"] == sel_id), None)
            if item:
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"**Name:** {item.get('name')}")
                    st.markdown(f"**Type:** {item.get('type')}")
                    st.markdown(f"**Tags:** {', '.join(item.get('tags', []))}")
                with c2:
                    st.markdown(f"**Status:** `{item.get('status')}`")
                    st.markdown(f"**SHA-256:** `{item.get('hash')}`")
                    st.markdown(f"**Created:** {item.get('created')}")
                st.markdown("**Notes:**")
                st.info(item.get("notes") or "None")
                
                if st.button("🗑️ Delete Evidence"):
                    requests.delete(f"{API}/evidence/{sel_id}")
                    st.rerun()

# ── Tab 2: Add ──────────────────────────────────────────────────────────────────
with tab2:
    with st.form("add_evidence"):
        e_name = st.text_input("Evidence Name*")
        e_type = st.selectbox("Type", ["disk-image", "document", "mobile-device", "memory-dump", "other"])
        e_size = st.text_input("Size (e.g. 500GB)")
        e_tags = st.text_input("Tags (comma separated)")
        e_notes = st.text_area("Notes")
        
        if st.form_submit_button("Add Evidence Item"):
            if e_name:
                tags = [t.strip() for t in e_tags.split(",") if t.strip()]
                try:
                    r = requests.post(f"{API}/evidence", 
                                      json={"name": e_name, "type": e_type, "size": e_size, "tags": tags, "notes": e_notes},
                                      timeout=5)
                    if r.status_code == 200:
                        st.success(f"Added! ID: {r.json().get('id')}")
                    else:
                        st.error(r.json().get("detail", "Error"))
                except Exception as ex:
                    st.error(str(ex))
            else:
                st.warning("Name is required.")

# ── Tab 3: Custody ──────────────────────────────────────────────────────────────
with tab3:
    items = fetch_evidence()
    c_id = st.selectbox("Select Evidence", [i["id"] for i in items], key="c_id")
    
    if c_id:
        item = next((i for i in items if i["id"] == c_id), None)
        if item:
            if st.button("✅ Verify Integrity"):
                try:
                    r = requests.post(f"{API}/evidence/{c_id}/verify", timeout=5)
                    if r.status_code == 200:
                        st.success("Integrity verified!")
                        st.rerun()
                except Exception as ex:
                    st.error(str(ex))
            
            st.divider()
            st.markdown("**Add Custody Event**")
            with st.form("custody_form"):
                cust_by = st.text_input("Performed By (Officer/Examiner)")
                cust_action = st.text_input("Action (e.g. Extracted to lab drive)")
                if st.form_submit_button("Add Event"):
                    if cust_by and cust_action:
                        try:
                            requests.post(f"{API}/evidence/{c_id}/custody", 
                                          json={"by": cust_by, "action": cust_action}, timeout=5)
                            st.success("Event added!")
                            st.rerun()
                        except Exception as ex:
                            st.error(str(ex))
            
            st.divider()
            st.markdown("**Chain of Custody Log**")
            clog = item.get("custodyLog", [])
            if clog:
                st.dataframe(pd.DataFrame(clog), use_container_width=True, hide_index=True)
