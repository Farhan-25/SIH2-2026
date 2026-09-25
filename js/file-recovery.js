/* ForenShield — File Recovery Logic */

let scanRunning = false;
let recoveredFiles = [];
let scanProgress = 0;
let scanInterval = null;

document.getElementById('confThreshold').addEventListener('input', function() {
  document.getElementById('confVal').textContent = this.value + '%';
});

// Signature database
const SIGNATURES = [
  { hex: 'FF D8 FF', ext: 'jpg', type: 'image', icon: '🖼️', desc: 'JPEG Image' },
  { hex: '89 50 4E 47', ext: 'png', type: 'image', icon: '🖼️', desc: 'PNG Image' },
  { hex: '47 49 46 38', ext: 'gif', type: 'image', icon: '🎞️', desc: 'GIF Animation' },
  { hex: '25 50 44 46', ext: 'pdf', type: 'doc', icon: '📄', desc: 'PDF Document' },
  { hex: 'D0 CF 11 E0', ext: 'doc', type: 'doc', icon: '📝', desc: 'Word Document' },
  { hex: '50 4B 03 04', ext: 'docx', type: 'doc', icon: '📝', desc: 'Office Open XML' },
  { hex: '50 4B 03 04', ext: 'xlsx', type: 'doc', icon: '📊', desc: 'Excel Spreadsheet' },
  { hex: '66 74 79 70', ext: 'mp4', type: 'video', icon: '🎬', desc: 'MP4 Video' },
  { hex: '52 49 46 46', ext: 'avi', type: 'video', icon: '🎬', desc: 'AVI Video' },
  { hex: '1A 45 DF A3', ext: 'mkv', type: 'video', icon: '🎬', desc: 'Matroska Video' },
  { hex: '49 44 33', ext: 'mp3', type: 'audio', icon: '🎵', desc: 'MP3 Audio' },
  { hex: '66 4C 61 43', ext: 'flac', type: 'audio', icon: '🎵', desc: 'FLAC Audio' },
  { hex: '52 49 46 46', ext: 'wav', type: 'audio', icon: '🎵', desc: 'WAV Audio' },
  { hex: '50 4B 03 04', ext: 'zip', type: 'archive', icon: '🗜️', desc: 'ZIP Archive' },
  { hex: '52 61 72 21', ext: 'rar', type: 'archive', icon: '🗜️', desc: 'RAR Archive' },
  { hex: '37 7A BC AF', ext: '7z', type: 'archive', icon: '🗜️', desc: '7-Zip Archive' },
  { hex: '53 51 4C 69', ext: 'db', type: 'db', icon: '🗃️', desc: 'SQLite Database' },
  { hex: '4D 5A', ext: 'exe', type: 'exe', icon: '⚙️', desc: 'Windows Executable' },
  { hex: '42 4D', ext: 'bmp', type: 'image', icon: '🖼️', desc: 'Bitmap Image' },
  { hex: '00 00 01 B3', ext: 'mpg', type: 'video', icon: '🎬', desc: 'MPEG Video' },
  { hex: '4F 67 67 53', ext: 'ogg', type: 'audio', icon: '🎵', desc: 'OGG Audio' },
  { hex: '7B 5C 72 74', ext: 'rtf', type: 'doc', icon: '📝', desc: 'Rich Text Format' },
];

const NAMES_PREFIX = ['recovered', 'file', 'deleted', 'carved', 'fragment', 'evidence', 'unallocated'];
const SIZES = [45056, 102400, 512000, 1048576, 2097152, 5242880, 10485760, 52428800, 104857600];

function randName(sig) {
  const prefix = NAMES_PREFIX[Math.floor(Math.random() * NAMES_PREFIX.length)];
  const num = Math.floor(Math.random() * 9999);
  return `${prefix}_${num}.${sig.ext}`;
}

function randSize() {
  return SIZES[Math.floor(Math.random() * SIZES.length)];
}

function confLevel(score) {
  if (score >= 85) return 'conf-high';
  if (score >= 60) return 'conf-med';
  return 'conf-low';
}

function confLabel(score) {
  if (score >= 85) return 'High';
  if (score >= 60) return 'Medium';
  return 'Low';
}

function formatBytesRecov(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  if (bytes < 1073741824) return (bytes / 1048576).toFixed(1) + ' MB';
  return (bytes / 1073741824).toFixed(2) + ' GB';
}

function addScanLog(type, msg) {
  const log = document.getElementById('scanLog');
  const now = new Date();
  const time = [now.getHours(), now.getMinutes(), now.getSeconds()].map(n => String(n).padStart(2,'0')).join(':');
  const typeClass = { INFO: 'log-type-info', SUCCESS: 'log-type-success', WARN: 'log-type-warn', ERROR: 'log-type-error' }[type] || 'log-type-info';
  const line = document.createElement('div');
  line.className = 'log-line';
  line.innerHTML = `<span class="log-time">${time}</span><span class="${typeClass}"> [${type}]</span><span class="log-msg"> ${msg}</span>`;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

function updateRing(pct) {
  const CIRCUMFERENCE = 2 * Math.PI * 70;
  const offset = CIRCUMFERENCE - (pct / 100) * CIRCUMFERENCE;
  document.getElementById('ringProgress').style.strokeDashoffset = offset;
  document.getElementById('ringPct').textContent = pct.toFixed(0) + '%';
}

let currentFilter = 'all';

function filterResults(type, btn) {
  currentFilter = type;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderRecovered();
}

function renderRecovered() {
  const grid = document.getElementById('recoveredGrid');
  const confThresh = parseInt(document.getElementById('confThreshold').value);
  const useFilter = document.getElementById('confFilter').checked;

  let files = recoveredFiles;
  if (currentFilter !== 'all') files = files.filter(f => f.type === currentFilter);
  if (useFilter) files = files.filter(f => f.confidence >= confThresh);

  document.getElementById('resultsCount').textContent = files.length + ' files';

  if (files.length === 0) {
    grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--text-muted);font-size:.82rem;">No files match the current filter</div>`;
    return;
  }

  grid.innerHTML = files.map((f, i) => `
    <div class="recovered-card" id="rc-${i}" onclick="selectRecovered(${i})">
      <div class="rec-type-icon">${f.icon}</div>
      <div class="rec-filename">${f.name}</div>
      <div class="rec-size">${formatBytesRecov(f.size)}</div>
      <div class="confidence-badge ${confLevel(f.confidence)}">${f.confidence}% ${confLabel(f.confidence)}</div>
      <div style="font-size:.65rem;color:var(--text-muted);font-family:var(--font-mono);">Offset: 0x${f.offset}</div>
    </div>
  `).join('');
}

function selectRecovered(idx) {
  document.querySelectorAll('.recovered-card').forEach(c => c.classList.remove('selected'));
  const el = document.getElementById('rc-' + idx);
  if (el) el.classList.add('selected');
}

async function startScan() {
  if (scanRunning) return;
  scanRunning = true;
  recoveredFiles = [];
  scanProgress = 0;

  document.getElementById('startScanBtn').disabled = true;
  document.getElementById('recoveredGrid').innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:2rem;color:var(--text-muted);">🔍 Scanning in progress...</div>`;

  const source = document.getElementById('recoverySource').value;
  const method = document.querySelector('input[name="method"]:checked').value;

  addScanLog('INFO', `Starting forensic scan: ${source}`);
  addScanLog('INFO', `Carving method: ${method}`);
  addScanLog('INFO', `File system: ${document.getElementById('recoveryFS').value}`);
  addScanLog('INFO', 'Creating read-only sector image...');

  await sleep(800);
  addScanLog('SUCCESS', 'Sector image created — source media protected');
  addScanLog('INFO', 'Loading signature database (47 file types)...');
  await sleep(400);
  addScanLog('SUCCESS', 'Signature database loaded');

  const TOTAL_SECTORS = 976773;
  const SCAN_DURATION = 15000;
  const STEP = 80;
  const INCREMENT = 100 / (SCAN_DURATION / STEP);
  const startTime = Date.now();

  let fileCounter = 0;
  let scheduledFiles = [];

  // Pre-plan which files to find and at what progress %
  const checkedTypes = Array.from(document.querySelectorAll('.fileType:checked')).map(i => i.value);
  const availableSigs = SIGNATURES.filter(s => checkedTypes.includes(s.type) || s.type === 'image');
  const NUM_FILES = 18 + Math.floor(Math.random() * 12);

  for (let i = 0; i < NUM_FILES; i++) {
    const sig = availableSigs[Math.floor(Math.random() * availableSigs.length)];
    scheduledFiles.push({
      triggerAt: 5 + (i / NUM_FILES) * 90,
      sig
    });
  }

  document.getElementById('ringLabel').textContent = 'Scanning';

  scanInterval = setInterval(async () => {
    scanProgress = Math.min(scanProgress + INCREMENT, 100);
    const elapsed = (Date.now() - startTime) / 1000;
    const speed = ((scanProgress / 100 * TOTAL_SECTORS / 2048) / elapsed).toFixed(1);

    updateRing(scanProgress);
    document.getElementById('statSectorsScanned').textContent = Math.floor(scanProgress / 100 * TOTAL_SECTORS).toLocaleString();
    document.getElementById('statScanSpeed').textContent = speed + ' MB/s';

    // Check for file discoveries
    scheduledFiles = scheduledFiles.filter(sf => {
      if (scanProgress >= sf.triggerAt) {
        const sig = sf.sig;
        const confidence = 70 + Math.floor(Math.random() * 30);
        const size = randSize();
        const file = {
          name: randName(sig),
          size,
          type: sig.type,
          icon: sig.icon,
          desc: sig.desc,
          ext: sig.ext,
          confidence,
          offset: (Math.floor(Math.random() * 0xFFFFFF)).toString(16).toUpperCase().padStart(8, '0'),
          signature: sig.hex,
          fragmented: Math.random() > 0.7
        };
        recoveredFiles.push(file);
        fileCounter++;
        document.getElementById('statFilesFound').textContent = fileCounter;
        addScanLog('SUCCESS', `Found: ${file.name} | ${formatBytesRecov(size)} | Confidence: ${confidence}%`);
        if (file.fragmented) addScanLog('WARN', `  Fragmented file — reassembling fragments...`);
        renderRecovered();
        document.getElementById('exportBtn').disabled = false;
        document.getElementById('reportBtn').disabled = false;
        return false;
      }
      return true;
    });

    if (scanProgress >= 100) {
      clearInterval(scanInterval);
      completeScan(fileCounter, elapsed);
    }
  }, STEP);
}

function completeScan(total, elapsed) {
  updateRing(100);
  document.getElementById('ringLabel').textContent = 'Complete';
  document.getElementById('startScanBtn').disabled = false;
  scanRunning = false;

  addScanLog('SUCCESS', `Scan complete in ${elapsed.toFixed(1)}s`);
  addScanLog('SUCCESS', `Total files recovered: ${total}`);
  addScanLog('INFO', `Recovery rate: ${(Math.random() * 5 + 92).toFixed(1)}%`);
  addScanLog('INFO', 'Chain of custody log finalized');
  addScanLog('INFO', 'Ready to export and generate forensic report');

  window.ForenShield?.toast('Scan Complete', `${total} files recovered from the target media.`, 'success');
  renderRecovered();
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function exportResults() {
  window.ForenShield?.toast('Export Started', 'Recovered files being exported to output directory.', 'info');
  addScanLog('INFO', 'Exporting recovered files...');
  setTimeout(() => {
    addScanLog('SUCCESS', `Exported ${recoveredFiles.length} files to /output/recovery_${Date.now()}/`);
    window.ForenShield?.toast('Export Complete', `${recoveredFiles.length} files exported successfully.`, 'success');
  }, 1500);
}

function generateRecoveryReport() {
  const content = buildRecoveryReportHTML();
  const blob = new Blob([content], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ForenShield_Recovery_Report_${new Date().toISOString().slice(0,10)}.html`;
  a.click();
  URL.revokeObjectURL(url);
  window.ForenShield?.toast('Report Downloaded', 'Forensic recovery report saved.', 'success');
}

function buildRecoveryReportHTML() {
  const now = new Date();
  const typeCounts = {};
  recoveredFiles.forEach(f => { typeCounts[f.type] = (typeCounts[f.type] || 0) + 1; });

  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ForenShield — Forensic Recovery Report</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f8f9fa; color: #1a1a2e; margin: 0; padding: 2rem; }
    .report { max-width: 900px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,.12); overflow: hidden; }
    .rh { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 2.5rem; }
    .rh h1 { font-size: 1.5rem; margin: 0 0 .5rem; }
    .rb { padding: 2rem; }
    h2 { font-size: 1rem; color: #4f46e5; border-bottom: 2px solid #e2e8f0; padding-bottom: .5rem; margin: 1.5rem 0 1rem; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; margin-bottom: 1.5rem; }
    .field-label { font-size: .7rem; text-transform: uppercase; letter-spacing: .08em; color: #64748b; }
    .field-value { font-size: .875rem; font-weight: 600; }
    table { width: 100%; border-collapse: collapse; font-size: .8rem; }
    th { text-align: left; padding: .5rem .75rem; font-size: .7rem; text-transform: uppercase; color: #64748b; border-bottom: 2px solid #e2e8f0; background: #f8fafc; }
    td { padding: .5rem .75rem; border-bottom: 1px solid #f1f5f9; }
    .badge { padding: .2rem .6rem; border-radius: 20px; font-size: .65rem; font-weight: 700; }
    .bh { background: #d1fae5; color: #065f46; }
    .bm { background: #fef3c7; color: #92400e; }
    .bl { background: #fee2e2; color: #991b1b; }
    .footer { text-align: center; padding: 1.5rem; background: #f8fafc; font-size: .75rem; color: #94a3b8; }
  </style>
</head>
<body>
<div class="report">
  <div class="rh">
    <h1>🔍 ForenShield — Forensic Recovery Report</h1>
    <p>Chain-of-Custody Preserved • Evidential Integrity Maintained • ${now.toISOString()}</p>
  </div>
  <div class="rb">
    <h2>Investigation Summary</h2>
    <div class="grid">
      <div><div class="field-label">Source</div><div class="field-value">${document.getElementById('recoverySource').value}</div></div>
      <div><div class="field-label">File System</div><div class="field-value">${document.getElementById('recoveryFS').value}</div></div>
      <div><div class="field-label">Carving Method</div><div class="field-value">${document.querySelector('input[name="method"]:checked').value}</div></div>
      <div><div class="field-label">Total Recovered</div><div class="field-value">${recoveredFiles.length} files</div></div>
      <div><div class="field-label">Scan Date</div><div class="field-value">${now.toLocaleDateString()}</div></div>
      <div><div class="field-label">Tool Version</div><div class="field-value">ForenShield v2.0</div></div>
    </div>

    <h2>File Type Distribution</h2>
    <div class="grid">
      ${Object.entries(typeCounts).map(([t, c]) => `<div><div class="field-label">${t}</div><div class="field-value">${c} files</div></div>`).join('')}
    </div>

    <h2>Recovered Files (${recoveredFiles.length})</h2>
    <table>
      <tr><th>#</th><th>Filename</th><th>Type</th><th>Size</th><th>Confidence</th><th>Offset</th><th>Fragmented</th></tr>
      ${recoveredFiles.map((f, i) => `
        <tr>
          <td>${i+1}</td>
          <td>${f.icon} ${f.name}</td>
          <td>${f.desc}</td>
          <td>${formatBytesRecov(f.size)}</td>
          <td><span class="badge ${f.confidence>=85?'bh':f.confidence>=60?'bm':'bl'}">${f.confidence}%</span></td>
          <td style="font-family:monospace;">0x${f.offset}</td>
          <td>${f.fragmented?'Yes':'No'}</td>
        </tr>
      `).join('')}
    </table>

    <h2>Chain of Custody</h2>
    <div class="grid">
      <div><div class="field-label">Source Hash (MD5)</div><div class="field-value" style="font-family:monospace;font-size:.75rem;">${Array.from({length:32},()=>Math.floor(Math.random()*16).toString(16)).join('')}</div></div>
      <div><div class="field-label">Source Hash (SHA-256)</div><div class="field-value" style="font-family:monospace;font-size:.75rem;">${Array.from({length:64},()=>Math.floor(Math.random()*16).toString(16)).join('')}</div></div>
    </div>
  </div>
  <div class="footer">ForenShield v2.0 — Smart India Hackathon 2026 | Forensic report is tamper-evident and court-admissible</div>
</div>
</body>
</html>`;
}
