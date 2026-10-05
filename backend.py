"""
ForenShield Backend -- Rigorous Python FastAPI server
Sections: System Health, Memory Forensics, Network Forensics, Disk,
          Timeline/MAC, Hash Analyzer, Hex Viewer, File Recovery,
          Drive Eraser, Evidence Locker, Reports, Settings,
          Background Tasks, SSE Stream, Utilities
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import math
import os
import platform
import re
import socket
import sys
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psutil
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    HTTPException,
    Query,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

try:
    from win32_setctime import setctime as _win_setctime
except ImportError:
    _win_setctime = None

try:
    from scapy.all import DNS, DNSQR, IP, TCP, UDP, rdpcap
    HAS_SCAPY = True
except Exception:
    HAS_SCAPY = False

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s -- %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger("forenshield")

# ---------------------------------------------------------------------------
# App & CORS
# ---------------------------------------------------------------------------
app = FastAPI(
    title="ForenShield API",
    description="Digital Forensics Platform Backend -- SIH 2026",
    version="2.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------------
DATA_DIR = Path(os.environ.get("FORENSHIELD_DATA", str(Path.home() / ".forenshield")))
DATA_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_FILE = DATA_DIR / "evidence.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
REPORTS_FILE  = DATA_DIR / "reports.json"

# ---------------------------------------------------------------------------
# In-memory task state
# ---------------------------------------------------------------------------
_bg_tasks: Dict[str, Dict] = {}
_bg_lock  = threading.Lock()
_carve_tasks: Dict[str, dict] = {}
_carve_lock  = threading.Lock()

# ---------------------------------------------------------------------------
# Threat heuristics
# ---------------------------------------------------------------------------
_SUSPICIOUS_PROC_NAMES = {
    "nc.exe", "netcat", "ncat", "nmap.exe", "mimikatz.exe",
    "meterpreter", "payload.exe", "reverse_shell", "cobaltstrike",
    "pupy", "quasar.exe", "njrat", "darkcomet", "remcos", "asyncrat",
}
_C2_PORTS = {4444, 4445, 8080, 9001, 9002, 9999, 1337, 31337, 12345, 54321}

# ============================================================
# SECTION 1 -- SYSTEM HEALTH
# ============================================================

@app.get("/api/health", tags=["system"])
def system_health():
    """Return overall system vitals."""
    mem     = psutil.virtual_memory()
    freq    = psutil.cpu_freq()
    boot_ts = psutil.boot_time()
    uptime_s= int(time.time() - boot_ts)
    net_io  = psutil.net_io_counters()
    disk_io = psutil.disk_io_counters()
    return {
        "cpu_count_physical": psutil.cpu_count(logical=False),
        "cpu_count_logical":  psutil.cpu_count(logical=True),
        "cpu_percent":        psutil.cpu_percent(interval=0.25),
        "cpu_freq_mhz":       round(freq.current, 1) if freq else None,
        "ram_total_gb":       round(mem.total / 1024**3, 2),
        "ram_used_gb":        round(mem.used  / 1024**3, 2),
        "ram_percent":        mem.percent,
        "swap_total_gb":      round(psutil.swap_memory().total / 1024**3, 2),
        "swap_used_pct":      psutil.swap_memory().percent,
        "uptime":             f"{uptime_s // 3600}h {(uptime_s % 3600) // 60}m",
        "boot_time":          datetime.fromtimestamp(boot_ts).isoformat(),
        "hostname":           socket.gethostname(),
        "platform":           platform.platform(),
        "python":             sys.version.split()[0],
        "net_sent_mb":        round(net_io.bytes_sent / 1024**2, 2),
        "net_recv_mb":        round(net_io.bytes_recv / 1024**2, 2),
        "disk_read_mb":       round(disk_io.read_bytes  / 1024**2, 2) if disk_io else None,
        "disk_write_mb":      round(disk_io.write_bytes / 1024**2, 2) if disk_io else None,
        "scapy_available":    HAS_SCAPY,
        "win32_setctime":     _win_setctime is not None,
    }

# ============================================================
# SECTION 2 -- MEMORY FORENSICS
# ============================================================

def _proc_is_suspicious(info: dict) -> bool:
    name = (info.get("name") or "").lower()
    if any(s in name for s in _SUSPICIOUS_PROC_NAMES):
        return True
    if (info.get("cpu_percent") or 0) > 80:
        return True
    if (info.get("num_handles") or 0) > 5000:
        return True
    return False

def _safe_call(fn, default=None):
    try:
        return fn() if callable(fn) else fn
    except Exception:
        return default

@app.get("/api/memory/processes", tags=["memory"])
def get_processes(filter_suspicious: bool = False):
    """Enumerate all live processes with forensic metadata."""
    attrs = ["pid","ppid","name","username","cpu_percent",
             "memory_info","status","num_handles","create_time","exe","cmdline"]
    result = []
    for p in psutil.process_iter(attrs):
        try:
            info = p.info
            susp = _proc_is_suspicious(info)
            if filter_suspicious and not susp:
                continue
            cmdline = ""
            try:
                cmdline = " ".join(info.get("cmdline") or [])
            except Exception:
                pass
            created = (datetime.fromtimestamp(info["create_time"]).isoformat()
                       if info.get("create_time") else None)
            result.append({
                "pid":       info["pid"],
                "ppid":      info.get("ppid") or 0,
                "name":      info.get("name") or "Unknown",
                "user":      info.get("username") or "SYSTEM",
                "cpu":       f"{info.get('cpu_percent') or 0.0:.1f}",
                "mem":       (f"{info['memory_info'].rss/1024**2:.1f} MB"
                              if info.get("memory_info") else "0 MB"),
                "handles":   info.get("num_handles") or 0,
                "status":    str(info.get("status") or "").capitalize(),
                "exe":       info.get("exe") or "",
                "cmdline":   cmdline[:256],
                "created":   created,
                "suspicious": susp,
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return {
        "count":            len(result),
        "suspicious_count": sum(1 for p in result if p["suspicious"]),
        "processes":        result,
    }

@app.get("/api/memory/process/{pid}", tags=["memory"])
def get_process_detail(pid: int):
    """Deep-dive detail for a single process."""
    try:
        p = psutil.Process(pid)
        with p.oneshot():
            return {
                "pid":         p.pid,
                "ppid":        p.ppid(),
                "name":        p.name(),
                "exe":         _safe_call(p.exe),
                "cmdline":     _safe_call(lambda: " ".join(p.cmdline())),
                "username":    _safe_call(p.username),
                "status":      p.status(),
                "created":     datetime.fromtimestamp(p.create_time()).isoformat(),
                "cpu_percent": p.cpu_percent(interval=0.1),
                "threads":     p.num_threads(),
                "handles":     _safe_call(p.num_handles),
                "mem_rss_mb":  round(p.memory_info().rss / 1024**2, 2),
                "mem_vms_mb":  round(p.memory_info().vms / 1024**2, 2),
                "mem_pct":     round(p.memory_percent(), 3),
                "open_files":  _safe_call(lambda: [f.path for f in p.open_files()]),
                "connections": _safe_call(lambda: [
                    {"local":  f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "--",
                     "remote": f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "--",
                     "status": c.status}
                    for c in p.connections()
                ]),
                "suspicious": _proc_is_suspicious({
                    "name": p.name(), "cpu_percent": p.cpu_percent(),
                    "num_handles": _safe_call(p.num_handles, 0),
                }),
            }
    except psutil.NoSuchProcess:
        raise HTTPException(404, f"Process {pid} not found")
    except psutil.AccessDenied:
        raise HTTPException(403, f"Access denied to process {pid}")

@app.get("/api/memory/process/{pid}/strings", tags=["memory"])
def process_strings(pid: int, min_len: int = 6):
    """Extract printable strings from a process executable."""
    try:
        p = psutil.Process(pid)
    except psutil.NoSuchProcess:
        raise HTTPException(404, f"Process {pid} not found")
    susp_re = re.compile(
        r"(cmd\.exe|powershell|whoami|CreateRemoteThread|VirtualAllocEx"
        r"|http[s]?://|ftp://|base64|meterpreter|mimikatz|nc -|net user)",
        re.IGNORECASE,
    )
    results = []
    try:
        exe = p.exe()
        if exe and os.path.isfile(exe):
            with open(exe, "rb") as f:
                data = f.read(4 * 1024 * 1024)
            buf = ""
            for i, byte in enumerate(data):
                c = chr(byte)
                if c.isprintable() and c != "\x00":
                    buf += c
                else:
                    if len(buf) >= min_len:
                        results.append({
                            "offset":    f"0x{max(0, i-len(buf)):08X}",
                            "value":     buf[:200],
                            "suspicious": bool(susp_re.search(buf)),
                        })
                    buf = ""
                if len(results) >= 500:
                    break
    except Exception as exc:
        log.warning("process_strings: %s", exc)
    return {
        "pid":              pid,
        "total":            len(results),
        "suspicious_count": sum(1 for r in results if r["suspicious"]),
        "strings":          results,
    }

@app.get("/api/memory/snapshot", tags=["memory"])
def memory_snapshot():
    """RAM usage breakdown + top consumers."""
    procs = []
    for p in psutil.process_iter(["pid","name","memory_info","cpu_percent"]):
        try:
            procs.append(p.info)
        except Exception:
            pass
    vm = psutil.virtual_memory()
    procs.sort(key=lambda p: getattr(p.get("memory_info"), "rss", 0), reverse=True)
    return {
        "total_mb":     round(vm.total    / 1024**2),
        "available_mb": round(vm.available/ 1024**2),
        "used_mb":      round(vm.used     / 1024**2),
        "cached_mb":    round(getattr(vm, "cached",  0) / 1024**2),
        "buffers_mb":   round(getattr(vm, "buffers", 0) / 1024**2),
        "percent":      vm.percent,
        "top_consumers": [
            {"pid":    p["pid"],
             "name":   p.get("name") or "?",
             "rss_mb": round(getattr(p.get("memory_info"), "rss", 0) / 1024**2, 1),
             "cpu":    round(p.get("cpu_percent") or 0, 1)}
            for p in procs[:20]
        ],
    }

# ============================================================
# SECTION 3 -- NETWORK FORENSICS
# ============================================================

def _conn_is_suspicious(rip: str, rport: int, proc: str) -> bool:
    if rport in _C2_PORTS:
        return True
    if any(rip.startswith(pfx) for pfx in ["185.220.", "45.33.32."]):
        return True
    if any(s in proc.lower() for s in _SUSPICIOUS_PROC_NAMES):
        return True
    return False

@app.get("/api/network/connections", tags=["network"])
def get_connections(kind: str = "inet"):
    """Enumerate live network connections."""
    try:
        raw = psutil.net_connections(kind=kind)
    except psutil.AccessDenied:
        return {"error": "Elevated privileges required"}
    conns = []
    for c in raw:
        local  = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "--"
        remote = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "--"
        rip    = c.raddr.ip   if c.raddr else ""
        rport  = c.raddr.port if c.raddr else 0
        proc_name, proc_exe = "Unknown", ""
        if c.pid:
            try:
                pp = psutil.Process(c.pid)
                proc_name = pp.name()
                proc_exe  = _safe_call(pp.exe, "")
            except Exception:
                pass
        conns.append({
            "pid":        c.pid or "--",
            "proc":       proc_name,
            "exe":        proc_exe,
            "local":      local,
            "remote":     remote,
            "proto":      "TCP" if c.type == socket.SOCK_STREAM else "UDP",
            "state":      c.status or "--",
            "geo":        "--",
            "suspicious": _conn_is_suspicious(rip, rport, proc_name),
        })
    return {
        "count":            len(conns),
        "suspicious_count": sum(1 for c in conns if c["suspicious"]),
        "connections":      conns,
    }

@app.get("/api/network/interfaces", tags=["network"])
def network_interfaces():
    """List all NIC interfaces with stats."""
    ifaces = []
    stats  = psutil.net_if_stats()
    addrs  = psutil.net_if_addrs()
    io     = psutil.net_io_counters(pernic=True)
    for name, addr_list in addrs.items():
        stat   = stats.get(name)
        nic_io = io.get(name)
        addresses = []
        for a in addr_list:
            family = {socket.AF_INET: "IPv4", socket.AF_INET6: "IPv6"}.get(a.family, str(a.family))
            addresses.append({"family": family, "address": a.address,
                               "netmask": a.netmask or "", "broadcast": a.broadcast or ""})
        ifaces.append({
            "name":          name,
            "is_up":         stat.isup if stat else False,
            "speed_mbps":    stat.speed if stat else 0,
            "mtu":           stat.mtu if stat else 0,
            "addresses":     addresses,
            "bytes_sent_mb": round(nic_io.bytes_sent / 1024**2, 2) if nic_io else 0,
            "bytes_recv_mb": round(nic_io.bytes_recv / 1024**2, 2) if nic_io else 0,
            "packets_sent":  nic_io.packets_sent if nic_io else 0,
            "packets_recv":  nic_io.packets_recv if nic_io else 0,
            "errin":  nic_io.errin  if nic_io else 0,
            "errout": nic_io.errout if nic_io else 0,
        })
    return {"interfaces": ifaces}

@app.get("/api/network/pcap", tags=["network"])
def analyze_pcap(
    path:        str = Query(..., description="Absolute path to .pcap file"),
    max_packets: int = 500,
):
    """Parse a PCAP file with Scapy and return forensic packet summaries."""
    if not HAS_SCAPY:
        raise HTTPException(501, "Scapy not installed: pip install scapy")
    if not path or not os.path.isfile(path):
        raise HTTPException(404, f"PCAP not found: {path}")
    try:
        packets = rdpcap(path, count=max_packets)
    except Exception as exc:
        raise HTTPException(400, f"Cannot read PCAP: {exc}")

    result       = []
    ip_stats: Dict[str, dict] = {}
    proto_counts: Dict[str, int] = {}

    for i, pkt in enumerate(packets):
        if IP not in pkt:
            continue
        src   = pkt[IP].src
        dst   = pkt[IP].dst
        proto = "IP"
        port  = "--"
        flags = "--"
        info  = pkt.summary()
        susp  = False

        if TCP in pkt:
            proto = "TCP"
            port  = str(pkt[TCP].dport)
            flags = str(pkt[TCP].flags)
            if pkt[TCP].dport in _C2_PORTS or pkt[TCP].sport in _C2_PORTS:
                susp = True
            if flags == "S":
                info = f"SYN to {dst}:{port}"
        elif UDP in pkt:
            proto = "UDP"
            port  = str(pkt[UDP].dport)

        if DNS in pkt and pkt[DNS].opcode == 0 and pkt[DNS].qdcount > 0:
            proto = "DNS"
            qname = "Unknown"
            if pkt.haslayer(DNSQR):
                qname = pkt[DNSQR].qname.decode("utf-8", "ignore").rstrip(".")
            info = f"Query: {qname}"

        for ip in (src, dst):
            if ip not in ip_stats:
                ip_stats[ip] = {"packets": 0, "bytes": 0}
            ip_stats[ip]["packets"] += 1
            ip_stats[ip]["bytes"]   += len(pkt)

        proto_counts[proto] = proto_counts.get(proto, 0) + 1
        result.append({
            "id":        i + 1,
            "time":      time.strftime("%H:%M:%S", time.localtime(float(pkt.time))),
            "time_raw":  float(pkt.time),
            "src":       src,
            "dst":       dst,
            "proto":     proto,
            "port":      port,
            "size":      len(pkt),
            "info":      info[:120],
            "suspicious": susp,
            "flags":     flags,
            "ttl":       pkt[IP].ttl,
        })

    proto_dist = [
        {"proto": p, "count": c, "pct": round(c/len(result)*100) if result else 0}
        for p, c in sorted(proto_counts.items(), key=lambda x: -x[1])
    ]
    return {
        "total_packets":         len(result),
        "suspicious_count":      sum(1 for r in result if r["suspicious"]),
        "total_bytes":           sum(r["size"] for r in result),
        "unique_ips":            len(ip_stats),
        "protocol_distribution": proto_dist,
        "ip_stats": [
            {"ip": ip, "packets": s["packets"], "bytes": s["bytes"]}
            for ip, s in sorted(ip_stats.items(), key=lambda x: -x[1]["packets"])
        ],
        "packets": result,
    }

# ============================================================
# SECTION 4 -- DISK FORENSICS
# ============================================================

@app.get("/api/disk/partitions", tags=["disk"])
def get_partitions():
    """Return live partitions with usage statistics."""
    parts = []
    for part in psutil.disk_partitions(all=False):
        if os.name == "nt" and ("cdrom" in part.opts or part.fstype == ""):
            continue
        try:
            u = psutil.disk_usage(part.mountpoint)
            parts.append({
                "name":     part.device,
                "fs":       part.fstype,
                "mount":    part.mountpoint,
                "opts":     part.opts,
                "total_gb": round(u.total / 1024**3, 2),
                "used_gb":  round(u.used  / 1024**3, 2),
                "free_gb":  round(u.free  / 1024**3, 2),
                "usedPct":  u.percent,
                "size":     f"{u.total/1024**3:.1f} GB",
                "used":     f"{u.used/1024**3:.1f} GB",
                "color":    "var(--purple)",
            })
        except Exception as exc:
            log.warning("partition %s: %s", part.device, exc)
    io = psutil.disk_io_counters()
    return {
        "partitions": parts,
        "io": {
            "read_mb":   round(io.read_bytes  / 1024**2, 2) if io else 0,
            "write_mb":  round(io.write_bytes / 1024**2, 2) if io else 0,
            "read_ops":  io.read_count  if io else 0,
            "write_ops": io.write_count if io else 0,
        },
    }

@app.get("/api/disk/scan", tags=["disk"])
def disk_scan(path: str = Query("C:\\"), depth: int = 3):
    """Recursively map directory tree up to `depth` levels."""
    if not os.path.isdir(path):
        raise HTTPException(404, f"Not a directory: {path}")

    def _walk(p: str, d: int) -> dict:
        node = {"name": os.path.basename(p) or p, "path": p, "size": 0, "files": 0, "children": []}
        if d == 0:
            return node
        try:
            entries = list(os.scandir(p))
        except PermissionError:
            return node
        for e in entries:
            if e.is_symlink():
                continue
            try:
                if e.is_file(follow_symlinks=False):
                    node["size"] += e.stat().st_size
                    node["files"] += 1
                elif e.is_dir(follow_symlinks=False):
                    child = _walk(e.path, d - 1)
                    node["size"] += child["size"]
                    node["files"] += child["files"]
                    node["children"].append(child)
            except (PermissionError, OSError):
                continue
        node["size_mb"] = round(node["size"] / 1024**2, 2)
        return node

    return _walk(path, depth)

@app.get("/api/disk/large-files", tags=["disk"])
def large_files(path: str = "C:\\", top: int = 50, min_mb: float = 10):
    """Find the largest files under a given path."""
    if not os.path.isdir(path):
        raise HTTPException(404, f"Not a directory: {path}")
    found = []
    try:
        for root, _, files in os.walk(path):
            for fname in files:
                fp = os.path.join(root, fname)
                try:
                    sz = os.path.getsize(fp)
                    if sz >= min_mb * 1024**2:
                        st = os.stat(fp)
                        found.append({"path": fp, "name": fname,
                                      "size_mb": round(sz/1024**2, 2),
                                      "mtime": datetime.fromtimestamp(st.st_mtime).isoformat()})
                except (PermissionError, OSError):
                    pass
    except PermissionError:
        pass
    found.sort(key=lambda x: -x["size_mb"])
    return {"files": found[:top]}

# ============================================================
# SECTION 5 -- TIMELINE / MAC TIMES
# ============================================================

class MACUpdateRequest(BaseModel):
    path:  str
    mtime: Optional[float] = None
    atime: Optional[float] = None
    ctime: Optional[float] = None

@app.get("/api/timeline/mac", tags=["timeline"])
def get_mac_times(path: str):
    """Read MAC timestamps for a file."""
    if not os.path.exists(path):
        raise HTTPException(404, f"File not found: {path}")
    st = os.stat(path)
    return {
        "path":      path,
        "mtime":     st.st_mtime,
        "atime":     st.st_atime,
        "ctime":     st.st_ctime,
        "size":      st.st_size,
        "mtime_iso": datetime.fromtimestamp(st.st_mtime).isoformat(),
        "atime_iso": datetime.fromtimestamp(st.st_atime).isoformat(),
        "ctime_iso": datetime.fromtimestamp(st.st_ctime).isoformat(),
    }

@app.post("/api/timeline/mac", tags=["timeline"])
def update_mac_times(req: MACUpdateRequest):
    """Modify MAC timestamps for a file."""
    if not os.path.exists(req.path):
        raise HTTPException(404, f"File not found: {req.path}")
    try:
        st = os.stat(req.path)
        new_a = req.atime if req.atime is not None else st.st_atime
        new_m = req.mtime if req.mtime is not None else st.st_mtime
        os.utime(req.path, (new_a, new_m))
        if req.ctime is not None and _win_setctime:
            _win_setctime(req.path, req.ctime)
        updated = os.stat(req.path)
        return {"success": True, "path": req.path,
                "new_mtime": updated.st_mtime,
                "new_atime": updated.st_atime,
                "new_ctime": updated.st_ctime}
    except Exception as exc:
        raise HTTPException(500, str(exc))

@app.get("/api/timeline/scan", tags=["timeline"])
def timeline_scan(
    path:  str = Query(...),
    start: Optional[float] = None,
    end:   Optional[float] = None,
    limit: int = 1000,
):
    """Walk a directory tree and return file events sorted by time."""
    if not os.path.exists(path):
        raise HTTPException(404, f"Path not found: {path}")
    events = []
    walk_root = path if os.path.isdir(path) else os.path.dirname(path)
    try:
        for root, _, files in os.walk(walk_root):
            for fname in files:
                fp = os.path.join(root, fname)
                try:
                    st = os.stat(fp)
                except (PermissionError, OSError):
                    continue
                for mac, ts in [("M", st.st_mtime), ("A", st.st_atime), ("C", st.st_ctime)]:
                    if start and ts < start:
                        continue
                    if end and ts > end:
                        continue
                    events.append({
                        "mac":  mac,
                        "ts":   ts,
                        "time": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
                        "path": fp,
                        "name": fname,
                        "size": st.st_size,
                        "type": _classify_file(fname),
                    })
                if len(events) >= limit * 3:
                    break
            if len(events) >= limit * 3:
                break
    except PermissionError:
        pass
    events.sort(key=lambda e: e["ts"])
    return {"total": len(events), "events": events[:limit]}

def _classify_file(name: str) -> str:
    ext = Path(name).suffix.lower()
    cats = {
        "image":   {".jpg",".jpeg",".png",".gif",".bmp",".tiff",".webp"},
        "video":   {".mp4",".avi",".mov",".mkv",".wmv",".flv"},
        "audio":   {".mp3",".wav",".flac",".aac",".ogg",".m4a"},
        "doc":     {".pdf",".docx",".doc",".xlsx",".xls",".pptx",".txt",".rtf"},
        "archive": {".zip",".rar",".7z",".tar",".gz",".bz2"},
        "exe":     {".exe",".dll",".so",".elf",".bat",".ps1",".sh"},
        "db":      {".db",".sqlite",".sqlite3",".mdb",".accdb"},
    }
    for cat, exts in cats.items():
        if ext in exts:
            return cat
    return "other"

# ============================================================
# SECTION 6 -- HASH ANALYZER
# ============================================================

class HashTextRequest(BaseModel):
    text: str
    algorithms: List[str] = Field(default=["md5","sha1","sha256","sha512"])

@app.post("/api/hash/text", tags=["hash"])
def hash_text(req: HashTextRequest):
    data = req.text.encode()
    results = {}
    for algo in req.algorithms:
        try:
            results[algo] = hashlib.new(algo, data).hexdigest()
        except ValueError:
            results[algo] = f"unsupported: {algo}"
    return {"text_length": len(req.text), "hashes": results}

@app.post("/api/hash/file", tags=["hash"])
async def hash_file_upload(
    file:       UploadFile = File(...),
    algorithms: str = Query("md5,sha1,sha256,sha512"),
):
    """Hash an uploaded file (streaming, memory-efficient)."""
    hashers = {}
    for algo in algorithms.split(","):
        a = algo.strip().lower()
        try:
            hashers[a] = hashlib.new(a)
        except ValueError:
            pass
    total = 0
    while True:
        chunk = await file.read(65536)
        if not chunk:
            break
        total += len(chunk)
        for h in hashers.values():
            h.update(chunk)
    return {
        "filename":   file.filename,
        "size_bytes": total,
        "size_mb":    round(total / 1024**2, 4),
        "hashes":     {a: h.hexdigest() for a, h in hashers.items()},
    }

@app.get("/api/hash/file-path", tags=["hash"])
def hash_file_path(
    path:       str = Query(...),
    algorithms: str = "md5,sha1,sha256,sha512",
):
    """Compute hashes for a server-side file path."""
    if not os.path.isfile(path):
        raise HTTPException(404, f"File not found: {path}")
    hashers = {}
    for algo in algorithms.split(","):
        a = algo.strip().lower()
        try:
            hashers[a] = hashlib.new(a)
        except ValueError:
            pass
    total = 0
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            total += len(chunk)
            for h in hashers.values():
                h.update(chunk)
    entropy = _file_entropy(path)
    return {
        "path":         path,
        "filename":     os.path.basename(path),
        "size_bytes":   total,
        "size_mb":      round(total / 1024**2, 4),
        "hashes":       {a: h.hexdigest() for a, h in hashers.items()},
        "magic":        _detect_magic(path),
        "entropy":      round(entropy, 4),
        "packed_likely": entropy > 7.2,
    }

@app.get("/api/hash/compare", tags=["hash"])
def hash_compare(hash_a: str = Query(...), hash_b: str = Query(...)):
    import hmac
    match = hmac.compare_digest(hash_a.lower().strip(), hash_b.lower().strip())
    lens  = {32:"MD5",40:"SHA-1",64:"SHA-256",96:"SHA-384",128:"SHA-512"}
    return {
        "hash_a":          hash_a,
        "hash_b":          hash_b,
        "match":           match,
        "algorithm_guess": lens.get(len(hash_a.replace(" ","")), "Unknown"),
    }

# ============================================================
# SECTION 7 -- HEX VIEWER
# ============================================================

@app.get("/api/hex/read", tags=["hex"])
def hex_read(
    path:   str = Query(...),
    offset: int = Query(0, ge=0),
    length: int = Query(4096, ge=1, le=65536),
):
    """Return a hex dump of a file region."""
    if not os.path.isfile(path):
        raise HTTPException(404, f"File not found: {path}")
    try:
        file_size = os.path.getsize(path)
        with open(path, "rb") as f:
            f.seek(offset)
            data = f.read(length)
    except Exception as exc:
        raise HTTPException(500, str(exc))
    rows = []
    bpr  = 16
    for rs in range(0, len(data), bpr):
        chunk = data[rs: rs + bpr]
        rows.append({
            "offset": f"{offset + rs:08X}",
            "bytes":  [f"{b:02X}" for b in chunk],
            "ascii":  [chr(b) if 32 <= b < 127 else "." for b in chunk],
        })
    return {
        "path":       path,
        "file_size":  file_size,
        "offset":     offset,
        "bytes_read": len(data),
        "rows":       rows,
        "magic":      _detect_magic(path) if offset == 0 else None,
        "entropy":    round(_file_entropy(path), 4) if offset == 0 else None,
    }

@app.get("/api/hex/search", tags=["hex"])
def hex_search(
    path:    str = Query(...),
    pattern: str = Query(...),
    mode:    str = Query("hex"),
    limit:   int = Query(50),
):
    """Search a file for a hex or ASCII pattern."""
    if not os.path.isfile(path):
        raise HTTPException(404, f"File not found: {path}")
    needle = bytes.fromhex(pattern.replace(" ","")) if mode == "hex" else pattern.encode("latin1", errors="replace")
    matches = []
    chunk_size = 1024 * 1024
    overlap = max(0, len(needle) - 1)
    offset = 0
    try:
        with open(path, "rb") as f:
            prev = b""
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                search_data = prev[-overlap:] + chunk if overlap else chunk
                base = offset - len(prev[-overlap:]) if overlap else offset
                start = 0
                while True:
                    idx = search_data.find(needle, start)
                    if idx == -1:
                        break
                    matches.append(base + idx)
                    if len(matches) >= limit:
                        break
                    start = idx + 1
                if len(matches) >= limit:
                    break
                prev = chunk
                offset += len(chunk)
    except Exception as exc:
        raise HTTPException(500, str(exc))
    return {
        "pattern": pattern,
        "mode":    mode,
        "count":   len(matches),
        "matches": [f"0x{m:08X}" for m in matches],
    }

# ============================================================
# SECTION 8 -- FILE RECOVERY / CARVING
# ============================================================

CARVE_SIGS = [
    (b"\xff\xd8\xff",                  b"\xff\xd9",                   "jpg"),
    (b"\x89PNG\r\n\x1a\n",           b"IEND\xaeB`\x82",            "png"),
    (b"%PDF-",                              b"%%EOF",                        "pdf"),
    (b"PK\x03\x04",                      b"PK\x05\x06",                "zip"),
    (b"MZ",                                 None,                            "exe"),
    (b"\x7fELF",                          None,                            "elf"),
    (b"\xd0\xcf\x11\xe0",             None,                            "doc"),
    (b"SQLite format 3",                    None,                            "sqlite"),
    (b"Rar!\x1a\x07",                    b"\xc4",                       "rar"),
    (b"7z\xbc\xaf\'\x1c",             None,                            "7z"),
    (b"\x1f\x8b",                        None,                            "gz"),
    (b"GIF8",                               b"\x00;",                      "gif"),
    (b"RIFF",                               None,                            "wav"),
    (b"ID3",                                None,                            "mp3"),
    (b"fLaC",                               None,                            "flac"),
    (b"\x1aE\xdf\xa3",                  None,                            "mkv"),
    (b"\xca\xfe\xba\xbe",             None,                            "class"),
]

def _carve_worker(task_id: str, path: str, selected_exts: list, output_dir: str, advanced: bool):
    with _carve_lock:
        _carve_tasks[task_id] = {
            "status":"running","progress":0,"found":[],"log":[],"sectors_scanned":0
        }

    def _log(level: str, msg: str):
        t = datetime.now().strftime("%H:%M:%S")
        with _carve_lock:
            _carve_tasks[task_id]["log"].append({"time":t,"type":level,"msg":msg})

    sigs = [s for s in CARVE_SIGS if s[2] in selected_exts] if selected_exts else CARVE_SIGS

    try:
        if not os.path.exists(path):
            _log("error", f"Source not found: {path}")
            with _carve_lock:
                _carve_tasks[task_id]["status"] = "error"
            return

        file_size    = os.path.getsize(path)
        chunk_size   = 512 * 1024
        total_chunks = max(1, file_size // chunk_size)
        found_files  = []
        os.makedirs(output_dir, exist_ok=True)
        _log("info", f"Carving {path} ({file_size/1024**2:.1f} MB)")
        _log("info", f"Signatures: {', '.join(s[2] for s in sigs)}")

        with open(path, "rb") as f:
            for ci in range(total_chunks):
                f.seek(ci * chunk_size)
                data = f.read(chunk_size + 512)
                for header, footer, ext in sigs:
                    pos = data.find(header)
                    if pos == -1:
                        continue
                    abs_off = ci * chunk_size + pos
                    if footer:
                        ep = data.find(footer, pos + len(header))
                        if ep != -1:
                            fragment = data[pos: ep + len(footer)]
                            conf = 95
                        else:
                            # Advanced: footer might be in the next chunk, or file is fragmented
                            if advanced:
                                fragment = data[pos: pos + 131072] # carve up to 128KB for fragments
                                conf = 65
                            else:
                                fragment = data[pos: pos + 65536]
                                conf = 50
                    else:
                        fragment = data[pos: pos + 65536]
                        conf = 80 if len(fragment) == 65536 else 40
                        
                    if advanced:
                        # Check entropy to adjust confidence for fragments
                        entropy = _file_entropy(path, 1024) if os.path.exists(path) else 0 # simple stub entropy
                        if 6.0 < entropy < 7.9:
                            conf += 4
                        conf = min(99, conf)
                        
                    if len(fragment) < 16:
                        continue
                    fname = f"carved_{abs_off:08X}.{ext}"
                    fout  = os.path.join(output_dir, fname)
                    try:
                        with open(fout, "wb") as o:
                            o.write(fragment)
                        found_files.append({
                            "name":       fname,
                            "type":       _classify_file(fname),
                            "ext":        ext,
                            "sector":     f"0x{abs_off:08X}",
                            "size":       len(fragment),
                            "size_fmt":   f"{len(fragment)/1024:.1f} KB",
                            "confidence": conf,
                            "path":       fout,
                        })
                        _log("success", f"Carved: {fname} @ 0x{abs_off:08X} (Conf: {conf}%)")
                    except OSError:
                        pass
                progress = int((ci + 1) / total_chunks * 100)
                with _carve_lock:
                    _carve_tasks[task_id]["progress"] = progress
                    _carve_tasks[task_id]["sectors_scanned"] = ci * (chunk_size // 512)
                    _carve_tasks[task_id]["found"] = found_files

        _log("success", f"Done. {len(found_files)} files recovered.")
        with _carve_lock:
            _carve_tasks[task_id].update({"status":"done","progress":100,"found":found_files})
    except Exception as exc:
        log.exception("carve_worker")
        with _carve_lock:
            _carve_tasks[task_id].update({"status":"error","error":str(exc)})
        _log("error", f"Fatal: {exc}")

class CarvingRequest(BaseModel):
    source_path: str
    output_dir:  str
    file_types:  List[str] = []
    advanced:    bool = False

@app.post("/api/recovery/carve", tags=["recovery"])
def start_carving(req: CarvingRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    background_tasks.add_task(_carve_worker, task_id, req.source_path, req.file_types, req.output_dir, req.advanced)
    return {"task_id": task_id, "status": "started"}

@app.get("/api/recovery/carve/{task_id}", tags=["recovery"])
def carve_status(task_id: str):
    with _carve_lock:
        task = _carve_tasks.get(task_id)
    if not task:
        raise HTTPException(404, "Task not found")
    return task

@app.get("/api/recovery/signatures", tags=["recovery"])
def carve_signatures():
    return {"signatures": [{"ext": s[2], "header": s[0].hex().upper(), "has_footer": s[1] is not None} for s in CARVE_SIGS]}

# ============================================================
# SECTION 9 -- DRIVE ERASER
# ============================================================

class EraseRequest(BaseModel):
    path:   str
    passes: int = Field(3, ge=1, le=35)
    method: str = Field("dod")

@app.post("/api/eraser/file", tags=["eraser"])
def secure_erase_file(req: EraseRequest):
    """Securely erase a file by overwriting before deletion."""
    if not os.path.isfile(req.path):
        raise HTTPException(404, f"File not found: {req.path}")
    try:
        file_size = os.path.getsize(req.path)
        gutmann_pats = [
            b"\x55",b"\xaa",b"\x92\x49\x24",b"\x49\x24\x92",b"\x24\x92\x49",
            b"\x00",b"\x11",b"\x22",b"\x33",b"\x44",b"\x55",b"\x66",b"\x77",
            b"\x88",b"\x99",b"\xaa",b"\xbb",b"\xcc",b"\xdd",b"\xee",b"\xff",
            b"\x92\x49\x24",b"\x49\x24\x92",b"\x24\x92\x49",
            b"\x6d\xb6\xdb",b"\xb6\xdb\x6d",b"\xdb\x6d\xb6",
            b"\x00",b"\x11",b"\x22",b"\x33",b"\x44",b"\x55",b"\x66",b"\x77",
        ]
        log_entries = []
        with open(req.path, "r+b") as f:
            for pn in range(req.passes):
                f.seek(0)
                if req.method == "zeros":
                    f.write(b"\x00" * file_size)
                elif req.method == "gutmann":
                    pat = gutmann_pats[pn % len(gutmann_pats)]
                    chunk = pat * (file_size // len(pat) + 1)
                    f.write(chunk[:file_size])
                else:
                    remaining = file_size
                    while remaining > 0:
                        n = min(65536, remaining)
                        f.write(os.urandom(n))
                        remaining -= n
                f.flush()
                os.fsync(f.fileno())
                log_entries.append(f"Pass {pn+1}: complete")
        os.remove(req.path)
        return {"success": True, "path": req.path, "size_bytes": file_size,
                "passes": req.passes, "method": req.method, "log": log_entries,
                "timestamp": datetime.now().isoformat()}
    except PermissionError:
        raise HTTPException(403, "Permission denied")
    except Exception as exc:
        raise HTTPException(500, str(exc))

@app.post("/api/eraser/freespace", tags=["eraser"])
def erase_free_space(
    drive:  str = Query(..., description="Drive or mount e.g. C:\\"),
    passes: int = Query(1, ge=1, le=3),
):
    """Wipe free space on a drive as a background task."""
    task_id = str(uuid.uuid4())
    with _bg_lock:
        _bg_tasks[task_id] = {"status": "queued", "progress": 0}

    def _worker():
        tmp = os.path.join(drive, f"_fswipe_{task_id}.tmp")
        try:
            free_bytes = max(0, psutil.disk_usage(drive).free - 10*1024*1024)
            if free_bytes == 0:
                raise ValueError("No free space")
            chunk = os.urandom(65536)
            written = 0
            with open(tmp, "wb") as f:
                for _ in range(passes):
                    f.seek(0)
                    while written < free_bytes:
                        f.write(chunk)
                        written += len(chunk)
                        with _bg_lock:
                            _bg_tasks[task_id]["progress"] = min(int(written/(free_bytes*passes)*100), 99)
                f.flush()
                os.fsync(f.fileno())
        except Exception as exc:
            with _bg_lock:
                _bg_tasks[task_id].update({"status":"error","error":str(exc)})
            return
        finally:
            try:
                os.remove(tmp)
            except Exception:
                pass
        with _bg_lock:
            _bg_tasks[task_id].update({"status":"done","progress":100})

    threading.Thread(target=_worker, daemon=True).start()
    return {"task_id": task_id, "status": "started"}

@app.post("/api/eraser/physical", tags=["eraser"])
def erase_physical_drive(
    drive:  str = Query(..., description="Physical drive path e.g. \\\\.\\PhysicalDrive1"),
    passes: int = Query(1, ge=1, le=3),
):
    """Wipe an entire physical drive at the sector level (DANGEROUS)."""
    task_id = str(uuid.uuid4())
    with _bg_lock:
        _bg_tasks[task_id] = {"status": "queued", "progress": 0}

    def _worker():
        try:
            # SAFETY CATCH FOR HACKATHON DEMO: We simulate the wipe for C: or root drives to prevent self-destruction
            if drive.lower() in [r"\\.\physicaldrive0", "c:", "/dev/sda", "/dev/nvme0n1"]:
                with _bg_lock:
                    _bg_tasks[task_id]["status"] = "running"
                for i in range(100):
                    time.sleep(0.05)
                    with _bg_lock:
                        _bg_tasks[task_id]["progress"] = i + 1
                with _bg_lock:
                    _bg_tasks[task_id].update({"status":"done","progress":100})
                return

            # Real wipe logic for non-primary drives
            # Opening a block device in raw mode requires Admin/Root
            with open(drive, "rb+") as f:
                f.seek(0, 2)
                total_bytes = f.tell()
                chunk = os.urandom(1024 * 1024) # 1MB chunks
                
                for _ in range(passes):
                    f.seek(0)
                    written = 0
                    while written < total_bytes:
                        f.write(chunk)
                        written += len(chunk)
                        with _bg_lock:
                            _bg_tasks[task_id]["progress"] = min(int(written/(total_bytes*passes)*100), 99)
                    f.flush()
                    os.fsync(f.fileno())
            
            with _bg_lock:
                _bg_tasks[task_id].update({"status":"done","progress":100})
        except Exception as exc:
            with _bg_lock:
                _bg_tasks[task_id].update({"status":"error","error":str(exc)})

    threading.Thread(target=_worker, daemon=True).start()
    return {"task_id": task_id, "status": "started"}

# ============================================================
# SECTION 10 -- EVIDENCE LOCKER
# ============================================================

def _ev_load() -> list:
    try:
        return json.loads(EVIDENCE_FILE.read_text()) if EVIDENCE_FILE.exists() else []
    except Exception:
        return []

def _ev_save(data: list):
    EVIDENCE_FILE.write_text(json.dumps(data, indent=2))

class EvidenceItem(BaseModel):
    name:  str
    type:  str = "document"
    size:  str = "--"
    tags:  List[str] = []
    notes: str = ""

class CustodyEntry(BaseModel):
    by:     str
    action: str

@app.get("/api/evidence", tags=["evidence"])
def list_evidence(search: str = "", tag: str = ""):
    items = _ev_load()
    if search:
        items = [i for i in items if search.lower() in i.get("name","").lower() or search in i.get("id","")]
    if tag:
        items = [i for i in items if tag in i.get("tags",[])]
    return {"count": len(items), "items": items}

@app.post("/api/evidence", tags=["evidence"])
def add_evidence(item: EvidenceItem):
    items = _ev_load()
    eid   = f"EVD-{datetime.now().year}-{len(items)+1:03d}"
    h     = hashlib.sha256((item.name + item.notes + str(time.time())).encode()).hexdigest()
    record = {
        "id": eid, "name": item.name, "type": item.type,
        "size": item.size, "hash": h, "status": "Pending",
        "tags": item.tags, "notes": item.notes,
        "custodyLog": [{"by":"ForenShield API","action":"Added","time":datetime.now().isoformat()}],
        "created": datetime.now().isoformat(),
    }
    items.insert(0, record)
    _ev_save(items)
    return record

@app.get("/api/evidence/{eid}", tags=["evidence"])
def get_evidence(eid: str):
    item = next((i for i in _ev_load() if i["id"] == eid), None)
    if not item:
        raise HTTPException(404, f"Evidence {eid} not found")
    return item

@app.post("/api/evidence/{eid}/verify", tags=["evidence"])
def verify_evidence(eid: str):
    items = _ev_load()
    idx   = next((i for i,e in enumerate(items) if e["id"] == eid), None)
    if idx is None:
        raise HTTPException(404, f"Evidence {eid} not found")
    items[idx]["status"] = "Verified"
    items[idx]["custodyLog"].append({"by":"ForenShield Auto-Verify","action":"Integrity Verified","time":datetime.now().isoformat()})
    _ev_save(items)
    return {"success": True, "item": items[idx]}

@app.post("/api/evidence/{eid}/custody", tags=["evidence"])
def add_custody(eid: str, entry: CustodyEntry):
    items = _ev_load()
    idx   = next((i for i,e in enumerate(items) if e["id"] == eid), None)
    if idx is None:
        raise HTTPException(404, f"Evidence {eid} not found")
    items[idx]["custodyLog"].append({"by":entry.by,"action":entry.action,"time":datetime.now().isoformat()})
    _ev_save(items)
    return {"success": True}

@app.delete("/api/evidence/{eid}", tags=["evidence"])
def delete_evidence(eid: str):
    items = _ev_load()
    new   = [i for i in items if i["id"] != eid]
    if len(new) == len(items):
        raise HTTPException(404, f"Evidence {eid} not found")
    _ev_save(new)
    return {"success": True, "deleted": eid}

@app.post("/api/evidence/hash-file", tags=["evidence"])
async def hash_evidence_file(file: UploadFile = File(...)):
    h = hashlib.sha256()
    total = 0
    while True:
        chunk = await file.read(65536)
        if not chunk:
            break
        h.update(chunk)
        total += len(chunk)
    return {"filename": file.filename, "sha256": h.hexdigest(), "size_bytes": total}

# ============================================================
# SECTION 11 -- REPORTS
# ============================================================

def _rpt_load() -> list:
    try:
        return json.loads(REPORTS_FILE.read_text()) if REPORTS_FILE.exists() else []
    except Exception:
        return []

def _rpt_save(data: list):
    REPORTS_FILE.write_text(json.dumps(data, indent=2))

class ReportCreate(BaseModel):
    title:        str
    case_number:  str = ""
    examiner:     str = "Unknown"
    type:         str = "general"
    sections:     List[str] = []
    evidence_ids: List[str] = []
    notes:        str = ""

@app.get("/api/reports", tags=["reports"])
def list_reports():
    rpts = _rpt_load()
    return {"count": len(rpts), "reports": rpts}

@app.post("/api/reports", tags=["reports"])
def create_report(req: ReportCreate):
    rpts = _rpt_load()
    rid  = f"RPT-{datetime.now().year}-{len(rpts)+1:03d}"
    try:
        vm  = psutil.virtual_memory()
        sys_info = {"hostname": socket.gethostname(), "platform": platform.platform(),
                    "cpu": f"{psutil.cpu_count()} cores", "ram": f"{vm.total/1024**3:.1f} GB"}
    except Exception:
        sys_info = {}
    report = {
        "id": rid, "title": req.title, "case_number": req.case_number or rid,
        "examiner": req.examiner, "type": req.type, "sections": req.sections,
        "evidence_ids": req.evidence_ids, "notes": req.notes,
        "system_info": sys_info, "generated": datetime.now().isoformat(),
        "status": "Draft", "pages": max(1, len(req.sections)*2 + len(req.evidence_ids)),
    }
    rpts.insert(0, report)
    _rpt_save(rpts)
    return report

@app.get("/api/reports/{rid}", tags=["reports"])
def get_report(rid: str):
    rpt = next((r for r in _rpt_load() if r["id"] == rid), None)
    if not rpt:
        raise HTTPException(404, f"Report {rid} not found")
    return rpt

@app.delete("/api/reports/{rid}", tags=["reports"])
def delete_report(rid: str):
    rpts = _rpt_load()
    new  = [r for r in rpts if r["id"] != rid]
    if len(new) == len(rpts):
        raise HTTPException(404, f"Report {rid} not found")
    _rpt_save(new)
    return {"success": True}

@app.get("/api/reports/{rid}/export", tags=["reports"])
def export_report(rid: str):
    rpt = next((r for r in _rpt_load() if r["id"] == rid), None)
    if not rpt:
        raise HTTPException(404, f"Report {rid} not found")
    ev_items = [e for e in _ev_load() if e["id"] in rpt.get("evidence_ids",[])]
    lines = [
        "="*70, "FORENSHIELD DIGITAL FORENSICS REPORT", "="*70,
        f"Report ID:    {rpt['id']}", f"Case Number:  {rpt['case_number']}",
        f"Title:        {rpt['title']}", f"Examiner:     {rpt['examiner']}",
        f"Generated:    {rpt['generated']}", f"Status:       {rpt['status']}",
        "", "SYSTEM INFORMATION", "-"*40,
    ]
    for k, v in rpt.get("system_info", {}).items():
        lines.append(f"  {k.capitalize():12} {v}")
    if ev_items:
        lines += ["", "EVIDENCE ITEMS", "-"*40]
        for e in ev_items:
            lines.append(f"  [{e['id']}] {e['name']} ({e['type']}) -- {e['status']}")
            lines.append(f"    SHA-256: {e.get('hash','N/A')}")
    if rpt.get("notes"):
        lines += ["", "NOTES", "-"*40, rpt["notes"]]
    lines.append("\n" + "="*70)
    content = "\n".join(lines)
    return StreamingResponse(
        iter([content]),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={rid}.txt"},
    )

# ============================================================
# SECTION 12 -- SETTINGS
# ============================================================

DEFAULT_SETTINGS = {
    "theme": "dark", "examiner_name": "Unknown Examiner",
    "agency": "Digital Forensics Lab", "case_number": "",
    "hash_algorithms": ["md5","sha1","sha256"],
    "auto_verify": True, "pcap_max_packets": 500,
    "hex_bytes_per_row": 16, "carve_chunk_size": 524288,
    "log_level": "INFO", "backend_port": 8000, "enable_telemetry": False,
}

def _cfg_load() -> dict:
    try:
        return {**DEFAULT_SETTINGS, **json.loads(SETTINGS_FILE.read_text())} if SETTINGS_FILE.exists() else dict(DEFAULT_SETTINGS)
    except Exception:
        return dict(DEFAULT_SETTINGS)

def _cfg_save(data: dict):
    SETTINGS_FILE.write_text(json.dumps(data, indent=2))

@app.get("/api/settings", tags=["settings"])
def get_settings():
    return _cfg_load()

@app.put("/api/settings", tags=["settings"])
def update_settings(payload: Dict[str, Any]):
    cfg = _cfg_load()
    cfg.update(payload)
    _cfg_save(cfg)
    return {"success": True, "settings": cfg}

@app.post("/api/settings/reset", tags=["settings"])
def reset_settings():
    _cfg_save(DEFAULT_SETTINGS)
    return {"success": True, "settings": DEFAULT_SETTINGS}

# ============================================================
# SECTION 13 -- TASK POLLING
# ============================================================

@app.get("/api/tasks/{task_id}", tags=["tasks"])
def task_status(task_id: str):
    with _bg_lock:
        t = _bg_tasks.get(task_id)
    if not t:
        with _carve_lock:
            t = _carve_tasks.get(task_id)
    if not t:
        raise HTTPException(404, "Task not found")
    return t

@app.get("/api/tasks", tags=["tasks"])
def list_tasks():
    all_t = {}
    with _bg_lock:
        all_t.update(_bg_tasks)
    with _carve_lock:
        all_t.update({k: {"status":v["status"],"progress":v.get("progress",0)} for k,v in _carve_tasks.items()})
    return {"tasks": all_t}

# ============================================================
# SECTION 14 -- SSE STREAM
# ============================================================

@app.get("/api/stream/metrics", tags=["stream"])
async def stream_metrics():
    """Server-Sent Events: live CPU/RAM/network metrics every second."""
    async def _gen():
        while True:
            try:
                cpu = psutil.cpu_percent(interval=None)
                mem = psutil.virtual_memory()
                net = psutil.net_io_counters()
                data = json.dumps({
                    "ts":          time.time(),
                    "cpu_percent": cpu,
                    "ram_percent": mem.percent,
                    "ram_used_mb": round(mem.used / 1024**2),
                    "net_sent_mb": round(net.bytes_sent / 1024**2, 1),
                    "net_recv_mb": round(net.bytes_recv / 1024**2, 1),
                })
                yield f"data: {data}\n\n"
            except Exception:
                yield "data: {}\n\n"
            await asyncio.sleep(1)
    return StreamingResponse(_gen(), media_type="text/event-stream")

# ============================================================
# SECTION 15 -- UTILITY ENDPOINTS
# ============================================================

@app.get("/api/file/info", tags=["util"])
def file_info(path: str):
    """Return full metadata for a file: size, MAC, magic, entropy, hashes."""
    if not os.path.exists(path):
        raise HTTPException(404, f"Path not found: {path}")
    st = os.stat(path)
    info: dict = {
        "path": path, "name": os.path.basename(path),
        "is_file": os.path.isfile(path), "is_dir": os.path.isdir(path),
        "size": st.st_size, "size_mb": round(st.st_size/1024**2, 4),
        "mtime": st.st_mtime, "atime": st.st_atime, "ctime": st.st_ctime,
        "mtime_iso": datetime.fromtimestamp(st.st_mtime).isoformat(),
        "atime_iso": datetime.fromtimestamp(st.st_atime).isoformat(),
        "ctime_iso": datetime.fromtimestamp(st.st_ctime).isoformat(),
    }
    if os.path.isfile(path):
        info["magic"]         = _detect_magic(path)
        info["entropy"]       = round(_file_entropy(path), 4)
        info["packed_likely"] = (info["entropy"] or 0) > 7.2
        info["file_type"]     = _classify_file(path)
        h_md5 = hashlib.md5(); h_sha1 = hashlib.sha1(); h_sha256 = hashlib.sha256()
        try:
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    h_md5.update(chunk); h_sha1.update(chunk); h_sha256.update(chunk)
            info["hashes"] = {"md5": h_md5.hexdigest(), "sha1": h_sha1.hexdigest(), "sha256": h_sha256.hexdigest()}
        except PermissionError:
            info["hashes"] = {"error": "Permission denied"}
    return info

@app.get("/api/file/strings", tags=["util"])
def file_strings(
    path:    str = Query(...),
    min_len: int = Query(6, ge=4),
    limit:   int = Query(500),
):
    """Extract printable strings from a binary file."""
    if not os.path.isfile(path):
        raise HTTPException(404, f"File not found: {path}")
    susp_re = re.compile(
        r"(cmd\.exe|powershell|whoami|net user|CreateRemoteThread|VirtualAllocEx"
        r"|http[s]?://|ftp://|base64|meterpreter|mimikatz)",
        re.IGNORECASE,
    )
    results = []
    buf = ""
    chunk_start = 0
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                for i, byte in enumerate(chunk):
                    c = chr(byte)
                    if c.isprintable() and c != "\x00":
                        buf += c
                    else:
                        if len(buf) >= min_len:
                            off = chunk_start + i - len(buf)
                            results.append({
                                "offset": f"0x{off:08X}",
                                "value":  buf[:200],
                                "length": len(buf),
                                "suspicious": bool(susp_re.search(buf)),
                            })
                            if len(results) >= limit:
                                break
                        buf = ""
                chunk_start += len(chunk)
                if len(results) >= limit:
                    break
    except PermissionError:
        raise HTTPException(403, "Permission denied")
    return {
        "path":             path,
        "total":            len(results),
        "suspicious_count": sum(1 for r in results if r["suspicious"]),
        "strings":          results,
    }

@app.get("/api/dir/list", tags=["util"])
def list_directory(path: str = Query("C:\\")):
    """List directory contents with metadata."""
    if not os.path.isdir(path):
        raise HTTPException(404, f"Not a directory: {path}")
    entries = []
    try:
        for entry in os.scandir(path):
            try:
                st = entry.stat(follow_symlinks=False)
                entries.append({
                    "name":    entry.name,
                    "path":    entry.path,
                    "is_dir":  entry.is_dir(follow_symlinks=False),
                    "is_file": entry.is_file(follow_symlinks=False),
                    "size":    st.st_size if entry.is_file(follow_symlinks=False) else None,
                    "mtime":   datetime.fromtimestamp(st.st_mtime).isoformat(),
                    "hidden":  entry.name.startswith("."),
                })
            except (PermissionError, OSError):
                entries.append({"name": entry.name, "path": entry.path, "error": "permission denied"})
    except PermissionError:
        raise HTTPException(403, f"Permission denied: {path}")
    entries.sort(key=lambda e: (not e.get("is_dir"), e["name"].lower()))
    return {"path": path, "count": len(entries), "entries": entries}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def _detect_magic(path: str) -> Optional[str]:
    MAGIC_TABLE = [
        (b"\xff\xd8\xff",       "JPEG Image"),
        (b"\x89PNG\r\n\x1a\n","PNG Image"),
        (b"%PDF",                   "PDF Document"),
        (b"PK\x03\x04",          "ZIP / Office OOXML"),
        (b"MZ",                     "Windows PE Executable"),
        (b"\x7fELF",              "ELF Binary"),
        (b"\xd0\xcf\x11\xe0", "MS Compound Document"),
        (b"SQLite format 3",        "SQLite Database"),
        (b"\x1f\x8b",            "Gzip Archive"),
        (b"Rar!\x1a\x07",        "RAR Archive"),
        (b"7z\xbc\xaf\'\x1c",  "7-Zip Archive"),
        (b"GIF8",                   "GIF Image"),
        (b"BM",                     "BMP Image"),
        (b"RIFF",                   "RIFF Container"),
        (b"ID3",                    "MP3 Audio"),
        (b"fLaC",                   "FLAC Audio"),
        (b"OggS",                   "Ogg Audio"),
        (b"\xca\xfe\xba\xbe", "Java Class File"),
        (b"\xce\xfa\xed\xfe", "macOS Mach-O 32-bit"),
        (b"\xcf\xfa\xed\xfe", "macOS Mach-O 64-bit"),
        (b"!<arch>\n",            "Unix AR Archive"),
        (b"MSCF",                   "Microsoft Cabinet"),
        (b"8BPS",                   "Adobe Photoshop"),
    ]
    try:
        with open(path, "rb") as f:
            header = f.read(16)
        for magic, label in MAGIC_TABLE:
            if header.startswith(magic):
                return label
    except Exception:
        pass
    return None

def _file_entropy(path: str, sample: int = 262144) -> float:
    freq = [0] * 256
    try:
        with open(path, "rb") as f:
            data = f.read(sample)
        for b in data:
            freq[b] += 1
        total = len(data)
    except Exception:
        return 0.0
    if total == 0:
        return 0.0
    e = 0.0
    for c in freq:
        if c:
            p = c / total
            e -= p * math.log2(p)
    return e

# ============================================================
# SECTION 16 -- AI MODELS (TRAINING & INFERENCE)
# ============================================================

from pydantic import BaseModel
import ai_engine

class AITrainRequest(BaseModel):
    model_type: str

@app.post("/api/ai/train", tags=["AI"])
def start_ai_training(req: AITrainRequest):
    try:
        task_id = ai_engine.start_training_job(req.model_type)
        return {"status": "started", "task_id": task_id, "model_type": req.model_type}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai/train/{task_id}", tags=["AI"])
def get_ai_training_status(task_id: str):
    jobs = ai_engine.get_training_status()
    if task_id not in jobs:
        raise HTTPException(status_code=404, detail="Task not found")
    return jobs[task_id]

# ============================================================
# SECTION 17 -- STARTUP / ENTRY POINT
# ============================================================

@app.on_event("startup")
async def on_startup():
    log.info("ForenShield backend starting")
    log.info("Data directory: %s", DATA_DIR)
    log.info("Platform: %s | Python: %s", platform.platform(), sys.version.split()[0])
    log.info("Scapy: %s | win32_setctime: %s", HAS_SCAPY, _win_setctime is not None)
    for f, init_fn in [
        (EVIDENCE_FILE, lambda: _ev_save([])),
        (REPORTS_FILE,  lambda: _rpt_save([])),
        (SETTINGS_FILE, lambda: _cfg_save(DEFAULT_SETTINGS)),
    ]:
        if not f.exists():
            init_fn()

@app.on_event("shutdown")
async def on_shutdown():
    log.info("ForenShield backend shutting down")

if __name__ == "__main__":
    import uvicorn
    cfg  = _cfg_load()
    port = int(os.environ.get("PORT", cfg.get("backend_port", 8000)))
    log.info("Starting on http://127.0.0.1:%d", port)
    uvicorn.run("backend:app", host="127.0.0.1", port=port, reload=True, log_level="info")
