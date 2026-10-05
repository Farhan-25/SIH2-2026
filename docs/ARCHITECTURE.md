# Architecture — ForenShield

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FORENSHIELD PLATFORM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   ┌──────────────────────────────────────────────────────────────────────┐  │
│   │                   REACT FRONTEND  (Vite + React 19)                   │  │
│   │                                                                        │  │
│   │  Dashboard  │ Memory  │ Network │ Disk  │ Timeline │ Hash │ Hex       │  │
│   │  Forensics  │ Forensics│ Forensics│Analyzer│ Analyzer │Analyzer│Viewer│  │
│   │                                                                        │  │
│   │  Evidence Locker  │  Reports  │  Settings  │  File Recovery          │  │
│   └────────────────────────────────────┬─────────────────────────────────┘  │
│                                        │ HTTP REST (localhost:8000)          │
│   ┌────────────────────────────────────▼─────────────────────────────────┐  │
│   │                   PYTHON BACKEND  (FastAPI + uvicorn)                 │  │
│   │                                                                        │  │
│   │  §1 Health  │ §2 Memory │ §3 Network │ §4 Disk │ §5 Timeline         │  │
│   │  §6 Hash    │ §7 Hex    │ §8 Carving │ §9 Erase│ §10 Evidence        │  │
│   │  §11 Reports│ §12 Config│ §13 Tasks  │ §14 SSE │ §15 Utils           │  │
│   │                                                                        │  │
│   │         Background Workers (threading)  │  Persistence Layer          │  │
│   │         ├── File Carving Worker          │  ├── evidence.json          │  │
│   │         └── Free-Space Wiper            │  ├── reports.json            │  │
│   │                                          │  └── settings.json          │  │
│   └────────────────────────────────────┬─────────────────────────────────┘  │
│                                        │                                     │
│   ┌───────────────┬────────────────────▼────────────────────────────────┐   │
│   │  OS / psutil  │  Scapy (PCAP)  │  win32_setctime  │  File System   │   │
│   └───────────────┴────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend (Python)

| Component | Library | Version | Purpose |
|---|---|---|---|
| Web Framework | FastAPI | 0.115 | REST API, routing, OpenAPI docs |
| ASGI Server | Uvicorn | 0.30 | HTTP server with async support |
| Data Validation | Pydantic v2 | 2.8 | Request/response schema validation |
| System Info | psutil | 6.0 | Process, network, disk, memory info |
| Packet Analysis | Scapy | 2.5 | PCAP parsing, protocol dissection |
| File Timestamps | win32-setctime | 1.1 | Windows ctime modification |

### Frontend (JavaScript)

| Component | Library | Version | Purpose |
|---|---|---|---|
| UI Framework | React | 19 | Component-based UI |
| Build Tool | Vite | 8.3 | Dev server, HMR, production bundling |
| Routing | React Router | 7 | Client-side navigation |
| Icons | Lucide React | 1.48 | SVG icon components |
| Styling | Vanilla CSS | — | Custom design system with CSS vars |

---

## Data Flow

### Memory Forensics Flow
```
User clicks "Start Analysis"
    → Frontend: POST /api/memory/processes
    → Backend: psutil.process_iter() enumerates all live processes
    → _proc_is_suspicious() scores each process
    → Response: JSON array with suspicious flags
    → Frontend: renders process table with red highlights
```

### File Carving Flow
```
User selects source + output, clicks "Start Carve"
    → Frontend: POST /api/recovery/carve {source_path, output_dir, file_types}
    → Backend: spawns _carve_worker() in background thread
    → Backend returns: {task_id, status: "started"}
    → Frontend: polls GET /api/recovery/carve/{task_id} every 2s
    → Worker reads file in 512KB chunks, searches for magic signatures
    → On match: writes carved file to output_dir
    → Frontend: shows live log + found files list
```

### PCAP Analysis Flow
```
User enters PCAP path, clicks "Analyze"
    → Frontend: GET /api/network/pcap?path=...
    → Backend: scapy.rdpcap() loads the file
    → Each IP packet analyzed: proto, flags, ports, DNS queries
    → C2 port heuristic applied (4444, 9999, 31337, etc.)
    → Response: packets[], protocol_distribution[], ip_stats[]
    → Frontend: renders packet table, DNS log, IP intelligence
```

### Evidence Locker Flow
```
User clicks "Add Evidence"
    → Frontend: POST /api/evidence {name, type, tags, notes}
    → Backend: generates SHA-256 of (name + notes + timestamp)
    → Creates evidence record with chain-of-custody log entry
    → Persists to ~/.forenshield/evidence.json
    → Response: full evidence record with ID (EVD-YYYY-NNN)
    → User can POST /api/evidence/{eid}/verify to mark as verified
```

---

## Security Considerations

### CORS Policy
Currently set to `allow_origins=["*"]` for development.  
In production, restrict to the specific frontend origin:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://your-domain.com"],
    ...
)
```

### Privilege Requirements
- **Windows**: Run as Administrator for full process enumeration and network connection listing
- **Linux**: Run as root or use capability bits (`CAP_SYS_PTRACE`, `CAP_NET_ADMIN`)

### Evidence Integrity
- Evidence hashes are computed on the client + verified server-side
- Chain-of-custody log is append-only and timestamped
- Production deployments should use a signed database (SQLite with WAL, or PostgreSQL)

### Secure Erasure
- The erase endpoint uses Python's `os.urandom()` for CSPRNG random bytes
- `os.fsync()` is called after each pass to flush OS write buffers
- NAND flash (SSD) overwriting is inherently unreliable — use ATA Secure Erase for SSDs in production

---

## Module Boundaries

```
forenshield/
├── backend.py            # All 16 API sections (monolith for hackathon)
│
└── forenshield-react/
    └── src/
        ├── App.jsx              # Router + theme + toast provider
        ├── components/
        │   ├── Navbar.jsx       # Navigation sidebar
        │   └── Toast.jsx        # Notification component
        └── pages/
            ├── Dashboard.jsx        # System overview
            ├── MemoryForensics.jsx  # §2 — live processes + strings
            ├── NetworkForensics.jsx # §3 — connections + PCAP
            ├── DiskAnalyzer.jsx     # §4 — partitions + SMART
            ├── Timeline.jsx         # §5 — MAC timeline + timestomping
            ├── HashAnalyzer.jsx     # §6 — hashes + entropy + magic
            ├── HexViewer.jsx        # §7 — binary inspector
            ├── FileRecovery.jsx     # §8 — file carving UI
            ├── DriveEraser.jsx      # §9 — secure erase UI
            ├── FileEraser.jsx       # §9 — per-file erase UI
            ├── EvidenceLocker.jsx   # §10 — chain of custody
            ├── Reports.jsx          # §11 — report generation
            └── Settings.jsx         # §12 — configuration UI
```
