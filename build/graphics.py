"""Animated hero graphics — a 'signal ring' motif: a monogram core with the page's
own real feature words orbiting it. CSS-only (no JS), same ember/ink/paper palette
as the rest of Signal DS, and frozen automatically by the global
prefers-reduced-motion rule in site.css."""

CENTER = {
    "home": "AH",
    "product-design": "UX",
    "webflow-development": "WF",
    "framer-development": "FR",
    "ai-product-builds": "AI",
}

TAGS = {
    "home": ["Product design", "Webflow", "Framer", "AI builds"],
    "product-design": ["User flows", "Wireframes", "Design system", "Handoff"],
    "webflow-development": ["CMS setup", "Interactions", "QA & testing", "Launch"],
    "framer-development": ["Landing pages", "Animation", "Framer CMS", "Performance"],
    "ai-product-builds": ["Redesign", "Component system", "Accessibility", "Ship"],
}

CAPTION = {
    "home": "One operator &#183; 4&#8211;6 weeks",
    "product-design": "Figma &#8594; developer handoff",
    "webflow-development": "A CMS your team can run",
    "framer-development": "Live in 1&#8211;2 weeks",
    "ai-product-builds": "Prototype &#8594; production",
}

ANGLES = [0, 90, 180, 270]

def hero_graphic(key):
    # .hg-slot carries the per-tag static angle (position on the ring); .hg-unrotate
    # immediately cancels that same static angle so descendants start upright, then
    # .hg-counter cancels the ring's *live* spin. Mixing a static and an animated
    # transform on one element breaks CSS's matrix interpolation, so each stays separate.
    slots = "".join(
        f'''<div class="hg-slot" style="transform:rotate({a}deg) translateY(calc(-1 * var(--hg-r)))">
      <div class="hg-unrotate" style="transform:rotate({-a}deg)">
        <div class="hg-center"><div class="hg-counter"><span class="hg-tag"><i></i>{t}</span></div></div>
      </div>
    </div>'''
        for a, t in zip(ANGLES, TAGS[key])
    )
    return f'''<div class="hg-wrap" aria-hidden="true" data-reveal>
  <div class="hero-graphic">
    <div class="hg-ring hg-ring-1"></div>
    <div class="hg-ring hg-ring-2"></div>
    <div class="hg-ring hg-ring-3"></div>
    <div class="hg-orbit-track"></div>
    <div class="hg-orbit">{slots}</div>
    <div class="hg-core"><span>{CENTER[key]}</span></div>
  </div>
  <div class="hg-caption mono">{CAPTION[key]}</div>
</div>'''
