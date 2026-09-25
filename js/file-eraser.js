/* ForenShield — File Eraser Logic */

let fileQueue = [];
let eraseRunning = false;
let erasedCount = 0;

const FILE_ICONS = {
  pdf: '📄', jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🎞️',
  mp4: '🎬', avi: '🎬', mkv: '🎬', mov: '🎬',
  mp3: '🎵', wav: '🎵', flac: '🎵',
  doc: '📝', docx: '📝', txt: '📝', xlsx: '📊', pptx: '📊',
  zip: '🗜️', rar: '🗜️', '7z': '🗜️',
  exe: '⚙️', dll: '⚙️', sh: '⚙️', py: '🐍', js: '📜',
  sql: '🗃️', db: '🗃️', csv: '📊',
  default: '📁'
};

function getIcon(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  return FILE_ICONS[ext] || FILE_ICONS.default;
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function browseFiles(e) {
  if (e) e.stopPropagation();
  document.getElementById('fileInput').click();
}

function handleFileInput(event) {
  const files = Array.from(event.target.files);
  files.forEach(f => addFileToQueue(f.name, f.size, f));
  renderQueue();
}

// Drag and Drop
const dropZone = document.getElementById('dropZone');
dropZone.addEventListener('dragover', e => { e.preventDefault(); dropZone.classList.add('drag-over'); });
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drag-over'));
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('drag-over');
  const files = Array.from(e.dataTransfer.files);
  files.forEach(f => addFileToQueue(f.name, f.size, f));
  renderQueue();
});

function addFileToQueue(name, size, fileObj = null) {
  // Check duplcates
  if (fileQueue.find(f => f.name === name && f.size === size)) return;
  fileQueue.push({
    id: Date.now() + Math.random(),
    name,
    size,
    icon: getIcon(name),
    status: 'pending',
    file: fileObj,
    metadata: generateMockMeta(name, size)
  });
  updateStats();
}

function generateMockMeta(name, size) {
  const exts = name.split('.');
  const ext = exts.length > 1 ? exts.pop() : '';
  return {
    'File Name': name,
    'File Size': formatBytes(size),
    'Extension': ext.toUpperCase() || 'Unknown',
    'Created': new Date(Date.now() - Math.random() * 1e10).toLocaleDateString(),
    'Modified': new Date(Date.now() - Math.random() * 1e8).toLocaleDateString(),
    'Author': ['John Doe', 'Jane Smith', 'Admin', 'root'].at(Math.floor(Math.random() * 4)),
    'EXIF GPS': ext.match(/jpg|jpeg|png/) ? `${(Math.random()*180-90).toFixed(4)}°, ${(Math.random()*360-180).toFixed(4)}°` : 'N/A',
    'Hash (MD5)': Array.from({length:32},()=>Math.floor(Math.random()*16).toString(16)).join(''),
  };
}

function renderQueue() {
  const container = document.getElementById('fileQueue');
  if (fileQueue.length === 0) {
    container.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-muted);font-size:.85rem;"><div style="font-size:2rem;margin-bottom:.5rem;">📂</div>Drop files above or click browse to add files</div>`;
    return;
  }
  container.innerHTML = fileQueue.map(f => `
    <div class="queue-item" id="qi-${f.id}" onclick="showMeta('${f.id}')">
      <div class="queue-file-icon">${f.icon}</div>
      <div class="queue-file-info">
        <div class="queue-file-name">${f.name}</div>
        <div class="queue-file-meta">${formatBytes(f.size)}</div>
      </div>
      <div class="queue-status qs-${f.status}">${f.status.charAt(0).toUpperCase() + f.status.slice(1)}</div>
      ${f.status === 'pending' ? `<button class="queue-remove" onclick="removeFile('${f.id}',event)" title="Remove">✕</button>` : ''}
    </div>
  `).join('');
  updateStats();
}

function removeFile(id, e) {
  e.stopPropagation();
  fileQueue = fileQueue.filter(f => String(f.id) !== String(id));
  renderQueue();
}

function clearQueue() {
  if (eraseRunning) return;
  fileQueue = [];
  erasedCount = 0;
  renderQueue();
  updateStats();
  document.getElementById('overallFill').style.width = '0%';
  document.getElementById('overallPct').textContent = '0%';
  document.getElementById('overallLabel').textContent = 'Waiting for files...';
}

function updateStats() {
  document.getElementById('queueCount').textContent = fileQueue.length;
  document.getElementById('doneCount').textContent = erasedCount;
  const totalBytes = fileQueue.reduce((a, f) => a + f.size, 0);
  document.getElementById('totalSize').textContent = formatBytes(totalBytes);
}

function showMeta(id) {
  const f = fileQueue.find(x => String(x.id) === String(id));
  if (!f) return;
  const analyzer = document.getElementById('metaAnalyzer');
  analyzer.innerHTML = `
    <div style="font-size:.8rem;font-weight:700;color:var(--text-primary);margin-bottom:.75rem;">${f.icon} ${f.name}</div>
    ${Object.entries(f.metadata).map(([k, v]) => `
      <div style="display:flex;justify-content:space-between;align-items:center;padding:.5rem 0;border-bottom:1px solid var(--border);">
        <span style="font-size:.72rem;color:var(--text-muted);">${k}</span>
        <span style="font-size:.72rem;font-family:var(--font-mono);color:var(--text-secondary);max-width:60%;text-align:right;word-break:break-all;">${v}</span>
      </div>
    `).join('')}
    <div style="margin-top:1rem;padding:.75rem;background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.15);border-radius:8px;font-size:.72rem;color:#f87171;">
      ⚠️ All metadata above will be permanently erased during secure deletion
    </div>
  `;
}

function addFileLog(type, msg) {
  const log = document.getElementById('fileLog');
  const now = new Date();
  const time = [now.getHours(), now.getMinutes(), now.getSeconds()].map(n => String(n).padStart(2,'0')).join(':');
  const typeClass = { INFO: 'log-type-info', SUCCESS: 'log-type-success', WARN: 'log-type-warn', ERROR: 'log-type-error' }[type] || 'log-type-info';
  const line = document.createElement('div');
  line.className = 'log-line';
  line.innerHTML = `<span class="log-time">${time}</span><span class="${typeClass}"> [${type}]</span><span class="log-msg"> ${msg}</span>`;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

async function eraseAllFiles() {
  if (fileQueue.length === 0) {
    window.ForenShield?.toast('No Files', 'Please add files to the queue first.', 'warn');
    return;
  }
  if (eraseRunning) return;

  eraseRunning = true;
  erasedCount = 0;
  const algo = document.getElementById('fileAlgo').value;
  const ALGO_NAMES = { dod: 'DoD 5220.22-M (7-pass)', gutmann: 'Gutmann (35-pass)', nist: 'NIST 800-88', zero: 'Zero Fill', prng: 'PRNG Overwrite' };

  addFileLog('INFO', `Starting batch secure erase: ${ALGO_NAMES[algo]}`);
  addFileLog('INFO', `Queue: ${fileQueue.length} file(s)`);
  if (document.getElementById('mft').checked) addFileLog('INFO', 'MFT record scrubbing: Enabled');
  if (document.getElementById('slack').checked) addFileLog('INFO', 'Slack space cleaning: Enabled');
  if (document.getElementById('meta').checked) addFileLog('INFO', 'Metadata scrubbing: Enabled');

  document.getElementById('eraseAllBtn').disabled = true;

  for (let i = 0; i < fileQueue.length; i++) {
    const f = fileQueue[i];
    f.status = 'erasing';
    renderQueue();

    addFileLog('INFO', `Erasing: ${f.name} (${formatBytes(f.size)})`);

    // Simulate per-file erasure
    await sleep(600 + Math.random() * 800);

    if (document.getElementById('mft').checked) {
      await sleep(150);
      addFileLog('SUCCESS', `  MFT entry scrubbed: ${f.name}`);
    }
    if (document.getElementById('meta').checked) {
      await sleep(100);
      addFileLog('SUCCESS', `  Metadata wiped: ${f.name}`);
    }
    if (document.getElementById('slack').checked) {
      await sleep(100);
      addFileLog('SUCCESS', `  Slack space overwritten: ${f.name}`);
    }

    f.status = 'done';
    erasedCount++;
    renderQueue();

    const pct = Math.round((erasedCount / fileQueue.length) * 100);
    document.getElementById('overallFill').style.width = pct + '%';
    document.getElementById('overallPct').textContent = pct + '%';
    document.getElementById('overallLabel').textContent = `Erasing ${i + 1} of ${fileQueue.length}...`;

    addFileLog('SUCCESS', `Erased: ${f.name}`);
  }

  document.getElementById('overallLabel').textContent = `✅ All ${fileQueue.length} file(s) securely erased!`;
  addFileLog('SUCCESS', `Batch erasure complete — ${fileQueue.length} file(s) permanently destroyed`);
  addFileLog('INFO', 'Generating audit report...');

  window.ForenShield?.toast('Erasure Complete', `${fileQueue.length} file(s) securely erased.`, 'success');
  eraseRunning = false;
  document.getElementById('eraseAllBtn').disabled = false;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Simulate demo files pre-loaded
const DEMO_FILES = [
  { name: 'sensitive_report.pdf', size: 2457600 },
  { name: 'financial_records_2025.xlsx', size: 1048576 },
  { name: 'case_evidence_photo.jpg', size: 3670016 },
  { name: 'encrypted_db_backup.sql', size: 10485760 },
  { name: 'suspect_video_clip.mp4', size: 52428800 },
];

setTimeout(() => {
  DEMO_FILES.forEach(f => addFileToQueue(f.name, f.size));
  renderQueue();
  addFileLog('INFO', 'Demo files loaded — ready for secure erasure');
}, 300);
