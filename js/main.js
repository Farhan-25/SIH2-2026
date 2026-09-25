/* ForenShield — main.js (Dashboard & Global Logic) */

// ============ Utilities Dropdown ============
function toggleToolsMenu() {
  const dd = document.getElementById('tools-dropdown');
  if (dd) dd.style.display = dd.style.display === 'none' ? 'block' : 'none';
}

document.addEventListener('click', (e) => {
  const menu = document.getElementById('tools-menu');
  const dd = document.getElementById('tools-dropdown');
  if (dd && menu && !menu.contains(e.target)) dd.style.display = 'none';
});

// ============ Theme Toggle ============
const themeBtn = document.getElementById('themeToggle');
const savedTheme = localStorage.getItem('foren-theme') || 'dark';
if (savedTheme === 'light') document.body.classList.add('light');

if (themeBtn) {
  themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('light');
    localStorage.setItem('foren-theme', document.body.classList.contains('light') ? 'light' : 'dark');
  });
}

// ============ Stat Counter Animation ============
function animateCounter(el, target, duration = 1500, isFloat = false) {
  const start = 0;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = 1 - Math.pow(1 - progress, 3);
    const value = start + (target - start) * ease;

    if (isFloat) {
      el.textContent = value.toFixed(1);
    } else {
      el.textContent = Math.floor(value);
    }

    if (progress < 1) requestAnimationFrame(update);
  }

  requestAnimationFrame(update);
}

// Observe stat values on scroll
const statEls = document.querySelectorAll('.stat-value[data-target]');
if (statEls.length) {
  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting && !entry.target.dataset.animated) {
        const target = parseFloat(entry.target.dataset.target);
        const isFloat = entry.target.dataset.target.includes('.');
        animateCounter(entry.target, target, 1800, isFloat);
        entry.target.dataset.animated = 'true';
      }
    });
  }, { threshold: 0.5 });
  statEls.forEach(el => io.observe(el));
}

// ============ Session Stats ============
const sessionStats = JSON.parse(sessionStorage.getItem('foren-stats') || '{"ops":0,"erased":0,"recovered":0,"reports":0}');

function updateStatDisplays() {
  const opEl = document.getElementById('stat-ops');
  const eraseEl = document.getElementById('stat-erased');
  const recovEl = document.getElementById('stat-recovered');
  const repEl = document.getElementById('stat-reports');
  if (opEl) opEl.textContent = sessionStats.ops;
  if (eraseEl) eraseEl.textContent = sessionStats.erased + ' GB';
  if (recovEl) recovEl.textContent = sessionStats.recovered;
  if (repEl) repEl.textContent = sessionStats.reports;
}
updateStatDisplays();

// ============ Activity Feed ============
const ACTIVITIES = [
  { type: 'green', msg: '<strong>System initialized</strong> — ForenShield v2.0 ready', time: 'Just now' },
  { type: 'blue', msg: '<strong>Storage scan complete</strong> — 4 devices detected', time: '2s ago' },
  { type: 'orange', msg: '<strong>Hash database loaded</strong> — 47 signatures ready', time: '5s ago' },
  { type: 'green', msg: '<strong>Compliance modules</strong> verified — NIST 800-88 active', time: '8s ago' },
];

let activityData = [...ACTIVITIES];

const realTimeEvents = [
  { type: 'blue', msg: '<strong>Drive health check</strong> — All drives nominal' },
  { type: 'green', msg: '<strong>Signature database updated</strong> — 3 new signatures added' },
  { type: 'orange', msg: '<strong>Entropy scan</strong> — Baseline established' },
  { type: 'blue', msg: '<strong>Audit log</strong> — Session checkpoint saved' },
  { type: 'green', msg: '<strong>Verification engine</strong> — CRC checksums cached' },
];

let rtIdx = 0;

function renderActivityFeed() {
  const feed = document.getElementById('activityFeed');
  if (!feed) return;

  feed.innerHTML = activityData.slice(0, 8).map(a => `
    <div class="activity-item">
      <span class="activity-dot dot-${a.type}"></span>
      <div>
        <div class="activity-text">${a.msg}</div>
        <div class="activity-time">${a.time}</div>
      </div>
    </div>
  `).join('');
}

renderActivityFeed();

// Auto-add activity every few seconds
setInterval(() => {
  const evt = realTimeEvents[rtIdx % realTimeEvents.length];
  activityData.unshift({ ...evt, time: 'Just now' });
  activityData = activityData.map((a, i) => ({ ...a, time: i === 0 ? 'Just now' : formatRelTime(i) }));
  if (activityData.length > 12) activityData.pop();
  rtIdx++;
  renderActivityFeed();
}, 6000);

function formatRelTime(idx) {
  const seconds = idx * 6;
  if (seconds < 60) return `${seconds}s ago`;
  return `${Math.floor(seconds / 60)}m ago`;
}

// ============ Devices List ============
const MOCK_DEVICES = [
  { icon: '💾', name: 'Samsung SSD 860 EVO', detail: '/dev/sda • 500 GB • SATA III', health: 'Good', healthClass: 'health-good' },
  { icon: '🗄️', name: 'WD Blue HDD', detail: '/dev/sdb • 1 TB • 7200 RPM', health: 'Good', healthClass: 'health-good' },
  { icon: '🔌', name: 'Kingston USB 3.1', detail: '/dev/sdc • 64 GB • USB 3.1', health: 'Good', healthClass: 'health-good' },
  { icon: '💿', name: 'Generic SD Card', detail: '/dev/sdd • 32 GB • UHS-I', health: 'Warning', healthClass: 'health-warn' },
];

function renderDevices() {
  const list = document.getElementById('devicesList');
  if (!list) return;
  list.innerHTML = MOCK_DEVICES.map(d => `
    <div class="device-item">
      <div class="device-icon">${d.icon}</div>
      <div class="device-info">
        <div class="device-name">${d.name}</div>
        <div class="device-detail">${d.detail}</div>
      </div>
      <div class="device-health ${d.healthClass}">${d.health}</div>
    </div>
  `).join('');
}

renderDevices();

const refreshBtn = document.getElementById('refreshDevices');
if (refreshBtn) {
  refreshBtn.addEventListener('click', () => {
    refreshBtn.textContent = '↻ Scanning...';
    setTimeout(() => {
      renderDevices();
      refreshBtn.textContent = '↺ Refresh';
    }, 1500);
  });
}

// ============ Toast Utility (Global) ============
window.ForenShield = window.ForenShield || {};

window.ForenShield.toast = function(title, message, type = 'info') {
  let container = document.querySelector('.toast-container');
  if (!container) {
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', info: 'ℹ️', warn: '⚠️' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <div class="toast-icon">${icons[type] || icons.info}</div>
    <div class="toast-content">
      <div class="toast-title">${title}</div>
      <div class="toast-message">${message}</div>
    </div>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(20px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
};

// ============ Navbar Active State ============
(function() {
  const path = window.location.pathname;
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
    const href = link.getAttribute('href') || '';
    if (path.endsWith('index.html') || path === '/' || path === '') {
      if (link.id === 'nav-home') link.classList.add('active');
    } else if (href && path.includes(href.replace('../', '').replace('.html', ''))) {
      link.classList.add('active');
    }
  });
})();

// ============ Navbar Scroll Effect ============
window.addEventListener('scroll', () => {
  const nb = document.getElementById('navbar');
  if (nb) {
    if (window.scrollY > 20) {
      nb.style.background = document.body.classList.contains('light')
        ? 'rgba(248,250,252,0.95)'
        : 'rgba(10,11,15,0.95)';
    } else {
      nb.style.background = '';
    }
  }
}, { passive: true });

// ============ Smooth Section Animations ============
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.module-card, .dash-panel, .wf-step, .tech-card').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});
