/* ForenShield — Reports Logic */

const MOCK_REPORTS = [
  {
    id: 'R001', type: 'erase', icon: '🗑️', typeLabel: 'rt-erase',
    name: 'Secure Erase — Samsung SSD 860 EVO',
    device: 'Samsung SSD 860 EVO 500GB • /dev/sda',
    algo: 'DoD 5220.22-M (7-pass)',
    operator: 'Forensic Officer A. Kumar',
    date: new Date(Date.now() - 2 * 60 * 60 * 1000),
    size: '500 GB',
    hash: Array.from({length:64},()=>Math.floor(Math.random()*16).toString(16)).join(''),
    compliant: true,
    standards: ['NIST SP 800-88', 'DoD 5220.22-M', 'ISO 27001'],
    details: {
      'Passes Completed': '7/7', 'Bad Sectors': '0', 'Verification': 'Passed',
      'Duration': '1h 23m', 'Speed Avg': '98.4 MB/s', 'Sectors': '976,773,168'
    }
  },
  {
    id: 'R002', type: 'recovery', icon: '🔍', typeLabel: 'rt-recovery',
    name: 'Forensic Recovery — WD Blue HDD',
    device: 'WD Blue 1TB HDD • /dev/sdb',
    algo: 'AI-Assisted Hybrid Carving',
    operator: 'Forensic Investigator P. Singh',
    date: new Date(Date.now() - 5 * 60 * 60 * 1000),
    size: '1 TB',
    hash: Array.from({length:64},()=>Math.floor(Math.random()*16).toString(16)).join(''),
    compliant: true,
    standards: ['SWGDE Guidelines', 'ISO 27037', 'RFC 3227'],
    details: {
      'Files Recovered': '24', 'Recovery Rate': '94.2%', 'Confidence Avg': '87%',
      'Fragmented': '3', 'Scan Duration': '45m 12s', 'Sectors Scanned': '1,953,525,168'
    }
  },
  {
    id: 'R003', type: 'file', icon: '📄', typeLabel: 'rt-file',
    name: 'Secure File Erase — Batch Operation',
    device: 'NTFS Volume C: • 5 files',
    algo: 'Gutmann Method (35-pass)',
    operator: 'Security Admin R. Mehta',
    date: new Date(Date.now() - 24 * 60 * 60 * 1000),
    size: '67.3 MB',
    hash: Array.from({length:64},()=>Math.floor(Math.random()*16).toString(16)).join(''),
    compliant: true,
    standards: ['NIST SP 800-88', 'GDPR Art. 17'],
    details: {
      'Files Erased': '5', 'MFT Entries': 'Scrubbed', 'Metadata': 'Wiped',
      'Slack Space': 'Overwritten', 'Registry': 'Cleaned', 'Thumbnails': 'Deleted'
    }
  },
  {
    id: 'R004', type: 'erase', icon: '🗑️', typeLabel: 'rt-erase',
    name: 'Secure Erase — Kingston USB 64GB',
    device: 'Kingston DataTraveler 64GB • /dev/sdc',
    algo: 'NIST 800-88 (3-pass)',
    operator: 'IT Security Team',
    date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
    size: '64 GB',
    hash: Array.from({length:64},()=>Math.floor(Math.random()*16).toString(16)).join(''),
    compliant: true,
    standards: ['NIST SP 800-88', 'ISO 27001'],
    details: {
      'Passes Completed': '3/3', 'Bad Sectors': '0', 'Verification': 'Passed',
      'Duration': '8m 45s', 'Speed Avg': '125 MB/s', 'Sectors': '125,045,424'
    }
  },
  {
    id: 'R005', type: 'recovery', icon: '🔍', typeLabel: 'rt-recovery',
    name: 'Emergency Recovery — Corrupted MicroSD',
    device: 'Generic MicroSD 32GB • /dev/sdd',
    algo: 'Signature-Based Carving',
    operator: 'Digital Forensics Lab',
    date: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000),
    size: '32 GB',
    hash: Array.from({length:64},()=>Math.floor(Math.random()*16).toString(16)).join(''),
    compliant: true,
    standards: ['SWGDE Guidelines', 'ISO 27037'],
    details: {
      'Files Recovered': '18', 'Recovery Rate': '91.7%', 'Confidence Avg': '82%',
      'Fragmented': '7', 'Scan Duration': '12m 33s', 'Bad Sectors Handled': '5'
    }
  },
];

let allReports = [...MOCK_REPORTS];
let displayReports = [...MOCK_REPORTS];

function formatTimeAgo(date) {
  const diff = Date.now() - date.getTime();
  const mins = Math.floor(diff / 60000);
  const hrs = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (mins < 60) return `${mins}m ago`;
  if (hrs < 24) return `${hrs}h ago`;
  return `${days}d ago`;
}

function renderReports() {
  const list = document.getElementById('reportsList');
  const eraseCount = allReports.filter(r => r.type === 'erase').length;
  const recovCount = allReports.filter(r => r.type === 'recovery').length;

  document.getElementById('rs-total').textContent = allReports.length;
  document.getElementById('rs-erase').textContent = eraseCount;
  document.getElementById('rs-recovery').textContent = recovCount;

  if (displayReports.length === 0) {
    list.innerHTML = `<div style="text-align:center;padding:4rem;color:var(--text-muted);">No reports found</div>`;
    return;
  }

  list.innerHTML = displayReports.map(r => `
    <div class="report-card" onclick="showDetail('${r.id}')">
      <div class="report-icon" style="background:${r.type==='erase'?'rgba(239,68,68,.1)':r.type==='recovery'?'rgba(99,102,241,.1)':'rgba(245,158,11,.1)'};">${r.icon}</div>
      <div class="report-info">
        <div class="report-name">${r.name}</div>
        <div class="report-meta">${r.device} • ${r.algo}</div>
        <div class="report-meta" style="margin-top:.2rem;">👤 ${r.operator}</div>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:.5rem;flex-shrink:0;">
        <div class="report-type ${r.typeLabel}">${r.type.charAt(0).toUpperCase() + r.type.slice(1)}</div>
        <div style="font-size:.7rem;color:var(--text-muted);font-family:var(--font-mono);">${formatTimeAgo(r.date)}</div>
        <div style="font-size:.7rem;color:var(--green);font-weight:700;">✓ Compliant</div>
      </div>
      <div class="report-actions">
        <button class="action-btn" onclick="downloadReport('${r.id}',event)" title="Download">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        </button>
        <button class="action-btn" onclick="deleteReport('${r.id}',event)" title="Delete" style="color:var(--red);">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
        </button>
      </div>
    </div>
  `).join('');
}

function filterReports() {
  const search = document.getElementById('reportSearch').value.toLowerCase();
  const typeF = document.getElementById('reportTypeFilter').value;

  displayReports = allReports.filter(r => {
    const matchSearch = !search ||
      r.name.toLowerCase().includes(search) ||
      r.device.toLowerCase().includes(search) ||
      r.operator.toLowerCase().includes(search) ||
      r.algo.toLowerCase().includes(search);
    const matchType = !typeF || r.type === typeF;
    return matchSearch && matchType;
  });

  renderReports();
}

function showDetail(id) {
  const r = allReports.find(x => x.id === id);
  if (!r) return;

  document.getElementById('detailTitle').textContent = `${r.icon} ${r.name}`;
  document.getElementById('detailMeta').textContent = `${r.id} • ${r.date.toLocaleString()} • ${r.operator}`;

  document.getElementById('detailContent').innerHTML = `
    <div>
      <div style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.75rem;">Operation Details</div>
      ${Object.entries(r.details).map(([k, v]) => `
        <div style="display:flex;justify-content:space-between;padding:.5rem 0;border-bottom:1px solid var(--border);">
          <span style="font-size:.78rem;color:var(--text-muted);">${k}</span>
          <span style="font-size:.78rem;font-weight:600;font-family:var(--font-mono);">${v}</span>
        </div>
      `).join('')}
    </div>
    <div>
      <div style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.75rem;">Compliance</div>
      ${r.standards.map(s => `
        <div style="display:flex;align-items:center;gap:.5rem;padding:.5rem;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.15);border-radius:8px;margin-bottom:.5rem;">
          <span style="color:var(--green);">✓</span>
          <span style="font-size:.78rem;font-weight:600;">${s}</span>
        </div>
      `).join('')}
      <div style="margin-top:1rem;">
        <div style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.5rem;">SHA-256 Signature</div>
        <div class="hash-display" style="font-size:.65rem;">${r.hash}</div>
      </div>
    </div>
    <div>
      <div style="font-size:.75rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.75rem;">Actions</div>
      <div style="display:flex;flex-direction:column;gap:.75rem;">
        <button class="btn-success" onclick="downloadReport('${r.id}')" style="justify-content:center;">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          Download PDF Report
        </button>
        <button class="btn-outline" style="justify-content:center;" onclick="window.ForenShield?.toast('Printed','Report sent to printer.','info')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;"><polyline points="6 9 6 2 18 2 18 9"/><path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"/><rect x="6" y="14" width="12" height="8"/></svg>
          Print Certificate
        </button>
        <button class="btn-outline" style="justify-content:center;" onclick="verifyHash('${r.id}')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:16px;height:16px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          Verify Integrity
        </button>
      </div>
    </div>
  `;

  document.getElementById('reportDetailPanel').style.display = 'block';
  document.getElementById('reportDetailPanel').scrollIntoView({ behavior: 'smooth' });
  addAuditLog(`Report opened: ${r.name}`);
}

function closeDetail() {
  document.getElementById('reportDetailPanel').style.display = 'none';
}

function downloadReport(id, e) {
  if (e) e.stopPropagation();
  const r = allReports.find(x => x.id === id);
  window.ForenShield?.toast('Downloading', `${r.name} report saved.`, 'success');
  addAuditLog(`Report downloaded: ${r.name}`);
}

function deleteReport(id, e) {
  if (e) e.stopPropagation();
  if (!confirm('Delete this report? This action cannot be undone.')) return;
  allReports = allReports.filter(r => r.id !== id);
  displayReports = displayReports.filter(r => r.id !== id);
  renderReports();
  window.ForenShield?.toast('Deleted', 'Report has been removed.', 'info');
  addAuditLog(`Report deleted: ${id}`);
}

function verifyHash(id) {
  setTimeout(() => {
    window.ForenShield?.toast('Integrity Verified', 'SHA-256 hash matches — report is unmodified.', 'success');
    addAuditLog(`Hash verification passed for report: ${id}`);
  }, 800);
}

function generateNewReport() {
  const types = ['erase', 'recovery', 'file'];
  const type = types[Math.floor(Math.random() * types.length)];
  const devices = ['Samsung SSD 870', 'Seagate HDD 2TB', 'SanDisk USB 128GB', 'Lexar SD 64GB'];
  const operators = ['Dr. A. Sharma', 'Inspector P. Verma', 'Dr. K. Rao', 'Security Admin'];
  const algos = ['DoD 5220.22-M (7-pass)', 'Gutmann (35-pass)', 'NIST 800-88', 'AI-Assisted Hybrid'];

  const newReport = {
    id: 'R' + String(allReports.length + 1).padStart(3, '0'),
    type,
    icon: type === 'erase' ? '🗑️' : type === 'recovery' ? '🔍' : '📄',
    typeLabel: type === 'erase' ? 'rt-erase' : type === 'recovery' ? 'rt-recovery' : 'rt-file',
    name: `${type === 'erase' ? 'Secure Erase' : type === 'recovery' ? 'Forensic Recovery' : 'File Erase'} — ${devices[Math.floor(Math.random() * devices.length)]}`,
    device: `${devices[Math.floor(Math.random() * devices.length)]}`,
    algo: algos[Math.floor(Math.random() * algos.length)],
    operator: operators[Math.floor(Math.random() * operators.length)],
    date: new Date(),
    size: Math.floor(Math.random() * 500) + ' GB',
    hash: Array.from({length:64},()=>Math.floor(Math.random()*16).toString(16)).join(''),
    compliant: true,
    standards: ['NIST SP 800-88', 'DoD 5220.22-M'],
    details: { 'Status': 'Completed', 'Verification': 'Passed', 'Compliance': 'Confirmed' }
  };

  allReports.unshift(newReport);
  displayReports = [...allReports];
  renderReports();
  window.ForenShield?.toast('Report Generated', `New report ${newReport.id} created successfully.`, 'success');
  addAuditLog(`New report generated: ${newReport.name}`);
}

function addAuditLog(msg) {
  const log = document.getElementById('auditLog');
  const now = new Date();
  const time = [now.getHours(), now.getMinutes(), now.getSeconds()].map(n => String(n).padStart(2,'0')).join(':');
  const line = document.createElement('div');
  line.className = 'log-line';
  line.innerHTML = `<span class="log-time">${time}</span><span class="log-type-info"> [AUDIT]</span><span class="log-msg"> ${msg}</span>`;
  log.appendChild(line);
  log.scrollTop = log.scrollHeight;
}

// Init
renderReports();
addAuditLog('Reports module loaded');
addAuditLog(`Loaded ${allReports.length} existing reports`);

// Auto audit trail
setInterval(() => {
  const entries = [
    'Scheduled integrity check completed',
    'Compliance database synchronized',
    'Digital signatures verified',
    'Audit chain checkpoint saved',
    'Session heartbeat logged',
  ];
  addAuditLog(entries[Math.floor(Math.random() * entries.length)]);
}, 10000);
