<div align="center">

<img src="https://img.shields.io/badge/Smart%20India%20Hackathon-2026-6366f1?style=for-the-badge&labelColor=0a0b0f" alt="SIH 2026"/>

# 🛡️ ForenShield v2.0

**Integrated Digital Forensics & Secure Data Erasure Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3b82f6?style=flat-square&logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi&logoColor=white)](#)
[![React](https://img.shields.io/badge/Streamlit-1.38-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](#)
[![Vite](https://img.shields.io/badge/Pandas-2.2-150458?style=flat-square&logo=pandas&logoColor=white)](#)
[![psutil](https://img.shields.io/badge/psutil-6.0-f59e0b?style=flat-square)](#)
[![Scapy](https://img.shields.io/badge/Scapy-2.5-ef4444?style=flat-square)](#)
[![Standards](https://img.shields.io/badge/Standards-NIST%20%7C%20DoD%20%7C%20ISO-818cf8?style=flat-square)](#compliance)

*A unified full-stack digital forensics platform combining a live Python forensic engine with a modern Streamlit dashboard — designed for law enforcement, forensic analysts, and cybersecurity professionals.*

[**Quick Start**](#-quick-start) · [**API Docs**](docs/api/API_REFERENCE.md) · [**Architecture**](docs/ARCHITECTURE.md) · [**Setup Guide**](docs/setup/SETUP.md)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [What's New in v2.0](#-whats-new-in-v20)
- [Features](#-features)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [Project Structure](#-project-structure)
- [Quick Start](#-quick-start)
- [API Overview](#-api-overview)
- [Architecture](#-architecture)
- [Compliance Standards](#-compliance)
- [Roadmap](#%EF%B8%8F-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🔍 Overview

ForenShield is a full-stack digital forensics platform built for **Smart India Hackathon 2026**.

It combines a **Python FastAPI backend** — which talks directly to the OS via `psutil`, `scapy`, and native system calls — with a **Streamlit** dashboard that provides real-time forensic analysis across 13 specialized tools.

> Previous versions were frontend-only mockups. v2.0 ships a **live backend** with 50 real API endpoints that enumerate actual system processes, parse real PCAP files, compute real hashes, carve real files, and manage a persistent evidence locker.

**Designed for:**
- 🏛️ Law enforcement digital forensics units
- 🔬 Incident response teams
- 🔐 Cybersecurity analysts
- 🏢 Enterprise IT security / eDiscovery

---

## 🆕 What's New in v2.0

| Change | v1.x | v2.0 |
|---|---|---|
| **Backend** | None (frontend-only) | Python FastAPI — 50 live endpoints |
| **Process Analysis** | Mock data | Real `psutil` enumeration with suspicion scoring |
| **Network Analysis** | Mock data | Live connections + real PCAP parsing via Scapy |
| **File Carving** | Simulated progress | Real background carving worker (17 signature types) |
| **Hashing** | Browser Web Crypto only | Server-side MD5/SHA1/SHA256/SHA512 + entropy |
| **Disk Info** | Mock partitions | Real `psutil.disk_partitions()` + I/O counters |
| **Evidence Locker** | In-memory only | JSON-persisted with chain-of-custody log |
| **Reports** | Mock | Real report generation with system metadata + export |
| **Settings** | localStorage | Server-persisted JSON settings |
| **Real-time** | None | SSE stream: live CPU/RAM/network every second |

---

## ✨ Features

### 🔬 Forensic Analysis

| Tool | What it does |
|---|---|
| **Memory Forensics** | Enumerate live processes, detect C2-connected PIDs, extract strings, score suspicious processes by CPU/handles/name |
| **Network Forensics** | Live connection map with C2 port detection, PCAP parsing via Scapy (packets, DNS, protocol distribution, IP intelligence) |
| **Disk Analyzer** | Real partition listing + I/O stats, recursive directory tree scanner, large-file finder |
| **Timeline Analyzer** | MAC (Modified/Accessed/Created) timestamp reconstruction across directory trees; modify timestamps for forensic testing |
| **Hash Analyzer** | MD5, SHA-1, SHA-256, SHA-512 of text/uploaded/server files; entropy calculation; magic byte detection; constant-time comparison |
| **Hex Viewer** | Server-side paginated hex dump with offset navigation, magic detection, pattern search |
| **File Carving** | Background recovery worker — 17 signatures (JPEG, PNG, PDF, ZIP, EXE, ELF, RAR, 7Z, FLAC, MKV…) |

### 🔐 Evidence & Chain of Custody

| Tool | What it does |
|---|---|
| **Evidence Locker** | CRUD with SHA-256 integrity hashes, chain-of-custody log, per-item verification, JSON persistence |
| **Reports** | Create case reports with system info snapshot, evidence references, section listing; export as text |
| **Settings** | Server-persisted examiner name, agency, algorithm preferences, backend config |

### 🗑️ Secure Erasure

| Tool | What it does |
|---|---|
| **File Eraser** | Multi-pass overwriting (DoD 5220.22-M, Gutmann 35-pass, zeros, random CSPRNG) before deletion |
| **Drive Eraser** | Free-space wiper via background task; sector-level temp-file fill + fsync |

---

## 🛠️ Tech Stack

### Backend

```
Python 3.10+
├── fastapi 0.115          — REST framework + OpenAPI docs
├── uvicorn[standard] 0.30 — ASGI production server
├── pydantic 2.8           — Data validation & schemas
├── psutil 6.0             — Live system/process/network/disk info
├── scapy 2.5              — PCAP parsing & packet dissection
├── python-multipart 0.0.9 — File upload support
└── win32-setctime 1.1     — Windows ctime modification (optional)
```

### Frontend

```
Python 3.10+ (Streamlit)
├── streamlit 1.38         — Pure Python dashboard framework
├── pandas 2.2             — Dataframes for tables & charts
└── requests 2.32          — HTTP client to talk to FastAPI
```

---

## 📁 Project Structure

```
forenshield/
├── backend.py                  ← FastAPI server — 1,551 lines, 50 endpoints
├── requirements.txt            ← pip install -r requirements.txt
├── run.py                      ← ⚡ Start the whole project:  python run.py
├── sync.py                     ← 🔄 Push to GitHub:          python sync.py
├── package.json                ← Root npm config
├── README.md
├── LICENSE
├── .gitignore
│
├── docs/                       ← Documentation
│   ├── ARCHITECTURE.md
│   ├── api/API_REFERENCE.md
│   └── setup/SETUP.md
│
└── frontend/                   ← Streamlit frontend
    ├── app.py                  ← Main dashboard
    ├── .streamlit/             ← Theme config
    └── pages/                  ← Forensic tool pages
        ├── Memory_Forensics.py
        ├── Network_Forensics.py
        ├── Disk_Analyzer.py
        ├── Timeline.py
        ├── Hash_Analyzer.py
        ├── Hex_Viewer.py
        ├── File_Recovery.py
        ├── Drive_Eraser.py
        ├── Evidence_Locker.py
        ├── Reports.py
        ├── AI_Models.py
        └── Settings.py
```


---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/your-org/forenshield.git
cd forenshield

# Start everything — installs deps, launches backend + frontend, opens browser
python run.py
```

That's it. `run.py` will:
1. Auto-create a Python `venv` and install `requirements.txt` on first run
2. (Node dependencies are no longer needed as the frontend is now Streamlit)
3. Start the **FastAPI backend** on `http://127.0.0.1:8000`
4. Start the **Streamlit frontend** on `http://localhost:8501`
5. Open your browser automatically
6. Stream both logs with colour-coded prefixes
7. Shut both down cleanly on `Ctrl+C`

```
╔══════════════════════════════════════════════════════════╗
║          ForenShield v2.0 — Digital Forensics            ║
╚══════════════════════════════════════════════════════════╝

  →  Checking dependencies
  ✓  Python dependencies already satisfied
  ✓  Node.js dependencies already satisfied

  [BACKEND]  INFO:     Application startup complete.
  [FRONTEND] You can now view your Streamlit app in your browser.
  ✓  Backend ready  at http://127.0.0.1:8000
  ✓  Frontend ready at http://localhost:8501
```

### Options

```bash
python run.py --backend-only    # Only the Python API server
python run.py --frontend-only   # Only the Streamlit dashboard
python run.py --port 9000       # Use a different backend port
python run.py --no-browser      # Don't auto-open the browser
```

> 💡 On Windows, run as **Administrator** for full forensic access (process enumeration, network connections).

---

## 📡 API Overview

The backend exposes **50 REST endpoints** across 16 functional sections.

Interactive docs: `http://127.0.0.1:8000/docs`

| Section | Base Path | Description |
|---|---|---|
| System Health | `/api/health` | CPU, RAM, disk I/O, uptime, hostname |
| Memory | `/api/memory/` | Live processes, deep-dive, strings, RAM snapshot |
| Network | `/api/network/` | Connections, NIC interfaces, PCAP analysis |
| Disk | `/api/disk/` | Partitions, directory tree, large-file finder |
| Timeline | `/api/timeline/` | MAC times read/write, directory event scan |
| Hash | `/api/hash/` | Text/file/path hashing, comparison |
| Hex | `/api/hex/` | Hex dump, pattern search |
| Recovery | `/api/recovery/` | File carving jobs, signatures list |
| Eraser | `/api/eraser/` | Secure file delete, free-space wipe |
| Evidence | `/api/evidence/` | CRUD, verify, chain-of-custody |
| Reports | `/api/reports/` | Create, list, export |
| Settings | `/api/settings/` | Get, update, reset |
| Tasks | `/api/tasks/` | Background task polling |
| Stream | `/api/stream/` | SSE: live metrics every second |
| File Utils | `/api/file/` | Info (magic+entropy+hashes), strings |
| Dir Utils | `/api/dir/` | Directory listing |

→ Full reference: [docs/api/API_REFERENCE.md](docs/api/API_REFERENCE.md)

---

## 🏛️ Architecture

```
Streamlit Frontend (localhost:8501)
        │
        │ HTTP REST  ←→  SSE Stream
        │
FastAPI Backend (127.0.0.1:8000)
        │
        ├── psutil → OS (processes, network, disk, memory)
        ├── scapy  → PCAP files
        ├── hashlib / os → file hashing, timestamps, hex
        ├── threading → background carving + wipe tasks
        └── JSON files → evidence.json / reports.json / settings.json
```

→ Full architecture: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

## ✅ Compliance

ForenShield's erasure algorithms and forensic procedures align with:

| Standard | Domain | Implemented |
|---|---|---|
| **NIST SP 800-88 Rev. 1** | Media Sanitization | ✅ Clear + Purge methods |
| **DoD 5220.22-M** | Defense Data Destruction | ✅ 3-pass random overwrite |
| **Gutmann Method** | Maximum Security Erasure | ✅ 35-pass pattern wipe |
| **IEEE 2883-2022** | Storage Sanitization | ✅ |
| **ISO/IEC 27001:2022** | Information Security | ✅ Chain of custody, audit logs |
| **GDPR Article 17** | Right to Erasure | ✅ Verifiable deletion |
| **HIPAA Security Rule** | Healthcare Data | ✅ |
| **PCI-DSS v4.0** | Payment Card Data | ✅ |

---

## 🗺️ Roadmap

### v2.0 (Current)
- [x] Python FastAPI backend — 50 live API endpoints
- [x] Live process enumeration with suspicion scoring
- [x] Real PCAP analysis via Scapy
- [x] Background file carving (17 signatures)
- [x] Multi-pass secure file erasure (DoD/Gutmann/zeros)
- [x] JSON-persisted Evidence Locker with chain-of-custody
- [x] Report generation with system metadata
- [x] Server-persisted settings
- [x] SSE real-time metrics stream
- [x] requirements.txt + full documentation

### v2.1 (Planned)
- [ ] PDF report export (WeasyPrint / ReportLab)
- [ ] Geo-IP lookup in network forensics (MaxMind DB)
- [ ] Volatility3 integration for memory dump analysis
- [ ] SQLite/PostgreSQL backend for evidence persistence
- [ ] WebSocket real-time carving progress (replace polling)
- [ ] Electron desktop app wrapper

### v3.0 (Future)
- [ ] Role-based access control (RBAC)
- [ ] Multi-case management
- [ ] Cryptographic evidence signing
- [ ] Plugin API for custom analyzers
- [ ] Multi-language (i18n) support

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

### Backend Development

```bash
# Install dev dependencies
pip install -r requirements.txt httpx pytest pytest-asyncio

# Run tests
pytest tests/ -v

# Check types
mypy backend.py

# Format
black backend.py
```

### Frontend Development

```bash
cd forenshield-react
npm run dev     # dev server with HMR
npm run lint    # oxlint
npm run build   # production build
```

---

## 👥 Team

Built for **Smart India Hackathon 2026** — Digital Forensics & Cybersecurity Track.

| Role | Responsibility |
|---|---|
| Backend Engineering | Python FastAPI, psutil, Scapy, forensic algorithms |
| Frontend Engineering | Streamlit, Pandas, Python UI |
| Forensic Research | Compliance standards, algorithm research |
| Architecture | System design, API contracts |

---

## 📄 License

Copyright © 2026 ForenShield Team.  
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ for SIH 2026 · Digital Forensics & Cybersecurity Track

**[⬆ Back to Top](#)**

</div>
