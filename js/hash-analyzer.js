/* ForenShield — Hash & Signature Analyzer Logic */

// ============ Signature Database ============
const SIG_DB = [
  { name: 'JPEG Image',        ext: 'jpg/jpeg', hex: 'FF D8 FF',        cat: 'image',   desc: 'Joint Photographic Experts Group' },
  { name: 'PNG Image',         ext: 'png',      hex: '89 50 4E 47 0D 0A 1A 0A', cat: 'image', desc: 'Portable Network Graphics' },
  { name: 'GIF Image',         ext: 'gif',      hex: '47 49 46 38',     cat: 'image',   desc: 'Graphics Interchange Format' },
  { name: 'BMP Image',         ext: 'bmp',      hex: '42 4D',           cat: 'image',   desc: 'Windows Bitmap' },
  { name: 'TIFF Image',        ext: 'tif/tiff', hex: '49 49 2A 00',     cat: 'image',   desc: 'Tagged Image File Format (LE)' },
  { name: 'TIFF Image (BE)',   ext: 'tif/tiff', hex: '4D 4D 00 2A',     cat: 'image',   desc: 'Tagged Image File Format (BE)' },
  { name: 'WEBP Image',        ext: 'webp',     hex: '52 49 46 46 ?? ?? ?? ?? 57 45 42 50', cat: 'image', desc: 'Google WebP' },
  { name: 'ICO File',          ext: 'ico',      hex: '00 00 01 00',     cat: 'image',   desc: 'Windows Icon' },
  { name: 'MP4 Video',         ext: 'mp4',      hex: '66 74 79 70',     cat: 'video',   desc: 'MPEG-4 Part 14 (offset 4)' },
  { name: 'AVI Video',         ext: 'avi',      hex: '52 49 46 46',     cat: 'video',   desc: 'Audio Video Interleave' },
  { name: 'Matroska Video',    ext: 'mkv',      hex: '1A 45 DF A3',     cat: 'video',   desc: 'Matroska Multimedia Container' },
  { name: 'MOV Video',         ext: 'mov',      hex: '66 74 79 70 71 74', cat: 'video', desc: 'Apple QuickTime Movie' },
  { name: 'FLV Video',         ext: 'flv',      hex: '46 4C 56 01',     cat: 'video',   desc: 'Flash Video' },
  { name: 'MPEG Video',        ext: 'mpeg/mpg', hex: '00 00 01 BA',     cat: 'video',   desc: 'MPEG Video Stream' },
  { name: 'WMV Video',         ext: 'wmv',      hex: '30 26 B2 75 8E 66 CF 11', cat: 'video', desc: 'Windows Media Video' },
  { name: 'MP3 Audio',         ext: 'mp3',      hex: 'FF FB / ID3',     cat: 'audio',   desc: 'MPEG Layer III Audio' },
  { name: 'FLAC Audio',        ext: 'flac',     hex: '66 4C 61 43',     cat: 'audio',   desc: 'Free Lossless Audio Codec' },
  { name: 'WAV Audio',         ext: 'wav',      hex: '52 49 46 46',     cat: 'audio',   desc: 'Waveform Audio File' },
  { name: 'OGG Audio',         ext: 'ogg',      hex: '4F 67 67 53',     cat: 'audio',   desc: 'OGG Vorbis Audio' },
  { name: 'AAC Audio',         ext: 'aac',      hex: 'FF F1 / FF F9',   cat: 'audio',   desc: 'Advanced Audio Coding' },
  { name: 'PDF Document',      ext: 'pdf',      hex: '25 50 44 46 2D',  cat: 'doc',     desc: 'Adobe Portable Document Format' },
  { name: 'MS Office (OLE)',   ext: 'doc/xls/ppt', hex: 'D0 CF 11 E0 A1 B1 1A E1', cat: 'doc', desc: 'Microsoft Compound File' },
  { name: 'Office Open XML',   ext: 'docx/xlsx/pptx', hex: '50 4B 03 04', cat: 'doc', desc: 'OOXML (ZIP-based Office)' },
  { name: 'RTF Document',      ext: 'rtf',      hex: '7B 5C 72 74 66',  cat: 'doc',     desc: 'Rich Text Format' },
  { name: 'HTML File',         ext: 'html/htm', hex: '3C 68 74 6D 6C',  cat: 'doc',     desc: 'Hypertext Markup Language' },
  { name: 'ZIP Archive',       ext: 'zip',      hex: '50 4B 03 04',     cat: 'archive', desc: 'ZIP Compressed Archive' },
  { name: 'RAR Archive',       ext: 'rar',      hex: '52 61 72 21 1A 07', cat: 'archive', desc: 'Roshal Archive' },
  { name: '7-Zip Archive',     ext: '7z',       hex: '37 7A BC AF 27 1C', cat: 'archive', desc: '7-Zip Archive' },
  { name: 'GZIP Archive',      ext: 'gz',       hex: '1F 8B 08',        cat: 'archive', desc: 'GNU Zip' },
  { name: 'BZIP2 Archive',     ext: 'bz2',      hex: '42 5A 68',        cat: 'archive', desc: 'Block Sorting Compressor' },
  { name: 'TAR Archive',       ext: 'tar',      hex: '75 73 74 61 72',  cat: 'archive', desc: 'Tape Archive (offset 257)' },
  { name: 'XZ Archive',        ext: 'xz',       hex: 'FD 37 7A 58 5A 00', cat: 'archive', desc: 'XZ Compressed Archive' },
  { name: 'SQLite Database',   ext: 'db/sqlite', hex: '53 51 4C 69 74 65 20 66 6F 72 6D 61 74 20 33 00', cat: 'db', desc: 'SQLite v3 Database' },
  { name: 'MS Access DB',      ext: 'mdb/accdb', hex: '00 01 00 00 53 74 61 6E 64 61 72 64', cat: 'db', desc: 'Microsoft Access Database' },
  { name: 'Windows EXE/DLL',   ext: 'exe/dll',  hex: '4D 5A',           cat: 'exe',     desc: 'DOS/Windows Portable Executable' },
  { name: 'ELF Executable',    ext: 'elf',      hex: '7F 45 4C 46',     cat: 'exe',     desc: 'Linux/Unix Executable' },
  { name: 'Mach-O Binary',     ext: 'macho',    hex: 'CE FA ED FE',     cat: 'exe',     desc: 'macOS Executable (32-bit)' },
  { name: 'Mach-O Binary 64',  ext: 'macho',    hex: 'CF FA ED FE',     cat: 'exe',     desc: 'macOS Executable (64-bit)' },
  { name: 'ISO Disc Image',    ext: 'iso',      hex: '43 44 30 30 31',  cat: 'archive', desc: 'ISO 9660 CD-ROM Image (offset 32769)' },
  { name: 'Disk Image (DD)',   ext: 'dd/img',   hex: 'Varies by FS',    cat: 'archive', desc: 'Raw disk image (raw copy)' },
  { name: 'E01 Forensic Image',ext: 'e01',      hex: '45 56 46 09 0D 0A FF 00', cat: 'archive', desc: 'EnCase Evidence File v1' },
  { name: 'Java Class',        ext: 'class',    hex: 'CA FE BA BE',     cat: 'exe',     desc: 'Java Bytecode Class' },
  { name: 'Photoshop PSD',     ext: 'psd',      hex: '38 42 50 53',     cat: 'image',   desc: 'Adobe Photoshop Document' },
  { name: 'Windows Registry',  ext: 'dat',      hex: '72 65 67 66',     cat: 'doc',     desc: 'Windows Registry Hive' },
  { name: 'Windows Event Log', ext: 'evtx',     hex: '45 6C 66 46 69 6C 65 00', cat: 'doc', desc: 'Windows Event Log' },
  { name: 'LNK Shortcut',      ext: 'lnk',      hex: '4C 00 00 00 01 14 02 00', cat: 'doc', desc: 'Windows Shell Link' },
  { name: 'Thumbs.db',         ext: 'db',       hex: 'D0 CF 11 E0',     cat: 'image',   desc: 'Windows Thumbnail Cache' },
];

let hashData = { md5: '', sha1: '', sha256: '', sha512: '' };
let displaySigs = [...SIG_DB];

// ============ Render Signature Table ============
function renderSigTable() {
  const tbody = document.getElementById('sigTableBody');
  const catColors = { image:'rgba(99,102,241,.1)', video:'rgba(139,92,246,.1)', audio:'rgba(6,182,212,.1)', doc:'rgba(245,158,11,.1)', archive:'rgba(16,185,129,.1)', db:'rgba(239,68,68,.1)', exe:'rgba(156,163,175,.1)' };
  const catTextColors = { image:'var(--purple-light)', video:'var(--violet-light)', audio:'var(--cyan)', doc:'var(--orange)', archive:'var(--green)', db:'#f87171', exe:'var(--text-muted)' };

  tbody.innerHTML = displaySigs.map(s => `
    <tr>
      <td style="font-weight:600;color:var(--text-primary);">${s.name}</td>
      <td style="font-family:var(--font-mono);font-size:.75rem;color:var(--purple-light);">.${s.ext}</td>
      <td><code style="font-family:var(--font-mono);font-size:.7rem;background:rgba(0,0,0,.3);padding:.2rem .5rem;border-radius:4px;color:var(--green);">${s.hex}</code></td>
      <td><span style="padding:.2rem .6rem;border-radius:20px;font-size:.65rem;font-weight:700;background:${catColors[s.cat]||'rgba(99,102,241,.1)'};color:${catTextColors[s.cat]||'var(--purple-light)'};">${s.cat.toUpperCase()}</span></td>
      <td style="color:var(--text-secondary);font-size:.8rem;">${s.desc}</td>
    </tr>
  `).join('');
}

function filterSigs() {
  const q = document.getElementById('sigSearch').value.toLowerCase();
  const cat = document.getElementById('sigCatFilter').value;
  displaySigs = SIG_DB.filter(s =>
    (!q || s.name.toLowerCase().includes(q) || s.ext.toLowerCase().includes(q) || s.hex.toLowerCase().includes(q) || s.desc.toLowerCase().includes(q)) &&
    (!cat || s.cat === cat)
  );
  renderSigTable();
}

renderSigTable();

// ============ Signature Identifier ============
function identifySignature() {
  const hex = document.getElementById('hexInput').value.trim().toUpperCase().replace(/[^0-9A-F ]/g, '').trim();
  if (!hex) {
    document.getElementById('sigResult').innerHTML = '<div style="text-align:center;padding:1.5rem;color:var(--text-muted);font-size:.8rem;">Enter hex bytes above to identify file type</div>';
    return;
  }

  const matches = SIG_DB.filter(s => {
    const sigHex = s.hex.replace(/[^0-9A-F]/gi, '').replace(/\?\?/g, '').toUpperCase();
    const inputHex = hex.replace(/ /g, '');
    if (sigHex.length < 4) return false;
    return inputHex.startsWith(sigHex.substring(0, Math.min(sigHex.length, 8)));
  });

  const container = document.getElementById('sigResult');
  if (matches.length === 0) {
    container.innerHTML = `
      <div style="padding:1rem;background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.2);border-radius:8px;">
        <div style="font-size:.85rem;font-weight:700;color:#f87171;margin-bottom:.25rem;">⚠️ Unknown Signature</div>
        <div style="font-size:.78rem;color:var(--text-secondary);">No matching file type found for this byte sequence. Possible encrypted, corrupted, or proprietary format.</div>
      </div>`;
    return;
  }

  container.innerHTML = matches.map(m => `
    <div style="padding:.875rem;background:rgba(16,185,129,.05);border:1px solid rgba(16,185,129,.2);border-radius:8px;margin-bottom:.5rem;">
      <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.35rem;">
        <div style="font-size:.9rem;font-weight:700;color:var(--green);">✓ ${m.name}</div>
        <code style="font-size:.7rem;font-family:var(--font-mono);color:var(--purple-light);">.${m.ext}</code>
      </div>
      <div style="font-size:.75rem;color:var(--text-secondary);">${m.desc}</div>
      <div style="font-size:.68rem;font-family:var(--font-mono);color:var(--text-muted);margin-top:.35rem;">Magic: ${m.hex}</div>
    </div>
  `).join('');
}

function testSig(hexStr) {
  document.getElementById('hexInput').value = hexStr;
  identifySignature();
}

// ============ Entropy Analyzer ============
function shannonEntropy(data) {
  if (!data || data.length === 0) return 0;
  const freq = {};
  for (const ch of data) freq[ch] = (freq[ch] || 0) + 1;
  let entropy = 0;
  const len = data.length;
  for (const count of Object.values(freq)) {
    const p = count / len;
    entropy -= p * Math.log2(p);
  }
  return entropy;
}

function analyzeEntropy() {
  const input = document.getElementById('entropyInput').value;
  const container = document.getElementById('entropyResult');
  if (!input) {
    container.innerHTML = '<div style="text-align:center;padding:1rem;color:var(--text-muted);font-size:.8rem;">Enter data above to analyze Shannon entropy</div>';
    return;
  }

  const H = shannonEntropy(input);
  const maxH = Math.log2(256);
  const normalizedH = (H / maxH) * 100;

  let assessment, color, assessment_detail;
  if (H < 1) { assessment = 'Very Low'; color = 'var(--green)'; assessment_detail = 'Highly repetitive or empty data'; }
  else if (H < 4) { assessment = 'Low'; color = '#86efac'; assessment_detail = 'Simple/structured data'; }
  else if (H < 5.5) { assessment = 'Normal'; color = 'var(--orange)'; assessment_detail = 'Typical text or document data'; }
  else if (H < 7) { assessment = 'High'; color = '#fb923c'; assessment_detail = 'May be compressed or structured binary'; }
  else if (H < 7.5) { assessment = 'Very High'; color = '#f87171'; assessment_detail = 'Likely compressed data'; }
  else { assessment = 'Maximum'; color = 'var(--red)'; assessment_detail = '⚠️ Likely ENCRYPTED or random data'; }

  const charFreq = {};
  for (const ch of input) charFreq[ch] = (charFreq[ch] || 0) + 1;
  const topChars = Object.entries(charFreq).sort((a,b)=>b[1]-a[1]).slice(0,5);

  container.innerHTML = `
    <div style="padding:1rem;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:8px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:.875rem;align-items:center;">
        <div>
          <div style="font-size:1.75rem;font-weight:800;font-family:var(--font-mono);color:${color};">${H.toFixed(4)}</div>
          <div style="font-size:.7rem;color:var(--text-muted);">bits/symbol</div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:.85rem;font-weight:700;color:${color};">${assessment} Entropy</div>
          <div style="font-size:.72rem;color:var(--text-muted);margin-top:.2rem;">${assessment_detail}</div>
        </div>
      </div>
      <div class="progress-bar" style="margin-bottom:.5rem;height:8px;">
        <div class="progress-fill" style="width:${normalizedH.toFixed(1)}%;background:${color};"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:.65rem;color:var(--text-muted);margin-bottom:.875rem;">
        <span>0 (Empty)</span><span>4 (Text)</span><span>7.5 (Compressed)</span><span>8 (Encrypted)</span>
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:.5rem;font-size:.72rem;">
        <div style="padding:.5rem;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:6px;">
          <div style="color:var(--text-muted);">Length</div>
          <div style="font-weight:700;font-family:var(--font-mono);">${input.length.toLocaleString()}</div>
        </div>
        <div style="padding:.5rem;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:6px;">
          <div style="color:var(--text-muted);">Unique Chars</div>
          <div style="font-weight:700;font-family:var(--font-mono);">${Object.keys(charFreq).length}</div>
        </div>
        <div style="padding:.5rem;background:rgba(255,255,255,.02);border:1px solid var(--border);border-radius:6px;">
          <div style="color:var(--text-muted);">Max Entropy</div>
          <div style="font-weight:700;font-family:var(--font-mono);">${maxH.toFixed(4)}</div>
        </div>
      </div>
    </div>
  `;
}

// ============ Pseudo-Hash (Forensic simulation) ============
// NOTE: Real app would use WebCrypto API with actual file bytes.
// This simulates hash computation for demonstration.
function simHash(input, len) {
  let h = 0x811c9dc5;
  for (let i = 0; i < input.length; i++) {
    h ^= input.charCodeAt(i);
    h = (h * 0x01000193) >>> 0;
    h ^= (i * 0x5bd1e995) >>> 0;
  }
  let result = '';
  const seed = [h, h ^ 0xdeadbeef, h ^ 0xcafebabe, h ^ 0x12345678];
  for (let j = 0; j < len; j++) {
    const s = seed[j % 4];
    const v = ((s * (j + 1) * 0x9e3779b9) >>> 0) ^ (s >> 4);
    seed[j % 4] = v;
    result += ((v >> ((j % 4) * 4)) & 0xf).toString(16);
  }
  return result;
}

function computeAllHashes(input) {
  hashData.md5    = simHash(input, 32);
  hashData.sha1   = simHash(input + '1', 40);
  hashData.sha256 = simHash(input + '256', 64);
  hashData.sha512 = simHash(input + '512', 128);

  document.getElementById('md5-val').textContent = hashData.md5;
  document.getElementById('sha1-val').textContent = hashData.sha1;
  document.getElementById('sha256-val').textContent = hashData.sha256;
  document.getElementById('sha512-val').textContent = hashData.sha512;
  document.getElementById('hashResults').style.display = 'block';

  document.getElementById('computedHash').value = hashData.sha256;
}

function hashText() {
  const text = document.getElementById('hashText').value;
  if (!text) { document.getElementById('hashResults').style.display = 'none'; return; }
  computeAllHashes(text);
  document.getElementById('fileMetaInfo').style.display = 'none';
}

function processHashFile(event) {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(e) {
    const content = e.target.result;
    computeAllHashes(content);

    const meta = document.getElementById('fileMetaInfo');
    meta.style.display = 'block';
    document.getElementById('fileMetaContent').innerHTML = [
      `Name: ${file.name}`,
      `Size: ${formatB(file.size)}`,
      `Type: ${file.type || 'Unknown'}`,
      `Last Modified: ${new Date(file.lastModified).toLocaleString()}`,
    ].join('\n');
  };
  reader.readAsBinaryString(file);
}

function formatB(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
  if (b < 1073741824) return (b/1048576).toFixed(1) + ' MB';
  return (b/1073741824).toFixed(2) + ' GB';
}

// Drag & drop for hash
const hDrop = document.getElementById('hashDropZone');
hDrop.addEventListener('dragover', e => { e.preventDefault(); hDrop.classList.add('drag-over'); });
hDrop.addEventListener('dragleave', () => hDrop.classList.remove('drag-over'));
hDrop.addEventListener('drop', e => {
  e.preventDefault();
  hDrop.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = ev => {
    computeAllHashes(ev.target.result);
    document.getElementById('fileMetaInfo').style.display = 'block';
    document.getElementById('fileMetaContent').innerHTML = `Name: ${file.name}\nSize: ${formatB(file.size)}\nType: ${file.type || 'Unknown'}\nLast Modified: ${new Date(file.lastModified).toLocaleString()}`;
  };
  reader.readAsBinaryString(file);
});

function copyHash(algo) {
  const val = hashData[algo] || document.getElementById(algo + '-val')?.textContent;
  if (!val) return;
  navigator.clipboard.writeText(val).then(() => {
    window.ForenShield?.toast('Copied', algo.toUpperCase() + ' hash copied to clipboard.', 'success');
  });
}

function verifyHash() {
  const known = document.getElementById('knownHash').value.trim().toLowerCase();
  const computed = document.getElementById('computedHash').value.trim().toLowerCase();
  const result = document.getElementById('verifyResult');

  if (!known || !computed) {
    result.style.display = 'block';
    result.innerHTML = `<div style="padding:.875rem;background:rgba(245,158,11,.06);border:1px solid rgba(245,158,11,.2);border-radius:8px;font-size:.82rem;color:var(--orange);">⚠️ Please provide both hashes to compare.</div>`;
    return;
  }

  const match = known === computed;
  const algo = detectAlgo(known);

  result.style.display = 'block';
  result.innerHTML = match
    ? `<div style="padding:1rem;background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.25);border-radius:8px;">
         <div style="font-size:1rem;font-weight:800;color:var(--green);margin-bottom:.35rem;">✅ INTEGRITY VERIFIED</div>
         <div style="font-size:.8rem;color:var(--text-secondary);">Hashes match — file has <strong>not been tampered with</strong>. Evidential integrity confirmed.</div>
         <div style="font-size:.72rem;color:var(--text-muted);margin-top:.5rem;font-family:var(--font-mono);">Algorithm: ${algo} • Verified: ${new Date().toLocaleString()}</div>
       </div>`
    : `<div style="padding:1rem;background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.25);border-radius:8px;">
         <div style="font-size:1rem;font-weight:800;color:#f87171;margin-bottom:.35rem;">❌ INTEGRITY MISMATCH</div>
         <div style="font-size:.8rem;color:var(--text-secondary);">Hashes do <strong>NOT match</strong> — file may have been modified, corrupted, or tampered with.</div>
         <div style="font-size:.72rem;color:var(--text-muted);margin-top:.5rem;font-family:var(--font-mono);">Algorithm: ${algo}</div>
       </div>`;
}

function detectAlgo(hash) {
  const len = hash.replace(/[^0-9a-f]/gi, '').length;
  if (len === 32) return 'MD5';
  if (len === 40) return 'SHA-1';
  if (len === 64) return 'SHA-256';
  if (len === 128) return 'SHA-512';
  return 'Unknown';
}
