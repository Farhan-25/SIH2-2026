/* ForenShield — Disk Analyzer Logic */

// ============ Mock Data ============
const PARTITIONS = [
  { label: 'EFI System', fs: 'FAT32', start: 2048, end: 1050623, sizeMB: 512, type: 'EFI', color: '#6366f1', pct: 5 },
  { label: 'Windows (C:)', fs: 'NTFS', start: 1050624, end: 838860800, sizeMB: 409600, type: 'Primary', color: '#3b82f6', pct: 45 },
  { label: 'Recovery', fs: 'NTFS', start: 838860801, end: 856064000, sizeMB: 8400, type: 'Recovery', color: '#f59e0b', pct: 8 },
  { label: 'Data (D:)', fs: 'NTFS', start: 856064001, end: 976773167, sizeMB: 58458, type: 'Primary', color: '#10b981', pct: 38 },
  { label: 'Unallocated', fs: '—', start: 0, end: 2047, sizeMB: 1, type: 'Unallocated', color: '#374151', pct: 4 },
];

const FS_TREE_DATA = [
  { path: '/', type: 'dir', children: [
    { path: '/Windows', type: 'dir', children: [
      { path: '/Windows/System32', type: 'dir', children: [
        { path: '/Windows/System32/ntdll.dll', type: 'file', size: 1900544, modified: '2025-06-01', deleted: false },
        { path: '/Windows/System32/kernel32.dll', type: 'file', size: 886784, modified: '2025-06-01', deleted: false },
        { path: '/Windows/System32/[DELETED]config.sys', type: 'file', size: 4096, modified: '2024-11-15', deleted: true },
      ]},
      { path: '/Windows/Temp', type: 'dir', children: [
        { path: '/Windows/Temp/tmp4729.tmp', type: 'file', size: 65536, modified: '2025-09-20', deleted: true },
        { path: '/Windows/Temp/~DF2845.tmp', type: 'file', size: 12288, modified: '2025-09-22', deleted: false },
      ]},
    ]},
    { path: '/Users', type: 'dir', children: [
      { path: '/Users/Suspect', type: 'dir', children: [
        { path: '/Users/Suspect/Desktop', type: 'dir', children: [
          { path: '/Users/Suspect/Desktop/financial_data.xlsx', type: 'file', size: 2097152, modified: '2025-09-18', deleted: false },
          { path: '/Users/Suspect/Desktop/[DELETED]evidence.pdf', type: 'file', size: 512000, modified: '2025-09-19', deleted: true },
          { path: '/Users/Suspect/Desktop/[DELETED]photo_001.jpg', type: 'file', size: 3145728, modified: '2025-09-17', deleted: true },
        ]},
        { path: '/Users/Suspect/AppData', type: 'dir', children: [
          { path: '/Users/Suspect/AppData/Thumbs.db', type: 'file', size: 24576, modified: '2025-09-20', deleted: false },
        ]},
      ]},
    ]},
    { path: '/pagefile.sys', type: 'file', size: 4294967296, modified: '2025-09-24', deleted: false },
    { path: '/hiberfil.sys', type: 'file', size: 8589934592, modified: '2025-09-23', deleted: false },
  ]}
];

const TIMELINE_EVENTS = [
  { ts: new Date('2025-09-24T22:31:00'), action: 'Modified', file: '/Users/Suspect/Desktop/financial_data.xlsx', type: 'file' },
  { ts: new Date('2025-09-24T21:14:00'), action: 'Deleted', file: '/Users/Suspect/Desktop/evidence.pdf', type: 'deleted' },
  { ts: new Date('2025-09-24T20:55:00'), action: 'Deleted', file: '/Users/Suspect/Desktop/photo_001.jpg', type: 'deleted' },
  { ts: new Date('2025-09-24T20:30:00'), action: 'Accessed', file: '/Windows/System32/ntdll.dll', type: 'access' },
  { ts: new Date('2025-09-23T18:22:00'), action: 'Created', file: '/Users/Suspect/Desktop/financial_data.xlsx', type: 'created' },
  { ts: new Date('2025-09-22T14:10:00'), action: 'Modified', file: '/Windows/Temp/~DF2845.tmp', type: 'file' },
  { ts: new Date('2025-09-21T11:04:00'), action: 'Deleted', file: '/Windows/Temp/tmp4729.tmp', type: 'deleted' },
  { ts: new Date('2025-09-20T09:30:00'), action: 'Accessed', file: '/Users/Suspect/AppData/Thumbs.db', type: 'access' },
  { ts: new Date('2025-09-19T16:45:00'), action: 'Modified', file: '/pagefile.sys', type: 'file' },
  { ts: new Date('2025-09-18T12:00:00'), action: 'Created', file: '/hiberfil.sys', type: 'created' },
];

let activeTab = 'fs';
let hexOffset = 0;
const BYTES_PER_SECTOR = 512;

// ============ Init ============
function analyzeImage() {
  const btn = document.getElementById('analyzeBtn');
  btn.textContent = '⟳ Analyzing...';
  btn.disabled = true;

  setTimeout(() => {
    btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Analyze`;
    btn.disabled = false;
    renderAll();
    window.ForenShield?.toast('Analysis Complete', 'Disk structure analyzed successfully.', 'success');
  }, 2000);
}

function renderAll() {
  renderDiskMap();
  renderPartitionTree();
  renderFSTree(FS_TREE_DATA[0].children, document.getElementById('fsTree'), 0);
  renderSMART();
  renderFSMeta();
  renderHexView();
  renderTimeline();
}

// ============ Disk Map Canvas ============
function renderDiskMap() {
  const canvas = document.getElementById('diskMap');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  let x = 0;
  const legend = document.getElementById('diskLegend');
  legend.innerHTML = '';

  PARTITIONS.forEach(p => {
    const w = (p.pct / 100) * W;
    ctx.fillStyle = p.color;
    ctx.fillRect(x, 0, w, H);
    ctx.strokeStyle = 'rgba(0,0,0,.3)';
    ctx.lineWidth = 2;
    ctx.strokeRect(x, 0, w, H);

    // Label
    ctx.fillStyle = 'white';
    ctx.font = 'bold 11px Inter, sans-serif';
    ctx.textAlign = 'center';
    if (w > 60) {
      ctx.fillText(p.label, x + w / 2, H / 2 - 5);
      ctx.font = '10px JetBrains Mono, monospace';
      ctx.fillStyle = 'rgba(255,255,255,.7)';
      ctx.fillText(p.fs + ' · ' + (p.sizeMB >= 1024 ? (p.sizeMB/1024).toFixed(0)+'GB' : p.sizeMB+'MB'), x + w / 2, H / 2 + 12);
    }

    // Legend dot
    const dot = document.createElement('div');
    dot.style.cssText = `display:flex;align-items:center;gap:.4rem;font-size:.72rem;color:var(--text-secondary);`;
    dot.innerHTML = `<div style="width:12px;height:12px;border-radius:3px;background:${p.color};flex-shrink:0;"></div>${p.label} (${p.fs})`;
    legend.appendChild(dot);

    x += w;
  });
}

// ============ Partition Tree ============
function renderPartitionTree() {
  const tree = document.getElementById('partitionTree');
  tree.innerHTML = `
    <div style="margin-bottom:.5rem;padding:.5rem;background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2);border-radius:6px;">
      <div style="color:var(--purple-light);font-weight:700;">📀 /dev/sda — 500GB</div>
      <div style="color:var(--text-muted);font-size:.68rem;">GPT Partition Table</div>
    </div>
    ${PARTITIONS.map((p, i) => `
      <div style="display:flex;align-items:center;gap:.5rem;padding:.5rem .75rem;margin-bottom:.35rem;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:6px;cursor:pointer;transition:all .2s;"
           onclick="selectPartition(${i})" onmouseover="this.style.borderColor='var(--border-hover)'" onmouseout="this.style.borderColor='var(--border)'">
        <div style="width:10px;height:10px;border-radius:2px;background:${p.color};flex-shrink:0;"></div>
        <div style="flex:1;">
          <div style="color:var(--text-primary);font-weight:600;">${p.label}</div>
          <div style="color:var(--text-muted);font-size:.65rem;">${p.fs} · ${p.sizeMB >= 1024 ? (p.sizeMB/1024).toFixed(0)+'GB' : p.sizeMB+'MB'}</div>
        </div>
        <div style="font-size:.62rem;color:var(--text-muted);">${p.type}</div>
      </div>
    `).join('')}
  `;
}

function selectPartition(idx) {
  window.ForenShield?.toast('Partition Selected', `Analyzing ${PARTITIONS[idx].label}...`, 'info');
}

// ============ SMART Data ============
function renderSMART() {
  const attrs = [
    { id: '01', name: 'Read Error Rate', val: 0, status: 'OK' },
    { id: '05', name: 'Reallocated Sectors', val: 0, status: 'OK' },
    { id: '09', name: 'Power-On Hours', val: 8421, status: 'OK' },
    { id: '0C', name: 'Power Cycle Count', val: 347, status: 'OK' },
    { id: 'C5', name: 'Pending Sectors', val: 0, status: 'OK' },
    { id: 'C6', name: 'Uncorrectable Errors', val: 0, status: 'OK' },
    { id: 'BB', name: 'Reported Uncorrect', val: 0, status: 'OK' },
    { id: 'C0', name: 'Unsafe Shutdown Count', val: 12, status: 'WARN' },
  ];

  document.getElementById('smartData').innerHTML = attrs.map(a => `
    <div style="display:flex;justify-content:space-between;align-items:center;padding:.35rem 0;border-bottom:1px solid var(--border);">
      <div>
        <span style="color:var(--text-muted);font-family:var(--font-mono);">${a.id} </span>
        <span style="color:var(--text-secondary);">${a.name}</span>
      </div>
      <div style="display:flex;align-items:center;gap:.5rem;">
        <span style="font-family:var(--font-mono);color:var(--text-primary);">${a.val}</span>
        <span style="font-size:.62rem;font-weight:700;padding:.1rem .4rem;border-radius:20px;${a.status==='OK'?'background:rgba(16,185,129,.1);color:var(--green);':'background:rgba(245,158,11,.1);color:var(--orange);'}">${a.status}</span>
      </div>
    </div>
  `).join('');
}

// ============ File System Tree ============
let allFSItems = [];
function flattenTree(nodes, depth = 0) {
  nodes.forEach(n => {
    allFSItems.push({ ...n, depth });
    if (n.children) flattenTree(n.children, depth + 1);
  });
}
flattenTree(FS_TREE_DATA[0].children);

function renderFSTree(nodes, container, depth) {
  nodes.forEach(n => {
    const div = document.createElement('div');
    div.style.cssText = `padding:.3rem .5rem;padding-left:${depth * 16 + 8}px;cursor:pointer;border-radius:4px;transition:background .15s;`;
    div.onmouseover = () => div.style.background = 'rgba(255,255,255,.04)';
    div.onmouseout = () => div.style.background = '';

    const isDeleted = n.deleted;
    const icon = n.type === 'dir' ? '📁' : getFileIcon(n.path);
    const name = n.path.split('/').pop();
    const sizeStr = n.size ? ` (${formatSz(n.size)})` : '';
    const modStr = n.modified ? ` · ${n.modified}` : '';

    div.innerHTML = `
      <span style="margin-right:.4rem;">${icon}</span>
      <span style="color:${isDeleted ? '#f87171' : n.type === 'dir' ? 'var(--purple-light)' : 'var(--text-primary)'};${isDeleted ? 'text-decoration:line-through;' : ''}">${name}</span>
      <span style="color:var(--text-muted);font-size:.65rem;">${sizeStr}${modStr}</span>
      ${isDeleted ? '<span style="margin-left:.5rem;font-size:.6rem;font-weight:700;background:rgba(239,68,68,.1);color:#f87171;padding:.1rem .4rem;border-radius:20px;">DELETED</span>' : ''}
    `;

    container.appendChild(div);
    if (n.children) renderFSTree(n.children, container, depth + 1);
  });
}

function filterFSTree() {
  const q = document.getElementById('fsSearch').value.toLowerCase();
  const container = document.getElementById('fsTree');
  container.innerHTML = '';
  if (!q) {
    renderFSTree(FS_TREE_DATA[0].children, container, 0);
    return;
  }
  const matches = allFSItems.filter(n => n.path.toLowerCase().includes(q));
  matches.forEach(n => {
    const div = document.createElement('div');
    div.style.cssText = 'padding:.3rem .5rem;border-radius:4px;';
    const icon = n.type === 'dir' ? '📁' : getFileIcon(n.path);
    div.innerHTML = `${icon} <span style="color:${n.deleted?'#f87171':'var(--text-primary)'};">${n.path}</span> <span style="color:var(--text-muted);font-size:.65rem;">${n.size ? '('+formatSz(n.size)+')' : ''}</span>`;
    container.appendChild(div);
  });
}

function getFileIcon(p) {
  const ext = p.split('.').pop().toLowerCase();
  const map = { dll:'⚙️', sys:'⚙️', exe:'⚙️', jpg:'🖼️', jpeg:'🖼️', png:'🖼️', pdf:'📄', xlsx:'📊', xls:'📊', doc:'📝', docx:'📝', tmp:'🗑️', db:'🗃️', ini:'⚙️', log:'📋' };
  return map[ext] || '📄';
}

function formatSz(b) {
  if (b < 1024) return b + 'B';
  if (b < 1048576) return (b/1024).toFixed(0) + 'KB';
  if (b < 1073741824) return (b/1048576).toFixed(1) + 'MB';
  return (b/1073741824).toFixed(1) + 'GB';
}

// ============ FS Metadata ============
function renderFSMeta() {
  document.getElementById('fsMeta').innerHTML = `
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1.5rem;">
      ${[
        ['File System', 'NTFS v3.1'],
        ['Volume Label', 'Windows (C:)'],
        ['Cluster Size', '4,096 bytes (8 sectors)'],
        ['Total Clusters', '102,359,808'],
        ['Used Clusters', '57,923,744 (56.6%)'],
        ['Free Clusters', '44,436,064 (43.4%)'],
        ['MFT Size', '1.2 GB'],
        ['MFT Entries', '312,481'],
        ['Volume GUID', '{5F4A2B3C-D1E2-4F56-8901-23456789ABCD}'],
        ['Created', '2024-03-15 09:22:41 UTC'],
        ['Last Check', '2025-09-23 04:15:02 UTC'],
        ['Serial Number', '0x4A2B3C5D'],
      ].map(([k,v]) => `
        <div style="padding:.75rem;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:8px;">
          <div style="font-size:.68rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:.07em;margin-bottom:.3rem;">${k}</div>
          <div style="font-size:.82rem;font-weight:600;font-family:var(--font-mono);">${v}</div>
        </div>
      `).join('')}
    </div>
    <div style="font-size:.8rem;font-weight:700;color:var(--text-secondary);margin-bottom:.75rem;">MFT Zone Map</div>
    <div class="sector-grid" style="grid-template-columns:repeat(60,1fr);">
      ${Array.from({length:180}, (_, i) => {
        const state = i < 80 ? 'used' : i < 95 ? 'mft' : i < 120 ? 'free' : i < 125 ? 'bad' : 'free';
        const colors = { used: 'rgba(99,102,241,.5)', mft: 'rgba(139,92,246,.9)', free: 'rgba(255,255,255,.05)', bad: 'rgba(239,68,68,.5)' };
        return `<div style="aspect-ratio:1;border-radius:2px;background:${colors[state]};"></div>`;
      }).join('')}
    </div>
    <div style="display:flex;gap:1rem;margin-top:.5rem;flex-wrap:wrap;">
      ${[['rgba(99,102,241,.5)','Used'],['rgba(139,92,246,.9)','MFT Zone'],['rgba(255,255,255,.05)','Free'],['rgba(239,68,68,.5)','Bad']].map(([c,l])=>`
        <div style="display:flex;align-items:center;gap:.4rem;font-size:.7rem;color:var(--text-muted);">
          <div style="width:10px;height:10px;border-radius:2px;background:${c};"></div>${l}
        </div>`).join('')}
    </div>
  `;
}

// ============ Hex Viewer ============
const HEX_BYTES = (() => {
  const arr = [];
  // MBR signature
  const mbr = [0x33, 0xC0, 0x8E, 0xD0, 0xBC, 0x00, 0x7C, 0x8B, 0xF4, 0x50, 0x07, 0x50, 0x1F, 0xFB, 0xFC, 0xBF,
               0x00, 0x06, 0xB9, 0x00, 0x01, 0xF2, 0xA5, 0xEA, 0x1D, 0x06, 0x00, 0x00, 0x60, 0x00, 0x00, 0x00,
               0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
               0x4E, 0x54, 0x46, 0x53, 0x20, 0x20, 0x20, 0x20, 0x00, 0x02, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00];
  mbr.forEach(b => arr.push(b));
  for (let i = mbr.length; i < 512 * 4; i++) arr.push(Math.floor(Math.random() * 256));
  arr[510] = 0x55; arr[511] = 0xAA; // MBR signature
  return arr;
})();

function renderHexView() {
  const offset = parseInt(document.getElementById('hexOffset').value) || 0;
  const bpr = parseInt(document.getElementById('hexBytesPerRow').value) || 16;
  const ROWS = 24;
  const total = ROWS * bpr;
  const bytes = HEX_BYTES.slice(offset, offset + total);

  let html = `<div style="color:var(--text-muted);margin-bottom:.5rem;font-size:.68rem;">Sector ${Math.floor(offset/512)} · Offset 0x${offset.toString(16).toUpperCase().padStart(8,'0')}</div>`;
  html += `<div style="display:grid;grid-template-columns:auto 1fr auto;gap:1rem;">`;

  // Offsets
  let offsets = '', hexStr = '', ascii = '';
  for (let row = 0; row < ROWS; row++) {
    const rowOffset = offset + row * bpr;
    offsets += `<div style="color:var(--text-muted);">${rowOffset.toString(16).toUpperCase().padStart(8,'0')}</div>`;

    let hexRow = '';
    let ascRow = '';
    for (let col = 0; col < bpr; col++) {
      const idx = row * bpr + col;
      const byte = bytes[idx];
      if (byte === undefined) { hexRow += `<span style="color:transparent;">00</span> `; ascRow += ' '; continue; }
      const isNull = byte === 0;
      const isPrint = byte >= 32 && byte < 127;
      const isSpecial = [0x55, 0xAA].includes(byte);
      const color = isSpecial ? '#f87171' : isNull ? 'var(--text-muted)' : isPrint ? '#86efac' : 'var(--text-secondary)';
      hexRow += `<span style="color:${color};">${byte.toString(16).toUpperCase().padStart(2,'0')}</span> `;
      ascRow += isPrint ? `<span style="color:${color};">${String.fromCharCode(byte)}</span>` : `<span style="color:var(--text-muted);">.</span>`;
      if (col === bpr/2 - 1) hexRow += ' ';
    }
    hexStr += `<div style="letter-spacing:.1em;">${hexRow}</div>`;
    ascii += `<div>${ascRow}</div>`;
  }

  html += `<div>${offsets}</div><div style="overflow-x:auto;">${hexStr}</div><div style="border-left:1px solid var(--border);padding-left:.75rem;">${ascii}</div>`;
  html += `</div>`;
  document.getElementById('hexView').innerHTML = html;
}

function prevSector() {
  const el = document.getElementById('hexOffset');
  el.value = Math.max(0, parseInt(el.value) - 512);
  renderHexView();
}

function nextSector() {
  const el = document.getElementById('hexOffset');
  el.value = parseInt(el.value) + 512;
  renderHexView();
}

// ============ Timeline ============
function renderTimeline() {
  const canvas = document.getElementById('timelineCanvas');
  const ctx = canvas.getContext('2d');
  const W = canvas.width, H = canvas.height;
  ctx.clearRect(0, 0, W, H);

  // Background
  ctx.fillStyle = 'rgba(0,0,0,.0)';
  ctx.fillRect(0, 0, W, H);

  // Grid lines
  ctx.strokeStyle = 'rgba(255,255,255,.05)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 10; i++) {
    const x = (i / 10) * W;
    ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke();
  }

  // Events as bars
  const minT = Math.min(...TIMELINE_EVENTS.map(e => e.ts.getTime()));
  const maxT = Math.max(...TIMELINE_EVENTS.map(e => e.ts.getTime()));
  const range = maxT - minT;

  const typeColors = { file: '#6366f1', deleted: '#ef4444', access: '#06b6d4', created: '#10b981' };

  TIMELINE_EVENTS.forEach((e, i) => {
    const x = ((e.ts.getTime() - minT) / range) * (W - 40) + 20;
    const color = typeColors[e.type] || '#94a3b8';
    ctx.fillStyle = color;
    ctx.shadowColor = color;
    ctx.shadowBlur = 6;
    ctx.beginPath();
    ctx.arc(x, H / 2, 7, 0, Math.PI * 2);
    ctx.fill();
    ctx.shadowBlur = 0;

    // Stem
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.setLineDash([3,3]);
    ctx.beginPath();
    if (i % 2 === 0) { ctx.moveTo(x, H/2 - 7); ctx.lineTo(x, 15); }
    else { ctx.moveTo(x, H/2 + 7); ctx.lineTo(x, H - 15); }
    ctx.stroke();
    ctx.setLineDash([]);
  });

  // Center line
  ctx.strokeStyle = 'rgba(255,255,255,.15)';
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(20, H/2); ctx.lineTo(W-20, H/2); ctx.stroke();

  // Event list
  document.getElementById('timelineList').innerHTML = TIMELINE_EVENTS.map(e => `
    <div style="display:flex;align-items:center;gap:.875rem;padding:.625rem .75rem;border-radius:6px;margin-bottom:.35rem;background:rgba(255,255,255,.02);border:1px solid var(--border);">
      <div style="width:8px;height:8px;border-radius:50%;background:${typeColors[e.type]||'#94a3b8'};flex-shrink:0;box-shadow:0 0 6px ${typeColors[e.type]||'#94a3b8'};"></div>
      <div style="font-size:.72rem;font-family:var(--font-mono);color:var(--text-muted);white-space:nowrap;">${e.ts.toLocaleString()}</div>
      <div style="font-size:.75rem;font-weight:600;color:${typeColors[e.type]||'var(--text-muted)'};min-width:60px;">${e.action}</div>
      <div style="font-size:.75rem;color:var(--text-secondary);font-family:var(--font-mono);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${e.file}</div>
    </div>
  `).join('');
}

// ============ Tab Switching ============
function switchTab(tab) {
  activeTab = tab;
  ['fs','hex','meta','timeline'].forEach(t => {
    document.getElementById('panel-' + t).style.display = t === tab ? 'block' : 'none';
    const btn = document.getElementById('tab-' + t);
    btn.style.borderBottomColor = t === tab ? 'var(--purple)' : 'transparent';
    btn.style.color = t === tab ? 'var(--purple-light)' : 'var(--text-muted)';
  });
}

// Auto-analyze on load
setTimeout(analyzeImage, 600);
