# Setup Guide — ForenShield v2.0

This guide walks you through setting up both the **Python backend** and the **Streamlit frontend** on Windows, Linux, or macOS.

---

## Prerequisites

| Tool | Minimum Version | Notes |
|---|---|---|
| Python | 3.10+ | 3.12+ recommended |
| Git | Any | For cloning the repo |
| pip | 23.0+ | `python -m pip install --upgrade pip` |

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/your-org/forenshield.git
cd forenshield
```

---

## Step 2 — Backend Setup (Python + FastAPI)

### 2.1 Create a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 2.2 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Verify Installation

```bash
python -c "import fastapi, psutil, pydantic; print('Core deps OK')"
python -c "from scapy.all import IP; print('Scapy OK')"        # optional
python -c "from win32_setctime import setctime; print('win32 OK')"  # Windows only
```

### 2.4 Start the Backend

```bash
# Development mode (auto-reload on changes)
python backend.py

# Or directly with uvicorn
uvicorn backend:app --host 127.0.0.1 --port 8000 --reload

# Production mode
uvicorn backend:app --host 0.0.0.0 --port 8000 --workers 4
```

Backend runs at: `http://127.0.0.1:8000`  
Swagger docs at: `http://127.0.0.1:8000/docs`

### 2.5 Environment Variables

| Variable | Default | Description |
|---|---|---|
| `FORENSHIELD_DATA` | `~/.forenshield` | Directory for persistent data (evidence, reports, settings) |
| `PORT` | `8000` | Override the backend port |

```bash
# Windows
set FORENSHIELD_DATA=D:\ForenShieldData
set PORT=9000
python backend.py

# Linux / macOS
FORENSHIELD_DATA=/data/forenshield PORT=9000 python backend.py
```

---

## Step 3 — Frontend Setup (Streamlit)

```bash
# Make sure your venv is activated
# Starts the Streamlit dashboard
streamlit run frontend/app.py
```

Frontend runs at: `http://localhost:8501`

---

## Step 4 — Running Both Together (Manually)

*(Note: You can simply use `python run.py` in the root folder to start both automatically.)*

Open **two terminals** side by side:

**Terminal 1 — Backend:**
```bash
cd forenshield
source venv/bin/activate    # or venv\Scripts\activate on Windows
python backend.py
```

**Terminal 2 — Frontend:**
```bash
cd forenshield
source venv/bin/activate    # or venv\Scripts\activate on Windows
streamlit run frontend/app.py
```

Then open `http://localhost:8501` in your browser.

---

## Windows-Specific Notes

### Running as Administrator (Recommended)

Several forensic features require elevated privileges on Windows:

- Full process enumeration (some system processes)
- Network connection listing (`psutil.net_connections`)
- File creation time modification (`win32-setctime`)
- Drive-level operations

Right-click your terminal → **Run as Administrator**, then start the backend.

### Scapy on Windows

Scapy requires **Npcap** for live capture (not needed for PCAP file analysis):

1. Download Npcap from: https://npcap.com/#download
2. Install with "WinPcap API-compatible Mode" checked
3. `pip install scapy`

---

## Linux-Specific Notes

```bash
# Install system deps for psutil
sudo apt-get install gcc python3-dev    # Ubuntu/Debian
sudo dnf install gcc python3-devel      # Fedora/RHEL

# For process string extraction from /proc/mem
sudo python backend.py    # or configure capabilities

# Scapy raw socket access
sudo pip install scapy
# Or run backend with: sudo python backend.py
```

---

## Troubleshooting

### `ModuleNotFoundError: No module named 'fastapi'`
```bash
# Make sure venv is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### `Access is denied` on Windows
Run your terminal as Administrator.

### `Port 8000 already in use`
```bash
# Windows — find and kill the process
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux
lsof -ti:8000 | xargs kill -9
```

### Scapy import fails
```bash
pip install --upgrade scapy
# On Windows: also install Npcap from https://npcap.com
```

### `win32_setctime` not found
```bash
pip install win32-setctime
```
This is optional — ctime modification simply won't work without it.

---

## Data Directory Structure

After first run, ForenShield creates:

```
~/.forenshield/
├── evidence.json     # Evidence locker persistence
├── reports.json      # Generated reports
└── settings.json     # User settings
```

You can back up or export these JSON files directly.
