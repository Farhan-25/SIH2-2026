/* ForenShield — Settings Logic */

const SETTINGS_SECTIONS = [
  { id: 'general',    label: '⚙️ General',       icon: '⚙️' },
  { id: 'erasure',    label: '🗑️ Erasure',        icon: '🗑️' },
  { id: 'recovery',   label: '🔍 Recovery',       icon: '🔍' },
  { id: 'compliance', label: '📋 Compliance',     icon: '📋' },
  { id: 'audit',      label: '📊 Audit & Logging',icon: '📊' },
  { id: 'security',   label: '🔐 Security',       icon: '🔐' },
  { id: 'network',    label: '🌐 Network',        icon: '🌐' },
  { id: 'advanced',   label: '🧪 Advanced',       icon: '🧪' },
];

let activeSection = 'general';

// Load saved settings
const defaults = {
  theme: 'dark',
  lang: 'en',
  notifications: true,
  autosave: true,
  defaultAlgo: 'dod',
  passes: '7',
  verify: true,
  badSectors: true,
  smart: true,
  autoReport: true,
  carvingMethod: 'ai',
  confThreshold: '70',
  chainCustody: true,
  fragmented: true,
  outputDir: '/forensics/recovered/',
  maxFileSize: '2048',
  complianceProfile: 'nist',
  gdpr: true,
  hipaa: false,
  pci: true,
  auditLevel: 'full',
  auditRetention: '365',
  digitalSig: true,
  tamperDetect: true,
  sessionTimeout: '30',
  requireConfirm: true,
  encryptLogs: true,
  logHash: 'sha256',
  remoteBackup: false,
  backupUrl: '',
  apiKey: '',
  parallelOps: '4',
  bufferSize: '64',
  useHardwareCmd: true,
  debugMode: false,
};

const settings = Object.assign({}, defaults, JSON.parse(localStorage.getItem('foren-settings') || '{}'));

const SECTION_CONTENT = {
  general: `
    <div class="panel" style="margin-bottom:1.5rem;">
      <div class="panel-title" style="margin-bottom:1.25rem;">⚙️ General Preferences</div>
      <div class="form-group">
        <label class="form-label">Application Theme</label>
        <select class="form-control" id="s-theme">
          <option value="dark" ${settings.theme==='dark'?'selected':''}>Dark (Default)</option>
          <option value="light" ${settings.theme==='light'?'selected':''}>Light</option>
          <option value="system" ${settings.theme==='system'?'selected':''}>System Default</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Language / Locale</label>
        <select class="form-control" id="s-lang">
          <option value="en" ${settings.lang==='en'?'selected':''}>English (US)</option>
          <option value="en-gb" ${settings.lang==='en-gb'?'selected':''}>English (UK)</option>
          <option value="hi">हिन्दी (Hindi)</option>
          <option value="de">Deutsch</option>
          <option value="fr">Français</option>
        </select>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Desktop Notifications</div><div class="toggle-desc">Show OS notifications on completion</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-notifications" ${settings.notifications?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Auto-Save Session</div><div class="toggle-desc">Preserve operation state on restart</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-autosave" ${settings.autosave?'checked':''}><span class="toggle-slider"></span></label>
      </div>
    </div>`,

  erasure: `
    <div class="panel" style="margin-bottom:1.5rem;">
      <div class="panel-title" style="margin-bottom:1.25rem;">🗑️ Erasure Defaults</div>
      <div class="form-group">
        <label class="form-label">Default Erasure Algorithm</label>
        <select class="form-control" id="s-defaultAlgo">
          <option value="dod" ${settings.defaultAlgo==='dod'?'selected':''}>DoD 5220.22-M (7-pass) — Military</option>
          <option value="nist" ${settings.defaultAlgo==='nist'?'selected':''}>NIST 800-88 (1–3 pass) — Standard</option>
          <option value="gutmann" ${settings.defaultAlgo==='gutmann'?'selected':''}>Gutmann Method (35-pass) — Extreme</option>
          <option value="zero" ${settings.defaultAlgo==='zero'?'selected':''}>Zero Fill (1-pass) — Basic</option>
          <option value="prng" ${settings.defaultAlgo==='prng'?'selected':''}>PRNG Overwrite (3-pass) — High</option>
          <option value="crypto" ${settings.defaultAlgo==='crypto'?'selected':''}>AES-256 Crypto Erase — SSD</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Custom Pass Count (for PRNG/Zero)</label>
        <input type="number" class="form-control" id="s-passes" value="${settings.passes}" min="1" max="35" style="font-family:var(--font-mono);"/>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Post-Erase Verification</div><div class="toggle-desc">Read-back verify after each pass</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-verify" ${settings.verify?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Bad Sector Mapping</div><div class="toggle-desc">Auto-detect and handle bad sectors</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-badSectors" ${settings.badSectors?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Collect SMART Data</div><div class="toggle-desc">Log drive health before/after erase</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-smart" ${settings.smart?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Auto-Generate Report</div><div class="toggle-desc">Create erasure certificate after completion</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-autoReport" ${settings.autoReport?'checked':''}><span class="toggle-slider"></span></label>
      </div>
    </div>`,

  recovery: `
    <div class="panel" style="margin-bottom:1.5rem;">
      <div class="panel-title" style="margin-bottom:1.25rem;">🔍 Recovery Defaults</div>
      <div class="form-group">
        <label class="form-label">Default Carving Method</label>
        <select class="form-control" id="s-carvingMethod">
          <option value="ai" ${settings.carvingMethod==='ai'?'selected':''}>AI-Assisted Hybrid (Recommended)</option>
          <option value="signature" ${settings.carvingMethod==='signature'?'selected':''}>Signature-Based</option>
          <option value="structure" ${settings.carvingMethod==='structure'?'selected':''}>Structure-Based</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Minimum Confidence Threshold (%)</label>
        <input type="number" class="form-control" id="s-confThreshold" value="${settings.confThreshold}" min="0" max="100" style="font-family:var(--font-mono);"/>
      </div>
      <div class="form-group">
        <label class="form-label">Default Output Directory</label>
        <input type="text" class="form-control" id="s-outputDir" value="${settings.outputDir}" placeholder="/forensics/recovered/" style="font-family:var(--font-mono);font-size:.82rem;"/>
      </div>
      <div class="form-group">
        <label class="form-label">Max File Size to Recover (MB)</label>
        <input type="number" class="form-control" id="s-maxFileSize" value="${settings.maxFileSize}" min="1" style="font-family:var(--font-mono);"/>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Chain of Custody Logging</div><div class="toggle-desc">Maintain forensic integrity evidence</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-chainCustody" ${settings.chainCustody?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Fragmented File Reconstruction</div><div class="toggle-desc">Attempt to reassemble split files</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-fragmented" ${settings.fragmented?'checked':''}><span class="toggle-slider"></span></label>
      </div>
    </div>`,

  compliance: `
    <div class="panel" style="margin-bottom:1.5rem;">
      <div class="panel-title" style="margin-bottom:1.25rem;">📋 Compliance Profile</div>
      <div class="form-group">
        <label class="form-label">Active Compliance Profile</label>
        <select class="form-control" id="s-complianceProfile">
          <option value="nist" ${settings.complianceProfile==='nist'?'selected':''}>NIST SP 800-88 (Default)</option>
          <option value="dod" ${settings.complianceProfile==='dod'?'selected':''}>DoD 5220.22-M</option>
          <option value="iso" ${settings.complianceProfile==='iso'?'selected':''}>ISO/IEC 27001:2022</option>
          <option value="custom" ${settings.complianceProfile==='custom'?'selected':''}>Custom Profile</option>
        </select>
      </div>
      <div style="font-size:.78rem;font-weight:700;color:var(--text-secondary);margin-bottom:.875rem;margin-top:1.25rem;">Regulatory Requirements</div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">GDPR Compliance Mode</div><div class="toggle-desc">EU General Data Protection Regulation Art. 17</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-gdpr" ${settings.gdpr?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">HIPAA Compliance Mode</div><div class="toggle-desc">US Health Insurance Portability Act</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-hipaa" ${settings.hipaa?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">PCI-DSS v4.0 Mode</div><div class="toggle-desc">Payment Card Industry Data Security</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-pci" ${settings.pci?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="info-box" style="margin-top:1rem;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <div><div class="info-title">DPDP Act 2023 (India)</div><div class="info-text">ForenShield is compliant with India's Digital Personal Data Protection Act. All erasure operations meet the data disposal requirements under Section 8(7).</div></div>
      </div>
    </div>`,

  audit: `
    <div class="panel" style="margin-bottom:1.5rem;">
      <div class="panel-title" style="margin-bottom:1.25rem;">📊 Audit & Logging</div>
      <div class="form-group">
        <label class="form-label">Audit Log Level</label>
        <select class="form-control" id="s-auditLevel">
          <option value="minimal" ${settings.auditLevel==='minimal'?'selected':''}>Minimal (Errors only)</option>
          <option value="standard" ${settings.auditLevel==='standard'?'selected':''}>Standard (Errors + Info)</option>
          <option value="full" ${settings.auditLevel==='full'?'selected':''}>Full (All operations) — Recommended</option>
          <option value="debug" ${settings.auditLevel==='debug'?'selected':''}>Debug (Verbose)</option>
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Log Retention Period (days)</label>
        <input type="number" class="form-control" id="s-auditRetention" value="${settings.auditRetention}" min="30" max="3650" style="font-family:var(--font-mono);"/>
      </div>
      <div class="form-group">
        <label class="form-label">Hash Algorithm for Log Signing</label>
        <select class="form-control" id="s-logHash">
          <option value="sha256" ${settings.logHash==='sha256'?'selected':''}>SHA-256 (Recommended)</option>
          <option value="sha512" ${settings.logHash==='sha512'?'selected':''}>SHA-512 (Strongest)</option>
          <option value="sha1" ${settings.logHash==='sha1'?'selected':''}>SHA-1 (Legacy)</option>
        </select>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Digital Signature on Reports</div><div class="toggle-desc">RSA-4096 sign all generated reports</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-digitalSig" ${settings.digitalSig?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Tamper Detection</div><div class="toggle-desc">Alert if audit log is modified externally</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-tamperDetect" ${settings.tamperDetect?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Encrypt Log Files</div><div class="toggle-desc">AES-256 encrypt stored audit logs</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-encryptLogs" ${settings.encryptLogs?'checked':''}><span class="toggle-slider"></span></label>
      </div>
    </div>`,

  security: `
    <div class="panel" style="margin-bottom:1.5rem;">
      <div class="panel-title" style="margin-bottom:1.25rem;">🔐 Security Settings</div>
      <div class="form-group">
        <label class="form-label">Session Timeout (minutes)</label>
        <input type="number" class="form-control" id="s-sessionTimeout" value="${settings.sessionTimeout}" min="5" max="480" style="font-family:var(--font-mono);"/>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Require Confirmation for Destructive Ops</div><div class="toggle-desc">Type ERASE/CONFIRM to proceed</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-requireConfirm" ${settings.requireConfirm?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Hardware Security Commands</div><div class="toggle-desc">Use ATA/NVMe/SCSI hardware erase commands</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-useHardwareCmd" ${settings.useHardwareCmd?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="warning-box" style="margin-top:1rem;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        <div class="warning-content">
          <div class="warning-title">Security Hardening</div>
          <div class="warning-text">In production, enable full-disk encryption for the ForenShield working directory and use a dedicated forensic workstation with secure boot enabled.</div>
        </div>
      </div>
    </div>`,

  network: `
    <div class="panel" style="margin-bottom:1.5rem;">
      <div class="panel-title" style="margin-bottom:1.25rem;">🌐 Network & Remote</div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Remote Backup of Reports</div><div class="toggle-desc">Automatically backup reports to a server</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-remoteBackup" ${settings.remoteBackup?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div class="form-group" style="margin-top:.75rem;">
        <label class="form-label">Backup Server URL</label>
        <input type="url" class="form-control" id="s-backupUrl" value="${settings.backupUrl}" placeholder="https://forensics-server.example.com/api/backup" style="font-family:var(--font-mono);font-size:.8rem;"/>
      </div>
      <div class="form-group">
        <label class="form-label">API Key</label>
        <input type="password" class="form-control" id="s-apiKey" value="${settings.apiKey}" placeholder="••••••••••••••••" style="font-family:var(--font-mono);"/>
      </div>
      <div class="info-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        <div><div class="info-title">Offline Mode</div><div class="info-text">ForenShield operates fully offline by default. Network features are optional and disabled by default for maximum security.</div></div>
      </div>
    </div>`,

  advanced: `
    <div class="panel" style="margin-bottom:1.5rem;">
      <div class="panel-title" style="margin-bottom:1.25rem;">🧪 Advanced Configuration</div>
      <div class="form-group">
        <label class="form-label">Parallel Operations</label>
        <input type="number" class="form-control" id="s-parallelOps" value="${settings.parallelOps}" min="1" max="16" style="font-family:var(--font-mono);"/>
      </div>
      <div class="form-group">
        <label class="form-label">I/O Buffer Size (MB)</label>
        <input type="number" class="form-control" id="s-bufferSize" value="${settings.bufferSize}" min="4" max="512" style="font-family:var(--font-mono);"/>
      </div>
      <div class="toggle-group">
        <div class="toggle-info"><div class="toggle-label">Debug Mode</div><div class="toggle-desc">Enable verbose logging for troubleshooting</div></div>
        <label class="toggle-switch"><input type="checkbox" id="s-debugMode" ${settings.debugMode?'checked':''}><span class="toggle-slider"></span></label>
      </div>
      <div style="margin-top:1.5rem;padding-top:1.5rem;border-top:1px solid var(--border);">
        <div style="font-size:.82rem;font-weight:700;color:var(--text-secondary);margin-bottom:.875rem;">Reset</div>
        <div style="display:flex;gap:.75rem;flex-wrap:wrap;">
          <button class="btn-outline" onclick="resetSettings()" style="font-size:.82rem;">Reset to Defaults</button>
          <button class="btn-outline" onclick="clearData()" style="font-size:.82rem;color:var(--red);border-color:rgba(239,68,68,.3);">Clear All Data</button>
          <button class="btn-outline" onclick="exportSettings()" style="font-size:.82rem;">Export Config</button>
        </div>
      </div>
    </div>`,
};

function buildSidebar() {
  const sb = document.getElementById('settingsSidebar');
  sb.innerHTML = SETTINGS_SECTIONS.map(s => `
    <button onclick="switchSection('${s.id}')" id="sb-${s.id}"
      style="display:flex;align-items:center;gap:.6rem;padding:.625rem .875rem;border-radius:6px;font-size:.82rem;font-weight:500;width:100%;text-align:left;background:${s.id===activeSection?'rgba(99,102,241,.12)':'none'};color:${s.id===activeSection?'var(--purple-light)':'var(--text-secondary)'};border:none;cursor:pointer;transition:all .15s;"
      onmouseover="this.style.background='rgba(99,102,241,.08)';this.style.color='var(--text-primary)'"
      onmouseout="this.style.background='${s.id===activeSection?'rgba(99,102,241,.12)':'none'}';this.style.color='${s.id===activeSection?'var(--purple-light)':'var(--text-secondary)'}'">
      ${s.label}
    </button>
  `).join('');
}

function switchSection(id) {
  activeSection = id;
  buildSidebar();
  document.getElementById('settingsContent').innerHTML = SECTION_CONTENT[id] || '';
}

function saveSettings() {
  const saved = {};
  const fields = ['theme','lang','defaultAlgo','passes','complianceProfile','auditLevel','auditRetention','logHash','sessionTimeout','outputDir','maxFileSize','backupUrl','apiKey','parallelOps','bufferSize','carvingMethod','confThreshold'];
  fields.forEach(f => {
    const el = document.getElementById('s-' + f);
    if (el) saved[f] = el.value;
  });
  const toggles = ['notifications','autosave','verify','badSectors','smart','autoReport','chainCustody','fragmented','gdpr','hipaa','pci','digitalSig','tamperDetect','encryptLogs','requireConfirm','useHardwareCmd','remoteBackup','debugMode'];
  toggles.forEach(f => {
    const el = document.getElementById('s-' + f);
    if (el) saved[f] = el.checked;
  });

  Object.assign(settings, saved);
  localStorage.setItem('foren-settings', JSON.stringify(settings));

  // Apply theme
  if (saved.theme === 'light') document.body.classList.add('light');
  else document.body.classList.remove('light');
  localStorage.setItem('foren-theme', saved.theme === 'light' ? 'light' : 'dark');

  window.ForenShield?.toast('Settings Saved', 'All preferences have been updated.', 'success');
}

function resetSettings() {
  if (!confirm('Reset all settings to factory defaults?')) return;
  localStorage.removeItem('foren-settings');
  Object.assign(settings, defaults);
  switchSection(activeSection);
  window.ForenShield?.toast('Settings Reset', 'All preferences restored to defaults.', 'info');
}

function clearData() {
  if (!confirm('Clear ALL ForenShield data? This cannot be undone.')) return;
  localStorage.clear();
  window.ForenShield?.toast('Data Cleared', 'All stored data has been removed.', 'warn');
}

function exportSettings() {
  const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `ForenShield_config_${new Date().toISOString().slice(0,10)}.json`;
  a.click();
  URL.revokeObjectURL(url);
  window.ForenShield?.toast('Config Exported', 'Settings file downloaded.', 'success');
}

// Init
buildSidebar();
switchSection('general');
