#!/usr/bin/env python3
"""Static page builder for anowarhdesign.com — shared shell + per-page content."""
import hashlib, json, os, pathlib
from avatar import wordmark, AVATAR_CSS

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://anowarhdesign.com"

# assets/site.css and assets/site.js keep the same URL every deploy (they are
# hand-written, not content-hashed build output), so a cache-busting query
# string is the only thing that forces browsers/edges to pick up a new
# version — see vercel.json: even with must-revalidate, anything that already
# cached the file under the old "immutable" header (a past bug) won't know to
# recheck without the URL itself changing.
def _asset_ver(name):
    return hashlib.md5((ROOT / "assets" / name).read_bytes()).hexdigest()[:10]

CSS_VER = _asset_ver("site.css")
JS_VER = _asset_ver("site.js")
# same reasoning as the CSS/JS cache-busting above: og-cover.jpg keeps the same
# URL across deploys, and social platforms (Facebook, Slack, WhatsApp, LinkedIn)
# cache a scraped link preview independently of our own Cache-Control header —
# a same-URL replacement can go on serving the old image indefinitely unless
# the URL itself changes.
OG_VER = hashlib.md5((ROOT / "uploads" / "og-cover.jpg").read_bytes()).hexdigest()[:10]

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
               "https://x.com/anowarhdesign",
               "https://upwork.com/freelancers/webflowframeruiuxfigmadesign"],
}

def slugify(name):
    import re
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

def breadcrumbs(trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": SITE + url}
        for i, (name, url) in enumerate(trail)]}

def faq_schema(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q,
         "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}

def review_schema(keys):
    """Review objects for the QUOTES actually rendered as visible <figure class="quote">
    on that page — schema must mirror on-page content, not every testimonial site-wide."""
    return [{"@type": "Review", "reviewBody": QUOTES[k][0],
             "author": {"@type": "Organization", "name": "Verified Upwork Client"},
             "itemReviewed": {"@id": SITE + "/#person"}} for k in keys]

def itemlist_schema(cases):
    return {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1,
         "item": {"@type": "CreativeWork", "name": name, "url": "https://" + host}}
        for i, (name, host, *_rest) in enumerate(cases)]}

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
      <a class="btn btn-ink btn-sm" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book a call</a>
    </div>
  </div>
</header>
<div class="nav-mini" aria-hidden="true">{wordmark(inert=True)}</div>'''

EMAIL = "hello@anowarhdesign.com"

def email_chip():
    return (f'<span class="email-chip"><a href="mailto:{EMAIL}">{EMAIL}</a>'
            f'<button type="button" class="copy-btn" data-copy="{EMAIL}" aria-label="Copy email address">'
            f'<svg class="ic-copy" viewBox="0 0 16 16" aria-hidden="true">'
            f'<rect x="5.5" y="5.5" width="8" height="8" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/>'
            f'<path d="M3.5 10.5v-6a1 1 0 0 1 1-1h6" fill="none" stroke="currentColor" stroke-width="1.3"/></svg>'
            f'<svg class="ic-check" viewBox="0 0 16 16" aria-hidden="true">'
            f'<path d="M3.5 8.5l3 3 6-6.5" fill="none" stroke="currentColor" stroke-width="1.6" '
            f'stroke-linecap="round" stroke-linejoin="round"/></svg></button></span>')

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
        <li><a href="https://upwork.com/freelancers/webflowframeruiuxfigmadesign" rel="noopener" target="_blank">Upwork</a></li>
        <li><a href="https://www.linkedin.com/in/anowarhdesign/" rel="noopener" target="_blank">LinkedIn</a></li>
        <li><a href="https://dribbble.com/anowarhdesign" rel="noopener" target="_blank">Dribbble</a></li>
        <li><a href="https://x.com/anowarhdesign" rel="noopener" target="_blank">X</a></li>
        <li class="foot-email">__EMAILCHIP__</li>
      </ul></div>
    </div>
    <div class="foot-base mono">
      <span>&#169; <span id="cpyear">2026</span> Anowar Hossain</span>
      <span>Dhaka &#183; GMT+6 &#8212; <span id="clock">--:--</span> local</span>
    </div>
  </div>
</footer>'''
FOOT = FOOT_TPL.replace('__FOOTMARK__', wordmark()).replace('__EMAILCHIP__', email_chip())

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
      <span class="mono" style="text-transform:none;letter-spacing:normal">Or write direct &#8212; {email_chip()}</span>
    </div>
  </div>
  <form class="band-form" data-brief-form novalidate>
    <span class="mono">Or send a quick brief</span>
    <div class="bf-row">
      <label><span>Full Name</span>
        <input type="text" name="name" autocomplete="name" placeholder="John Doe"></label>
      <label><span>Your Email<i class="bf-req" aria-hidden="true">*</i></span>
        <input type="email" name="email" autocomplete="email" placeholder="yourmail@gmail.com" required
          aria-required="true"></label>
    </div>
    <label><span>WhatsApp Number</span>
      <input type="tel" name="whatsapp" autocomplete="tel" placeholder="123 456 7890"></label>
    <div class="bf-budget">
      <span class="bf-label">Project Budget</span>
      <div class="bf-chips" role="group" aria-label="Project budget">
        <button type="button" data-chip aria-pressed="false">Less than $1K</button>
        <button type="button" data-chip aria-pressed="false">$1K&#8211;$2K</button>
        <button type="button" data-chip aria-pressed="false">$2K&#8211;$4K</button>
        <button type="button" data-chip aria-pressed="false">$4K&#8211;$10K</button>
        <button type="button" data-chip aria-pressed="false">More than $10K</button>
      </div>
    </div>
    <label><span>Project Details<i class="bf-req" aria-hidden="true">*</i></span>
      <textarea name="details" rows="3" placeholder="I want to redesign my website.." required
        aria-required="true"></textarea></label>
    <input type="text" name="company" class="bf-hp" tabindex="-1" autocomplete="off" aria-hidden="true">
    <button class="btn btn-ink" type="submit">Send Inquiry <span class="arw">&#8594;</span></button>
    <span class="mono bf-note" data-bf-note>Sent straight to my inbox &#8212; I reply within 24 hours</span>
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
                    # italic serif descenders (j, y, g...) sit lower than the reveal
                    # mask's overflow:hidden box expects — give that line extra room
                    cls = "line line-serif" if 'class="serif"' in piece else "line"
                    parts.append(f'<span class="{cls}"><span>{piece}</span></span>')
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
<meta property="og:image" content="{SITE}/uploads/og-cover.jpg?v={OG_VER}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Anowar Hossain — UI/UX design and Webflow / Framer development">
<meta property="og:site_name" content="Anowar Hossain">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/uploads/og-cover.jpg?v={OG_VER}">
<link rel="icon" href="/uploads/favicon.ico" sizes="32x32">
<link rel="icon" type="image/svg+xml" href="/uploads/mark.svg">
<link rel="icon" type="image/png" href="/uploads/mark-64.png" sizes="64x64">
<link rel="apple-touch-icon" href="/uploads/mark-180.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=JetBrains+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/assets/site.css?v={CSS_VER}">
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
<script defer src="/assets/site.js?v={JS_VER}"></script>
</body>
</html>
'''
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(html, encoding="utf-8")
    return url

# ─────────────────────────── shared blocks ───────────────────────────

BADGE = '''<div class="badge" data-reveal>
  <img class="uw" src="/uploads/upwork-mark.png" width="22" height="22" alt="" aria-hidden="true">
  <span style="font-weight:500">Top Rated on Upwork</span>
  <span class="div" aria-hidden="true"></span>
  <span style="color:var(--ash)">100% job success &#183; 2,237 hours &#183; 399+ projects</span>
</div>'''

# ── client logo wall: real logos, recolored to one flat brand-neutral tone
# (ash, #4E4945) so every source site's original colors read as one cohesive
# set — SVGs are inlined so `currentColor` picks up that tone, PNGs already
# have it baked in via an alpha-channel recolor pass. Icon-only marks are
# paired with a text label.
LOGO_DIR = ROOT / "uploads" / "logos"
# (name, filename, pair with a text label, intrinsic px size for PNGs — avoids CLS)
LOGOS = [
    ("Blockstak", "blockstak.svg", False, None),
    ("Optiify", "optiify.svg", False, None),
    ("EAX Media", "eaxmedia.png", False, (350, 166)),
    ("CADDi", "caddi.svg", False, None),
    ("Assistments", "assistments.png", False, (1109, 160)),
    ("Stratus Neuro", "stratusneuro.png", False, (144, 48)),
    ("SecureCDP", "securecdp.png", True, (245, 160)),
    ("UberStrategist", "uberstrategist.png", False, (310, 53)),
    ("Fit3D", "fit3d.png", False, (266, 62)),
    ("UserVoice", "uservoice.svg", False, None),
    ("Spoiler Alert", "spoileralert.svg", False, None),
    ("0xBow", "0xbow.svg", True, None),
    ("Gym Insight", "gyminsight.png", False, (165, 52)),
    ("Spiritus", "spiritus.svg", False, None),
    ("Ethereum Community Foundation", "ecf.png", False, (305, 48)),
]

def _logo_item(name, filename, with_label, size):
    if filename.endswith(".svg"):
        mark = (LOGO_DIR / filename).read_text(encoding="utf-8")
    else:
        w, h = size
        mark = f'<img src="/uploads/logos/{filename}" width="{w}" height="{h}" alt="" loading="lazy">'
    label = f'<span class="lw-name">{name}</span>' if with_label else ""
    return f'<span class="logowall-item" title="{name}">{mark}{label}</span>'

_run = "".join(_logo_item(*l) for l in LOGOS)
LOGOWALL = f'''<div style="display:flex;flex-direction:column;gap:10px" data-reveal>
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

CASES = [
 ("Blockstak", "blockstak.ai", "UI/UX &#183; EdTech / AI", "linear-gradient(140deg,#0C1802 0%,#1B3D0C 100%)",
  "#B8F2A0", "Full UI/UX for a GenAI learning platform &#8212; course system, contests and mentor booking designed as one product."),
 ("Optiify", "optiify.ai", "UI/UX &#183; PropTech / AI", "linear-gradient(140deg,#050B1F 0%,#152B6B 100%)",
  "#A8C9FF", "UI/UX for an AI copilot that runs building HVAC operations &#8212; dense operational data made legible in plain language."),
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
 ("Fit3D", "fit3d.com", "Webflow &#183; Healthtech", "linear-gradient(140deg,#100E0C 0%,#2A1F16 100%)",
  "#E8B98F", "Ten years and $25M of body-scanning R&amp;D compressed into one clear pitch, credible enough for gyms and clinics to buy on the spot."),
 ("THE ONE Bespoke", "theonebespoke.com", "Webflow &#183; Fashion / AI", "linear-gradient(140deg,#17130F 0%,#3A2530 100%)",
  "#E8B4C8", "An AI dress configurator that still feels handcrafted &#8212; the interface stays out of the way of the couture."),
 ("CFS", "cfsnnn.com", "Webflow &#183; Proptech / AI", "linear-gradient(140deg,#0E161A 0%,#163A44 100%)",
  "#8FD8E0", "Predictive tenant-risk scoring for retail real estate &#8212; a data-dense product made legible to portfolio managers, not just analysts."),
 ("Accord", "black-potential-500630.framer.app", "Framer &#183; AI &#183; Ecommerce", "linear-gradient(140deg,#15130A 0%,#3D3315 100%)",
  "#E0C468", "An AI voice agent that calls abandoned-cart shoppers on a brand&#8217;s behalf &#8212; conversational recovery flows designed to feel personal, not automated."),
 ("EAX Media", "eaxmedia.com", "UI/UX &#183; Marketing agency", "linear-gradient(140deg,#0A0F1F 0%,#12224D 100%)",
  "#9FC2E0", "A fractional-CMO marketing site built to make ROI legible &#8212; lead-gen positioning and performance data given equal weight to the pitch."),
 ("Astate Concierge", "astateconcierge.com", "UI/UX &#183; Webflow &#183; Home services", "linear-gradient(140deg,#14150F 0%,#33301C 100%)",
  "#B8C49A", "A concierge home-services brand built to feel like a trusted advisor, not a task app &#8212; warm, editorial design for a high-touch membership service."),
]

THUMBS = {"Blockstak": "/uploads/thumbs/blockstak.webp", "Optiify": "/uploads/thumbs/optiify.webp",
          "EAX Media": "/uploads/thumbs/eaxmedia.webp",
          "Astate Concierge": "/uploads/thumbs/astateconcierge.webp",
          "SalesPeak AI": "/uploads/thumbs/salespeak.webp", "0xBow": "/uploads/thumbs/0xbow.webp",
          "Eric Kanigan": "/uploads/thumbs/erickanigan.webp", "WaterH": "/uploads/thumbs/waterh.webp",
          "CADDi": "/uploads/thumbs/caddi.webp", "Assistments": "/uploads/thumbs/assistments.webp",
          "Stratus Neuro": "/uploads/thumbs/stratusneuro.webp", "SecureCDP": "/uploads/thumbs/securecdp.webp",
          "Accord": "/uploads/thumbs/accord.webp", "Ethereum Community Foundation": "/uploads/thumbs/ecf.webp",
          "CivilGrid": "/uploads/thumbs/civilgrid.webp", "Alex Minkin Design": "/uploads/thumbs/alexminkin.webp",
          "Genta": "/uploads/thumbs/genta.webp", "Golf Cart Maps": "/uploads/thumbs/golfcartmaps.webp",
          "Brellium": "/uploads/thumbs/brellium.webp", "Delphyr": "/uploads/thumbs/delphyr.webp",
          "Sitegrow": "/uploads/thumbs/sitegrow.webp", "AIVA+": "/uploads/thumbs/aiva.webp",
          "Level Exam": "/uploads/thumbs/levelexam.webp", "APEX": "/uploads/thumbs/apex.webp",
          "SHF Smarter Homes": "/uploads/thumbs/shf.webp", "Allen Shine Power Washing": "/uploads/thumbs/allenshine.webp",
          "ClearThink Marketing": "/uploads/thumbs/clearthink.webp", "Protect the Nest Movers": "/uploads/thumbs/ptnmovers.webp",
          "Trust Fund Baddies Academy": "/uploads/thumbs/tfba.webp", "LKI Consulting": "/uploads/thumbs/lki.webp",
          "SuperX": "/uploads/thumbs/superx.webp", "Willow Creek Cottage": "/uploads/thumbs/willowcreek.webp",
          "Hecker Homeservice": "/uploads/thumbs/heckerhome.webp", "Nonfiction": "/uploads/thumbs/nonfiction.webp",
          "USCO": "/uploads/thumbs/usco.webp", "RentKeep": "/uploads/thumbs/rentkeep.webp",
          "Nawafith": "/uploads/thumbs/nawafith.webp", "Shila Rahman": "/uploads/thumbs/shilarahman.webp",
          "Instautomation": "/uploads/thumbs/instautomation.webp", "Email Ethos": "/uploads/thumbs/emailethos.webp",
          "MacWell": "/uploads/thumbs/macwell.webp", "CFS": "/uploads/thumbs/cfs.webp",
          "Gustorx": "/uploads/thumbs/gustorx.webp", "Faceless Education": "/uploads/thumbs/facelesseducation.webp",
          "meFuse": "/uploads/thumbs/mefuse.webp", "THE ONE Bespoke": "/uploads/thumbs/theone.webp",
          "FindingFemaleFriends>50": "/uploads/thumbs/fff50.webp", "Tina K": "/uploads/thumbs/tinaks.webp",
          "CarWebsite": "/uploads/thumbs/carwebsite.webp", "Notion Depot": "/uploads/thumbs/notiondepot.webp",
          "Embedded Finance Review": "/uploads/thumbs/embeddedfinance.webp",
          "UberStrategist": "/uploads/thumbs/uberstrategist.webp", "Fit3D": "/uploads/thumbs/fit3d.webp",
          "UserVoice": "/uploads/thumbs/uservoice.webp", "Spiritus": "/uploads/thumbs/spiritus.webp",
          "Spoiler Alert": "/uploads/thumbs/spoileralert.webp", "Gym Insight": "/uploads/thumbs/gyminsight.webp",
          "Prison Mathematics Project": "/uploads/thumbs/prisonmath.webp"}

def case_card(c):
    name, host, tag, grad, tagcol, blurb = c
    slug = slugify(name)
    shot = THUMBS.get(name)
    thumb = (f'<div class="thumb has-shot" style="background:{grad}">'
             f'<img src="{shot}" alt="{name} website" loading="lazy" width="900" height="600">'
             f'<span class="mono" style="color:{tagcol}">{tag}</span></div>') if shot else (
             f'<div class="thumb" style="background:{grad}">'
             f'<span class="ghost" aria-hidden="true">{name}</span>'
             f'<span class="mono" style="color:{tagcol}">{tag}</span></div>')
    return f'''<a class="card card-hover case" href="/work/{slug}"
  data-reveal data-cursor="View">
  {thumb}
  <div class="body"><h3>{name}</h3><p style="font-size:14.5px;color:var(--ash)">{blurb}</p>
    <span class="go">See the case study <span class="arw">&#8594;</span></span></div>
</a>'''

# ── individual case study pages: most client work here is under NDA, so
# these never claim process detail or metrics that were never cleared to
# publish — they show the same public-facing blurb as the card, a big
# thumbnail, a link to the still-visitable live site, and a straight
# explanation that the rest is a conversation, not a page.
LOCK_SVG = '''<svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="14" y="28" width="36" height="28" rx="8" stroke="currentColor" stroke-width="4"/>
  <path d="M22 28V20a10 10 0 0 1 20 0v8" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
  <circle cx="32" cy="40" r="3.5" fill="currentColor"/>
  <path d="M32 43.5V48" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
</svg>'''

def case_study_body(c, deploy_rows=None):
    name, host, tag, grad, tagcol, blurb = c
    shot = THUMBS.get(name)
    thumb = (f'<div class="cs-shot" style="background:{grad}">'
             f'<img src="{shot}" alt="{name} website" width="900" height="600" loading="lazy"></div>') if shot else (
             f'<div class="cs-shot" style="background:{grad}"><span class="ghost" aria-hidden="true">{name}</span></div>')
    # tagcol is a light, dark-background-only accent (used in the card thumb's
    # gradient overlay) — reused directly on the paper background here it'd be
    # near-illegible, so this line always uses the same on-paper ember tone
    # the rest of the site uses for accents at body size.
    others = [r for r in (deploy_rows or []) if r[0] != name]
    other_work = f'''
<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Keep looking</span>
      <h2>More work,<br>shipped &amp; live.</h2></div></div>
    {work_rows(others)}
  </div>
</section>''' if others else ""
    return f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <a class="cs-back" href="/work" data-reveal>&#8592; Back to work</a>
      <h1 data-reveal>{name}</h1>
      <p class="mono" data-reveal style="color:var(--ember-deep);margin-top:4px">{tag}</p>
      <p class="answer" data-reveal>{blurb}</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://{host}" target="_blank" rel="noopener" data-cursor="Visit">Visit live site <span class="arw">&#8599;</span></a>
      </div>
    </div>
    <aside class="hero-aside">{thumb}</aside>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="cs-nda" data-reveal>
      <div class="cs-nda-icon">{LOCK_SVG}</div>
      <div class="cs-nda-copy">
        <h2>This project is under NDA.</h2>
        <p>Screens, process notes and specifics from this engagement are covered by a client confidentiality
          agreement, so they don&#8217;t go on a public page &#8212; but I am glad to walk you through the actual
          work, decisions and outcome on a call.</p>
      </div>
      <a class="btn btn-primary" data-magnet href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book a walkthrough call <span class="arw">&#8594;</span></a>
    </div>
  </div>
</section>
{other_work}
<section style="padding-top:clamp(48px,6vw,88px);padding-bottom:0">{band("Want something like this?", "Bring the brief. You will get a fixed quote, a timeline, and a straight answer about what is realistic.")}</section>
'''

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
  "$1,500&#8211;$3,500", ["UX audit", "User flows", "High-fidelity UI", "Design system", "Prototype", "Handoff"]),
 ("Webflow development", "/services/webflow-development", "02",
  "Production Webflow builds with an editor-proof CMS your marketing team can run alone.",
  "$1,250&#8211;$3,000", ["Pixel-perfect build", "CMS setup", "Interactions", "Migration", "SEO basics", "Launch support"]),
 ("Framer development", "/services/framer-development", "03",
  "Launch-speed Framer sites for fundraises, announcements and product drops.",
  "From $450", ["Landing pages", "Custom components", "CMS", "GSAP", "Performance", "Launch support"]),
 ("AI product builds", "/services/ai-product-builds", "04",
  "Lovable, v0 and Claude Code prototypes taken the last 30% to something you can ship.",
  "$750&#8211;$2,000", ["Design pass", "Component system", "Responsive", "Accessibility", "Handover docs"]),
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
