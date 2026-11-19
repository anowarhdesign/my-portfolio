// The studio: a baked-light room drawn with unlit shaders, a few live parts on top,
// and a monitor you can fly into. three.js r186, no post-processing.
import * as THREE from 'three';
import { GLTFLoader } from '../vendor/jsm/loaders/GLTFLoader.js';
import { createOS, WALLPAPERS } from './os.js';

const BASE = new URL('..', import.meta.url).href;            // .../studio/
const VER = new URL(import.meta.url).searchParams.get('v');
const asset = p => BASE + p + (VER ? '?v=' + VER : '');     // baked files change URL with every build
const Q = new URLSearchParams(location.search);
const FROZEN = Q.has('t') ? parseFloat(Q.get('t')) : null;
const VIEW = Q.get('view') || '';
// Language comes from <html lang>. English is the source; other languages load studio/i18n/<lang>.json,
// a map from the English string to its translation (written by build/pages3.py). T() translates,
// N() only marks a string so the build finds it, L() points an internal link at this language's pages.
// The mini-OS itself stays in English.
const LANG = (document.documentElement.lang || 'en').toLowerCase();
const LBASE = LANG === 'en' ? '' : '/' + LANG;
let I18N = {};
const T = s => I18N[s] || s;
const N = s => s;
const L = h => (LBASE && h.startsWith('/') && !/^\/(studio|uploads|assets|api)\b/.test(h)) ? LBASE + (h === '/' ? '' : h) : h;
const plainCache = new Map();
const TP = s => { if (!plainCache.has(s)) { const d = document.createElement('div'); d.innerHTML = T(s); plainCache.set(s, d.textContent); } return plainCache.get(s); };
const loadI18n = () => LANG === 'en' ? Promise.resolve({}) : fetch(asset('i18n/' + LANG + '.json')).then(r => r.ok ? r.json() : {}).catch(() => ({}));
const localData = d => LBASE ? { ...d, services: d.services.map(x => ({ ...x, url: L(x.url) })), cases: d.cases.map(x => ({ ...x, url: L(x.url) })) } : d;
const root = document.getElementById('studio');
const canvas = root.querySelector('canvas.st-gl');
const tip = root.querySelector('.st-tip');
const cardEl = root.querySelector('.st-card');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;

const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const smooth = (a, b, x) => { const t = clamp((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t); };
const ease = t => t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;

// ───────────────────────── shaders ─────────────────────────
const VERT = /* glsl */`
attribute vec2 lmuv;
uniform float uTime, uSway; uniform vec3 uPivot;
varying vec2 vUv, vLm; varying vec3 vW, vN;
void main(){
  vUv = uv; vLm = lmuv;
  vec4 wp = modelMatrix * vec4(position, 1.0);
  if (uSway > 0.0) {
    float d = distance(wp.xyz, uPivot);
    float w = smoothstep(0.04, 0.55, d) * uSway;
    wp.x += (sin(uTime * 0.9 + wp.y * 7.0 + wp.z * 5.0) * 0.010 + sin(uTime * 0.37 + wp.y * 3.0) * 0.022) * w;
    wp.z += cos(uTime * 0.7 + wp.x * 6.0) * 0.012 * w;
  }
  vW = wp.xyz; vN = normalize(mat3(modelMatrix) * normal);
  gl_Position = projectionMatrix * viewMatrix * wp;
}`;

const COMMON = /* glsl */`
precision highp float;
varying vec2 vUv, vLm; varying vec3 vW, vN;
uniform float uFade;
vec3 aces(vec3 x){ return clamp((x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14), 0.0, 1.0); }
vec3 outc(vec3 c){ return pow(max(c, 0.0), vec3(1.0 / 2.2)) * uFade; }
float hash(vec2 p){ return fract(sin(dot(p, vec2(41.3, 289.1))) * 43758.5453); }
`;

const FRAG_ROOM = COMMON + /* glsl */`
uniform sampler2D uMap, uLmW, uLmP, uLmB, uEnv, uScrA, uScrB;
uniform float uHasMap, uRefl, uHi, uAlpha, uDesk, uMonOn, uEnvGain, uCon;
uniform vec3 uColor, uMon, uCam, uW, uP, uRange;
uniform mat4 uScrAInv, uScrBInv; uniform vec2 uScrSize;
vec2 equirect(vec3 d){ return vec2(atan(d.x, -d.z) / 6.2831853 + 0.5, asin(clamp(d.y, -1.0, 1.0)) / 3.14159265 + 0.5); }
void main(){
  vec3 alb = uColor; if (uHasMap > 0.5) alb *= texture2D(uMap, vUv).rgb;
  vec3 Wl = pow(texture2D(uLmW, vLm).rgb, vec3(2.2)) * uRange.x * mix(0.22, 1.0, smoothstep(-2.09, -1.96, vW.x));
  vec3 Pl = pow(texture2D(uLmP, vLm).rgb, vec3(2.2)) * uRange.y;
  vec3 Bm = pow(texture2D(uLmB, vLm).rgb, vec3(2.2)) * uRange.z;
  vec3 col = alb * (Wl * uW + Pl * uP + Bm * uMon);
  vec3 V = normalize(vW - uCam); vec3 N = normalize(vN); if (dot(N, V) > 0.0) N = -N;
  vec3 R = reflect(V, N);
  float fr = pow(1.0 - max(dot(-V, N), 0.0), 4.0);
  if (uRefl > 0.0) col += texture2D(uEnv, equirect(R)).rgb * uRefl * (0.12 + 0.88 * fr) * uEnvGain;
  if (uDesk > 0.5) {
    vec3 lo = (uScrAInv * vec4(vW, 1.0)).xyz, ld = (uScrAInv * vec4(R, 0.0)).xyz; float t = -lo.z / ld.z;
    vec2 p = (lo + ld * t).xy / uScrSize + 0.5;
    vec2 e = smoothstep(vec2(-0.05), vec2(0.05), p) * smoothstep(vec2(-0.05), vec2(0.05), 1.0 - p);
    vec3 r = (t > 0.0 ? pow(texture2D(uScrA, vec2(p.x, 1.0 - p.y), 3.0).rgb, vec3(2.2)) * e.x * e.y / (1.0 + t * 2.5) : vec3(0.0));
    lo = (uScrBInv * vec4(vW, 1.0)).xyz; ld = (uScrBInv * vec4(R, 0.0)).xyz; t = -lo.z / ld.z;
    p = (lo + ld * t).xy / uScrSize + 0.5;
    e = smoothstep(vec2(-0.05), vec2(0.05), p) * smoothstep(vec2(-0.05), vec2(0.05), 1.0 - p);
    r += (t > 0.0 ? pow(texture2D(uScrB, vec2(p.x, 1.0 - p.y), 3.0).rgb, vec3(2.2)) * e.x * e.y / (1.0 + t * 2.5) : vec3(0.0));
    col += r * uMonOn * (0.10 + 0.55 * fr);
  }
  col = aces(col);
  col = mix(col, col * col * (3.0 - 2.0 * col), uCon);
  col += vec3(0.20, 0.11, 0.05) * uHi * (0.35 + 0.65 * fr);
  col += (hash(gl_FragCoord.xy) - 0.5) * 0.012;
  gl_FragColor = vec4(outc(col), uAlpha);
}`;

const FRAG_EMIT = COMMON + /* glsl */`
uniform sampler2D uMap; uniform float uHasMap, uGain, uHi, uScan, uTime, uDec; uniform vec3 uColor;
void main(){
  vec3 col = uColor; if (uHasMap > 0.5) { vec3 tx = texture2D(uMap, vUv).rgb; col *= uDec > 0.5 ? pow(tx, vec3(2.2)) : tx; }
  col *= uGain;
  if (uScan > 0.0) col *= 1.0 - uScan * 0.06 * (0.5 + 0.5 * sin(vUv.y * 620.0 + uTime * 6.0));
  col += vec3(0.07, 0.04, 0.02) * uHi;
  gl_FragColor = vec4(outc(col), 1.0);
}`;

const FRAG_GLOW = /* glsl */`
precision highp float; varying vec2 vUv; uniform vec3 uColor; uniform float uGain, uFade;
void main(){ vec2 p = vUv * 2.0 - 1.0; float a = pow(max(1.0 - dot(p, p), 0.0), 2.4); gl_FragColor = vec4(uColor * a * uGain * uFade, 1.0); }`;

// No WebGL, or the room failed to load: keep the still image and let the button open the OS directly.
function fallback() {
  if (root.classList.contains('st-nogl')) return;
  root.classList.add('st-nogl');
  fetch(asset('data.json')).then(r => r.json()).then(data => {
    const html = document.documentElement;
    const o = createOS({ root: document.querySelector('.os'), data: localData(data), asset, onExit: () => html.classList.remove('st-os-open'), onWallpaper() {} });
    root.querySelectorAll('[data-st="enter"]').forEach(b => b.addEventListener('click', ev => { ev.preventDefault(); o.open({ instant: true }); html.classList.add('st-os-open'); }));
    addEventListener('keydown', ev => { if (ev.key === 'Escape' && o.isOpen()) o.close(); });
  }).catch(() => {});
}

// ───────────────────────── renderer ─────────────────────────
let renderer;
try {
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance', alpha: false });
} catch (e) { fallback(); throw e; }
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;   // the shaders encode
renderer.setClearColor(0x0b0a0c, 1);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 16 / 9, 0.08, 20);
const U = {                                                // shared uniforms
  uTime: { value: 0 }, uFade: { value: 0 }, uW: { value: new THREE.Color(1, 1, 1) }, uP: { value: new THREE.Color(1, 1, 1) }, uEnvGain: { value: 1 }, uCon: { value: 0.45 }, uMon: { value: new THREE.Color(0, 0, 0) }, uMonOn: { value: 0 },
  uCam: { value: new THREE.Vector3() }, uEnv: { value: null }, uScrA: { value: null }, uScrB: { value: null },
  uScrAInv: { value: new THREE.Matrix4() }, uScrBInv: { value: new THREE.Matrix4() }, uScrSize: { value: new THREE.Vector2(0.53, 0.298) },
  uRange: { value: new THREE.Vector3(6, 6, 2) },
};

// ───────────────────────── screens (canvas textures) ─────────────────────────
function makeScreen(w, h) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.NoColorSpace; tex.flipY = false; tex.anisotropy = 8;
  tex.generateMipmaps = true; tex.minFilter = THREE.LinearMipmapLinearFilter;
  return { c, g: c.getContext('2d', { willReadFrequently: true }), tex };
}
const scrMain = makeScreen(1280, 720), scrSide = makeScreen(1024, 576);
U.uScrA.value = scrMain.tex; U.uScrB.value = scrSide.tex;
const wallImgs = {}; let wallpaper = localStorage.getItem('st-wall') || 'fern';
const thumbs = [];
let DATA = null, os = null;
const BOOT_AT = 1.9;       // seconds after the room appears
const lampK = t => { const k = smooth(0.55, 1.5, t); return k * (t < 1.5 ? 0.82 + 0.18 * Math.sin(t * 47) * Math.sin(t * 13) : 1); };
const LOOKS = { W: [0.10, 0.14, 0.37], P: [0.80, 0.58, 0.35] };

function crt(g, w, h, k, draw) {   // k: 0..1 power-on. A tube that opens from a line.
  g.fillStyle = '#020203'; g.fillRect(0, 0, w, h);
  if (k <= 0) return 0;
  const line = smooth(0.0, 0.18, k), open = smooth(0.14, 0.42, k), steady = smooth(0.42, 0.7, k);
  const flick = k < 0.8 ? 0.72 + 0.28 * Math.sin(k * 90) * Math.sin(k * 37) : 1;
  const hh = Math.max(3, h * open), ww = w * (0.04 + 0.96 * line);
  g.save();
  g.beginPath(); g.rect((w - ww) / 2, (h - hh) / 2, ww, hh); g.clip();
  if (steady > 0) { g.globalAlpha = steady; draw(); g.globalAlpha = 1; }
  g.fillStyle = `rgba(214,236,255,${(1 - steady) * 0.95})`; g.fillRect(0, 0, w, h);
  g.restore();
  return clamp((0.25 * line + 0.75 * open) * flick, 0, 1.25);
}
function cover(g, img, x, y, w, h) {
  if (!img || !img.width) { g.fillStyle = '#10201c'; g.fillRect(x, y, w, h); return; }
  const s = Math.max(w / img.width, h / img.height), iw = img.width * s, ih = img.height * s;
  g.drawImage(img, x + (w - iw) / 2, y + (h - ih) / 2, iw, ih);
}
function rr(g, x, y, w, h, r) { g.beginPath(); g.roundRect(x, y, w, h, r); }
// draw a line of text, shrinking it until it fits (translations run longer than the English)
function fitText(g, s, x, y, maxW, px, font) { let q = px; do { g.font = font.replace('#', q); q -= 4; } while (g.measureText(s).width > maxW && q > 24); g.fillText(s, x, y); }
function drawDesktop(g, w, h, t) {
  cover(g, wallImgs[wallpaper], 0, 0, w, h);
  const boot = clamp((t - BOOT_AT - 1.0) / 1.4, 0, 1);
  if (boot < 1) {            // boot card
    g.fillStyle = `rgba(8,8,10,${1 - smooth(0.75, 1, boot)})`; g.fillRect(0, 0, w, h);
    g.globalAlpha = 1 - smooth(0.75, 1, boot);
    g.fillStyle = '#F4F1EB'; g.font = '600 54px Archivo, Arial, sans-serif'; g.textAlign = 'center';
    g.fillText('Anowar OS', w / 2, h / 2 - 16);
    g.fillStyle = 'rgba(244,241,235,.16)'; rr(g, w / 2 - 150, h / 2 + 22, 300, 6, 3); g.fill();
    g.fillStyle = '#F14E1C'; rr(g, w / 2 - 150, h / 2 + 22, 300 * smooth(0, 0.72, boot), 6, 3); g.fill();
    g.globalAlpha = 1; g.textAlign = 'left';
    return;
  }
  g.fillStyle = 'rgba(12,12,14,.62)'; g.fillRect(0, 0, w, 38);
  g.fillStyle = '#F4F1EB'; g.font = '600 18px Archivo, Arial, sans-serif'; g.textAlign = 'left';
  g.fillText('Anowar OS', 20, 26);
  g.fillStyle = 'rgba(244,241,235,.7)'; g.font = '500 16px "JetBrains Mono", monospace';
  const d = new Date(); g.textAlign = 'right';
  g.fillText(d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), w - 20, 26); g.textAlign = 'left';
  // an invitation large enough to read from across the room
  g.fillStyle = 'rgba(6,8,8,.34)'; g.fillRect(0, 38, w, h - 38);
  g.textAlign = 'center';
  g.fillStyle = '#F4F1EB'; fitText(g, TP(N('Step inside.')), w / 2, 300, w - 110, 118, '700 #px Archivo, Arial, sans-serif');
  g.fillStyle = '#FF9A6C'; fitText(g, TP(N('The work is in here.')), w / 2, 392, w - 110, 70, 'italic #px "Instrument Serif", Georgia, serif');
  const cta = TP(N('Click the screen')); g.font = '600 32px Archivo, Arial, sans-serif'; const bw = Math.max(340, Math.min(w - 120, g.measureText(cta).width + 96));
  const pu = (t * 0.55) % 1;
  g.strokeStyle = `rgba(241,78,28,${0.8 * (1 - pu)})`; g.lineWidth = 4; rr(g, w / 2 - bw / 2 - pu * 26, 452 - pu * 16, bw + pu * 52, 76 + pu * 32, 38 + pu * 16); g.stroke();
  g.fillStyle = '#F14E1C'; rr(g, w / 2 - bw / 2, 452, bw, 76, 38); g.fill();
  g.fillStyle = '#fff'; fitText(g, cta, w / 2, 501, bw - 60, 32, '600 #px Archivo, Arial, sans-serif');
  g.textAlign = 'left';
  // dock
  const n = 9, dw = n * 58 + 20; g.fillStyle = 'rgba(12,12,14,.6)'; rr(g, (w - dw) / 2, h - 76, dw, 60, 18); g.fill();
  const cols = ['#F14E1C', '#F4F1EB', '#5652E0', '#3DE0D0', '#FFB070', '#F4F1EB', '#8FE8C4', '#FF80C0', '#C4C7CC'];
  for (let i = 0; i < n; i++) { g.fillStyle = cols[i]; rr(g, (w - dw) / 2 + 16 + i * 58, h - 66, 42, 42, 11); g.fill(); }
}
function drawWork(g, w, h, t) {
  const n = thumbs.length; g.fillStyle = '#0E0D0C'; g.fillRect(0, 0, w, h);
  if (!n) return;
  const seg = 4.2, k = (t / seg) % n, i = Math.floor(k), f = k - i;
  cover(g, thumbs[i].img, 0, 0, w, h);
  if (f > 0.86) { g.globalAlpha = smooth(0.86, 1, f); cover(g, thumbs[(i + 1) % n].img, 0, 0, w, h); g.globalAlpha = 1; }
  const gr = g.createLinearGradient(0, h - 190, 0, h); gr.addColorStop(0, 'rgba(8,8,10,0)'); gr.addColorStop(1, 'rgba(8,8,10,.92)');
  g.fillStyle = gr; g.fillRect(0, h - 190, w, 190);
  const cur = thumbs[f > 0.93 ? (i + 1) % n : i];
  g.fillStyle = '#F14E1C'; g.font = '500 17px "JetBrains Mono", monospace'; g.fillText(TP(N('Selected work')), 34, h - 92);
  g.fillStyle = '#F4F1EB'; g.font = '700 46px Archivo, Arial, sans-serif'; g.fillText(cur.name, 34, h - 42);
  g.fillStyle = 'rgba(244,241,235,.75)'; g.font = '500 17px "JetBrains Mono", monospace'; g.textAlign = 'right';
  g.fillText(TP(cur.tag), w - 34, h - 46); g.textAlign = 'left';
  g.fillStyle = 'rgba(244,241,235,.25)'; g.fillRect(34, h - 22, w - 68, 3);
  g.fillStyle = '#F14E1C'; g.fillRect(34, h - 22, (w - 68) * f, 3);
}
const TINT = { fern: [0.62, 1.0, 0.86], dusk: [1.0, 0.74, 0.86], ember: [1.0, 0.62, 0.44], paper: [1.0, 0.95, 0.86] };
let lastScr = -1;
function updateScreens(t) {
  const k = clamp((t - BOOT_AT) / 1.5, 0, 1), k2 = clamp((t - BOOT_AT - 0.35) / 1.5, 0, 1);
  const steady = t > BOOT_AT + 3.2;
  const key = steady ? Math.floor(t * 12) : t;
  if (key === lastScr) return; lastScr = key;
  const a = crt(scrMain.g, scrMain.c.width, scrMain.c.height, k, () => drawDesktop(scrMain.g, scrMain.c.width, scrMain.c.height, t));
  const b = crt(scrSide.g, scrSide.c.width, scrSide.c.height, k2, () => drawWork(scrSide.g, scrSide.c.width, scrSide.c.height, t));
  scrMain.tex.needsUpdate = true; scrSide.tex.needsUpdate = true;
  const tn = TINT[wallpaper] || TINT.fern, on = (a + b) * 0.5;
  U.uMon.value.setRGB(tn[0] * 1.5 * on, tn[1] * 1.3 * on, tn[2] * 1.15 * on);
  U.uMonOn.value = on;
}

// ───────────────────────── materials ─────────────────────────
const lm = {}; const mats = new Map(); const emitters = []; const hot = []; const glows = [];
function roomMat(src, g, key, sway, pivot) {
  const id = `${src.uuid}|${g}|${key || ''}|${sway ? pivot.x.toFixed(2) : ''}`;
  if (mats.has(id)) return mats.get(id);
  const ud = src.userData || {}; const alpha = ud.alpha ?? 1;
  const m = new THREE.ShaderMaterial({
    vertexShader: VERT, fragmentShader: FRAG_ROOM, side: THREE.DoubleSide, transparent: alpha < 1, depthWrite: alpha >= 1,
    uniforms: {
      ...U, uMap: { value: src.map || null }, uHasMap: { value: src.map ? 1 : 0 }, uColor: { value: src.color.clone() },
      uLmW: { value: lm[g + 'W'] }, uLmP: { value: lm[g + 'P'] }, uLmB: { value: lm[g + 'B'] }, uRefl: { value: ud.refl || 0 }, uHi: { value: 0 }, uAlpha: { value: alpha },
      uDesk: { value: src.name === 'desk_top' ? 1 : 0 }, uSway: { value: sway ? 1 : 0 }, uPivot: { value: pivot || new THREE.Vector3() },
    },
  });
  mats.set(id, m); return m;
}
function emitMat(opts) {
  return new THREE.ShaderMaterial({
    vertexShader: VERT, fragmentShader: FRAG_EMIT, side: THREE.DoubleSide,
    uniforms: { ...U, uMap: { value: opts.map || null }, uHasMap: { value: opts.map ? 1 : 0 }, uColor: { value: opts.color || new THREE.Color(1, 1, 1) },
      uGain: { value: opts.gain ?? 1 }, uHi: { value: 0 }, uScan: { value: opts.scan || 0 }, uDec: { value: opts.dec || 0 }, uSway: { value: 0 }, uPivot: { value: new THREE.Vector3() } },
  });
}
function glow(pos, w, h, color, gain) {
  const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.ShaderMaterial({
    vertexShader: 'varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: FRAG_GLOW, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true,
    uniforms: { uColor: { value: new THREE.Color(color) }, uGain: { value: gain }, uFade: U.uFade },
  }));
  m.position.copy(pos); m.renderOrder = 5; m.userData.gain = gain; m.userData.lamp = gain > 0; scene.add(m); glows.push(m); return m;
}

// hotspots: mesh-name prefixes -> what a click does
const HOT = [
  { key: 'os', what: N('The main monitor'), label: N('Step inside the computer'), match: ['screen_main', 'main__'] },
  { key: 'work', what: N('The second monitor'), label: N('Selected work'), match: ['screen_side', 'side__'] },
  { key: 'services', what: N('The laptop'), label: N('Services'), match: ['laptop__', 'screen_laptop'] },
  { key: 'record', what: N('The plaque on the wall'), label: N('Track record'), match: ['plaque'] },
  { key: 'about', what: N('The prints on the shelf'), label: N('About Anowar'), match: ['print_', 'avatar__', 'headline__'] },
  { key: 'process', what: N('The book on the pegboard'), label: N('How a project runs'), match: ['book__'] },
  { key: 'contact', what: N('The phone'), label: N('Get in touch'), match: ['phone__'] },
  { key: 'design', what: N('The drawing tablet'), label: N('Product design'), match: ['tablet__', 'stylus'] },
  { key: 'reviews', what: N('The headphones'), label: N('What clients say'), match: ['hp1__', 'hp2__', 'glow_hp'] },
  { key: 'cases', what: N('The film camera'), label: N('Case studies'), match: ['camera__'] },
  { key: 'ai', what: N('The PC tower'), label: N('AI automation'), match: ['pc__', 'glow_pc'] },
  { key: 'pricing', what: N('The coffee mug'), label: N('Pricing'), match: ['mug'] },
  { key: 'stack', what: N('The keyboard and mouse'), label: N('Toolkit'), match: ['keyboard__', 'deskmouse__'] },
  { key: 'hours', what: N('The hanging plant'), label: N('Working hours'), match: ['hang__', 'sway_hang'] },
];
const hotOf = name => HOT.find(h => h.match.some(p => name.startsWith(p)));
const hotState = Object.fromEntries(HOT.map(h => [h.key, { hi: 0, target: 0, mats: new Set(), box: new THREE.Box3() }]));

// ───────────────────────── load ─────────────────────────
const tl = new THREE.TextureLoader();
const loadTex = (url, srgb) => new Promise((res, rej) => tl.load(url, t => { t.flipY = false; t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace; t.anisotropy = 4; res(t); }, undefined, rej));
const loadImg = url => new Promise(res => { const i = new Image(); i.onload = () => res(i); i.onerror = () => res(null); i.src = url; });
const screens = {};

async function load() {
  const [data, i18n, gltf, w0, p0, b0, w1, p1, b1, env] = await Promise.all([
    fetch(asset('data.json')).then(r => r.json()),
    loadI18n(),
    new GLTFLoader().loadAsync(asset('baked/studio.glb')),
    ...['lm0_W', 'lm0_P', 'lm0_B', 'lm1_W', 'lm1_P', 'lm1_B'].map(n => loadTex(asset('baked/' + n + '.webp'))),
    new Promise(res => tl.load(asset('baked/env.jpg'), t => { t.colorSpace = THREE.SRGBColorSpace; t.wrapS = THREE.RepeatWrapping; res(t); })),
  ]);
  DATA = data; I18N = i18n; Object.assign(lm, { '0W': w0, '0P': p0, '0B': b0, '1W': w1, '1P': p1, '1B': b1 }); U.uEnv.value = env;
  Object.keys(WALLPAPERS).forEach(k => loadImg(asset(WALLPAPERS[k].file)).then(i => { wallImgs[k] = i; lastScr = -1; }));
  data.cases.filter(c => c.thumb).slice(0, 8).forEach(c => loadImg(c.thumb).then(img => img && thumbs.push({ img, name: c.name.replace(/&amp;/g, '&'), tag: c.tag })));

  const meshes = []; gltf.scene.traverse(o => o.isMesh && meshes.push(o));
  gltf.scene.updateMatrixWorld(true);
  for (const o of meshes) {
    const g = o.userData.lm ?? -1, src = o.material, name = o.name, h = hotOf(name);
    if (o.geometry.attributes.uv1) o.geometry.setAttribute('lmuv', o.geometry.attributes.uv1);
    else o.geometry.setAttribute('lmuv', o.geometry.attributes.uv);
    if (g >= 0) {
      const sway = name.startsWith('sway_');
      let pivot = null;
      if (sway) { const bb = new THREE.Box3().setFromObject(o); pivot = bb.getCenter(new THREE.Vector3()); pivot.y = bb.min.y; if (name.startsWith('sway_hang')) pivot.set(-0.72, 2.03, 0.20); }
      o.material = roomMat(src, g, h?.key, sway, pivot);
    } else if (name === 'screen_main' || name === 'screen_side') {
      o.material = emitMat({ map: name === 'screen_main' ? scrMain.tex : scrSide.tex, gain: name === 'screen_main' ? 1.0 : 0.8, scan: 1, dec: 1 }); screens[name] = o;
    } else if (name === 'screen_laptop') { o.material = emitMat({ map: src.emissiveMap, gain: 0.85 }); emitters.push({ o, base: 0.85, kind: 'laptop' });
    } else if (name === 'win__sky') { o.material = emitMat({ map: src.emissiveMap, gain: 1.15 }); emitters.push({ o, base: 1.15, kind: 'sky' });
    } else { o.material = emitMat({ color: src.emissive.clone(), gain: 1.9 }); emitters.push({ o, base: 1.9, kind: name }); }
    if (h) { hot.push(o); o.userData.hot = h.key; hotState[h.key].mats.add(o.material); hotState[h.key].box.expandByObject(o); }
  }
  scene.add(gltf.scene);

  // screen frames for the fly-in and the desk reflection
  for (const [nm, u] of [['screen_main', U.uScrAInv], ['screen_side', U.uScrBInv]]) {
    const o = screens[nm]; o.geometry.computeBoundingBox();
    const c = o.geometry.boundingBox.getCenter(new THREE.Vector3()), s = o.geometry.boundingBox.getSize(new THREE.Vector3());
    o.userData.center = o.localToWorld(c.clone()); o.userData.quat = o.getWorldQuaternion(new THREE.Quaternion());
    o.userData.normal = new THREE.Vector3(0, 0, 1).applyQuaternion(o.userData.quat); o.userData.size = s;
    u.value.compose(o.userData.center, o.userData.quat, new THREE.Vector3(1, 1, 1)).invert();
    U.uScrSize.value.set(s.x, s.y);
  }
  // soft additive glows where the light sources are
  const sm = screens.screen_main.userData, ss = screens.screen_side.userData;
  glows.mon = [glow(sm.center.clone().addScaledVector(sm.normal, 0.012), 1.25, 0.95, '#9cc8ff', 0.0), glow(ss.center.clone().addScaledVector(ss.normal, 0.012), 1.25, 0.95, '#9cc8ff', 0.0)];
  glow(new THREE.Vector3(sm.center.x, sm.center.y + 0.172, sm.center.z + 0.05), 0.72, 0.16, '#ffb469', 0.42);
  glow(new THREE.Vector3(ss.center.x, ss.center.y + 0.172, ss.center.z + 0.05), 0.72, 0.16, '#ffb469', 0.42);
  glow(new THREE.Vector3(0, 0.98, 0.06), 2.3, 0.9, '#ff8a3c', 0.16);
  glow(new THREE.Vector3(0.715, 1.06, 0.45), 0.30, 0.30, '#6a6cff', 0.5);
  glow(new THREE.Vector3(0.715, 0.87, 0.45), 0.30, 0.30, '#ff4fd8', 0.5);
  glow(new THREE.Vector3(-1.46, 1.45, 0.05), 2.0, 2.2, '#8a6cff', 0.10).userData.lamp = false;
  glow(new THREE.Vector3(-0.02, 2.045, 0.13), 1.0, 0.16, '#ffb469', 0.34);
  makeDust(); makeGlass();
  os = createOS({ root: document.querySelector('.os'), data: localData(data), asset, onExit: flyOut, onWallpaper: w => { wallpaper = w; lastScr = -1; } });
  bind(); resize(); requestAnimationFrame(frame);
  root.classList.add('st-ready');
  if (VIEW === 'os') { state.mode = 'os'; state.fly = 1; os.open({ instant: true, app: Q.get('app') }); }
  else if (VIEW.startsWith('card-')) openCard(VIEW.slice(5));
}

// ───────────────────────── live parts ─────────────────────────
let dust;
function makeDust() {
  const n = 420, p = new Float32Array(n * 3), s = new Float32Array(n);
  for (let i = 0; i < n; i++) { p[i * 3] = -1.9 + Math.random() * 3.4; p[i * 3 + 1] = 0.75 + Math.random() * 1.75; p[i * 3 + 2] = 0.1 + Math.random() * 2.3; s[i] = Math.random(); }
  const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(p, 3)); g.setAttribute('seed', new THREE.BufferAttribute(s, 1));
  dust = new THREE.Points(g, new THREE.ShaderMaterial({
    blending: THREE.AdditiveBlending, depthWrite: false, transparent: true, uniforms: { uTime: U.uTime, uFade: U.uFade, uPx: { value: 1 }, uMonOn: U.uMonOn },
    vertexShader: `attribute float seed; uniform float uTime, uPx; varying float vA; varying vec3 vC; uniform float uMonOn;
      void main(){ vec3 p = position; float t = uTime * 0.05 + seed * 40.0;
        p.x += sin(t * 1.7 + seed * 9.0) * 0.16; p.y += mod(t * 0.35 + seed, 1.0) * 0.5 - 0.25 + sin(t * 2.3) * 0.05; p.z += cos(t * 1.3 + seed * 5.0) * 0.14;
        float win = smoothstep(1.5, 0.2, distance(p.xy, vec2(-1.3, 1.5))) * smoothstep(2.4, 0.2, p.z);   // dusk light from the window
        float bar = smoothstep(0.7, 0.05, distance(p, vec3(0.0, 1.25, 0.35)));                           // light bars and screens
        vA = (win * 0.75 + bar * (0.6 + 0.5 * uMonOn)) * (0.45 + 0.55 * sin(t * 9.0 + seed * 60.0));
        vC = mix(vec3(0.75, 0.62, 1.0), vec3(1.0, 0.78, 0.5), bar / (bar + win + 0.001));
        vec4 mv = viewMatrix * vec4(p, 1.0); gl_Position = projectionMatrix * mv; gl_PointSize = uPx * (1.8 + seed * 3.4) / -mv.z; }`,
    fragmentShader: `precision highp float; varying float vA; varying vec3 vC; uniform float uFade;
      void main(){ vec2 d = gl_PointCoord - 0.5; float a = smoothstep(0.5, 0.0, length(d)); gl_FragColor = vec4(vC * a * a * vA * 0.9 * uFade, 1.0); }`,
  }));
  dust.renderOrder = 6; dust.frustumCulled = false; scene.add(dust);
}
function makeGlass() {   // the window pane: a faint reflection of the room that shifts with the camera
  const m = new THREE.Mesh(new THREE.PlaneGeometry(0.92, 1.2), new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, uniforms: { uEnv: U.uEnv, uCam: U.uCam, uFade: U.uFade },
    vertexShader: 'varying vec3 vW; void main(){ vec4 w = modelMatrix * vec4(position, 1.0); vW = w.xyz; gl_Position = projectionMatrix * viewMatrix * w; }',
    fragmentShader: `precision highp float; varying vec3 vW; uniform sampler2D uEnv; uniform vec3 uCam; uniform float uFade;
      void main(){ vec3 V = normalize(vW - uCam); vec3 R = reflect(V, vec3(0.0, 0.0, 1.0));
        vec2 uv = vec2(atan(R.x, -R.z) / 6.2831853 + 0.5, asin(clamp(R.y, -1.0, 1.0)) / 3.14159265 + 0.5);
        float fr = pow(1.0 - abs(V.z), 3.0); vec3 c = texture2D(uEnv, uv).rgb * (0.10 + 0.8 * fr);
        float streak = smoothstep(0.0, 1.0, sin((vW.x + vW.y) * 9.0) * 0.5 + 0.5) * 0.02;
        gl_FragColor = vec4((c + streak) * uFade, 1.0); }`,
  }));
  m.position.set(-1.46, 1.55, -0.055); m.renderOrder = 4; scene.add(m);
}

// ───────────────────────── camera ─────────────────────────
const state = { mode: 'room', fly: 0, flyFrom: 0, flyTo: 0, flyT0: 0, flyDur: 1.7, mx: 0, my: 0, cx: 0, cy: 0, card: null, hover: null, t: 0 };
const HOME = new THREE.Vector3(-0.30, 1.46, 3.02), LOOK = new THREE.Vector3(-0.30, 1.19, 0.0);
const tmpA = new THREE.Vector3(), tmpB = new THREE.Vector3(), tmpL = new THREE.Vector3(), qA = new THREE.Quaternion(), qB = new THREE.Quaternion(), mLook = new THREE.Matrix4();
const FOV0 = 37;
function baseFov() { const a = camera.aspect; const need = 2 * Math.atan(Math.tan(THREE.MathUtils.degToRad(FOV0) / 2) * Math.max(1, 1.55 / a)); return clamp(THREE.MathUtils.radToDeg(need), FOV0, 80); }
const sideShift = () => smooth(1.15, 1.7, camera.aspect);   // 0 on tall screens (scene centred), 1 on wide ones
function placeCamera(t, dt) {
  const k = 1 - Math.exp(-dt * 3.2);
  state.cx += (state.mx - state.cx) * k; state.cy += (state.my - state.cy) * k;
  const drift = reduced ? 0 : 1;
  const sh = sideShift();
  tmpA.set(HOME.x * sh + state.cx * 0.42 + Math.sin(t * 0.11) * 0.07 * drift, HOME.y - state.cy * 0.13 + Math.sin(t * 0.17 + 1.0) * 0.022 * drift, HOME.z - Math.abs(state.cx) * 0.05 + Math.cos(t * 0.09) * 0.05 * drift);
  tmpL.set(LOOK.x * sh + state.cx * 0.16, LOOK.y - state.cy * 0.06, 0);
  if (state.focus) { tmpA.lerp(state.focus.pos, state.focusK); tmpL.lerp(state.focus.look, state.focusK); }
  mLook.lookAt(tmpA, tmpL, camera.up); qA.setFromRotationMatrix(mLook);
  const fov0 = baseFov();
  if (state.fly > 0) {
    const s = screens.screen_main.userData, f = THREE.MathUtils.degToRad(fov0);
    const dist = Math.min(s.size.y / (2 * Math.tan(f / 2)), s.size.x / (2 * Math.tan(f / 2) * camera.aspect));
    tmpB.copy(s.center).addScaledVector(s.normal, dist);
    mLook.lookAt(tmpB, s.center, camera.up); qB.setFromRotationMatrix(mLook);
    const e = ease(state.fly);
    camera.position.lerpVectors(tmpA, tmpB, e); camera.quaternion.slerpQuaternions(qA, qB, e);
  } else { camera.position.copy(tmpA); camera.quaternion.copy(qA); }
  if (camera.fov !== fov0) { camera.fov = fov0; camera.updateProjectionMatrix(); }
  U.uCam.value.copy(camera.position);
}
function flyIn(app) {
  if (state.mode !== 'room') return;
  closeCard(); state.mode = 'in'; state.flyT0 = performance.now(); state.flyFrom = state.fly; state.flyTo = 1; state.app = app;
  root.classList.add('st-flying'); document.documentElement.classList.add('st-fly'); tip.hidden = true;
}
function flyOut() {
  if (state.mode !== 'os') return;
  state.mode = 'out'; state.flyT0 = performance.now(); state.flyFrom = 1; state.flyTo = 0; lastScr = -1;
  document.documentElement.classList.remove('st-os-open');
}

// ───────────────────────── cards ─────────────────────────
function cardHTML(key) {
  const d = DATA, link = (href, text, primary) => `<a class="st-btn${primary ? ' st-btn-p' : ''}" href="${L(href)}"${href.startsWith('http') ? ' target="_blank" rel="noopener"' : ''}>${text}</a>`;
  const svc = n => d.services.find(s => s.name === n);
  const svcBlock = s => `<p>${T(s.blurb)}</p><p class="st-mono">${T(s.price)}</p><ul class="st-chips">${s.chips.map(c => `<li>${T(c)}</li>`).join('')}</ul>`;
  switch (key) {
    case 'services': return [T('Services'), `<ul class="st-list">${d.services.map(s => `<li><a href="${L(s.url)}"><b>${T(s.name)}</b><span>${T(s.price)}</span></a></li>`).join('')}</ul>`, link('/services', T('All services'), 1)];
    case 'record': return [T('Track record'), `<ul class="st-ticks">${d.facts.map(f => `<li>${T(f)}</li>`).join('')}</ul>`, link('/about', T('About me'), 1)];
    case 'about': return [T('About Anowar'), d.about.map(p => `<p>${T(p)}</p>`).join(''), link('/about', T('Read more'), 1) + link(d.call, T('Book a call'))];
    case 'process': return [T('How a project runs'), `<ol class="st-steps">${d.steps.map(s => `<li><b>${T(s.name)}</b><span>${T(s.text)}</span></li>`).join('')}</ol>`, link('/process', T('The full process'), 1)];
    case 'contact': return [T('Get in touch'), `<p>${T('A 30-minute discovery call, then a fixed quote.')} ${d.checks.map(T).join('. ')}.</p><p class="st-mono"><a href="mailto:${d.email}">${d.email}</a></p>`, link(d.call, T('Book the discovery call'), 1) + link(d.brief, T('Start a project')) + link('/contact', T('Contact page'))];
    case 'design': { const s = svc('Product design'); return [T(s.name), svcBlock(s), link(s.url, T('See product design'), 1)]; }
    case 'ai': { const s = svc('AI automation'), b = svc('AI product builds'); return [T('AI automation'), svcBlock(s) + `<p><b>${T(b.name)}.</b> ${T(b.blurb)}</p>`, link(s.url, T('See AI automation'), 1) + link(b.url, T('AI product builds'))]; }
    case 'reviews': return [T('What clients say'), d.quotes.slice(0, 3).map(q => `<blockquote><span lang="en">${q.text}</span><cite>${T(q.by)}</cite></blockquote>`).join(''), link('/work', T('See the work'), 1)];
    case 'cases': return [T('Case studies'), `<ul class="st-list">${d.cases.slice(0, 7).map(c => `<li><a href="${L(c.url)}"><b>${c.name}</b><span>${T(c.tag)}</span></a></li>`).join('')}</ul>`, link('/work', T('All work'), 1)];
    case 'pricing': return [T('Pricing'), `<ul class="st-list">${d.bands.map(b => `<li><a href="${L('/pricing')}"><b>${T(b.name)}</b><span>${T(b.price)}</span></a></li>`).join('')}</ul><p>${T('Every project is a fixed quote agreed after the discovery call.')}</p>`, link('/pricing', T('Full pricing'), 1)];
    case 'stack': return [T('Toolkit'), `<ul class="st-chips">${d.stack.map(c => `<li>${c}</li>`).join('')}</ul>`, link('/about', T('How I work'), 1)];
    case 'hours': return [T('Working hours'), `<p>${T('I work on GMT+6. Overlap with New York runs roughly 09:00&#8211;13:00 ET, and nearly the full working day overlaps with London and Berlin.')}</p><p>${T('Written updates and recorded walkthroughs keep progress moving between calls.')}</p>`, link('/process', T('How we work together'), 1)];
  }
  return null;
}
function openCard(key) {
  const c = cardHTML(key); if (!c) return;
  state.card = key; tip.hidden = true; root.classList.add('st-carded');
  cardEl.innerHTML = `<button class="st-x" aria-label="${T('Close')}">&#215;</button><span class="st-mono st-eyebrow">${T(HOT.find(h => h.key === key).what)}</span><h2>${c[0]}</h2><div class="st-body">${c[1]}</div><div class="st-actions">${c[2]}</div>`;
  cardEl.hidden = false; requestAnimationFrame(() => cardEl.classList.add('on'));
  cardEl.querySelector('.st-x').onclick = closeCard;
  const b = hotState[key].box, ctr = b.getCenter(new THREE.Vector3());
  state.focus = { pos: new THREE.Vector3(ctr.x * 0.55 - 0.18, ctr.y * 0.55 + 0.62, 1.75), look: new THREE.Vector3(ctr.x - 0.22, ctr.y, 0) }; state.focusTo = 1;
}
function closeCard() { if (!state.card) return; state.card = null; root.classList.remove('st-carded'); cardEl.classList.remove('on'); state.focusTo = 0; setTimeout(() => { if (!state.card) cardEl.hidden = true; }, 260); }

// ───────────────────────── input ─────────────────────────
const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(); let down = null;
function pick(ev) {
  const r = canvas.getBoundingClientRect(); ptr.set(((ev.clientX - r.left) / r.width) * 2 - 1, -((ev.clientY - r.top) / r.height) * 2 + 1);
  ray.setFromCamera(ptr, camera); const hit = ray.intersectObjects(hot, false)[0]; return hit ? hit.object.userData.hot : null;
}
function act(key) { if (key === 'os') flyIn(); else if (key === 'work') flyIn('work'); else if (state.card === key) closeCard(); else openCard(key); }
function bind() {
  root.addEventListener('pointermove', ev => {
    const r = root.getBoundingClientRect(); state.mx = clamp(((ev.clientX - r.left) / r.width) * 2 - 1, -1, 1); state.my = clamp(((ev.clientY - r.top) / r.height) * 2 - 1, -1, 1);
    if (state.mode !== 'room' || ev.target !== canvas) { setHover(null); return; }
    const k = pick(ev); setHover(k);
    if (k) { tip.textContent = TP(HOT.find(h => h.key === k).label); tip.style.transform = `translate(${ev.clientX - r.left + 16}px, ${ev.clientY - r.top + 18}px)`; }
  });
  root.addEventListener('pointerleave', () => { state.mx = 0; state.my = 0; setHover(null); });
  canvas.addEventListener('pointerdown', ev => { down = { x: ev.clientX, y: ev.clientY }; });
  canvas.addEventListener('pointerup', ev => {
    if (!down || Math.hypot(ev.clientX - down.x, ev.clientY - down.y) > 8 || state.mode !== 'room') return;
    const k = pick(ev); if (k) act(k); else closeCard();
  });
  addEventListener('keydown', ev => {
    if (ev.key === 'Escape') { if (state.mode === 'os') os.close(); else closeCard(); }
    if (ev.key === 'Enter' && state.mode === 'room' && document.activeElement === document.body) flyIn();
  });
  root.querySelectorAll('[data-st]').forEach(b => b.addEventListener('click', ev => { ev.preventDefault(); const a = b.dataset.st; if (a === 'enter') flyIn(); else act(a); }));
  addEventListener('resize', resize);
  new ResizeObserver(resize).observe(root);
}
function setHover(k) {
  if (state.hover === k) return; state.hover = k;
  for (const key in hotState) hotState[key].target = key === k ? 1 : 0;
  canvas.style.cursor = k ? 'pointer' : ''; tip.hidden = !k || !!state.card;
}

// ───────────────────────── frame ─────────────────────────
let scale = 1, acc = 0, frames = 0, lastT = performance.now(), t0 = performance.now(), fps = 60;
function resize() {
  const w = root.clientWidth, h = root.clientHeight; if (!w || !h) return;
  const pr = Math.min(devicePixelRatio || 1, 2) * scale;
  renderer.setPixelRatio(pr); renderer.setSize(w, h, false);
  camera.aspect = w / h; camera.updateProjectionMatrix();
  if (dust) dust.material.uniforms.uPx.value = h * pr * 0.0035;
}
function frame(now) {
  requestAnimationFrame(frame);
  const dt = Math.min(0.05, (now - lastT) / 1000); lastT = now;
  const t = FROZEN ?? (now - t0) / 1000; state.t = t;
  // fly state
  if (state.mode === 'in' || state.mode === 'out') {
    const u = clamp((now - state.flyT0) / 1000 / (reduced ? 0.01 : state.flyDur), 0, 1);
    state.fly = state.flyFrom + (state.flyTo - state.flyFrom) * u;
    if (state.mode === 'in' && u > 0.95 && !os.isOpen()) { os.open({ app: state.app }); document.documentElement.classList.add('st-os-open'); }
    if (u >= 1) { if (state.mode === 'in') state.mode = 'os'; else { state.mode = 'room'; root.classList.remove('st-flying'); document.documentElement.classList.remove('st-fly'); } }
  }
  if (state.mode === 'os' && os.isOpen() && FROZEN === null) return;      // the room is hidden behind the OS: stop drawing it
  if (document.hidden) return;
  U.uTime.value = t; U.uFade.value = FROZEN !== null ? 1 : smooth(0, 0.9, t);
  state.focusK = (state.focusK || 0) + ((state.focusTo || 0) - (state.focusK || 0)) * (1 - Math.exp(-dt * 4));
  if (state.focusK < 0.002 && !state.focusTo) state.focus = null;
  const lk = lampK(t), br = 1 + 0.025 * Math.sin(t * 0.21);
  U.uW.value.setRGB(LOOKS.W[0] * br, LOOKS.W[1] * br, LOOKS.W[2] * br); U.uP.value.setRGB(LOOKS.P[0] * lk, LOOKS.P[1] * lk, LOOKS.P[2] * lk);
  U.uEnvGain.value = 0.9 + 0.5 * lk;
  updateScreens(t); placeCamera(t, dt);
  for (const k in hotState) { const h = hotState[k]; h.hi += (h.target - h.hi) * (1 - Math.exp(-dt * 10)); for (const m of h.mats) m.uniforms.uHi.value = h.hi; }
  for (const e of emitters) {
    let g = e.base;
    if (e.kind.startsWith('glow_pc')) g *= 0.8 + 0.2 * Math.sin(t * 1.3 + (e.kind.endsWith('b') ? 2 : 0));
    else if (e.kind === 'glow_hp') g *= 0.7 + 0.3 * Math.sin(t * 0.8);
    else if (e.kind === 'sky') g *= br;
    if (e.kind.startsWith('glow_') ) g *= lk; else if (e.kind === 'laptop') g *= smooth(BOOT_AT + 0.5, BOOT_AT + 1.6, t);
    e.o.material.uniforms.uGain.value = g;
  }
  for (const g of glows) if (g.userData.lamp) g.material.uniforms.uGain.value = g.userData.gain * lk;
  if (glows.mon) for (const g of glows.mon) { g.material.uniforms.uGain.value = 0.16 * U.uMonOn.value; g.material.uniforms.uColor.value.copy(U.uMon.value).multiplyScalar(0.7); }
  renderer.render(scene, camera);
  // adaptive resolution
  acc += dt; frames++;
  if (acc >= 1) {
    fps = frames / acc; acc = 0; frames = 0; root.dataset.fps = fps.toFixed(0);
    if (FROZEN === null) { if (fps < 48 && scale > 0.6) { scale = Math.max(0.6, scale - 0.1); resize(); } else if (fps > 58 && scale < 1) { scale = Math.min(1, scale + 0.05); resize(); } }
  }
}
window.__studio = { LOOKS, U, state, get fps() { return fps; }, get scale() { return scale; }, flyIn, flyOut, openCard, closeCard, hotState, camera };
load().catch(e => { console.error(e); fallback(); });
