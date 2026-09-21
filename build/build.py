#!/usr/bin/env python3
"""Static page builder for anowarhdesign.com — shared shell + per-page content."""
import json, os, pathlib
from avatar import wordmark, AVATAR_CSS

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://anowarhdesign.com"

NAV = [("Services", "/services"), ("Work", "/work"), ("Pricing", "/pricing"),
       ("Process", "/process"), ("About", "/about")]

PERSON = {
    "@type": "Person", "@id": SITE + "/#person", "name": "Anowar Hossain",
    "alternateName": "Md Anowar Hossain", "url": SITE + "/",
    "image": SITE + "/uploads/avatar.jpg",
    "jobTitle": "UI/UX Designer & Webflow / Framer Developer",
    "email": "mailto:hello@anowarhdesign.com",
    "address": {"@type": "PostalAddress", "addressCountry": "BD"},
    "areaServed": [{"@type": "Country", "name": n} for n in
                   ["United States", "United Kingdom", "Canada", "Australia", "Germany", "Netherlands"]],
    "knowsLanguage": ["en", "bn"],
    "knowsAbout": ["UI/UX Design", "Webflow Development", "Framer Development", "Figma",
                   "Design Systems", "Landing Page Design", "AI product design"],
    "sameAs": ["https://www.linkedin.com/in/anowarhdesign/", "https://dribbble.com/anowarhdesign",
               "https://x.com/anowarhdesign"],
}

def breadcrumbs(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + url}
        for i, (name, url) in enumerate(trail)]}

def faq_schema(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

def faq_html(items):
    out = ['<div class="faq" data-reveal>']
    for q, a in items:
        out.append(f'<details><summary>{q}<span class="pm" aria-hidden="true"></span></summary><div class="a">{a}</div></details>')
    out.append('</div>')
    return "\n".join(out)

def nav(current):
    cur = ' aria-current="page"'
    links = "".join(
        '<a href="%s"%s>%s</a>' % (u, cur if u == current else "", n) for n, u in NAV)
    return f'''<header class="nav">
  <div class="nav-in">
    {wordmark()}
    <nav class="navlinks" aria-label="Primary">{links}</nav>
    <div style="display:flex;gap:10px;align-items:center">
      <button class="navtoggle" type="button" aria-expanded="false" aria-label="Open menu">Menu</button>
      <a class="btn btn-ink btn-sm" href="/contact">Book a call</a>
    </div>
  </div>
</header>'''

FOOT_TPL = '''<footer class="foot">
  <div class="wrap">
    <div class="foot-grid">
      <div>
        __FOOTMARK__
        <p class="lead" style="margin-top:14px;max-width:34ch">UI/UX design and Webflow &amp; Framer
          development for teams in the US, UK and Europe. One operator, no handoffs.</p>
      </div>
      <div><h3>Services</h3><ul>
        <li><a href="/services/product-design">Product design</a></li>
        <li><a href="/services/webflow-development">Webflow development</a></li>
        <li><a href="/services/framer-development">Framer development</a></li>
        <li><a href="/services/ai-product-builds">AI product builds</a></li>
      </ul></div>
      <div><h3>Company</h3><ul>
        <li><a href="/work">Work</a></li>
        <li><a href="/pricing">Pricing</a></li>
        <li><a href="/process">Process</a></li>
        <li><a href="/about">About</a></li>
        <li><a href="/contact">Contact</a></li>
      </ul></div>
      <div><h3>Elsewhere</h3><ul>
        <li><a href="https://www.linkedin.com/in/anowarhdesign/" rel="noopener" target="_blank">LinkedIn</a></li>
        <li><a href="https://dribbble.com/anowarhdesign" rel="noopener" target="_blank">Dribbble</a></li>
        <li><a href="https://x.com/anowarhdesign" rel="noopener" target="_blank">X</a></li>
        <li><a href="mailto:hello@anowarhdesign.com">hello@anowarhdesign.com</a></li>
      </ul></div>
    </div>
    <div class="foot-base mono">
      <span>&#169; <span id="cpyear">2026</span> Anowar Hossain</span>
      <span>Dhaka &#183; GMT+6 &#8212; <span id="clock">--:--</span> local</span>
    </div>
  </div>
</footer>'''
FOOT = FOOT_TPL.replace('__FOOTMARK__', wordmark())

BAND_CHECKS = ["Reply within 24 hours", "Fixed quote, no hourly meter", "One operator, start to finish"]

def band(title, text, cta="Book the discovery call"):
    checks = "".join(f'<li><span class="ck">&#10003;</span>{x}</li>' for x in BAND_CHECKS)
    return f'''<div class="band" data-reveal>
  <div class="band-pitch">
    <h2>{title}</h2>
    <p class="lead">{text}</p>
    <ul class="band-checks">{checks}</ul>
    <div class="band-who">
      <img src="/uploads/portrait-380.webp" width="44" height="44" alt="Anowar Hossain" loading="lazy">
      <div><strong>Anowar Hossain</strong><span>UI/UX Designer &amp; Developer</span></div>
    </div>
    <div style="display:flex;flex-direction:column;gap:12px;align-items:flex-start;margin-top:6px">
      <a class="btn btn-primary" data-magnet data-cursor="Book" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">{cta} <span class="arw">&#8594;</span></a>
      <span class="mono">Or write direct &#8212; hello@anowarhdesign.com</span>
    </div>
  </div>
  <form class="band-form" data-brief-form novalidate>
    <span class="mono">Or send a quick brief</span>
    <div class="bf-row">
      <label>Name<input type="text" name="name" autocomplete="name" required></label>
      <label>Email<input type="email" name="email" autocomplete="email" required></label>
    </div>
    <div class="bf-budget">
      <span class="bf-label">Rough budget</span>
      <div class="bf-chips" role="group" aria-label="Rough budget">
        <button type="button" data-chip aria-pressed="false">Under $2k</button>
        <button type="button" data-chip aria-pressed="false">$2k&#8211;$6k</button>
        <button type="button" data-chip aria-pressed="false">$6k+</button>
      </div>
    </div>
    <label>What are you building?<textarea name="details" rows="3" required></textarea></label>
    <button class="btn btn-ink" type="submit">Send the brief <span class="arw">&#8594;</span></button>
    <span class="mono bf-note">Opens your email app, prefilled &#8212; nothing is sent from here</span>
  </form>
</div>'''


def polish(body):
    """Post-process page markup: section indices, line-mask headlines, counters."""
    import re as _re
    # section header eyebrows get the index rule
    body = _re.sub(r'(<div class="sec-head">\s*<div>\s*)<span class="mono">',
                   r'\1<span class="mono idx">', body)
    # headlines split into masked lines
    def _lines(m):
        attrs, inner = m.group(1), m.group(2)
        parts, buf = [], inner
        buf = buf.replace('<span class="serif">', '\x00<span class="serif">')
        for chunk in buf.split('\x00'):
            for piece in chunk.split('<br>'):
                piece = piece.strip()
                if piece:
                    parts.append(f'<span class="line"><span>{piece}</span></span>')
        return f'<h1 class="lines"{attrs}>' + "".join(parts) + '</h1>'
    body = _re.sub(r'<h1([^>]*)>(.*?)</h1>', _lines, body, flags=_re.S)
    # stat numbers animate up
    def _count(m):
        raw, suf = m.group(1), m.group(2) or ""
        return (f'<div class="n" data-count="{raw.replace(",", "")}" data-suffix="{suf}">'
                f'{raw}{suf}</div>')
    body = _re.sub(r'<div class="n">([\d,]+)(%|\+)?</div>', _count, body)
    return body

def page(path, title, desc, body, schema, current="", trail=None):
    body = polish(body)
    url = SITE + ("/" if path == "index.html" else "/" + path.replace("/index.html", ""))
    graph = [PERSON] + schema
    if trail:
        graph.append(breadcrumbs(trail))
    jsonld = json.dumps({"@context": "https://schema.org", "@graph": graph}, indent=2)
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="author" content="Anowar Hossain">
<meta name="robots" content="index, follow">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#F4F1EB">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/uploads/og-cover.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Anowar Hossain — UI/UX design and Webflow / Framer development">
<meta property="og:site_name" content="Anowar Hossain">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/uploads/og-cover.jpg">
<link rel="icon" href="/uploads/favicon.ico" sizes="32x32">
<link rel="icon" type="image/svg+xml" href="/uploads/mark.svg">
<link rel="icon" type="image/png" href="/uploads/mark-64.png" sizes="64x64">
<link rel="apple-touch-icon" href="/uploads/mark-180.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">
{jsonld}
</script>
</head>
<body>
<a class="skip" href="#top">Skip to content</a>
<div class="grain" aria-hidden="true"></div>
<div class="cursor" aria-hidden="true"><span class="lbl"></span></div>
<div class="cursor-dot" aria-hidden="true"></div>
<div class="progress" aria-hidden="true"><i></i></div>
<div id="peek" aria-hidden="true"><img class="shot" alt="" width="900" height="600"><span class="name"></span><div class="inner"><span class="bar"><i></i><i></i><i></i></span><span class="host"></span></div></div>
{nav(current)}
<main id="top">
{body}
</main>
{FOOT}
<nav class="dock" aria-label="Quick links">
  <a href="/services">Services</a><a href="/work">Work</a><a href="/pricing">Pricing</a>
  <a href="/about">About</a>
  <a class="cta" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book a call</a>
</nav>
<script>window.va = window.va || function () {{ (window.vaq = window.vaq || []).push(arguments); }};</script>
<script defer src="/_vercel/insights/script.js"></script>
<script>window.si = window.si || function () {{ (window.siq = window.siq || []).push(arguments); }};</script>
<script defer src="/_vercel/speed-insights/script.js"></script>
<script defer src="/assets/site.js"></script>
</body>
</html>
'''
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    return url

# ─────────────────────────── shared blocks ───────────────────────────

BADGE = '''<div class="badge" data-reveal>
  <span class="uw" aria-hidden="true">U</span>
  <span style="font-weight:500">Top Rated on Upwork</span>
  <span class="div" aria-hidden="true"></span>
  <span style="color:var(--ash)">100% job success &#183; 2,237 hours</span>
</div>'''

NAMES = ["CADDi", "Assistments", "Stratus Neuro", "SecureCDP", "UberStrategist", "Fit3D",
         "UserVoice", "Spoiler Alert", "0xBow", "Gym Insight"]
_run = "".join(f"<span>{n}</span>" for n in NAMES)
LOGOWALL = f'''<div style="display:flex;flex-direction:column;gap:6px" data-reveal>
  <span class="mono">Shipped for teams at</span>
  <div class="marquee"><div class="marquee-track">{_run}{_run}</div></div>
</div>'''

QUOTES = {
 "framer": ("He knows Framer inside and out. Frankly, I think he should charge more.",
            "Upwork review &#183; Framer template &amp; CMS customization &#183; Nov 2025"),
 "webflow": ("I asked him not just to do a task in Webflow, but to teach me how I could do it. He trained me as we accomplished the task. He is patient, articulate, and has a deep understanding of the platform.",
             "Upwork review &#183; Webflow build &amp; training &#183; Sep 2025"),
 "design": ("Anowar is the happiest, nicest, most responsive designer I&#8217;ve ever worked with. He&#8217;s a fast worker, on time, and truly a blessing.",
            "Upwork review &#183; Figma UI/UX design &#183; 85 hours"),
 "rigor": ("He demonstrated great professionalism, excellent communication, and impeccable technical rigor. The work was delivered on time, well-structured, and with genuine attention to detail.",
           "Upwork review &#183; Framer responsive bug fix &#183; Jul 2025"),
 "startup": ("He gave good insight and feedback from a user perspective which is valuable for a product. He is a great fit to work in a startup environment.",
             "Upwork review &#183; Framer website design &amp; support"),
 "english": ("His communication in English is flawless, which made the whole process smooth and efficient. He was always responsive and made sure all my requirements were met with precision.",
             "Upwork review &#183; Website to Framer &#183; 2024"),
 "listen": ("He truly listened to my needs, wants and ideas for the project. He was able to take all of my feedback and craft a beautiful design.",
            "Upwork review &#183; Click to Convert widget &#183; 42 hours"),
 "teach": ("Extremely professional, patient, and polite. He not only delivered an incredible job that went beyond my expectations but also took the time to teach me how Framer works.",
           "Upwork review &#183; Framer portfolio design &#183; Sep 2025"),
}

def quote(key, extra=""):
    q, att = QUOTES[key]
    return f'<figure class="quote" data-reveal{extra}><q>{q}</q><figcaption class="att">{att}</figcaption></figure>'

TZ = '''<div class="wrap"><div class="tzbar mono">
  <span>Dhaka &#183; GMT+6 &#8212; overlaps New York mornings &amp; London afternoons</span>
  <span style="color:var(--ink)">Replies within 24 hours</span>
</div></div>'''

CASES = [
 ("CADDi", "us.caddi.com", "Webflow &#183; Enterprise", "linear-gradient(140deg,#16150F 0%,#3A1D10 100%)",
  "#FFB48F", "US market entry for a manufacturing intelligence platform &#8212; dense technical content made legible."),
 ("Assistments", "assistments.org", "Webflow &#183; Edtech", "linear-gradient(140deg,#10161A 0%,#12303A 100%)",
  "#8FD8E8", "Nonprofit edtech with many audiences and a small team &#8212; a CMS the staff run without a developer."),
 ("0xBow", "0xbow.io", "Framer &#183; Web3", "linear-gradient(140deg,#14101A 0%,#2E1A46 100%)",
  "#C7A8FF", "A privacy protocol made legible &#8212; motion used as explanation rather than decoration."),
 ("Stratus Neuro", "stratusneuro.com", "Webflow &#183; Medtech", "linear-gradient(140deg,#0F1614 0%,#123A2E 100%)",
  "#8FE8C4", "Regulated-industry credibility: careful claims, accessible patterns, clinician-friendly navigation."),
 ("SecureCDP", "securecdp.com", "Webflow &#183; Cybersecurity", "linear-gradient(140deg,#12131A 0%,#1E2A4A 100%)",
  "#9DB8FF", "Security SaaS positioning &#8212; a marketing site that survives a technical buyer&#8217;s scrutiny."),
 ("Eric Kanigan", "www.erickanigan.photography", "Webflow &#183; Fine art", "linear-gradient(140deg,#17140F 0%,#3A3123 100%)",
  "#E8D5A8", "Editorial restraint for award-winning wildlife photography &#8212; typography that stays out of the way."),
 ("SalesPeak AI", "salespeak.ai", "Webflow &#183; AI / B2B SaaS", "linear-gradient(140deg,#0F1218 0%,#1B2942 100%)",
  "#A8C5FF", "Explaining an AI sales platform to enterprise buyers who distrust AI marketing copy."),
 ("WaterH", "www.waterh.com/pages/about-waterh-app", "UI/UX &#183; Healthcare", "linear-gradient(140deg,#0E1618 0%,#123840 100%)",
  "#8FE3F0", "A smart-bottle companion app where usability and accessibility were requirements, not afterthoughts."),
]

THUMBS = {"SalesPeak AI": "/uploads/thumbs/salespeak.webp", "0xBow": "/uploads/thumbs/0xbow.webp",
          "Eric Kanigan": "/uploads/thumbs/erickanigan.webp", "WaterH": "/uploads/thumbs/waterh.webp",
          "CADDi": "/uploads/thumbs/caddi.webp", "Assistments": "/uploads/thumbs/assistments.webp"}

def case_card(c):
    name, host, tag, grad, tagcol, blurb = c
    shot = THUMBS.get(name)
    thumb = (f'<div class="thumb has-shot" style="background:{grad}">'
             f'<img src="{shot}" alt="{name} website" loading="lazy" width="900" height="600">'
             f'<span class="mono" style="color:{tagcol}">{tag}</span></div>') if shot else (
             f'<div class="thumb" style="background:{grad}">'
             f'<span class="ghost" aria-hidden="true">{name}</span>'
             f'<span class="mono" style="color:{tagcol}">{tag}</span></div>')
    return f'''<a class="card card-hover case" href="https://{host}" target="_blank" rel="noopener"
  data-reveal data-cursor="Visit">
  {thumb}
  <div class="body"><h3>{name}</h3><p style="font-size:14.5px;color:var(--ash)">{blurb}</p>
    <span class="go">Visit live site <span class="arw">&#8594;</span></span></div>
</a>'''

def work_rows(items):
    out = ['<div class="rows">']
    for i, (name, host, tag, grad, tagcol, blurb) in enumerate(items):
        shot = THUMBS.get(name)
        img = f' data-peek-img="{shot}"' if shot else ""
        out.append(f'''<a class="row" href="https://{host}" target="_blank" rel="noopener"
  data-peek="{grad}" data-peek-name="{name}" data-host="{host}"{img} data-cursor="Visit">
  <span class="row-num">{i+1:02d}</span>
  <span class="row-name">{name}</span>
  <span class="mono row-tag">{tag}</span>
  <span class="row-arrow" aria-hidden="true">&#8599;</span>
</a>''')
    out.append('</div>')
    return "\n".join(out)

SERVICES = [
 ("Product design", "/services/product-design", "01",
  "UX and interface design for SaaS and mobile products, delivered developer-ready in Figma.",
  "$3,000&#8211;$7,000", ["UX audit", "User flows", "High-fidelity UI", "Design system", "Prototype", "Handoff"]),
 ("Webflow development", "/services/webflow-development", "02",
  "Production Webflow builds with an editor-proof CMS your marketing team can run alone.",
  "$2,500&#8211;$6,000", ["Pixel-perfect build", "CMS setup", "Interactions", "Migration", "SEO basics", "Launch support"]),
 ("Framer development", "/services/framer-development", "03",
  "Launch-speed Framer sites for fundraises, announcements and product drops.",
  "From $900", ["Landing pages", "Custom components", "CMS", "GSAP", "Performance", "Launch support"]),
 ("AI product builds", "/services/ai-product-builds", "04",
  "Lovable, v0 and Claude Code prototypes taken the last 30% to something you can ship.",
  "$1,500&#8211;$4,000", ["Design pass", "Component system", "Responsive", "Accessibility", "Handover docs"]),
]

def service_card(s, ember=False):
    name, url, num, blurb, price, chips = s
    cls = "card card-ember" if ember else "card"
    return f'''<a class="{cls}" href="{url}" data-reveal style="display:flex;flex-direction:column;gap:10px">
  <span class="mono" style="color:{'#FFE3D6' if ember else 'var(--ember)'}">{num}</span>
  <h3>{name}</h3>
  <p style="font-size:14.5px">{blurb}</p>
  <span style="margin-top:6px;font-weight:600;color:{'#fff' if ember else 'var(--ember-deep)'}">{price}</span>
</a>'''

print("builder ready")
