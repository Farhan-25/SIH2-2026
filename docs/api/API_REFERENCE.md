# ForenShield — API Reference

> Base URL: `http://127.0.0.1:8000`  
> Interactive docs: `http://127.0.0.1:8000/docs` (Swagger UI)  
> Alternative: `http://127.0.0.1:8000/redoc`

---

## Table of Contents

- [System Health](#system-health)
- [Memory Forensics](#memory-forensics)
- [Network Forensics](#network-forensics)
- [Disk Forensics](#disk-forensics)
- [Timeline / MAC Times](#timeline--mac-times)
- [Hash Analyzer](#hash-analyzer)
- [Hex Viewer](#hex-viewer)
- [File Recovery / Carving](#file-recovery--carving)
- [Drive Eraser](#drive-eraser)
- [Evidence Locker](#evidence-locker)
- [Reports](#reports)
- [Settings](#settings)
- [Background Tasks](#background-tasks)
- [SSE Stream](#sse-stream)
- [Utilities](#utilities)

---

## System Health

### `GET /api/health`
Returns overall system vitals.

**Response:**
```json
{
  "cpu_count_physical": 8,
  "cpu_count_logical": 16,
  "cpu_percent": 12.4,
  "cpu_freq_mhz": 3600.0,
  "ram_total_gb": 31.88,
  "ram_used_gb": 18.2,
  "ram_percent": 57.1,
  "uptime": "4h 22m",
  "hostname": "WORKSTATION-01",
  "platform": "Windows-11-10.0.26100",
  "scapy_available": true,
  "win32_setctime": true
}
```

---

## Memory Forensics

### `GET /api/memory/processes`
Enumerate all live processes with suspicion scoring.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `filter_suspicious` | bool | `false` | Return only flagged processes |

**Response:**
```json
{
  "count": 145,
  "suspicious_count": 2,
  "processes": [
    {
      "pid": 4444,
      "ppid": 1024,
      "name": "nc.exe",
      "user": "ADMIN",
      "cpu": "0.1",
      "mem": "0.9 MB",
      "handles": 12,
      "status": "Running",
      "exe": "C:\\Users\\user\\Downloads\\nc.exe",
      "cmdline": "nc.exe -lvnp 4444",
      "created": "2026-09-25T08:16:00",
      "suspicious": true
    }
  ]
}
```

### `GET /api/memory/process/{pid}`
Deep-dive detail for a single process (open files, connections, memory).

### `GET /api/memory/process/{pid}/strings`
Extract printable strings from a process executable. Flags suspicious patterns.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `min_len` | int | `6` | Minimum string length |

### `GET /api/memory/snapshot`
Full RAM usage breakdown + top 20 memory consumers.

---

## Network Forensics

### `GET /api/network/connections`
Live network connections with C2 port detection.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `kind` | str | `"inet"` | `inet`, `tcp`, `udp`, `unix` |

**Response:**
```json
{
  "count": 38,
  "suspicious_count": 1,
  "connections": [
    {
      "pid": 6666,
      "proc": "nc.exe",
      "local": "192.168.1.105:4444",
      "remote": "185.220.101.12:9999",
      "proto": "TCP",
      "state": "ESTABLISHED",
      "suspicious": true
    }
  ]
}
```

### `GET /api/network/interfaces`
All NIC interfaces with addresses, speed, and I/O statistics.

### `GET /api/network/pcap`
Parse a PCAP file and return forensic packet summaries. **Requires Scapy.**

| Query Param | Type | Required | Description |
|---|---|---|---|
| `path` | str | ✅ | Absolute path to `.pcap` / `.pcapng` file |
| `max_packets` | int | | Max packets to parse (default: 500) |

**Response includes:** `total_packets`, `suspicious_count`, `protocol_distribution`, `ip_stats`, `packets[]`

---

## Disk Forensics

### `GET /api/disk/partitions`
Live partition listing with usage stats and disk I/O counters.

### `GET /api/disk/scan`
Recursive directory tree map with per-folder file count and size.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `path` | str | `C:\` | Root directory to map |
| `depth` | int | `3` | Recursion depth |

### `GET /api/disk/large-files`
Find the N largest files under a path (useful for evidence triage).

| Query Param | Type | Default | Description |
|---|---|---|---|
| `path` | str | `C:\` | Search root |
| `top` | int | `50` | Max results |
| `min_mb` | float | `10` | Minimum file size in MB |

---

## Timeline / MAC Times

### `GET /api/timeline/mac`
Read Modified / Accessed / Created timestamps for a file.

| Query Param | Type | Required | Description |
|---|---|---|---|
| `path` | str | ✅ | Absolute file path |

**Response:** `mtime`, `atime`, `ctime` (UNIX) + `*_iso` (ISO 8601) fields.

### `POST /api/timeline/mac`
**Modify** MAC timestamps (timestomping simulation for forensic testing).

```json
{
  "path": "C:\\Temp\\malware.exe",
  "mtime": 1748000000.0,
  "atime": 1748000000.0,
  "ctime": 1748000000.0
}
```

> ⚠️ `ctime` modification requires `win32-setctime` on Windows.

### `GET /api/timeline/scan`
Walk a directory tree and return all file events sorted by time.

| Query Param | Type | Description |
|---|---|---|
| `path` | str | Directory or file to scan |
| `start` | float | UNIX timestamp lower bound |
| `end` | float | UNIX timestamp upper bound |
| `limit` | int | Max events returned (default: 1000) |

---

## Hash Analyzer

### `POST /api/hash/text`
Compute multiple hashes of a text string.

```json
{ "text": "Hello, world!", "algorithms": ["md5","sha256"] }
```

### `POST /api/hash/file`
Hash an uploaded file (streaming). Send as `multipart/form-data`.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `algorithms` | str | `"md5,sha1,sha256,sha512"` | Comma-separated algorithm list |

### `GET /api/hash/file-path`
Hash a file at a server-side path + detect magic bytes + calculate entropy.

| Query Param | Type | Required | Description |
|---|---|---|---|
| `path` | str | ✅ | Absolute file path |
| `algorithms` | str | | Comma-separated algorithms |

### `GET /api/hash/compare`
Constant-time comparison of two hashes.

| Query Param | Type | Required |
|---|---|---|
| `hash_a` | str | ✅ |
| `hash_b` | str | ✅ |

---

## Hex Viewer

### `GET /api/hex/read`
Return a paginated hex dump of a file.

| Query Param | Type | Default | Description |
|---|---|---|---|
| `path` | str | ✅ | File path |
| `offset` | int | `0` | Byte offset to start from |
| `length` | int | `4096` | Bytes to read (max: 65536) |

**Response:** `rows[]` with `offset`, `bytes[]`, `ascii[]` per 16-byte row.

### `GET /api/hex/search`
Search a file for a hex or ASCII pattern.

| Query Param | Type | Description |
|---|---|---|
| `path` | str | File path |
| `pattern` | str | Hex (`"FF D8 FF"`) or ASCII string |
| `mode` | str | `"hex"` or `"ascii"` |
| `limit` | int | Max matches (default: 50) |

---

## File Recovery / Carving

### `POST /api/recovery/carve`
Launch a background file carving job on a disk image or partition.

```json
{
  "source_path": "D:\\",
  "output_dir":  "C:\\RecoveredFiles",
  "file_types":  ["jpg", "pdf", "zip"]
}
```

**Response:** `{ "task_id": "uuid", "status": "started" }`

### `GET /api/recovery/carve/{task_id}`
Poll carving progress.

**Response:** `status`, `progress` (0–100), `found[]`, `log[]`, `sectors_scanned`

### `GET /api/recovery/signatures`
List all 17 supported carving signatures (JPEG, PNG, PDF, ZIP, EXE, ELF, DOC, SQLite, RAR, 7Z, GZ, GIF, WAV, MP3, FLAC, MKV, Java).

---

## Drive Eraser

### `POST /api/eraser/file`
Securely erase a single file with multi-pass overwriting before deletion.

```json
{
  "path":   "C:\\Users\\user\\sensitive.docx",
  "passes": 3,
  "method": "dod"
}
```

| `method` | Description |
|---|---|
| `dod` | DoD 5220.22-M — random data overwrite |
| `gutmann` | Gutmann 35-pass with rotating patterns |
| `zeros` | Simple zero-fill |
| `random` | CSPRNG random bytes |

### `POST /api/eraser/freespace`
Wipe free space on a drive by filling then removing a temp file. Background task.

| Query Param | Type | Description |
|---|---|---|
| `drive` | str | Drive letter e.g. `C:\` |
| `passes` | int | Number of passes (1–3) |

---

## Evidence Locker

All data is persisted to `~/.forenshield/evidence.json`.

### `GET /api/evidence` — List all items
### `POST /api/evidence` — Add new evidence item
### `GET /api/evidence/{eid}` — Get single item
### `POST /api/evidence/{eid}/verify` — Mark as integrity-verified
### `POST /api/evidence/{eid}/custody` — Append chain-of-custody event
### `DELETE /api/evidence/{eid}` — Remove item
### `POST /api/evidence/hash-file` — Upload and hash a file for registration

**Add Evidence body:**
```json
{
  "name":  "Suspect Hard Drive Image",
  "type":  "disk-image",
  "size":  "500 GB",
  "tags":  ["primary", "suspect"],
  "notes": "Samsung 500GB SSD from suspect laptop"
}
```

---

## Reports

Persisted to `~/.forenshield/reports.json`.

### `GET /api/reports` — List all reports
### `POST /api/reports` — Create new report record
### `GET /api/reports/{rid}` — Get single report
### `DELETE /api/reports/{rid}` — Delete report
### `GET /api/reports/{rid}/export` — Export as plain-text download

**Create Report body:**
```json
{
  "title":        "Case 47 — Incident Analysis",
  "case_number":  "INC-2026-047",
  "examiner":     "Det. S. Kumar",
  "type":         "incident",
  "sections":     ["memory", "network", "timeline"],
  "evidence_ids": ["EVD-2026-001", "EVD-2026-003"],
  "notes":        "Rootkit deployment via PowerShell"
}
```

---

## Settings

Persisted to `~/.forenshield/settings.json`.

### `GET /api/settings` — Get all settings
### `PUT /api/settings` — Update settings (partial merge)
### `POST /api/settings/reset` — Reset to defaults

**Default settings:**
```json
{
  "theme":             "dark",
  "examiner_name":     "Unknown Examiner",
  "agency":            "Digital Forensics Lab",
  "hash_algorithms":   ["md5","sha1","sha256"],
  "auto_verify":       true,
  "pcap_max_packets":  500,
  "hex_bytes_per_row": 16,
  "backend_port":      8000
}
```

---

## Background Tasks

### `GET /api/tasks` — List all background tasks
### `GET /api/tasks/{task_id}` — Poll task status

**Task status response:**
```json
{
  "status":   "running",
  "progress": 47,
  "found":    [...],
  "log":      [{ "time": "12:34:56", "type": "success", "msg": "Carved: file.jpg" }]
}
```

---

## SSE Stream

### `GET /api/stream/metrics`
Server-Sent Events stream — emits live system metrics every second.

Connect via JavaScript:
```js
const es = new EventSource("http://127.0.0.1:8000/api/stream/metrics")
es.onmessage = (e) => {
  const { cpu_percent, ram_percent, net_sent_mb } = JSON.parse(e.data)
}
```

---

## Utilities

### `GET /api/file/info`
Return comprehensive metadata: size, MAC times, magic bytes, entropy, MD5/SHA1/SHA256.

| Query Param | Type | Required |
|---|---|---|
| `path` | str | ✅ |

### `GET /api/file/strings`
Extract printable strings from a binary file (like Unix `strings`). Flags suspicious patterns.

| Query Param | Type | Default |
|---|---|---|
| `path` | str | required |
| `min_len` | int | `6` |
| `limit` | int | `500` |

### `GET /api/dir/list`
List directory contents with per-entry metadata.

| Query Param | Type | Default |
|---|---|---|
| `path` | str | `C:\` |

---

## Error Responses

All errors return standard FastAPI HTTP exceptions:

```json
{ "detail": "File not found: C:\\missing.exe" }
```

| Code | Meaning |
|---|---|
| `400` | Bad request (malformed PCAP, invalid path) |
| `403` | Permission denied (elevated privileges needed) |
| `404` | Resource not found |
| `500` | Internal server error |
| `501` | Feature requires optional dependency (e.g., Scapy) |
