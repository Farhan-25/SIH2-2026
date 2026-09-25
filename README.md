<div align="center">

<img src="https://img.shields.io/badge/Smart%20India%20Hackathon-2026-6366f1?style=for-the-badge&labelColor=0a0b0f" alt="SIH 2026"/>

# 🛡️ ForenShield v2.0

**Integrated Secure Data Erasure & Advanced Forensic File Recovery**

[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-6366f1?style=flat-square)](#)
[![Track](https://img.shields.io/badge/Track-Digital%20Forensics-f59e0b?style=flat-square)](#)
[![Standards](https://img.shields.io/badge/Standards-NIST%20%7C%20DoD%20%7C%20ISO-818cf8?style=flat-square)](#compliance)
[![Status](https://img.shields.io/badge/Status-Active%20Development-10b981?style=flat-square)](#)

*A unified software platform that integrates military-grade secure data sanitization with advanced forensic-grade file carving and recovery.*

[**Documentation**](pages/about.html) · [**Report Bug**](#contributing) · [**Request Feature**](#contributing)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Core Modules](#core-modules)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Compliance Standards](#compliance)
- [Architecture](#architecture)
- [Roadmap](#roadmap)
- [Team](#team)
- [License](#license)

---

## 🔍 Overview

ForenShield is a unified web-based frontend platform developed for the **Smart India Hackathon 2026** under the **Digital Forensics & Cybersecurity** track. It addresses the critical need for a single, comprehensive tool that replaces multiple disparate solutions used by:

- 🏛️ Law enforcement agencies
- 🔬 Digital forensic investigators
- 🔐 Cybersecurity professionals
- 🏢 Enterprise IT security teams
- 🏥 Healthcare & compliance officers

> **Note:** This repository contains the **frontend implementation** of ForenShield. The UI is production-ready and designed for integration with a backend forensic engine.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🗑️ **Secure Drive Eraser** | Military-grade full-disk sanitization with DoD 5220.22-M, Gutmann (35-pass), NIST 800-88 |
| 📂 **File & Folder Eraser** | Selective file-level deletion with metadata scrubbing, MFT entry wipe, and slack space overwrite |
| 🔄 **File Recovery** | AI-assisted forensic file carving with signature-based, structure, and fragment reassembly methods |
| 🔐 **Hash Analyzer** | MD5, SHA-1, SHA-256, SHA-512, SHA-3 verification with file integrity comparison |
| 💽 **Disk Analyzer** | SMART data analysis, bad sector mapping, drive health reporting |
| 📊 **Reports** | Cryptographically-signed, chain-of-custody forensic audit reports with PDF export |
| ⚙️ **Settings** | Granular configuration for erasure algorithms, compliance profiles, audit logging, and security |
| 🌙 **Dark/Light Mode** | Full system-level theme support with preference persistence |

---

## 🧩 Core Modules

### Module 01 — Secure Drive Eraser
Low-level sector-by-sector overwrite engine with hardware command support.
- ATA Secure Erase & Enhanced Secure Erase
- NVMe Format NVM command
- SCSI SANITIZE command
- Multi-pass overwrite (1–35 passes)
- Bad sector mapping and handling
- Post-erase cryptographic verification

### Module 02 — File & Folder Eraser
File-level selective deletion with full trace and metadata elimination.
- MFT (Master File Table) entry scrubbing
- Slack space overwrite
- Windows Registry cleaning
- EXIF & metadata wipe
- Recycle Bin purging
- Temp file & thumbnail elimination

### Module 03 — File Carving & Recovery
Forensic-grade recovery using multi-technique carving and AI classification.
- Signature-based file carving (47+ formats)
- File structure analysis
- AI-assisted hybrid recovery
- Fragment reassembly for fragmented files
- Chain-of-custody evidence tracking
- Confidence scoring per recovered file

### Module 04 — Hash Analyzer
Multi-algorithm cryptographic verification tool.
- Supports MD5, SHA-1, SHA-256, SHA-512, SHA-3-256
- File-to-hash comparison
- Batch file verification
- Hash database lookup
- Real-time computation progress

### Module 05 — Disk Analyzer
Comprehensive storage device health and usage analysis.
- SMART attribute monitoring
- Partition map visualization
- File system distribution charts
- Predictive failure analysis
- Bad sector heat map

---

## 🖥️ Tech Stack

| Layer | Technology |
|---|---|
| **UI Framework** | Vanilla HTML5 + CSS3 + JavaScript (ES2022+) |
| **Typography** | Inter (UI) + JetBrains Mono (code/data) via Google Fonts |
| **Styling** | Custom CSS with CSS Variables design system |
| **Animations** | CSS transitions + Web Animations API + IntersectionObserver |
| **Storage** | localStorage / sessionStorage for settings & session state |
| **Charts** | Pure SVG + CSS-driven data visualizations |
| **Icons** | Inline SVG (zero external dependency) |

---

## 📁 Project Structure

```
forenshield/
├── index.html                  # Dashboard (main entry point)
├── LICENSE                     # MIT License
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
│
├── css/
│   ├── styles.css              # Global design system, variables, layouts
│   └── pages.css               # Page-specific component styles
│
├── js/
│   ├── main.js                 # Dashboard logic, global utilities, toast system
│   ├── drive-eraser.js         # Drive sanitization UI logic
│   ├── file-eraser.js          # File/folder eraser UI logic
│   ├── file-recovery.js        # Recovery engine UI and carving logic
│   ├── hash-analyzer.js        # Hash computation and verification logic
│   ├── disk-analyzer.js        # Disk health and SMART data logic
│   ├── reports.js              # Report generation and export logic
│   └── settings.js             # Settings persistence and UI logic
│
└── pages/
    ├── drive-eraser.html       # Drive Eraser page
    ├── file-eraser.html        # File Eraser page
    ├── file-recovery.html      # File Recovery page
    ├── hash-analyzer.html      # Hash Analyzer page
    ├── disk-analyzer.html      # Disk Analyzer page
    ├── reports.html            # Reports & Audit Logs page
    ├── settings.html           # Settings page
    └── about.html              # Documentation & About page
```

---

## 🚀 Getting Started

ForenShield is a pure frontend application — **no build step or server required**.

### Prerequisites

- A modern web browser (Chrome 90+, Firefox 88+, Edge 90+, Safari 14+)
- Git (optional, for cloning)

### Quick Start

**Option 1 — Direct File Open**

```bash
# Clone the repository
git clone https://github.com/your-org/forenshield.git
cd forenshield

# Open in browser
start index.html          # Windows
open index.html           # macOS
xdg-open index.html       # Linux
```

**Option 2 — Local Dev Server (recommended)**

```bash
# Using Python
python -m http.server 8080

# Using Node.js
npx serve .

# Using VS Code
# Install "Live Server" extension → Right-click index.html → "Open with Live Server"
```

Then navigate to `http://localhost:8080` in your browser.

---

## 📐 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│        HTML5 Pages  ←→  CSS Design System  ←→  JS Modules   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    APPLICATION LAYER                         │
│   ForenShield.toast()  │  Settings API  │  Session Storage   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                 INTEGRATION LAYER  (Planned)                 │
│     REST API  │  WebSocket real-time  │  File System API     │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                    BACKEND ENGINE (TBD)                      │
│  Erasure Engine  │  Carving Engine  │  Hash Engine  │  SMART │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Compliance

ForenShield is designed to comply with the following standards:

| Standard | Domain | Status |
|---|---|---|
| **NIST SP 800-88 Rev. 1** | Media Sanitization | ✅ Implemented |
| **DoD 5220.22-M** | Defense Data Destruction | ✅ Implemented |
| **IEEE 2883-2022** | Storage Device Sanitization | ✅ Implemented |
| **ISO/IEC 27001:2022** | Information Security Management | ✅ Implemented |
| **GDPR Article 17** | Right to Erasure | ✅ Implemented |
| **HIPAA Security Rule** | Healthcare Data Protection | ✅ Implemented |
| **PCI-DSS v4.0** | Payment Card Industry | ✅ Implemented |
| **SOX Section 802** | Financial Records | ✅ Implemented |
| **HMG IS5** | UK Government Sanitization | ✅ Implemented |

---

## 🗺️ Roadmap

- [x] Dashboard with real-time activity feed
- [x] Drive Eraser UI with algorithm selector
- [x] File & Folder Eraser with target queue
- [x] File Recovery with confidence scoring
- [x] Hash Analyzer with multi-algorithm support
- [x] Disk Analyzer with SMART data visualization
- [x] Reports with audit trail
- [x] Settings with full compliance profiles
- [x] Light/Dark theme with persistence
- [ ] Backend API integration (Node.js / Python)
- [ ] Electron desktop app wrapper
- [ ] Real-time WebSocket progress streaming
- [ ] PDF report generation (server-side)
- [ ] Plugin system for custom erasure algorithms
- [ ] Multi-language (i18n) support
- [ ] Role-based access control (RBAC)

---

## 👥 Team

Built for **Smart India Hackathon 2026** — Digital Forensics & Cybersecurity Track.

| Role | Responsibility |
|---|---|
| Frontend Development | UI/UX, CSS Design System, JavaScript Logic |
| Forensic Research | Compliance standards, algorithm research |
| Architecture | System design, API integration planning |

---

## 📄 License

Copyright © 2026 ForenShield Team.  
This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ for SIH 2026 · Digital Forensics & Cybersecurity Track

**[⬆ Back to Top](#)**

</div>
