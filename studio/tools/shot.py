"""Headless check on the real GPU: load, send input, screenshot, measure frame rate.
usage: python shot.py '<json list of {name, url?, q?, size?, wait?, locale?, steps?}>'
steps: ["move",x,y] ["click",x,y] ["dbl",x,y] ["drag",x1,y1,x2,y2] ["key","Escape"] ["type","text"] ["wheel",dy] ["wait",ms] ["eval","js"] ["shot","suffix"] ["fps",seconds]"""
import json, pathlib, sys
from playwright.sync_api import sync_playwright

OUT = pathlib.Path(__file__).resolve().parent.parent / "raw" / "shots"
OUT.mkdir(parents=True, exist_ok=True)
jobs = json.loads(sys.argv[1])
FPS_JS = """(sec) => new Promise(res => { let n = 0, t0 = performance.now(), worst = 0, last = t0;
  const f = (t) => { n++; worst = Math.max(worst, t - last); last = t; if (t - t0 >= sec * 1000) res({fps: +(n / ((t - t0) / 1000)).toFixed(1), worstMs: +worst.toFixed(1)}); else requestAnimationFrame(f); };
  requestAnimationFrame(f); })"""
with sync_playwright() as p:
    b = p.chromium.launch(headless=True, args=["--use-angle=d3d11", "--enable-gpu", "--ignore-gpu-blocklist", "--enable-webgl"] + (["--disable-frame-rate-limit"] if "--uncapped" in sys.argv else []))
    for job in jobs:
        w, h = job.get("size", [1920, 1080])
        ctx = b.new_context(viewport={"width": w, "height": h}, device_scale_factor=job.get("dpr", 1), has_touch=job.get("touch", False), locale=job.get("locale", "en-US"))
        pg = ctx.new_page()
        # never send test traffic to the live analytics property
        ctx.route(lambda u: any(k in u for k in ("googletagmanager.com", "google-analytics.com", "analytics.google.com", "doubleclick.net", "/_vercel/", "google.com")), lambda r: r.abort())
        errs = []
        pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") and "ERR_FAILED" not in m.text and "404" not in m.text else None)
        pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
        SKIP = ("googletagmanager", "analytics", "doubleclick", "_vercel", "google.com")
        pg.on("requestfailed", lambda r: errs.append(f"failed: {r.url}") if not any(k in r.url for k in SKIP) else None)
        ext = []
        pg.on("request", lambda r: ext.append(r.url) if not r.url.startswith(("http://localhost", "data:", "blob:")) and not any(k in r.url for k in SKIP) else None)
        url = job.get("url", "http://localhost:8121/studio/dev.html") + ("?" + job["q"] if job.get("q") else "")
        pg.goto(url, wait_until="load")
        try:
            pg.wait_for_selector(job.get("ready", ".st-ready"), timeout=20000, state="attached")
        except Exception as e:
            errs.append("not ready: " + str(e)[:80])
        pg.wait_for_timeout(job.get("wait", 600))
        name = job["name"]
        def shot(sfx=""):
            path = OUT / f"{name}{sfx}.jpg"
            pg.screenshot(path=str(path), type="jpeg", quality=88)
            print("shot", path.name)
        for st in job.get("steps", []):
            k = st[0]
            if k == "move": pg.mouse.move(st[1], st[2], steps=6)
            elif k == "click": pg.mouse.click(st[1], st[2])
            elif k == "dbl": pg.mouse.dblclick(st[1], st[2])
            elif k == "drag": pg.mouse.move(st[1], st[2]); pg.mouse.down(); pg.mouse.move(st[3], st[4], steps=12); pg.mouse.up()
            elif k == "key": pg.keyboard.press(st[1])
            elif k == "type": pg.keyboard.type(st[1], delay=15)
            elif k == "wheel": pg.mouse.wheel(0, st[1])
            elif k == "wait": pg.wait_for_timeout(st[1])
            elif k == "eval": print("eval:", json.dumps(pg.evaluate(st[1]))[:600])
            elif k == "shot": shot(st[1])
            elif k == "fps": print("fps:", pg.evaluate(FPS_JS, st[1]), "| app:", pg.evaluate("({fps: +document.getElementById('studio').dataset.fps, scale: window.__studio && __studio.scale})"))
        if not any(s[0] == "shot" for s in job.get("steps", [])):
            shot()
        if job.get("gpu"):
            print("gpu:", pg.evaluate("(() => { const g = document.createElement('canvas').getContext('webgl2'); const e = g.getExtension('WEBGL_debug_renderer_info'); return e ? g.getParameter(e.UNMASKED_RENDERER_WEBGL) : 'n/a'; })()"))
        if ext: print("external requests:", sorted(set(u.split('?')[0][:70] for u in ext)))
        for e in errs[:12]: print("  !", e[:300])
        ctx.close()
    b.close()
