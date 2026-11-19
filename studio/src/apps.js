// Programs for Anowar OS. Each one is { title, w, h, mount(body, os, win) -> cleanup? }.
const ext = href => href.startsWith('http') ? ' target="_blank" rel="noopener"' : '';
// the programs are English only, but page links keep the visitor on their language's pages
const LB = (l => l && l !== 'en' ? '/' + l : '')((document.documentElement.lang || '').toLowerCase());
const loc = h => (LB && h.startsWith('/')) ? LB + (h === '/' ? '' : h) : h;
const btn = (href, text, primary) => `<a class="os-btn${primary ? ' p' : ''}" href="${loc(href)}"${ext(href)}>${text}</a>`;
const txt = s => { const d = document.createElement('div'); d.innerHTML = s; return d.textContent; };

// ───────────────────────── content programs ─────────────────────────
const about = { title: 'About', w: 560, h: 500, mount(b, os) {
  const d = os.data;
  b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">about.txt</span>
    <h2>A person, <em>not a vendor.</em></h2>${d.about.map(p => `<p>${p}</p>`).join('')}
    <ul class="os-ticks">${d.facts.map(f => `<li>${f}</li>`).join('')}</ul>
    <div class="os-row">${btn(d.call, 'Book a call', 1)}${btn('/about', 'Full about page')}</div></div>`;
} };
const work = { title: 'Work', w: 760, h: 540, mount(b, os) {
  const d = os.data;
  b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">Selected work</span><h2>Real clients. <em>Shipped to production.</em></h2>
    <div class="os-grid">${d.cases.map(c => `<a class="os-case" href="${c.url}">${c.thumb ? `<img src="${c.thumb}" alt="${txt(c.name)} website" loading="lazy" width="900" height="600">` : '<i></i>'}<b>${c.name}</b><span class="os-mono">${c.tag}</span><p>${c.blurb}</p></a>`).join('')}</div>
    <span class="os-mono os-eb" style="margin-top:22px">Every site, shipped and live</span>
    <ul class="os-rows">${d.deploys.map(c => `<li><a href="https://${c.host}" target="_blank" rel="noopener"><b>${c.name}</b><span class="os-mono">${c.tag}</span></a></li>`).join('')}</ul>
    <div class="os-row">${btn('/work', 'Open the work page', 1)}</div></div>`;
} };
const services = { title: 'Services', w: 600, h: 520, mount(b, os) {
  const d = os.data;
  b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">The five</span><h2>Design and build, <em>under one roof.</em></h2>
    ${d.services.map(s => `<a class="os-svc" href="${s.url}"><span class="os-mono">${s.num}</span><div><b>${s.name}</b><p>${s.blurb}</p><ul class="os-chips">${s.chips.map(c => `<li>${c}</li>`).join('')}</ul></div><span class="os-mono os-price">${s.price}</span></a>`).join('')}
    <div class="os-row">${btn(d.call, 'Book the discovery call', 1)}${btn('/services', 'All services')}</div></div>`;
} };
const pricing = { title: 'Pricing', w: 540, h: 480, mount(b, os) {
  const d = os.data;
  b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">The bands</span><h2>Fixed quotes. <em>No hourly meters.</em></h2>
    <table class="os-table">${d.bands.map(x => `<tr><th>${x.name}<small>${x.sub}</small></th><td>${x.price}<small>${x.time}</small></td></tr>`).join('')}</table>
    <ul class="os-ticks">${d.checks.map(c => `<li>${c}</li>`).join('')}</ul>
    <div class="os-row">${btn(d.call, 'Get a fixed quote', 1)}${btn('/pricing', 'Full pricing')}</div></div>`;
} };
const process = { title: 'Process', w: 560, h: 520, mount(b, os) {
  const d = os.data;
  b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">The eight stages</span><h2>How a project <em>runs.</em></h2>
    <ol class="os-steps">${d.steps.map((s, i) => `<li><span class="os-mono">${String(i + 1).padStart(2, '0')}</span><div><b>${s.name}</b><p>${s.text}</p></div></li>`).join('')}</ol>
    <div class="os-row">${btn('/process', 'The full process', 1)}</div></div>`;
} };
const reviews = { title: 'Reviews', w: 560, h: 480, mount(b, os) {
  b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">Verbatim, from Upwork</span><h2>What clients <em>say.</em></h2>
    ${os.data.quotes.map(q => `<blockquote class="os-q">${q.text}<cite class="os-mono">${q.by}</cite></blockquote>`).join('')}</div>`;
} };
const faq = { title: 'Questions', w: 580, h: 500, mount(b, os) {
  b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">Straight answers</span><h2>Common <em>questions.</em></h2>
    ${os.data.faq.map(f => `<details class="os-faq"><summary>${f.q}</summary><p>${f.a}</p></details>`).join('')}</div>`;
} };
const contact = { title: 'Contact', w: 500, h: 430, mount(b, os) {
  const d = os.data;
  b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">Start here</span><h2>Step one <em>is a call.</em></h2>
    <p>Thirty minutes, no pitch. If I am not the right fit for the project, I will tell you on that call.</p>
    <ul class="os-ticks">${d.checks.map(c => `<li>${c}</li>`).join('')}</ul>
    <div class="os-col">${btn(d.call, 'Book the discovery call', 1)}${btn(d.brief, 'Start a project without a call')}${btn('mailto:' + d.email, d.email)}${btn('/contact', 'Contact page')}</div></div>`;
} };

// ───────────────────────── terminal ─────────────────────────
const terminal = { title: 'Terminal', w: 620, h: 420, mount(b, os) {
  const d = os.data, hist = []; let hi = 0;
  b.innerHTML = '<div class="os-term"><div class="os-out"></div><label class="os-in"><span>anowar@studio ~ %</span><input spellcheck="false" autocomplete="off" autocapitalize="off" aria-label="Terminal input"></label></div>';
  const out = b.querySelector('.os-out'), input = b.querySelector('input'), term = b.querySelector('.os-term');
  const print = (s, cls) => { const p = document.createElement('pre'); if (cls) p.className = cls; p.innerHTML = s; out.appendChild(p); term.scrollTop = term.scrollHeight; };
  const files = {
    'about.txt': () => d.about.map(txt).join('\n\n'),
    'services.txt': () => d.services.map(s => `${s.num}  ${txt(s.name).padEnd(22)} ${txt(s.price)}`).join('\n'),
    'pricing.txt': () => d.bands.map(x => `${txt(x.name).padEnd(18)} ${txt(x.price).padEnd(16)} ${txt(x.time)}`).join('\n'),
    'process.txt': () => d.steps.map((s, i) => `${i + 1}. ${s.name}`).join('\n'),
    'contact.txt': () => `call   ${d.call}\nbrief  ${d.brief}\nemail  ${d.email}`,
    'record.txt': () => d.facts.join('\n'),
  };
  const cmds = {
    help: () => `Read the short version
  about  services  work  pricing  process  contact

Look around
  ls   cat &lt;file&gt;

Open a program
  open &lt;name&gt;   ${os.list().join(' ')}

Change the wallpaper
  wallpaper &lt;name&gt;   ${Object.keys(os.wallpapers).join(' ')}

Also
  hire  neofetch  date  whoami  echo  history  clear  exit
  and a few that are not listed`,
    about: () => files['about.txt'](), services: () => files['services.txt'](), pricing: () => files['pricing.txt'](), process: () => files['process.txt'](), contact: () => files['contact.txt'](),
    work: () => d.cases.map(c => `${txt(c.name).padEnd(20)} ${txt(c.tag)}`).join('\n') + `\n\n${d.deploys.length} more in: open work`,
    ls: () => Object.keys(files).join('   '),
    cat: a => files[a[0]] ? files[a[0]]() : a[0] ? `cat: ${a[0]}: no such file. Try ls.` : 'cat: which file? Try ls.',
    open: a => os.launch(a[0]) ? `Opening ${a[0]}.` : `open: ${a[0] || 'nothing'} is not a program. Try: ${os.list().join(', ')}`,
    wallpaper: a => os.wallpapers[a[0]] ? (os.setWall(a[0]), `Wallpaper set to ${a[0]}.`) : `wallpaper: choose one of ${Object.keys(os.wallpapers).join(', ')}`,
    whoami: () => 'A visitor with good taste. The owner is Anowar Hossain: UI/UX designer, Webflow and Framer developer, AI automation expert.',
    date: () => new Date().toString(),
    echo: a => a.join(' '),
    history: () => hist.map((h, i) => `${String(i + 1).padStart(3)}  ${h}`).join('\n') || 'Nothing yet.',
    hire: () => { window.open(d.call, '_blank', 'noopener'); return 'Good call. Opening the discovery call page.'; },
    neofetch: () => `   <b class="e">●</b>   anowar@studio\n  <b class="e">●●●</b>  OS       Anowar OS, runs in a monitor on a desk\n   <b class="e">●</b>   Shell    a terminal written for this page\n        Uptime   ${Math.round(performance.now() / 1000)} seconds\n        Stack    ${d.stack.slice(0, 6).join(', ')}\n        Record   ${d.facts.slice(0, 3).join(', ')}`,
    sudo: () => 'Nice try. The only admin here is Anowar.',
    coffee: () => 'Brewing. The orange mug on the desk is already full.',
    rm: () => 'Nothing was deleted. The work is shipped and live.',
    vim: () => 'You are free to leave at any time. Type exit.',
    ping: () => 'pong. Replies within 24 hours, usually sooner.',
    clear: () => { out.innerHTML = ''; return ''; },
    exit: () => { setTimeout(() => os.close(), 300); return 'Back to the studio.'; },
  };
  const run = line => {
    print(`<span class="p">anowar@studio ~ %</span> ${line.replace(/</g, '&lt;')}`);
    const [c, ...a] = line.trim().split(/\s+/); if (!c) return;
    hist.push(line); hi = hist.length;
    const f = cmds[c.toLowerCase()]; const r = f ? f(a) : `${c}: command not found. Type help.`;
    if (r) print(r, f ? '' : 'err'); os.audio.blip(f ? 620 : 200, 0.04, 'square', 0.05);
  };
  print('Anowar OS terminal. Type <b>help</b> to see what works here.');
  input.addEventListener('keydown', ev => {
    if (ev.key === 'Enter') { run(input.value); input.value = ''; }
    else if (ev.key === 'ArrowUp') { if (hi > 0) input.value = hist[--hi]; ev.preventDefault(); }
    else if (ev.key === 'ArrowDown') { input.value = hi < hist.length - 1 ? hist[++hi] : (hi = hist.length, ''); ev.preventDefault(); }
    else if (ev.key === 'Tab') { ev.preventDefault(); const m = Object.keys(cmds).filter(k => k.startsWith(input.value)); if (m.length === 1) input.value = m[0] + ' '; }
    if (ev.key !== 'Escape') ev.stopPropagation();
  });
  term.addEventListener('click', () => input.focus()); setTimeout(() => input.focus(), 60);
} };

// ───────────────────────── paint ─────────────────────────
const paint = { title: 'Paint', w: 640, h: 470, mount(b, os, win) {
  const cols = ['#0E0D0C', '#F14E1C', '#5652E0', '#3DE0D0', '#3C8A45', '#FFB070', '#FF80C0', '#F4F1EB'];
  b.innerHTML = `<div class="os-paint"><div class="os-tools">${cols.map((c, i) => `<button class="sw${i === 1 ? ' on' : ''}" style="--c:${c}" data-c="${c}" aria-label="Colour ${c}"></button>`).join('')}
    <input type="range" min="2" max="40" value="10" aria-label="Brush size"><button class="t" data-a="clear">Clear</button><button class="t" data-a="save">Save PNG</button></div><canvas></canvas></div>`;
  const cv = b.querySelector('canvas'), g = cv.getContext('2d'), size = b.querySelector('input'); let col = cols[1], last = null, inited = false;
  const fit = () => { const r = cv.getBoundingClientRect(); if (!r.width) return; const old = inited ? g.getImageData(0, 0, cv.width, cv.height) : null; cv.width = r.width; cv.height = r.height; g.fillStyle = '#F4F1EB'; g.fillRect(0, 0, cv.width, cv.height); if (old) g.putImageData(old, 0, 0); else hello(); inited = true; };
  const hello = () => { g.strokeStyle = '#F14E1C'; g.lineWidth = 9; g.lineCap = 'round'; g.lineJoin = 'round'; g.beginPath();
    const w = cv.width, h = cv.height; for (let i = 0; i <= 60; i++) { const t = i / 60, x = w * (0.15 + 0.7 * t), y = h * 0.5 + Math.sin(t * 9) * h * 0.18 * (1 - t * 0.3); i ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
    g.fillStyle = '#4E4945'; g.font = '500 14px "JetBrains Mono", monospace'; g.fillText('draw something', 22, h - 20); };
  const pos = e => { const r = cv.getBoundingClientRect(); return [e.clientX - r.left, e.clientY - r.top]; };
  cv.addEventListener('pointerdown', e => { cv.setPointerCapture(e.pointerId); last = pos(e); g.fillStyle = col; g.beginPath(); g.arc(last[0], last[1], size.value / 2, 0, 7); g.fill(); });
  cv.addEventListener('pointermove', e => { if (!last) return; const p = pos(e); g.strokeStyle = col; g.lineWidth = +size.value; g.lineCap = 'round'; g.beginPath(); g.moveTo(last[0], last[1]); g.lineTo(p[0], p[1]); g.stroke(); last = p; });
  const end = () => { last = null; }; cv.addEventListener('pointerup', end); cv.addEventListener('pointercancel', end);
  b.querySelector('.os-tools').addEventListener('click', e => { const t = e.target.closest('button'); if (!t) return;
    if (t.dataset.c) { col = t.dataset.c; b.querySelectorAll('.sw').forEach(s => s.classList.toggle('on', s === t)); }
    else if (t.dataset.a === 'clear') { g.fillStyle = '#F4F1EB'; g.fillRect(0, 0, cv.width, cv.height); }
    else if (t.dataset.a === 'save') { const a = document.createElement('a'); a.download = 'studio-painting.png'; a.href = cv.toDataURL('image/png'); a.click(); } });
  win.onResize = fit; requestAnimationFrame(fit);
} };

// ───────────────────────── drum pads ─────────────────────────
const beats = { title: 'Beats', w: 560, h: 430, mount(b, os) {
  const A = os.audio;
  const noise = (c, dur) => { const buf = c.createBuffer(1, c.sampleRate * dur, c.sampleRate), d = buf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1; const s = c.createBufferSource(); s.buffer = buf; return s; };
  const env = (c, g, v, dur, t) => { g.gain.setValueAtTime(v, t); g.gain.exponentialRampToValueAtTime(0.0001, t + dur); };
  const tone = (f, dur, type = 'triangle', v = 0.3) => (c, t) => { const o = c.createOscillator(), g = c.createGain(); o.type = type; o.frequency.setValueAtTime(f, t); env(c, g, v, dur, t); o.connect(g).connect(A.out); o.start(t); o.stop(t + dur + 0.02); };
  const V = [
    ['Kick', 'a', (c, t) => { const o = c.createOscillator(), g = c.createGain(); o.frequency.setValueAtTime(150, t); o.frequency.exponentialRampToValueAtTime(42, t + 0.14); env(c, g, 0.9, 0.3, t); o.connect(g).connect(A.out); o.start(t); o.stop(t + 0.32); }],
    ['Snare', 's', (c, t) => { const n = noise(c, 0.2), f = c.createBiquadFilter(), g = c.createGain(); f.type = 'highpass'; f.frequency.value = 1400; env(c, g, 0.5, 0.18, t); n.connect(f).connect(g).connect(A.out); n.start(t); tone(190, 0.1, 'triangle', 0.25)(c, t); }],
    ['Hat', 'd', (c, t) => { const n = noise(c, 0.06), f = c.createBiquadFilter(), g = c.createGain(); f.type = 'highpass'; f.frequency.value = 7000; env(c, g, 0.3, 0.05, t); n.connect(f).connect(g).connect(A.out); n.start(t); }],
    ['Clap', 'f', (c, t) => { [0, 0.012, 0.026].forEach(o => { const n = noise(c, 0.12), f = c.createBiquadFilter(), g = c.createGain(); f.type = 'bandpass'; f.frequency.value = 1500; env(c, g, 0.4, 0.1, t + o); n.connect(f).connect(g).connect(A.out); n.start(t + o); }); }],
    ['Bass C', 'j', tone(65.4, 0.35, 'sawtooth', 0.22)], ['Bass G', 'k', tone(98, 0.35, 'sawtooth', 0.22)],
    ['Bell E', 'l', tone(659.3, 0.5, 'sine', 0.25)], ['Bell G', ';', tone(784, 0.5, 'sine', 0.25)],
  ];
  const pat = [[1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0], [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0], [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0]];
  b.innerHTML = `<div class="os-beats"><div class="os-gate"><p>Sound is off until you turn it on.</p><button class="os-btn p" type="button">Enable sound</button></div>
    <div class="os-pads">${V.map((v, i) => `<button type="button" data-i="${i}"><b>${v[0]}</b><kbd>${v[1].toUpperCase()}</kbd></button>`).join('')}</div>
    <div class="os-seq">${pat.map((r, i) => `<div>${r.map((on, j) => `<i data-r="${i}" data-s="${j}" class="${on ? 'on' : ''}${j % 4 === 0 ? ' q' : ''}"></i>`).join('')}</div>`).join('')}</div>
    <div class="os-row"><button class="os-btn p" data-a="play" type="button">Play loop</button><button class="os-btn" data-a="clear" type="button">Clear</button><span class="os-mono">112 bpm</span></div></div>`;
  const gate = b.querySelector('.os-gate'), pads = [...b.querySelectorAll('.os-pads button')], playBtn = b.querySelector('[data-a=play]'); let timer = null, step = 0;
  const sync = on => { gate.hidden = on; }; A.listeners.add(sync); sync(A.enabled);
  gate.querySelector('button').onclick = () => A.enable();
  const hit = (i, t) => { if (!A.enabled) { gate.classList.remove('nudge'); void gate.offsetWidth; gate.classList.add('nudge'); return; } V[i][2](A.ctx, t ?? A.ctx.currentTime); pads[i].classList.remove('hit'); void pads[i].offsetWidth; pads[i].classList.add('hit'); };
  b.querySelector('.os-pads').addEventListener('pointerdown', e => { const p = e.target.closest('button'); if (p) hit(+p.dataset.i); });
  b.querySelector('.os-seq').addEventListener('click', e => { const c = e.target.closest('i'); if (c) { const r = +c.dataset.r, s = +c.dataset.s; pat[r][s] ^= 1; c.classList.toggle('on', !!pat[r][s]); } });
  const cells = [...b.querySelectorAll('.os-seq i')];
  const tick = () => { cells.forEach(c => c.classList.toggle('now', +c.dataset.s === step)); pat.forEach((r, i) => { if (r[step]) hit(i); }); step = (step + 1) % 16; };
  const stop = () => { clearInterval(timer); timer = null; playBtn.textContent = 'Play loop'; cells.forEach(c => c.classList.remove('now')); };
  b.addEventListener('click', e => { const a = e.target.closest('[data-a]'); if (!a) return;
    if (a.dataset.a === 'play') { if (timer) return stop(); if (!A.enabled) return hit(0); step = 0; tick(); timer = setInterval(tick, 60000 / 112 / 4); playBtn.textContent = 'Stop'; }
    else if (a.dataset.a === 'clear') { pat.forEach(r => r.fill(0)); cells.forEach(c => c.classList.remove('on')); } });
  const key = e => { if (e.target.matches('input, textarea') || e.repeat) return; const i = V.findIndex(v => v[1] === e.key.toLowerCase()); if (i >= 0) hit(i); };
  addEventListener('keydown', key);
  return () => { stop(); removeEventListener('keydown', key); A.listeners.delete(sync); };
} };

// ───────────────────────── game: clear the backlog ─────────────────────────
const game = { title: 'Backlog', w: 560, h: 460, mount(b, os, win) {
  b.innerHTML = '<div class="os-game"><canvas></canvas><div class="os-hud os-mono"><span data-s>0</span><span data-m>Move the mouse. Clear the backlog.</span></div></div>';
  const cv = b.querySelector('canvas'), g = cv.getContext('2d'), sEl = b.querySelector('[data-s]'), mEl = b.querySelector('[data-m]');
  const cols = ['#F14E1C', '#FF8055', '#5652E0', '#3DE0D0', '#FFB070']; const labels = ['bug', 'copy', 'spec', 'QA', 'ship'];
  let W = 0, H = 0, px = 0.5, ball, bricks, score = 0, lives = 3, raf = 0, over = false, last = 0, moved = false;
  const reset = full => { if (full) { score = 0; lives = 3; over = false; bricks = []; for (let r = 0; r < 5; r++) for (let c = 0; c < 9; c++) bricks.push({ r, c, on: true }); }
    ball = { x: 0.5, y: 0.72, vx: (Math.random() < 0.5 ? -1 : 1) * 0.32, vy: -0.52, held: true, t: 0 }; mEl.textContent = 'Move the mouse. Clear the backlog.'; };
  const fit = () => { const r = cv.getBoundingClientRect(); if (!r.width) return; const dp = Math.min(devicePixelRatio || 1, 2); W = r.width; H = r.height; cv.width = W * dp; cv.height = H * dp; g.setTransform(dp, 0, 0, dp, 0, 0); };
  const brick = k => { const bw = 1 / 9, x = k.c * bw + 0.006, y = 0.08 + k.r * 0.062; return [x, y, bw - 0.012, 0.046]; };
  const frame = now => { raf = requestAnimationFrame(frame); const dt = Math.min(0.033, (now - last) / 1000 || 0); last = now; if (!W) return fit();
    const pw = 0.2, py = 0.92;
    if (!over) { if (ball.held) { ball.x = px; if (moved) ball.t += dt; if (ball.t > 0.55) ball.held = false; } else {
      ball.x += ball.vx * dt; ball.y += ball.vy * dt;
      if (ball.x < 0.015) { ball.x = 0.015; ball.vx = Math.abs(ball.vx); } if (ball.x > 0.985) { ball.x = 0.985; ball.vx = -Math.abs(ball.vx); } if (ball.y < 0.02) { ball.y = 0.02; ball.vy = Math.abs(ball.vy); }
      if (ball.vy > 0 && ball.y > py - 0.02 && ball.y < py + 0.02 && Math.abs(ball.x - px) < pw / 2 + 0.01) { ball.vy = -Math.abs(ball.vy) * 1.02; ball.vx = (ball.x - px) / (pw / 2) * 0.6; os.audio.blip(330, 0.04, 'square', 0.06); }
      for (const k of bricks) { if (!k.on) continue; const [x, y, w, h] = brick(k); if (ball.x > x && ball.x < x + w && ball.y > y && ball.y < y + h) { k.on = false; ball.vy *= -1; score += 10; sEl.textContent = score; os.audio.blip(520 + k.r * 70, 0.05, 'triangle', 0.08); break; } }
      if (ball.y > 1.04) { lives--; if (lives <= 0) { over = true; mEl.textContent = 'The backlog wins this round. Click to try again.'; } else { reset(false); mEl.textContent = `${lives} ${lives === 1 ? 'try' : 'tries'} left.`; } }
      if (bricks.every(k => !k.on)) { over = true; mEl.textContent = 'Backlog cleared. Shipped. Click to play again.'; }
    } }
    g.fillStyle = '#0E0D0C'; g.fillRect(0, 0, W, H);
    g.font = '500 11px "JetBrains Mono", monospace'; g.textAlign = 'center'; g.textBaseline = 'middle';
    for (const k of bricks) { if (!k.on) continue; const [x, y, w, h] = brick(k); g.fillStyle = cols[k.r]; g.beginPath(); g.roundRect(x * W, y * H, w * W, h * H, 6); g.fill(); if (w * W > 44) { g.fillStyle = k.r < 2 ? '#0E0D0C' : '#F4F1EB'; g.fillText(labels[k.r], (x + w / 2) * W, (y + h / 2) * H + 1); } }
    g.fillStyle = '#F4F1EB'; g.beginPath(); g.roundRect((px - pw / 2) * W, py * H, pw * W, 10, 5); g.fill();
    g.fillStyle = '#F14E1C'; g.beginPath(); g.arc(ball.x * W, ball.y * H, 7, 0, 7); g.fill();
    for (let i = 0; i < lives; i++) { g.fillStyle = '#F14E1C'; g.beginPath(); g.arc(W - 16 - i * 16, H - 14, 4, 0, 7); g.fill(); } };
  cv.addEventListener('pointermove', e => { const r = cv.getBoundingClientRect(); px = Math.min(0.9, Math.max(0.1, (e.clientX - r.left) / r.width)); moved = true; });
  cv.addEventListener('pointerdown', () => { if (over) { reset(true); sEl.textContent = 0; } });
  const key = e => { if (e.key === 'ArrowLeft') { px = Math.max(0.1, px - 0.06); moved = true; } if (e.key === 'ArrowRight') { px = Math.min(0.9, px + 0.06); moved = true; } };
  addEventListener('keydown', key); win.onResize = fit; reset(true); raf = requestAnimationFrame(frame);
  return () => { cancelAnimationFrame(raf); removeEventListener('keydown', key); };
} };

// ───────────────────────── settings ─────────────────────────
const settings = { title: 'Settings', w: 500, h: 400, mount(b, os) {
  const draw = () => { b.innerHTML = `<div class="os-doc"><span class="os-mono os-eb">Wallpaper</span>
    <div class="os-walls">${Object.entries(os.wallpapers).map(([k, w]) => `<button type="button" data-w="${k}" class="${os.wall === k ? 'on' : ''}" style="background-image:url(${os.asset(w.file)})"><span>${w.name}</span></button>`).join('')}</div>
    <span class="os-mono os-eb" style="margin-top:20px">Sound</span>
    <div class="os-row"><button type="button" class="os-btn${os.audio.enabled ? '' : ' p'}" data-snd>${os.audio.enabled ? 'Turn sound off' : 'Enable sound'}</button><span class="os-note">All sound is made in code. Nothing plays until you turn it on.</span></div>
    <span class="os-mono os-eb" style="margin-top:20px">About this computer</span><p class="os-note">Anowar OS runs inside the monitor on the desk. The wallpaper you pick also changes the light the screens throw on the room. Press Escape to step back out.</p></div>`; };
  draw();
  b.addEventListener('click', e => { const w = e.target.closest('[data-w]'); if (w) { os.setWall(w.dataset.w); draw(); } if (e.target.closest('[data-snd]')) { os.audio.toggle(); draw(); } });
} };

export const APPS = { about, work, services, pricing, process, reviews, faq, contact, terminal, paint, beats, game, settings };
