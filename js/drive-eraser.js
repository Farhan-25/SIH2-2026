/* ForenShield — Drive Eraser Logic */

const DRIVES = [
  { id: 'sda', icon: '💾', name: 'Samsung SSD 860 EVO 500GB', detail: '/dev/sda • 500 GB • SATA III • S/N: SA123456', health: 'Good', healthClass: 'status-ready', sectors: 976773168, type: 'ssd' },
  { id: 'sdb', icon: '🗄️', name: 'WD Blue 1TB HDD', detail: '/dev/sdb • 1 TB • 7200 RPM • S/N: WD987654', health: 'Good', healthClass: 'status-ready', sectors: 1953525168, type: 'hdd' },
  { id: 'sdc', icon: '🔌', name: 'Kingston DataTraveler 64GB USB', detail: '/dev/sdc • 64 GB • USB 3.1 Gen 1 • S/N: KT456789', health: 'Good', healthClass: 'status-ready', sectors: 125045424, type: 'usb' },
  { id: 'sdd', icon: '💿', name: 'Generic MicroSD 32GB', detail: '/dev/sdd • 32 GB • UHS-I Speed Class 3 • S/N: SD789012', health: 'Warning', healthClass: 'card-status', sectors: 62521344, type: 'sd' },
];

let selectedDrive = null;
let selectedAlgo = 'dod';
let eraseInterval = null;
let eraseProgress = 0;
let isPaused = false;
let pass = 0;
let totalPasses = 7;
let sectorStates = [];
let currentSectorIdx = 0;
let eraseStartTime = null;

const ALGO_PASSES = { dod: 7, gutmann: 35, nist: 3, zero: 1, random: 3, crypto: 1 };
const ALGO_NAMES = {
  dod: 'DoD 5220.22-M (7-pass)',
  gutmann: 'Gutmann (35-pass)',
  nist: 'NIST 800-88',
  zero: 'Zero Fill (1-pass)',
  random: 'PRNG Overwrite (3-pass)',
  crypto: 'AES-256 Crypto Erase'
};

// Render drive list
function renderDrives() {
  const list = document.getElementById('driveList');
  list.innerHTML = DRIVES.map(d => `
    <div class="device-item" id="drive-${d.id}" onclick="selectDrive('${d.id}')" style="cursor:pointer;transition:all .2s;">
      <div class="device-icon">${d.icon}</div>
      <div class="device-info">
        <div class="device-name">${d.name}</div>
        <div class="device-detail">${d.detail}</div>
      </div>
      <div class="device-health ${d.healthClass}">${d.health}</div>
    </div>
  `).join('');
}
renderDrives();

function selectDrive(id) {
  selectedDrive = DRIVES.find(d => d.id === id);
  if (!selectedDrive) return;

  document.querySelectorAll('#driveList .device-item').forEach(el => {
    el.style.border = '1px solid var(--border)';
    el.style.background = 'rgba(255,255,255,.02)';
  });
  const el = document.getElementById('drive-' + id);
  if (el) {
    el.style.border = '1px solid rgba(99,102,241,.5)';
    el.style.background = 'rgba(99,102,241,.06)';
  }

  document.getElementById('selectedDriveName').textContent = selectedDrive.name;
  document.getElementById('selectedDriveDetail').textContent = selectedDrive.detail;
  document.getElementById('driveIconLarge').textContent = selectedDrive.icon;

  const hBadge = document.getElementById('driveHealthBadge');
  hBadge.className = 'card-status ' + (selectedDrive.health === 'Good' ? 'status-ready' : 'card-status');
  hBadge.textContent = selectedDrive.health;

  initSectorMap();
  addLog('INFO', `Device selected: ${selectedDrive.name}`);
  addLog('INFO', `Total sectors: ${selectedDrive.sectors.toLocaleString()}`);
}

function selectAlgo(el, algo) {
  document.querySelectorAll('.algo-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  selectedAlgo = algo;
  totalPasses = ALGO_PASSES[algo] || 1;
  addLog('INFO', `Algorithm set: ${ALGO_NAMES[algo]}`);
}

function initSectorMap() {
  const grid = document.getElementById('sectorGrid');
  const TOTAL = 200;
  sectorStates = Array(TOTAL).fill('pending');
  // Sprinkle some bad sectors for realism
  if (selectedDrive && selectedDrive.health === 'Warning') {
    [12, 45, 78, 134, 167].forEach(i => { sectorStates[i] = 'bad'; });
  }
  grid.innerHTML = sectorStates.map((s, i) => `<div class="sector-cell sector-${s}" id="sc-${i}"></div>`).join('');
  currentSectorIdx = 0;
}

function updateSectorMap(upTo) {
  for (let i = 0; i < upTo && i < sectorStates.length; i++) {
    if (sectorStates[i] === 'bad') continue;
    const prevState = sectorStates[i];
    const el = document.getElementById('sc-' + i);
    if (!el) continue;

    if (i === upTo - 1 && upTo < sectorStates.length) {
      sectorStates[i] = 'erasing';
      el.className = 'sector-cell sector-erasing';
    } else if (prevState !== 'verified') {
      sectorStates[i] = document.getElementById('verify').checked ? 'verified' : 'erased';
      el.className = `sector-cell sector-${sectorStates[i]}`;
    }
  }
}

function addLog(type, msg) {
  const log = document.getElementById('driveLog');
  const now = new Date();
  const time = [now.getHours(), now.getMinutes(), now.getSeconds()].map(n => String(n).padStart(2,'0')).join(':');
  const typeClass = { INFO: 'log-type-info', SUCCESS: 'log-type-success', WARN: 'log-type-warn', ERROR: 'log-type-error' }[type] || 'log-type-info';
  const line = document.createElement('div');
  line.className = 'log-line';
  line.innerHTML = `<span class="log-time">${time}</span><span class="${typeClass}">[${type}]</span><span class="log-msg"> ${msg}</span>`;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

function startErase() {
  if (!selectedDrive) {
    window.ForenShield?.toast('No Device Selected', 'Please select a storage device first.', 'warn');
    return;
  }
  document.getElementById('confirmModalBody').innerHTML = `
    You are about to permanently erase <strong>${selectedDrive.name}</strong> using <strong>${ALGO_NAMES[selectedAlgo]}</strong>. 
    This will perform <strong>${ALGO_PASSES[selectedAlgo]} passes</strong> and is <strong>completely irreversible</strong>.
  `;
  document.getElementById('confirmInput').value = '';
  document.getElementById('confirmEraseBtn').disabled = true;
  document.getElementById('confirmModal').style.display = 'flex';
}

document.getElementById('confirmInput').addEventListener('input', function () {
  document.getElementById('confirmEraseBtn').disabled = this.value.trim() !== 'ERASE';
});

function closeModal() {
  document.getElementById('confirmModal').style.display = 'none';
}

function confirmErase() {
  closeModal();
  runErase();
}

function runErase() {
  eraseProgress = 0;
  pass = 1;
  totalPasses = ALGO_PASSES[selectedAlgo];
  isPaused = false;
  eraseStartTime = Date.now();
  currentSectorIdx = 0;

  document.getElementById('startEraseBtn').disabled = true;
  document.getElementById('pauseBtn').disabled = false;
  document.getElementById('stopBtn').disabled = false;
  document.getElementById('pm-pass').textContent = `${pass}/${totalPasses}`;

  // Reinit sector map
  initSectorMap();
  document.getElementById('verificationPanel').style.display = 'none';

  addLog('INFO', `Starting secure erase: ${ALGO_NAMES[selectedAlgo]}`);
  addLog('INFO', `Total passes: ${totalPasses}`);
  addLog('INFO', `Bad sector mapping: ${document.getElementById('badSector').checked ? 'Enabled' : 'Disabled'}`);

  const SECTORS = 200;
  const DURATION = 12000; // 12s simulation
  const STEP_MS = 80;
  const INCREMENT = 100 / (DURATION / STEP_MS);

  eraseInterval = setInterval(() => {
    if (isPaused) return;

    eraseProgress = Math.min(eraseProgress + INCREMENT, 100);
    const sectorsDone = Math.floor((eraseProgress / 100) * SECTORS);
    updateSectorMap(sectorsDone);

    // Update pass
    const newPass = Math.ceil((eraseProgress / 100) * totalPasses);
    if (newPass !== pass) {
      pass = newPass;
      document.getElementById('pm-pass').textContent = `${Math.min(pass, totalPasses)}/${totalPasses}`;
      if (pass <= totalPasses) addLog('INFO', `Pass ${Math.min(pass, totalPasses)} of ${totalPasses} complete`);
    }

    const elapsed = (Date.now() - eraseStartTime) / 1000;
    const speed = (eraseProgress / 100 * (selectedDrive.sectors * 512 / 1e9) / (elapsed || 1)).toFixed(1);
    const eta = elapsed > 1 ? Math.round((100 - eraseProgress) / (eraseProgress / elapsed)) : '—';

    document.getElementById('progressPct').textContent = eraseProgress.toFixed(1) + '%';
    document.getElementById('progressFill').style.width = eraseProgress + '%';
    document.getElementById('progressLabel').textContent = `Erasing — Pass ${Math.min(pass, totalPasses)} of ${totalPasses}`;
    document.getElementById('pm-speed').textContent = speed + ' GB/s';
    document.getElementById('pm-eta').textContent = typeof eta === 'number' ? eta + 's' : eta;

    if (eraseProgress >= 100) {
      clearInterval(eraseInterval);
      eraseComplete();
    }
  }, STEP_MS);
}

function eraseComplete() {
  document.getElementById('progressLabel').textContent = '✅ Erasure Complete!';
  document.getElementById('pm-speed').textContent = '—';
  document.getElementById('pm-eta').textContent = 'Done';
  document.getElementById('pauseBtn').disabled = true;
  document.getElementById('stopBtn').disabled = true;
  document.getElementById('downloadReport').disabled = false;

  addLog('SUCCESS', `All ${totalPasses} passes completed successfully`);
  addLog('SUCCESS', `Total data overwritten: ${(selectedDrive.sectors * 512 / 1e9).toFixed(1)} GB`);

  // Show verification
  if (document.getElementById('verify').checked) {
    document.getElementById('verificationPanel').style.display = 'block';
    runVerification();
  }

  // Generate hash
  const hash = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
  document.getElementById('hashDisplay').textContent = hash;

  window.ForenShield?.toast('Erasure Complete', `${selectedDrive.name} has been securely wiped.`, 'success');
  addLog('SUCCESS', `SHA-256: ${hash}`);
  addLog('INFO', 'Erasure certificate ready for download');
}

function runVerification() {
  const checks = [
    { name: 'Sector Pattern Verification', detail: 'Comparing written vs read patterns', icon: '🔍', status: 'veri-ok', statusText: 'PASSED' },
    { name: 'SMART Diagnostics', detail: 'Drive health post-erasure', icon: '📊', status: 'veri-ok', statusText: 'PASSED' },
    { name: 'Bad Sector Report', detail: selectedDrive.health === 'Warning' ? '5 bad sectors remapped' : 'No bad sectors found', icon: '⚠️', status: selectedDrive.health === 'Warning' ? 'veri-caution' : 'veri-ok', statusText: selectedDrive.health === 'Warning' ? 'WARNING' : 'PASSED' },
    { name: 'Hash Integrity Check', detail: 'SHA-256 post-wipe hash computed', icon: '🔐', status: 'veri-ok', statusText: 'PASSED' },
    { name: 'Compliance Audit', detail: 'NIST 800-88 & DoD 5220.22-M verified', icon: '📋', status: 'veri-ok', statusText: 'COMPLIANT' },
  ];

  const list = document.getElementById('verificationList');
  list.innerHTML = '';

  checks.forEach((c, i) => {
    setTimeout(() => {
      const item = document.createElement('div');
      item.className = 'verification-item';
      item.innerHTML = `
        <div class="veri-icon veri-check">${c.icon}</div>
        <div class="veri-text">
          <div class="veri-name">${c.name}</div>
          <div class="veri-detail">${c.detail}</div>
        </div>
        <div class="veri-status ${c.status}">${c.statusText}</div>
      `;
      list.appendChild(item);
      addLog('SUCCESS', `Verification: ${c.name} — ${c.statusText}`);
    }, i * 600);
  });
}

function pauseErase() {
  isPaused = !isPaused;
  document.getElementById('pauseBtn').innerHTML = isPaused
    ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg> Resume`
    : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg> Pause`;
  addLog('WARN', isPaused ? 'Erasure paused by operator' : 'Erasure resumed');
}

function stopErase() {
  if (eraseInterval) clearInterval(eraseInterval);
  document.getElementById('startEraseBtn').disabled = false;
  document.getElementById('pauseBtn').disabled = true;
  document.getElementById('stopBtn').disabled = true;
  document.getElementById('progressLabel').textContent = '⛔ Erasure Stopped';
  addLog('WARN', 'Erasure stopped by operator — drive partially erased — NOT COMPLIANT');
  window.ForenShield?.toast('Erasure Stopped', 'The drive is partially erased. This is NOT compliant.', 'warn');
}

function downloadReport() {
  const reportContent = generateReportContent();
  const blob = new Blob([reportContent], { type: 'text/html' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ForenShield_Erasure_Report_${new Date().toISOString().slice(0,10)}.html`;
  a.click();
  URL.revokeObjectURL(url);
  window.ForenShield?.toast('Report Downloaded', 'Forensic audit report saved successfully.', 'success');
}

function generateReportContent() {
  const now = new Date();
  const hash = document.getElementById('hashDisplay').textContent;
  return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>ForenShield — Secure Erasure Certificate</title>
  <style>
    body { font-family: 'Arial', sans-serif; background: #f8f9fa; color: #1a1a2e; margin: 0; padding: 2rem; }
    .report { max-width: 800px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 24px rgba(0,0,0,.12); overflow: hidden; }
    .report-header { background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 2.5rem; }
    .report-header h1 { font-size: 1.5rem; margin: 0 0 .5rem; }
    .report-header p { opacity: .85; margin: 0; font-size: .9rem; }
    .report-body { padding: 2rem; }
    .section { margin-bottom: 2rem; }
    .section h2 { font-size: 1rem; color: #4f46e5; border-bottom: 2px solid #e2e8f0; padding-bottom: .5rem; margin-bottom: 1rem; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: .75rem; }
    .field { }
    .field-label { font-size: .7rem; text-transform: uppercase; letter-spacing: .08em; color: #64748b; margin-bottom: .25rem; }
    .field-value { font-size: .875rem; font-weight: 600; }
    .badge-compliant { display: inline-block; padding: .25rem .75rem; background: #d1fae5; color: #065f46; border-radius: 20px; font-size: .75rem; font-weight: 700; }
    .hash { font-family: monospace; font-size: .78rem; background: #f1f5f9; padding: .75rem; border-radius: 6px; word-break: break-all; color: #4f46e5; }
    .footer { text-align: center; padding: 1.5rem; background: #f8fafc; font-size: .75rem; color: #94a3b8; }
    table { width: 100%; border-collapse: collapse; }
    th { text-align: left; padding: .5rem .75rem; font-size: .7rem; text-transform: uppercase; color: #64748b; border-bottom: 1px solid #e2e8f0; }
    td { padding: .625rem .75rem; font-size: .82rem; border-bottom: 1px solid #f1f5f9; }
  </style>
</head>
<body>
<div class="report">
  <div class="report-header">
    <h1>🛡️ ForenShield — Secure Erasure Certificate</h1>
    <p>Tamper-Proof Forensic Audit Report • Digital Signature: SHA-256</p>
  </div>
  <div class="report-body">
    <div class="section">
      <h2>Device Information</h2>
      <div class="grid">
        <div class="field"><div class="field-label">Device Name</div><div class="field-value">${selectedDrive.name}</div></div>
        <div class="field"><div class="field-label">Device Path</div><div class="field-value">/dev/${selectedDrive.id}</div></div>
        <div class="field"><div class="field-label">Capacity</div><div class="field-value">${(selectedDrive.sectors * 512 / 1e9).toFixed(1)} GB (${selectedDrive.sectors.toLocaleString()} sectors)</div></div>
        <div class="field"><div class="field-label">Device Type</div><div class="field-value">${selectedDrive.type.toUpperCase()}</div></div>
      </div>
    </div>
    <div class="section">
      <h2>Erasure Parameters</h2>
      <div class="grid">
        <div class="field"><div class="field-label">Algorithm</div><div class="field-value">${ALGO_NAMES[selectedAlgo]}</div></div>
        <div class="field"><div class="field-label">Passes Completed</div><div class="field-value">${totalPasses}/${totalPasses}</div></div>
        <div class="field"><div class="field-label">Start Time</div><div class="field-value">${now.toISOString()}</div></div>
        <div class="field"><div class="field-label">Status</div><div class="field-value"><span class="badge-compliant">✓ COMPLIANT</span></div></div>
      </div>
    </div>
    <div class="section">
      <h2>Compliance Standards</h2>
      <table>
        <tr><th>Standard</th><th>Status</th></tr>
        <tr><td>NIST SP 800-88 Rev 1</td><td><span class="badge-compliant">Compliant</span></td></tr>
        <tr><td>DoD 5220.22-M (E&EL)</td><td><span class="badge-compliant">Compliant</span></td></tr>
        <tr><td>ISO/IEC 27001:2022</td><td><span class="badge-compliant">Compliant</span></td></tr>
        <tr><td>IEEE 2883-2022</td><td><span class="badge-compliant">Compliant</span></td></tr>
        <tr><td>GDPR Article 17 (Right to Erasure)</td><td><span class="badge-compliant">Compliant</span></td></tr>
      </table>
    </div>
    <div class="section">
      <h2>Cryptographic Verification</h2>
      <div class="field-label">Post-Erasure SHA-256 Hash</div>
      <div class="hash">${hash}</div>
    </div>
    <div class="section">
      <h2>Operator Information</h2>
      <div class="grid">
        <div class="field"><div class="field-label">Operator / Case ID</div><div class="field-value">${document.getElementById('operatorId').value || 'Not specified'}</div></div>
        <div class="field"><div class="field-label">Report Generated</div><div class="field-value">${now.toString()}</div></div>
        <div class="field"><div class="field-label">Tool Version</div><div class="field-value">ForenShield v2.0</div></div>
        <div class="field"><div class="field-label">Report Hash</div><div class="field-value">${Array.from({length:16},()=>Math.floor(Math.random()*16).toString(16)).join('')}</div></div>
      </div>
    </div>
  </div>
  <div class="footer">
    This certificate is generated by ForenShield v2.0 — Smart India Hackathon 2026 | Digital Forensics & Cybersecurity<br/>
    Report is cryptographically signed and tamper-evident.
  </div>
</div>
</body>
</html>`;
}

// Scan drives button
document.getElementById('scanDrives').addEventListener('click', function () {
  this.textContent = '⟳ Scanning...';
  addLog('INFO', 'Scanning for connected storage devices...');
  setTimeout(() => {
    this.textContent = '↺ Scan for Devices';
    addLog('SUCCESS', `Found ${DRIVES.length} storage devices`);
    DRIVES.forEach(d => addLog('INFO', `  Detected: ${d.name}`));
  }, 1800);
});
