#!/usr/bin/env python3
"""QA sweep: markup, metadata, schema, links, a11y, performance."""
import json, re, pathlib, urllib.request, collections
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = 'http://localhost:8121'
PATHS = ['/', '/services/', '/services/product-design/', '/services/webflow-development/',
         '/services/framer-development/', '/services/ai-product-builds/', '/work/',
         '/pricing/', '/process/', '/about/', '/contact/']
issues, notes = [], []

def add(level, page, msg):
    (issues if level == 'FAIL' else notes).append(f"[{level}] {page}: {msg}")

# ── static checks over the built files ──
titles, descs = {}, {}
for p in PATHS:
    f = ROOT / (p.strip('/') + '/index.html' if p != '/' else 'index.html')
    s = f.read_text(encoding='utf-8')
    title = re.search(r'<title>(.*?)</title>', s, re.S).group(1)
    desc = re.search(r'name="description" content="([^"]*)"', s).group(1)
    titles.setdefault(title, []).append(p); descs.setdefault(desc, []).append(p)
    if len(title) > 62: add('WARN', p, f'title {len(title)} chars (>62 truncates in SERPs)')
    if not (120 <= len(desc) <= 165): add('WARN', p, f'description {len(desc)} chars (aim 120-165)')
    h1s = re.findall(r'<h1[^>]*>', s)
    if len(h1s) != 1: add('FAIL', p, f'{len(h1s)} H1s')
    can = re.search(r'canonical" href="([^"]+)"', s).group(1)
    if not can.startswith('https://anowarhdesign.com'): add('FAIL', p, f'bad canonical {can}')
    if can.rstrip('/') != ('https://anowarhdesign.com' + p.rstrip('/')).rstrip('/'):
        add('FAIL', p, f'canonical mismatch: {can}')
    # schema
    ld = json.loads(re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', s, re.S).group(1))
    types = [n.get('@type') for n in ld['@graph']]
    if 'Person' not in types: add('FAIL', p, 'no Person schema')
    if p != '/' and 'BreadcrumbList' not in types: add('WARN', p, 'no BreadcrumbList')
    # answer block within the first screenful of copy
    if '<p class="answer"' not in s and p != '/':
        add('WARN', p, 'no answer block (AEO extraction target)')
    # images
    for img in re.findall(r'<img[^>]*>', s):
        if 'alt=' not in img: add('FAIL', p, f'img without alt: {img[:60]}')
        if 'width=' not in img or 'height=' not in img:
            add('WARN', p, f'img without dimensions (CLS risk): {img[:60]}')
for t, ps in titles.items():
    if len(ps) > 1: add('FAIL', ','.join(ps), f'duplicate title: {t[:50]}')
for d, ps in descs.items():
    if len(ps) > 1: add('FAIL', ','.join(ps), f'duplicate description')

# ── sitemap / robots / llms ──
sm = (ROOT / 'sitemap.xml').read_text()
locs = re.findall(r'<loc>(.*?)</loc>', sm)
for p in PATHS:
    u = 'https://anowarhdesign.com' + (p.rstrip('/') or '/')
    if u not in locs: add('FAIL', p, 'missing from sitemap.xml')
if len(locs) != len(PATHS): add('WARN', 'sitemap', f'{len(locs)} urls vs {len(PATHS)} pages')
rb = (ROOT / 'robots.txt').read_text()
for bot in ['GPTBot', 'ClaudeBot', 'PerplexityBot', 'Google-Extended']:
    if bot not in rb: add('WARN', 'robots.txt', f'{bot} not named')
if 'Sitemap:' not in rb: add('FAIL', 'robots.txt', 'no Sitemap line')
if not (ROOT / 'llms.txt').exists(): add('WARN', 'llms.txt', 'missing')

# ── live checks ──
results = {}
with sync_playwright() as pw:
    br = pw.chromium.launch()
    pg = br.new_page(viewport={'width': 1440, 'height': 950})
    seen_links, weights = set(), {}
    pg.on('pageerror', lambda e: add('FAIL', 'runtime', str(e)[:90]))
    for p in PATHS:
        bytes_total = {'n': 0}
        def on_resp(r):
            try: bytes_total['n'] += int(r.headers.get('content-length') or 0)
            except Exception: pass
        pg.on('response', on_resp)
        r = pg.goto(B + p, wait_until='load'); pg.wait_for_timeout(700)
        if r.status != 200: add('FAIL', p, f'HTTP {r.status}')
        # metrics
        m = pg.evaluate("""(()=>{const n=performance.getEntriesByType('navigation')[0]||{};
          const paints=performance.getEntriesByType('paint');
          const fcp=(paints.find(x=>x.name==='first-contentful-paint')||{}).startTime||0;
          const res=performance.getEntriesByType('resource');
          return {dcl:Math.round(n.domContentLoadedEventEnd||0), fcp:Math.round(fcp),
                  reqs:res.length, js:Math.round(res.filter(r=>r.initiatorType==='script')
                    .reduce((a,b)=>a+(b.transferSize||0),0)/1024),
                  css:Math.round(res.filter(r=>r.initiatorType==='link'&&/\\.css|fonts/.test(r.name))
                    .reduce((a,b)=>a+(b.transferSize||0),0)/1024)};})()""")
        weights[p] = m
        # links
        for h in pg.eval_on_selector_all('a[href^="/"]', 'e=>[...new Set(e.map(x=>x.getAttribute("href")))]'):
            if h in seen_links: continue
            seen_links.add(h)
            u = B + (h if h.endswith('/') or '.' in h.split('/')[-1] else h + '/')
            try: code = urllib.request.urlopen(u, timeout=6).getcode()
            except Exception as ex: code = getattr(ex, 'code', 'ERR')
            if code != 200: add('FAIL', p, f'broken internal link {h} -> {code}')
        # a11y-ish
        a11y = pg.evaluate("""(()=>{
          const out={};
          out.landmarks = !!document.querySelector('main') && !!document.querySelector('header') && !!document.querySelector('footer');
          out.headingJumps = (()=>{let last=0,bad=0;document.querySelectorAll('h1,h2,h3,h4').forEach(h=>{
            const l=+h.tagName[1]; if(last && l-last>1) bad++; last=l;});return bad;})();
          out.emptyLinks = [...document.querySelectorAll('a')].filter(a=>!a.textContent.trim() && !a.getAttribute('aria-label')).length;
          out.smallTargets = [...document.querySelectorAll('a,button')].filter(el=>{
            const r=el.getBoundingClientRect(); return r.height>0 && r.height<32;}).length;
          out.lang = document.documentElement.lang;
          return out;})()""")
        if not a11y['landmarks']: add('FAIL', p, 'missing landmark elements')
        if a11y['headingJumps']: add('WARN', p, f"{a11y['headingJumps']} heading level jumps")
        if a11y['emptyLinks']: add('FAIL', p, f"{a11y['emptyLinks']} links with no accessible name")
        if a11y['lang'] != 'en': add('FAIL', p, 'html lang not set')
        results[p] = {'a11y': a11y, 'perf': m}
        pg.remove_listener('response', on_resp)
    # mobile pass on the homepage
    mob = br.new_page(viewport={'width': 390, 'height': 844})
    mob.goto(B + '/', wait_until='load'); mob.wait_for_timeout(700)
    if mob.evaluate("document.documentElement.scrollWidth > innerWidth + 1"):
        add('FAIL', 'mobile', 'horizontal overflow at 390px')
    tiny = mob.evaluate("""[...document.querySelectorAll('p,li,span')].filter(e=>{
        const s=getComputedStyle(e); return parseFloat(s.fontSize)<12 && e.textContent.trim().length>12;}).length""")
    if tiny: add('WARN', 'mobile', f'{tiny} text nodes under 12px')
    br.close()

print("\n".join(issues) if issues else "No failures.")
print("\n--- warnings ---")
print("\n".join(notes) if notes else "none")
print("\n--- weight & speed (local, uncached) ---")
for p, v in results.items():
    m = v['perf']
    print(f"{p:36} fcp {m['fcp']:>4}ms  dcl {m['dcl']:>4}ms  reqs {m['reqs']:>2}  js {m['js']:>3}KB  css/fonts {m['css']:>3}KB")
