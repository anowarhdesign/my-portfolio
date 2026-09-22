"""Hero visuals — one abstract, text-free composition per page, each built
from shapes that nod at what that page is actually about (a wireframe canvas
for product design, a browser/CMS rows for Webflow, a motion streak for
Framer, a rough-to-clean shape for AI builds, a fanned card stack for work,
a price tag for pricing, a step path for process, a speech bubble for
contact). Same ember/ink/paper palette throughout — ember is the site's only
accent. CSS/SVG only, frozen automatically by the global
prefers-reduced-motion rule in site.css. Canvas is a tall 2:3 portrait
(viewBox 0 0 400 600) since the panel runs the full viewport height.

Each composition is assembled from top-level "pieces" (_piece()) that
animate in with a staggered delay once the panel scrolls into view — never
by putting a CSS transform on an element that already carries its own
static SVG transform= attribute (that combination silently breaks matrix
interpolation; every piece here gets a fresh wrapping <g> instead, so the
hand-set rotate/translate on the shape inside is never touched)."""

def _piece(inner):
    return f'<g class="hv-piece">{inner}</g>'

def _assemble(*chunks):
    return "".join(_piece(c) for c in chunks)

def _defs(uid, extra=""):
    return f'''<defs>
      <linearGradient id="{uid}-ring" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="var(--ember-lift)"/>
        <stop offset="1" stop-color="var(--ember-deep)"/>
      </linearGradient>
      <radialGradient id="{uid}-sphere" cx="35%" cy="30%" r="75%">
        <stop offset="0" stop-color="#FFF6EE"/>
        <stop offset=".45" stop-color="var(--ember-lift)"/>
        <stop offset="1" stop-color="var(--ember-deep)"/>
      </radialGradient>
      <linearGradient id="{uid}-glass" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="var(--card)"/>
        <stop offset=".5" stop-color="var(--paper-2)"/>
        <stop offset="1" stop-color="var(--card)"/>
      </linearGradient>
      <linearGradient id="{uid}-soft" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="var(--ember-soft)"/>
        <stop offset="1" stop-color="rgba(241,78,28,.22)"/>
      </linearGradient>
      {extra}
      <filter id="{uid}-shadow" x="-60%" y="-60%" width="220%" height="220%">
        <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#0E0D0C" flood-opacity=".18"/>
      </filter>
    </defs>'''

def _wrap(uid, defs, body):
    return f'''<div class="hero-visual" aria-hidden="true" data-reveal>
  <svg viewBox="0 0 400 600" class="hv-svg" preserveAspectRatio="xMidYMid slice">
    {defs}
    <g class="hv-float">{body}</g>
  </svg>
</div>'''

# ─────────────────────── home: the flagship cluster ───────────────────────
def _home(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="430" rx="140" ry="18"/>'
    cluster = f'''<g filter="url(#{uid}-shadow)">
        <circle cx="150" cy="220" r="58" fill="none" stroke="url(#{uid}-ring)" stroke-width="23"/>
        <circle cx="288" cy="180" r="48" fill="url(#{uid}-sphere)"/>
        <rect x="205" y="240" width="42" height="126" rx="21" fill="url(#{uid}-glass)"
          stroke="var(--line-2)" transform="rotate(-18 226 303)"/>
        <polygon fill="url(#{uid}-soft)" stroke="var(--ember)" stroke-width="1.2"
          transform="translate(100 360) rotate(10)" points="32,0 60,16 60,48 32,64 4,48 4,16"/>
        <path d="M 260 370 A 44 44 0 1 1 256 414" fill="none" stroke="var(--ember-deep)"
          stroke-width="13" stroke-linecap="round"/>
      </g>'''
    dot1 = '<circle cx="90" cy="120" r="4" fill="var(--ember)"/>'
    dot2 = '<circle cx="335" cy="100" r="3" fill="var(--ember)"/>'
    dot3 = '<circle cx="350" cy="300" r="5" fill="var(--ember)"/>'
    return _wrap(uid, defs, _assemble(floor, cluster, dot1, dot2, dot3))

# ───────────────────── services: four disciplines, stacked ─────────────────────
def _services(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="560" rx="120" ry="14"/>'
    stack = f'''<g filter="url(#{uid}-shadow)">
        <rect x="120" y="70" width="160" height="106" rx="18" fill="url(#{uid}-glass)" stroke="var(--line-2)"/>
        <rect x="146" y="96" width="60" height="10" rx="5" fill="var(--ember-soft)"/>
        <rect x="146" y="116" width="90" height="8" rx="4" fill="var(--line-2)"/>
        <rect x="130" y="210" width="140" height="96" rx="48" fill="none" stroke="url(#{uid}-ring)" stroke-width="16"/>
        <circle cx="200" cy="258" r="14" fill="var(--ember-lift)"/>
        <path d="M120 400 L200 372 L280 400 L280 430 L200 402 L120 430 Z" fill="url(#{uid}-soft)" stroke="var(--ember)" stroke-width="1.2"/>
        <circle cx="200" cy="500" r="46" fill="url(#{uid}-sphere)"/>
        <path d="M182 500 l12 12 24 -24" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
      </g>'''
    dot1 = '<circle cx="100" cy="150" r="3" fill="var(--ember)"/>'
    dot2 = '<circle cx="310" cy="440" r="4" fill="var(--ember)"/>'
    return _wrap(uid, defs, _assemble(floor, stack, dot1, dot2))

# ───────────────── product design: canvas, layout blocks, cursor ─────────────────
def _product_design(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="520" rx="130" ry="16"/>'
    canvas = f'''<g filter="url(#{uid}-shadow)">
        <rect x="90" y="130" width="220" height="300" rx="16" fill="url(#{uid}-glass)" stroke="var(--line-2)" stroke-width="1.5"/>
        <rect x="116" y="160" width="90" height="14" rx="7" fill="var(--ember-soft)"/>
        <rect x="116" y="188" width="150" height="60" rx="8" fill="var(--paper-2)" stroke="var(--line-2)"/>
        <rect x="116" y="264" width="68" height="68" rx="8" fill="var(--ember-soft)"/>
        <rect x="196" y="264" width="68" height="68" rx="8" fill="var(--paper-2)" stroke="var(--line-2)"/>
        <rect x="116" y="346" width="148" height="12" rx="6" fill="var(--line-2)"/>
        <rect x="116" y="368" width="100" height="12" rx="6" fill="var(--line-2)"/>
        <circle cx="120" cy="120" r="10" fill="url(#{uid}-ring)" opacity=".9"/>
        <circle cx="150" cy="120" r="10" fill="var(--ember-lift)" opacity=".65"/>
        <circle cx="180" cy="120" r="10" fill="var(--ember-deep)" opacity=".45"/>
      </g>'''
    # the cursor lands last, as if clicking to confirm the layout just built
    cursor = f'''<g filter="url(#{uid}-shadow)" transform="translate(272 372) rotate(-14)">
        <path d="M0 0 L0 46 L12 34 L22 56 L32 51 L22 29 L38 29 Z" fill="var(--ink)"/>
      </g>'''
    dot1 = '<circle cx="336" cy="150" r="4" fill="var(--ember)"/>'
    dot2 = '<circle cx="80" cy="440" r="3" fill="var(--ember)"/>'
    return _wrap(uid, defs, _assemble(floor, canvas, cursor, dot1, dot2))

# ───────────────── webflow: browser chrome + structured CMS rows ─────────────────
def _webflow(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="500" rx="130" ry="16"/>'
    browser = f'''<g filter="url(#{uid}-shadow)">
        <rect x="80" y="120" width="240" height="290" rx="16" fill="url(#{uid}-glass)" stroke="var(--line-2)" stroke-width="1.5"/>
        <rect x="80" y="120" width="240" height="38" rx="16" fill="var(--paper-2)"/>
        <circle cx="104" cy="139" r="6" fill="var(--ember)"/>
        <circle cx="124" cy="139" r="6" fill="var(--ember-lift)"/>
        <circle cx="144" cy="139" r="6" fill="var(--line-2)"/>
        <rect x="104" y="184" width="192" height="46" rx="10" fill="var(--ember-soft)" stroke="var(--ember)" stroke-width="1"/>
        <rect x="104" y="242" width="192" height="46" rx="10" fill="var(--paper-2)" stroke="var(--line-2)"/>
        <rect x="104" y="300" width="192" height="46" rx="10" fill="var(--paper-2)" stroke="var(--line-2)"/>
        <rect x="104" y="358" width="192" height="34" rx="10" fill="var(--paper-2)" stroke="var(--line-2)" stroke-dasharray="4 4"/>
      </g>'''
    cms_ball = f'<circle cx="330" cy="440" r="30" fill="url(#{uid}-sphere)" filter="url(#{uid}-shadow)"/>'
    dot1 = '<circle cx="60" cy="200" r="4" fill="var(--ember)"/>'
    dot2 = '<circle cx="340" cy="150" r="3" fill="var(--ember)"/>'
    return _wrap(uid, defs, _assemble(floor, browser, cms_ball, dot1, dot2))

# ───────────────── framer: motion streaks + launch chevron ─────────────────
def _framer(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="500" rx="130" ry="16"/>'
    streaks = f'''<g filter="url(#{uid}-shadow)">
        <path d="M110 420 L190 130" stroke="var(--line-2)" stroke-width="10" stroke-linecap="round" opacity=".5"/>
        <path d="M160 420 L240 160" stroke="var(--ember-soft)" stroke-width="14" stroke-linecap="round"/>
        <path d="M220 420 L300 200" stroke="url(#{uid}-ring)" stroke-width="20" stroke-linecap="round"/>
        <polygon points="180,220 180,300 250,260" fill="url(#{uid}-sphere)"/>
      </g>'''
    chevron = f'''<g filter="url(#{uid}-shadow)" transform="translate(120 360)">
        <path d="M0 40 L34 0 L34 24 L68 24 L68 56 L34 56 L34 80 Z" fill="var(--ink)" opacity=".9"/>
      </g>'''
    dot1 = '<circle cx="90" cy="150" r="4" fill="var(--ember)"/>'
    dot2 = '<circle cx="330" cy="440" r="3" fill="var(--ember)"/>'
    dot3 = '<circle cx="310" cy="120" r="5" fill="var(--ember-lift)"/>'
    return _wrap(uid, defs, _assemble(floor, streaks, chevron, dot1, dot2, dot3))

# ───────────────── ai product builds: rough shape → clean shape ─────────────────
def _ai_builds(uid):
    defs = _defs(uid, extra=f'''<filter id="{uid}-rough">
        <feTurbulence type="fractalNoise" baseFrequency=".045" numOctaves="2" seed="4" result="n"/>
        <feDisplacementMap in="SourceGraphic" in2="n" scale="14"/>
      </filter>''')
    floor = '<ellipse class="hv-floor" cx="200" cy="500" rx="130" ry="16"/>'
    # the rough prototype lands first, the polished card lands after —
    # the reveal order itself acts out "AI got you 70%, the rest is the job"
    rough = f'''<g filter="url(#{uid}-shadow)">
        <rect x="90" y="160" width="120" height="120" rx="10" fill="var(--paper-2)" stroke="var(--ash-2)"
          stroke-width="2" filter="url(#{uid}-rough)"/>
        <path d="M226 220 L268 220 M256 206 L270 220 L256 234" fill="none" stroke="var(--ember)"
          stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
      </g>'''
    clean = f'''<g filter="url(#{uid}-shadow)">
        <rect x="196" y="280" width="140" height="140" rx="26" fill="url(#{uid}-glass)" stroke="var(--line-2)"/>
        <rect x="220" y="316" width="92" height="12" rx="6" fill="var(--ember-soft)"/>
        <rect x="220" y="340" width="70" height="10" rx="5" fill="var(--line-2)"/>
        <rect x="220" y="362" width="92" height="34" rx="8" fill="var(--paper-2)" stroke="var(--line-2)"/>
      </g>'''
    spark1 = '<path d="M110 130 l6 16 16 6 -16 6 -6 16 -6 -16 -16 -6 16 -6 Z" fill="var(--ember-lift)"/>'
    spark2 = '<path d="M330 460 l4 10 10 4 -10 4 -4 10 -4 -10 -10 -4 10 -4 Z" fill="var(--ember)"/>'
    dot = '<circle cx="80" cy="440" r="3" fill="var(--ember)"/>'
    return _wrap(uid, defs, _assemble(floor, rough, clean, spark1, spark2, dot))

# ───────────────── work: fanned stack of project cards ─────────────────
def _work(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="520" rx="140" ry="16"/>'
    # the stack deals in one card at a time, back to front
    card_back = f'''<g filter="url(#{uid}-shadow)">
        <rect x="110" y="180" width="150" height="200" rx="14" fill="var(--paper-2)" stroke="var(--line-2)"
          transform="rotate(-16 185 280)"/>
      </g>'''
    card_mid = f'''<g filter="url(#{uid}-shadow)">
        <rect x="125" y="170" width="150" height="200" rx="14" fill="url(#{uid}-glass)" stroke="var(--line-2)"
          transform="rotate(-5 200 270)"/>
      </g>'''
    card_front = f'''<g filter="url(#{uid}-shadow)">
        <rect x="140" y="160" width="150" height="200" rx="14" fill="url(#{uid}-soft)" stroke="var(--ember)"
          transform="rotate(7 215 260)"/>
        <rect x="160" y="205" width="90" height="10" rx="5" fill="var(--ember-deep)" opacity=".7"
          transform="rotate(7 215 260)"/>
        <rect x="160" y="225" width="60" height="8" rx="4" fill="var(--ember-deep)" opacity=".45"
          transform="rotate(7 215 260)"/>
      </g>'''
    dot1 = '<circle cx="90" cy="140" r="4" fill="var(--ember)"/>'
    dot2 = '<circle cx="330" cy="440" r="3" fill="var(--ember)"/>'
    dot3 = '<circle cx="70" cy="440" r="3" fill="var(--ember-lift)"/>'
    return _wrap(uid, defs, _assemble(floor, card_back, card_mid, card_front, dot1, dot2, dot3))

# ───────────────── pricing: price tag + stacked coins ─────────────────
def _pricing(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="500" rx="130" ry="16"/>'
    tag = f'''<g filter="url(#{uid}-shadow)" transform="rotate(-8 200 250)">
        <path d="M120 160 L240 160 L310 230 L240 300 L120 300 Z" fill="url(#{uid}-glass)" stroke="var(--line-2)" stroke-width="1.5"/>
        <circle cx="150" cy="230" r="12" fill="var(--paper)" stroke="var(--line-2)"/>
      </g>'''
    coins = f'''<g filter="url(#{uid}-shadow)">
        <circle cx="160" cy="400" r="42" fill="url(#{uid}-sphere)"/>
        <circle cx="220" cy="420" r="34" fill="var(--ember-lift)" opacity=".85"/>
        <circle cx="180" cy="450" r="26" fill="var(--ember-deep)" opacity=".7"/>
      </g>'''
    dot1 = '<circle cx="90" cy="150" r="4" fill="var(--ember)"/>'
    dot2 = '<circle cx="330" cy="180" r="3" fill="var(--ember)"/>'
    return _wrap(uid, defs, _assemble(floor, tag, coins, dot1, dot2))

# ───────────────── process: a winding path of steps ─────────────────
def _process(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="560" rx="120" ry="14"/>'
    path = '''<path d="M120 500 C120 440 260 440 260 380 C260 320 120 320 120 260 C120 200 260 200 260 140"
        fill="none" stroke="var(--line-2)" stroke-width="4" stroke-dasharray="2 10" stroke-linecap="round"/>'''
    # the four stops land one after another, in walking order — step 1,
    # step 2, step 3, step 4 — same idea as the "same eight steps" copy
    step1 = f'<g filter="url(#{uid}-shadow)"><circle cx="120" cy="500" r="20" fill="var(--paper-2)" stroke="var(--line-2)" stroke-width="1.5"/></g>'
    step2 = f'<g filter="url(#{uid}-shadow)"><circle cx="260" cy="380" r="22" fill="url(#{uid}-glass)" stroke="var(--line-2)" stroke-width="1.5"/></g>'
    step3 = f'<g filter="url(#{uid}-shadow)"><circle cx="120" cy="260" r="24" fill="url(#{uid}-soft)" stroke="var(--ember)" stroke-width="1.5"/></g>'
    step4 = f'<g filter="url(#{uid}-shadow)"><circle cx="260" cy="140" r="30" fill="url(#{uid}-sphere)"/></g>'
    dot1 = '<circle cx="90" cy="440" r="3" fill="var(--ember)"/>'
    dot2 = '<circle cx="320" cy="240" r="4" fill="var(--ember)"/>'
    return _wrap(uid, defs, _assemble(floor, path, step1, step2, step3, step4, dot1, dot2))

# ───────────────── contact: speech bubble + broadcast rings ─────────────────
def _contact(uid):
    defs = _defs(uid)
    floor = '<ellipse class="hv-floor" cx="200" cy="500" rx="130" ry="16"/>'
    # rings ping outward first, then the message lands, then it sends —
    # a small "reaching out" sequence
    ring1 = '<circle cx="200" cy="230" r="70" fill="none" stroke="var(--ember)" stroke-width="1.5" opacity=".35"/>'
    ring2 = '<circle cx="200" cy="230" r="100" fill="none" stroke="var(--ember)" stroke-width="1.5" opacity=".2"/>'
    bubble = f'''<g filter="url(#{uid}-shadow)">
        <path d="M110 170 h180 a20 20 0 0 1 20 20 v90 a20 20 0 0 1 -20 20 h-110 l-40 36 v-36 h-30
          a20 20 0 0 1 -20 -20 v-90 a20 20 0 0 1 20 -20 Z" fill="url(#{uid}-glass)" stroke="var(--line-2)"/>
        <circle cx="150" cy="240" r="8" fill="var(--ember)"/>
        <circle cx="190" cy="240" r="8" fill="var(--ember-lift)"/>
        <circle cx="230" cy="240" r="8" fill="var(--ember-deep)"/>
      </g>'''
    arrow = f'''<g filter="url(#{uid}-shadow)" transform="translate(150 400) rotate(-20)">
        <path d="M0 30 L110 0 L70 30 L110 60 Z" fill="var(--ink)" opacity=".9"/>
      </g>'''
    dot1 = '<circle cx="330" cy="440" r="4" fill="var(--ember)"/>'
    dot2 = '<circle cx="70" cy="150" r="3" fill="var(--ember)"/>'
    return _wrap(uid, defs, _assemble(floor, ring1, ring2, bubble, arrow, dot1, dot2))

_BUILDERS = {
    "home": _home,
    "services": _services,
    "product-design": _product_design,
    "webflow-development": _webflow,
    "framer-development": _framer,
    "ai-product-builds": _ai_builds,
    "work": _work,
    "pricing": _pricing,
    "process": _process,
    "contact": _contact,
}

def hero_visual(key):
    builder = _BUILDERS.get(key, _home)
    uid = f"hv-{key}".replace(" ", "")
    return builder(uid)
