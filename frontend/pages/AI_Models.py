"""AI Models — Train anomaly detection, NLP, and Deep Learning models."""
import time
import requests, streamlit as st

API = "http://127.0.0.1:8000/api"
st.set_page_config(page_title="AI Models · ForenShield", page_icon="🧠", layout="wide")

st.markdown("""<style>
#MainMenu,footer{visibility:hidden}
[data-testid="metric-container"]{background:#12141c;border:1px solid #1e2035;border-radius:12px;padding:16px 20px}
</style>""", unsafe_allow_html=True)

st.markdown("## 🧠 AI Model Training")
st.caption("Train machine learning models for anomaly detection, malware analysis, and NLP.")

tab1, tab2, tab3 = st.tabs(["📉 Anomaly Detection", "💬 NLP Log Analyzer", "👾 Deep Learning (CNN)"])

def render_trainer(model_type, title, desc, icon):
    st.subheader(f"{icon} {title}")
    st.markdown(desc)
    
    if st.button(f"Train {title} Model", key=f"btn_{model_type}"):
        with st.spinner("Starting training job..."):
            try:
                r = requests.post(f"{API}/ai/train", json={"model_type": model_type}, timeout=5)
                if r.status_code == 200:
                    task_id = r.json().get("task_id")
                    st.session_state[f"task_{model_type}"] = task_id
                    st.success(f"Training started! Task ID: `{task_id}`")
                else:
                    st.error(r.json().get("detail", "Error"))
            except Exception as e:
                st.error(f"Failed to reach backend: {e}")
                
    task_id = st.session_state.get(f"task_{model_type}")
    if task_id:
        st.divider()
        st.markdown(f"**Training Status** (`{task_id}`)")
        
        auto_poll = st.checkbox(f"🔄 Auto-poll (2s)", key=f"poll_{model_type}", value=True)
        
        try:
            r = requests.get(f"{API}/ai/train/{task_id}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                progress = data.get("progress", 0)
                
                st.progress(progress, text=f"Status: {status.upper()} - {progress}%")
                
                logs = data.get("log", [])
                if logs:
                    st.markdown("**Logs:**")
                    st.code("\n".join(logs))
                    
                if status == "completed":
                    st.success("Model trained successfully!")
            else:
                st.warning("Task not found on backend.")
        except Exception as e:
            st.error(f"Failed to fetch status: {e}")
            
        if auto_poll and status == "training":
            time.sleep(2)
            st.rerun()

with tab1:
    render_trainer(
        "anomaly", 
        "IsolationForest", 
        "Trains a Scikit-learn IsolationForest on system metrics (CPU, RAM, Handles) to detect suspicious processes and network traffic.",
        "📉"
    )

with tab2:
    render_trainer(
        "nlp", 
        "Transformer (BERT)", 
        "Fine-tunes a BERT-based language model on extracted process strings and log files to identify malicious artifacts.",
        "💬"
    )

with tab3:
    render_trainer(
        "deep_learning", 
        "1D-CNN (PyTorch)", 
        "Trains a 1D Convolutional Neural Network on binary byte sequences to classify malware signatures.",
        "👾"
    )
