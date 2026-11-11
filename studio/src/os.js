// Anowar OS: the small operating system inside the monitor. Plain DOM, so text stays sharp at full resolution.
import { APPS } from './apps.js';

export const WALLPAPERS = {
  fern: { name: 'Fern', file: 'baked/wall_fern.jpg' },
  dusk: { name: 'Dusk lake', file: 'baked/wall_dusk.jpg' },
  ember: { name: 'Ember', file: 'baked/wall_ember.jpg' },
  paper: { name: 'Paper', file: 'baked/wall_paper.jpg' },
};

const I = d => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;
export const ICONS = {
  about: I('<circle cx="12" cy="8" r="3.4"/><path d="M5 20c.8-3.6 3.4-5.4 7-5.4s6.200 1.800 7 5.400"/>'),
  work: I('<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3 15l4.500-4.500 4 4 3-3 6.500 6.500"/>'),
  services: I('<path d="M12 3l8 4.500-8 4.500-8-4.500z"/><path d="M4 12l8 4.500 8-4.500M4 16.500L12 21l8-4.500"/>'),
  pricing: I('<path d="M4 12.500V5h7.500L20 13.500 13.500 20z"/><circle cx="8.500" cy="9.500" r="1.300"/>'),
  process: I('<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M6 16V11a3 3 0 013-3h7"/>'),
  reviews: I('<path d="M12 4l2.400 5 5.600.700-4.100 3.800 1.100 5.500-5-2.800-5 2.800 1.100-5.500L4 9.700 9.600 9z"/>'),
  faq: I('<circle cx="12" cy="12" r="9"/><path d="M9.500 9.500a2.500 2.500 0 114 2c-.9.600-1.500 1.100-1.500 2.200"/><path d="M12 17.200v.100"/>'),
  contact: I('<rect x="3" y="5.500" width="18" height="13" rx="2.500"/><path d="M4 7.500l8 6 8-6"/>'),
  terminal: I('<rect x="3" y="4.500" width="18" height="15" rx="2.500"/><path d="M7 10l3 2.500L7 15M12.500 15H17"/>'),
  paint: I('<path d="M14.500 4.500l5 5L9 20H4v-5z"/><path d="M12.500 6.500l5 5"/>'),
  beats: I('<rect x="4" y="4" width="6.500" height="6.500" rx="1.500"/><rect x="13.500" y="4" width="6.500" height="6.500" rx="1.500"/><rect x="4" y="13.500" width="6.500" height="6.500" rx="1.500"/><rect x="13.500" y="13.500" width="6.500" height="6.500" rx="1.500"/>'),
  game: I('<rect x="3" y="8" width="18" height="10" rx="5"/><path d="M8 11.500v3M6.500 13h3M15.500 12.200v.100M17.500 14v.100"/>'),
  settings: I('<circle cx="12" cy="12" r="3"/><path d="M12 3v2.500M12 18.500V21M3 12h2.500M18.500 12H21M5.600 5.600l1.800 1.800M16.600 16.600l1.800 1.800M5.600 18.400l1.800-1.800M16.600 7.400l1.800-1.800"/>'),
  sound: I('<path d="M4 10v4h3.500L12 18V6L7.500 10z"/><path d="M15.500 9.500a3.500 3.500 0 010 5M18 7a7 7 0 010 10"/>'),
  mute: I('<path d="M4 10v4h3.500L12 18V6L7.500 10z"/><path d="M16 10l4 4M20 10l-4 4"/>'),
  exit: I('<path d="M10 5H6a2 2 0 00-2 2v10a2 2 0 002 2h4M15 8l4 4-4 4M19 12H9"/>'),
};

// ───────────────────────── sound (WebAudio, silent until enabled) ─────────────────────────
export const audio = {
  ctx: null, enabled: false, listeners: new Set(),
  enable() { if (!this.ctx) { this.ctx = new (window.AudioContext || window.webkitAudioContext)(); this.out = this.ctx.createGain(); this.out.gain.value = 0.5; this.out.connect(this.ctx.destination); }
    this.ctx.resume(); this.enabled = true; this.listeners.forEach(f => f(true)); this.blip(660, 0.05); },
  disable() { this.enabled = false; this.listeners.forEach(f => f(false)); },
  toggle() { this.enabled ? this.disable() : this.enable(); },
  blip(freq = 520, dur = 0.04, type = 'sine', vol = 0.12) {
    if (!this.enabled) return; const c = this.ctx, o = c.createOscillator(), g = c.createGain();
    o.type = type; o.frequency.value = freq; g.gain.setValueAtTime(vol, c.currentTime); g.gain.exponentialRampToValueAtTime(0.0001, c.currentTime + dur);
    o.connect(g).connect(this.out); o.start(); o.stop(c.currentTime + dur + 0.01); },
};

export function createOS({ root, data, asset, onExit, onWallpaper }) {
  let open = false, z = 10, wall = localStorage.getItem('st-wall') || 'fern';
  const wins = new Map();
  root.innerHTML = `
    <div class="os-boot"><div class="os-boot-in"><b>Anowar OS</b><i><s></s></i><span class="os-mono">starting up</span></div></div>
    <div class="os-desk">
      <header class="os-bar">
        <b class="os-brand">Anowar OS</b><span class="os-app os-mono"></span><span class="os-sp"></span>
        <button class="os-snd" type="button">${ICONS.mute}<span>Enable sound</span></button>
        <span class="os-clock os-mono"></span>
        <button class="os-exit" type="button">${ICONS.exit}<span>Back to the studio</span></button>
      </header>
      <div class="os-icons"></div>
      <div class="os-wins"></div>
      <nav class="os-dock" aria-label="Programs"></nav>
    </div>`;
  const desk = root.querySelector('.os-desk'), winsEl = root.querySelector('.os-wins'), dock = root.querySelector('.os-dock'), icons = root.querySelector('.os-icons');
  const appName = root.querySelector('.os-app'), clock = root.querySelector('.os-clock'), snd = root.querySelector('.os-snd');
  const setWall = k => { if (!WALLPAPERS[k]) return; wall = k; localStorage.setItem('st-wall', k); desk.style.backgroundImage = `url(${asset(WALLPAPERS[k].file)})`; root.dataset.wall = k; onWallpaper && onWallpaper(k); };
  setWall(wall);
  setInterval(() => { clock.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); }, 1000);
  clock.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  snd.onclick = () => audio.toggle();
  audio.listeners.add(on => { snd.innerHTML = `${on ? ICONS.sound : ICONS.mute}<span>${on ? 'Sound on' : 'Enable sound'}</span>`; snd.classList.toggle('on', on); });
  root.querySelector('.os-exit').onclick = () => api.close();

  const api = {
    data, asset, audio, wallpapers: WALLPAPERS, get wall() { return wall; }, setWall,
    isOpen: () => open,
    open({ instant, app } = {}) {
      open = true; root.hidden = false; root.classList.add('on'); document.documentElement.classList.add('st-os-open');
      const seen = sessionStorage.getItem('st-booted');
      root.classList.toggle('booting', !instant && !seen);
      const first = () => { root.classList.remove('booting'); if (!wins.size) { api.launch(app || 'about'); if (!app) api.launch('work', { x: 0.46, y: 0.16 }); } else if (app) api.launch(app); };
      if (instant || seen) first(); else { sessionStorage.setItem('st-booted', '1'); setTimeout(first, 1500); }
    },
    close() { open = false; root.classList.remove('on'); setTimeout(() => { if (!open) root.hidden = true; }, 420); onExit && onExit(); },
    launch(id, pos) {
      const def = APPS[id]; if (!def) return null;
      if (wins.has(id)) { const w = wins.get(id); focus(w); w.el.classList.remove('min'); return w; }
      const el = document.createElement('section'); el.className = 'os-win'; el.dataset.app = id; el.setAttribute('aria-label', def.title);
      const W = winsEl.clientWidth || innerWidth, H = winsEl.clientHeight || innerHeight - 110;
      const w = Math.min(def.w || 620, W - 16), h = Math.min(def.h || 460, H - 12), n = wins.size;
      const x = pos ? pos.x * W : Math.max(8, (W - w) / 2 - 90 + n * 34), y = pos ? pos.y * H : Math.max(6, (H - h) / 2 - 40 + n * 26);
      Object.assign(el.style, { width: w + 'px', height: h + 'px', left: clamp(x, 4, Math.max(4, W - w - 4)) + 'px', top: clamp(y, 4, Math.max(4, H - h - 4)) + 'px' });
      el.innerHTML = `<header class="os-tb"><button class="os-x" aria-label="Close ${def.title}"></button><button class="os-m" aria-label="Maximize ${def.title}"></button><span class="os-ti">${ICONS[id] || ''}<b>${def.title}</b></span></header><div class="os-body"></div><i class="os-rs" aria-hidden="true"></i>`;
      winsEl.appendChild(el);
      const win = { id, el, body: el.querySelector('.os-body'), cleanup: null };
      wins.set(id, win); win.cleanup = def.mount(win.body, api, win) || null;
      el.querySelector('.os-x').onclick = () => api.kill(id);
      el.querySelector('.os-m').onclick = () => { el.classList.toggle('max'); win.onResize && win.onResize(); };
      el.addEventListener('pointerdown', () => focus(win), true);
      drag(el.querySelector('.os-tb'), el, win); resize(el.querySelector('.os-rs'), el, win);
      focus(win); syncDock(); audio.blip(740, 0.05);
      requestAnimationFrame(() => el.classList.add('in'));
      return win;
    },
    kill(id) { const w = wins.get(id); if (!w) return; w.cleanup && w.cleanup(); w.el.classList.remove('in'); setTimeout(() => w.el.remove(), 160); wins.delete(id); syncDock(); audio.blip(380, 0.05);
      const top = [...wins.values()].sort((a, b) => b.el.style.zIndex - a.el.style.zIndex)[0]; appName.textContent = top ? APPS[top.id].title : ''; },
    list: () => Object.keys(APPS),
  };
  function focus(win) { win.el.style.zIndex = ++z; winsEl.querySelectorAll('.os-win.top').forEach(e => e.classList.remove('top')); win.el.classList.add('top'); appName.textContent = APPS[win.id].title; }
  function syncDock() { dock.querySelectorAll('button').forEach(b => b.classList.toggle('run', wins.has(b.dataset.app))); }
  function drag(handle, el, win) {
    handle.addEventListener('pointerdown', ev => {
      if (ev.target.closest('button') || el.classList.contains('max')) return;
      const sx = ev.clientX, sy = ev.clientY, ox = el.offsetLeft, oy = el.offsetTop; handle.setPointerCapture(ev.pointerId);
      const mv = e => { el.style.left = clamp(ox + e.clientX - sx, -el.offsetWidth + 80, winsEl.clientWidth - 80) + 'px'; el.style.top = clamp(oy + e.clientY - sy, 0, winsEl.clientHeight - 40) + 'px'; };
      const up = () => { handle.removeEventListener('pointermove', mv); handle.removeEventListener('pointerup', up); };
      handle.addEventListener('pointermove', mv); handle.addEventListener('pointerup', up);
    });
    handle.addEventListener('dblclick', ev => { if (!ev.target.closest('button')) { el.classList.toggle('max'); win.onResize && win.onResize(); } });
  }
  function resize(handle, el, win) {
    handle.addEventListener('pointerdown', ev => {
      ev.preventDefault(); const sx = ev.clientX, sy = ev.clientY, ow = el.offsetWidth, oh = el.offsetHeight; handle.setPointerCapture(ev.pointerId);
      const mv = e => { el.style.width = Math.max(300, ow + e.clientX - sx) + 'px'; el.style.height = Math.max(220, oh + e.clientY - sy) + 'px'; win.onResize && win.onResize(); };
      const up = () => { handle.removeEventListener('pointermove', mv); handle.removeEventListener('pointerup', up); };
      handle.addEventListener('pointermove', mv); handle.addEventListener('pointerup', up);
    });
  }
  // dock and desktop icons
  const groups = [['about', 'work', 'services', 'pricing', 'process', 'reviews', 'faq', 'contact'], ['terminal', 'paint', 'beats', 'game', 'settings']];
  dock.innerHTML = groups.map(g => g.map(id => `<button type="button" data-app="${id}" aria-label="${APPS[id].title}">${ICONS[id]}<span>${APPS[id].title}</span></button>`).join('')).join('<hr>');
  dock.addEventListener('click', ev => { const b = ev.target.closest('button'); if (b) api.launch(b.dataset.app); });
  icons.innerHTML = ['work', 'terminal', 'paint', 'beats', 'game'].map(id => `<button type="button" data-app="${id}">${ICONS[id]}<span>${APPS[id].title}</span></button>`).join('');
  icons.addEventListener('dblclick', ev => { const b = ev.target.closest('button'); if (b) api.launch(b.dataset.app); });
  icons.addEventListener('click', ev => { const b = ev.target.closest('button'); if (b && matchMedia('(pointer: coarse)').matches) api.launch(b.dataset.app); });
  icons.addEventListener('keydown', ev => { if (ev.key === 'Enter') { const b = ev.target.closest('button'); if (b) api.launch(b.dataset.app); } });
  return api;
}
export const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
