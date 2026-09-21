"""Animated hero graphics — a bordered 'diagram card' (dot-grid background,
corner tick marks, curved connectors from a monogram core to labelled feature
nodes) in the style of a SaaS product diagram. CSS/SVG only (no JS), the
page's own real feature words, and the same ember/ink/paper palette as the
rest of Signal DS (ember is the site's only accent). Frozen automatically by
the global prefers-reduced-motion rule in site.css."""

CENTER = {
    "home": "AH",
    "product-design": "UX",
    "webflow-development": "WF",
    "framer-development": "FR",
    "ai-product-builds": "AI",
    "services": "04",
    "work": "WK",
    "pricing": "$",
    "process": "08",
    "contact": "@",
}

TAGS = {
    "home": ["Product design", "Webflow", "Framer", "AI builds"],
    "product-design": ["User flows", "Wireframes", "Design system", "Handoff"],
    "webflow-development": ["CMS setup", "Interactions", "QA & testing", "Launch"],
    "framer-development": ["Landing pages", "Animation", "Framer CMS", "Performance"],
    "ai-product-builds": ["Redesign", "Component system", "Accessibility", "Ship"],
    "services": ["Product design", "Webflow", "Framer", "AI builds"],
    "work": ["Enterprise", "Edtech", "Medtech", "Cybersecurity"],
    "pricing": ["Landing page", "Marketing site", "Product design", "AI build"],
    "process": ["Discovery", "UX planning", "Development", "Launch"],
    "contact": ["24h reply", "New York", "London", "Berlin"],
}

CAPTION = {
    "home": "One operator &#183; 4&#8211;6 weeks",
    "product-design": "Figma &#8594; developer handoff",
    "webflow-development": "A CMS your team can run",
    "framer-development": "Live in 1&#8211;2 weeks",
    "ai-product-builds": "Prototype &#8594; production",
    "services": "Four ways to work together",
    "work": "Eight builds, shipped live",
    "pricing": "Fixed quotes, no hourly meters",
    "process": "Same eight steps, every project",
    "contact": "Replies within 24 hours",
}

# node positions as % of the card, and the matching SVG points (0-320 x 0-256)
# for the connector curves drawn between each node and the center.
NODES = [("tl", 14, 20), ("tr", 86, 20), ("bl", 14, 80), ("br", 86, 80)]
CENTER_PT = (160, 128)
SVG_PT = {"tl": (46, 51), "tr": (274, 51), "bl": (46, 205), "br": (274, 205)}

def _connector(key, i):
    x, y = SVG_PT[key]
    cx, cy = CENTER_PT
    midy = (y + cy) / 2
    path_id = f"hgpath-{i}"
    return (f'<path id="{path_id}" d="M{x} {y} C {x} {midy}, {cx} {midy}, {cx} {cy}" '
            f'class="hg-connector"/>')

def hero_graphic(key):
    corners = "".join(f'<span class="hg-corner hg-corner-{c}"></span>' for c in
                       ("tl", "tr", "bl", "br"))
    svg_paths = "".join(_connector(pos, i) for i, (pos, *_r) in enumerate(NODES))
    nodes = "".join(
        f'''<div class="hg-node" style="left:{x}%;top:{y}%">
      <span class="hg-node-dot" aria-hidden="true"></span><span class="hg-node-label">{t}</span>
    </div>'''
        for (pos, x, y), t in zip(NODES, TAGS[key])
    )
    return f'''<div class="hg-wrap" aria-hidden="true" data-reveal>
  <div class="hero-graphic">
    {corners}
    <svg class="hg-svg" viewBox="0 0 320 256" preserveAspectRatio="none" aria-hidden="true">{svg_paths}</svg>
    {nodes}
    <div class="hg-center"><span>{CENTER[key]}</span></div>
  </div>
  <div class="hg-caption mono">{CAPTION[key]}</div>
</div>'''
