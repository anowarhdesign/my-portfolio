"""Hero visuals — abstract floating glass-like objects (ring, sphere, capsule,
hexagon, ribbon arc), no text or data of any kind. Pure decoration, in the
site's own ember/ink/paper palette so it reads as one brand rather than a
random stock-illustration style. CSS/SVG only, frozen automatically by the
global prefers-reduced-motion rule in site.css."""

# each page gets a different rotation/shape-swap so the composition varies
# without needing a bespoke illustration per page.
SEEDS = {
    "home": 0,
    "services": 1,
    "product-design": 2,
    "webflow-development": 3,
    "framer-development": 4,
    "ai-product-builds": 0,
    "work": 1,
    "pricing": 2,
    "process": 3,
    "contact": 4,
}

# five fixed compositions (not random — deterministic per seed so a rebuild
# always looks the same): rotation of the whole cluster, and which shape
# variant (of two) fills the "capsule" and "hex" slots.
_COMPOSITIONS = [
    {"tilt": -4, "capsule": "a", "hex": "a"},
    {"tilt": 6, "capsule": "b", "hex": "a"},
    {"tilt": -8, "capsule": "a", "hex": "b"},
    {"tilt": 10, "capsule": "b", "hex": "b"},
    {"tilt": -6, "capsule": "a", "hex": "a"},
]

def hero_visual(key):
    seed = SEEDS.get(key, 0)
    c = _COMPOSITIONS[seed % len(_COMPOSITIONS)]
    tilt = c["tilt"]
    capsule_rot = -18 if c["capsule"] == "a" else 14
    hex_rot = 12 if c["hex"] == "a" else -20
    uid = f"hv{seed}"

    return f'''<div class="hero-visual" aria-hidden="true" data-reveal>
  <svg viewBox="0 0 400 340" class="hv-svg">
    <defs>
      <linearGradient id="{uid}-ring" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="var(--ember-lift)"/>
        <stop offset="1" stop-color="var(--ember-deep)"/>
      </linearGradient>
      <radialGradient id="{uid}-sphere" cx="35%" cy="30%" r="75%">
        <stop offset="0" stop-color="#FFF6EE"/>
        <stop offset=".45" stop-color="var(--ember-lift)"/>
        <stop offset="1" stop-color="var(--ember-deep)"/>
      </radialGradient>
      <linearGradient id="{uid}-capsule" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="var(--card)"/>
        <stop offset=".5" stop-color="var(--paper-2)"/>
        <stop offset="1" stop-color="var(--card)"/>
      </linearGradient>
      <linearGradient id="{uid}-hex" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="var(--ember-soft)"/>
        <stop offset="1" stop-color="rgba(241,78,28,.22)"/>
      </linearGradient>
      <filter id="{uid}-shadow" x="-60%" y="-60%" width="220%" height="220%">
        <feDropShadow dx="0" dy="10" stdDeviation="10" flood-color="#0E0D0C" flood-opacity=".18"/>
      </filter>
    </defs>

    <ellipse class="hv-floor" cx="204" cy="294" rx="132" ry="16"/>

    <g transform="rotate({tilt} 200 170)">
      <g class="hv-float">
        <g filter="url(#{uid}-shadow)">
          <circle class="hv-ring" cx="138" cy="146" r="52" fill="none" stroke="url(#{uid}-ring)" stroke-width="21"/>
          <circle class="hv-sphere" cx="272" cy="118" r="44" fill="url(#{uid}-sphere)"/>
          <rect class="hv-capsule" x="197" y="150" width="40" height="118" rx="20"
            fill="url(#{uid}-capsule)" stroke="var(--line-2)" stroke-width="1"
            transform="rotate({capsule_rot} 217 209)"/>
          <polygon class="hv-hex" fill="url(#{uid}-hex)" stroke="var(--ember)" stroke-width="1.2"
            transform="translate(96 244) rotate({hex_rot})"
            points="30,0 56,15 56,45 30,60 4,45 4,15"/>
          <path class="hv-arc" d="M 300 230 A 42 42 0 1 1 296 272" fill="none"
            stroke="var(--ember-deep)" stroke-width="12" stroke-linecap="round"/>
        </g>
        <circle class="hv-dot hv-dot-1" cx="80" cy="90" r="4" fill="var(--ember)"/>
        <circle class="hv-dot hv-dot-2" cx="330" cy="70" r="3" fill="var(--ember)"/>
        <circle class="hv-dot hv-dot-3" cx="350" cy="200" r="5" fill="var(--ember)"/>
      </g>
    </g>
  </svg>
</div>'''
