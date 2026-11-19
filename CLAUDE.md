# anowarhdesign.com

Personal site for Anowar Hossain — UI/UX designer and Webflow / Framer developer, Dhaka (GMT+6),
working with US, UK and EU clients. Static HTML, no framework, deployed on Vercel from this repo.
One dynamic piece: `api/contact.js`, a Vercel serverless function (plain Node, zero-config — no
framework needed for `/api/*.js` to work on Vercel).

## Contact form backend

The quick-brief form in the CTA band (`band()` in `build.py`) POSTs JSON to `/api/contact.js`,
which emails it via Resend to `anowarhdesign@gmail.com` (reply-to set to the visitor's address).
**Requires a `RESEND_API_KEY` environment variable in the Vercel project** (Settings -> Environment
Variables — a free Resend account and API key take a couple of minutes at resend.com). Without it
the function returns 500 and the form shows "Couldn't send — email hello@anowarhdesign.com
directly instead"; the form degrades gracefully, it doesn't break. The sender is
`onboarding@resend.dev` (Resend's shared test sender, works with no domain verification); verifying
`anowarhdesign.com` with Resend later would let mail go out as `@anowarhdesign.com` instead, purely
a deliverability/branding upgrade, not required for the form to work.

**Spam defenses** (`api/contact.js`), layered instead of a CAPTCHA — confirmed live 2026-09-22,
`npm`-free unit tests for the logic live at conversation-scratchpad time only (not committed; the
handler is plain enough to re-test the same way if it's ever touched: mock `req`/`res`, stub
`global.fetch`, assert `res.statusCode`):
1. Honeypot field (`company`, hidden via CSS in `.bf-hp`) — bots fill it, humans never see it.
2. Time-trap — `site.js` records `loadedAt` when the form becomes interactive; the server silently
   pretends success (200, no email sent) for anything submitted in under ~2.5s or missing
   `loadedAt` outright (i.e. not submitted through the real JS path).
3. Origin/Referer must match `anowarhdesign.com` / `www.anowarhdesign.com` if present (403 if not).
4. Link-count heuristic on `name`/`details` — more than 3 URLs silently drops it.
5. Best-effort per-IP rate limit (5 / 15 min), in-memory. Resets on cold start, not shared across
   concurrent instances — stops naive burst scripts, not a hard guarantee. A durable limit needs
   Vercel KV or similar; not worth the extra infrastructure unless this proves insufficient.

Real bot/human failures (missing required fields, bad email format) still return 400 with an error
message — only the "this looks automated" cases pretend success, deliberately, so a scripted client
doesn't get useful signal to adapt its timing.

## How this site is built

**The HTML is generated. Do not hand-edit the page files** — `index.html`, `services/…`, `work/…`
etc. are all output. Edit the generators in `build/`, then rebuild:

```bash
build/build_all.sh                       # regenerates every page in every language + sitemap.xml + llms.txt
python3 -m http.server 8000              # from the repo root, to preview
python3 build/qa.py                      # full QA sweep (needs a server on :8121)
```

`qa.py` expects the site served at `http://localhost:8121` — start one first:
`python3 -m http.server 8121 &`. It needs `playwright` (`pip install playwright && playwright install chromium`).

### build/ layout

| File | What's in it |
| --- | --- |
| `build.py` | Page shell: `<head>`, schema, nav, footer, dock, shared components (cards, quotes, FAQ, CTA band), and `polish()` — a post-pass that adds section indices, splits H1s into masked lines and turns stat numbers into count-up targets |
| `avatar.py` | The wordmark SVG (`AN[face]WAR`) and its CSS. Also the source for every icon |
| `pages.py` | Home + services hub |
| `pages2.py` | The four service pages, from one `service_page()` template |
| `pages3.py` | Work, pricing, process, about, contact, plus `sitemap.xml` and `llms.txt` |
| `i18n.py` | The translation pass: turns the English markup into `/de/`, `/es/`, `/fr/`, `/nl/` pages (see "Languages") |
| `i18n_tool.py` | Export untranslated copy, validate and merge translations, report status |
| `i18n/<lang>.json` | One catalogue per language: English source text -> translation |
| `qa.py` | Crawls every page: titles, descriptions, canonicals, H1 count, schema, broken links, image alt/dimensions, heading order, landmarks, mobile overflow, load metrics |

Assets in `assets/site.css` and `assets/site.js` are hand-written and edited directly. `page()` in
`build.py` appends `?v=<md5 of the file>` to both `<link>`/`<script>` tags automatically — **never
strip that query string or point either tag at a bare `/assets/site.css` / `/assets/site.js`**.
`vercel.json` used to cache `/assets/(.*)` as `immutable, max-age=31536000`, which is only safe for
content-hashed filenames; these two files keep the same URL every deploy, so that header made
Vercel's edge (and browsers) go on serving whatever they'd cached from a *previous* deploy
indefinitely — confirmed live on 2026-09-21: the aliased domain served CSS from the prior commit
while every other alias of the same (correct) deployment served the current one. Header is now
`max-age=0, must-revalidate`; the `?v=` hash is the actual fix — it's a genuinely new URL on every
content change, so it can't be served stale regardless of any cache's headers.

`uploads/logos/` holds the real client logos used in the home hero's marquee (`LOGOWALL` in
`build.py`). Every logo — whatever its source colors — is recolored to one flat tone (`#4E4945`,
matching `--ash`) so the wall reads as one cohesive set: SVGs use `fill="currentColor"` and are
inlined into the page (an `<img src="*.svg">` would NOT pick up `currentColor` — it needs its own
document context); PNGs have the color already baked in via an alpha-channel recolor pass. Icon-only
marks are paired with a text label in `LOGOS` (`build.py`). To add a client, save their logo the same
way and add a row to `LOGOS`.

## Design system — Signal DS v3

Paper base (`#F4F1EB`) with ink sections (`#0E0D0C`) alternating for rhythm; ember (`#F14E1C`) is the
only accent. Ember at body size drops to `#BF3A11` for contrast.

- **Type**: Archivo 600 display / 400 body, Instrument Serif italic for accent lines, JetBrains Mono
  for eyebrows and metadata. All from Google Fonts.
- **Geometry**: pill buttons and chips, 24px card radius, generous section padding (84–180px).
- **Motion**: no libraries. `site.js` is ~6KB of vanilla JS — spring-lerped cursor, elastic project
  preview (velocity-driven rotation and squash), IntersectionObserver reveals, count-up stats,
  magnetic buttons, card spotlight. Everything honours `prefers-reduced-motion`; cursor and preview
  disable themselves on touch.
- **No GSAP.** It was removed deliberately: the old build blanked the page when the CDN failed.

## Content rules

1. **No invented numbers.** There are no client metrics — nobody supplied any. Cases run on scope and
   craft instead. If a figure isn't verifiable, it doesn't go on the site.
2. **Answer-first.** Every page opens with a self-contained 40–80 word block (`<p class="answer">`)
   that answers the query the page targets. This is the AEO extraction surface; keep it.
3. **Testimonials are verbatim public Upwork reviews**, labelled with contract and date. Never
   paraphrase them.
4. **One page owns one query.** Don't add a page that competes with an existing one — see the
   keyword map in the planning doc.

### Facts, as verified

Top Rated on Upwork · 100% job success · 2,237 hours logged · 399+ projects completed · 6+ years ·
clients in US, UK, Canada, Australia, EU. Credentials: Webflow Experts Certification, Google UX
Design Professional Certificate. Price bands (halved 2026-09-22 from the original figures — verify
before quoting elsewhere): landing page from $450, marketing site $1,250–$3,000, product design
$1,500–$3,500, AI product build $750–$2,000, care plan $150–$450/mo.

"399+ projects completed" (2026-09-21, confirmed by Anowar as accurate across all platforms, not
just the 50 completed Upwork contracts) replaces the old site's unverified "398+ projects" claim,
which had been deliberately dropped for lacking that confirmation. Don't revert this without a
fresh confirmation — the number is only as good as the last person who checked it.

## State

Twenty-seven pages (home, services hub, five service pages, work, pricing, process, about, contact,
fifteen case studies), each in five languages.
QA passes with zero failures. FCP 320–410ms locally, 1KB JS per page.

### Next, in priority order

1. **Insights** — `/insights/` doesn't exist yet. Twelve articles planned; the first three
   (Framer vs Webflow, what a Webflow site costs, how to hire a Webflow developer) matter most.
2. **Case study pages** — `/work/<slug>/`. Currently the work page links out to client sites, so
   visitors leave. Six were planned; each needs pages, timeline and role from Anowar.
3. **Project thumbnails** — six exist (`uploads/thumbs/`: SalesPeak AI, 0xBow, Eric Kanigan, WaterH,
   CADDi, Assistments). The rest fall back to a name-on-gradient card. Drop new screenshots into
   `uploads/thumbs/<slug>.webp` at 900×600 and add them to `THUMBS` in `build.py`.
4. **Upwork profile URL** — the testimonials need a link so buyers can verify them.
5. **Search Console + Bing Webmaster Tools** — not verified yet, so there's no query data.

### Known gaps

- `erickanigan.photography` was corrected from a guessed `.com`; other hosts in `CASES` and
  `DEPLOYS` (build.py, pages3.py) were inferred from the old site and are worth double-checking.
- An unused Ethereum Community Foundation screenshot sits in `uploads/Screenshot_9.png` — if that's
  Anowar's work it belongs in the project list.
- `uploads/pasted-1784209874396-0.png` is unidentified.

## Languages (added 2026-11-19)

English is the source and lives at the root. German, Spanish, French and Dutch are generated from it
into `/de/`, `/es/`, `/fr/`, `/nl/` with the same paths (`/de/pricing`). **Never hand-edit those folders,
and never write copy straight into a language folder** — they are build output like every other page.

How it works: `page()` in `build.py` renders English, then runs the same markup through
`i18n.Translator` once per language. The translator cuts the page into *units* (the copy inside the
lowest element holding a sentence), replaces inline tags with numbered placeholders
(`Or <1>start a project</1> without a call`) and looks the unit up in `build/i18n/<lang>.json`. It also
translates `alt` / `aria-label` / `placeholder` / `title` / `data-cursor`, the title and description,
JSON-LD text, the strings `site.js` shows (every `tr("…")` call) and the room's text (every `T('…')` /
`N('…')` in `studio/src/app.js`, written to `studio/i18n/<lang>.json`). Internal links are rewritten to
stay inside the language; each page carries the full reciprocal `hreflang` set plus `x-default`, and
`sitemap.xml` lists every language version.

Changing copy:
1. Edit the English in the generator as before and rebuild. Any unit without a translation falls back
   to English on the translated pages and is listed in `build/i18n/_missing.json` (QA fails on it).
2. `python build/i18n_tool.py export de` writes what is missing to `build/i18n/_work/src.NN.json`;
   translate into `de.NN.json` (`{"<id>": "translation"}`), then `i18n_tool.py merge de` and rebuild.
   `i18n_tool.py status` shows where every language stands; `prune <lang>` drops unused entries.
3. The checker enforces: same placeholders, **same numbers in the same format** as the English
   (`$1,500–$3,500`, `2,237`) and no entities — so a translation can never change a figure. The build
   then swaps the separators mechanically per language (`locnum()` in `i18n.py`: `2.237` in de/nl/es,
   `2 237` in fr, `2,5` for decimals), including the count-up stats (`data-sep`).

Rules:
- Mark anything that must not be translated with `translate="no"`: client names, the wordmark, the
  email address, and above all the Upwork quotes (`<q translate="no" lang="en">`) — content rule 3
  (verbatim reviews) holds in every language, so they stay in English with a translated attribution.
- Tone: German formal `Sie`, Spanish `tú` (neutral, no `vosotros`), French `vous`, Dutch `je`.
- Slugs stay English in every language, so the switcher always maps a page to its twin.
- `SITE` in `build.py` is `https://www.anowarhdesign.com` because that is the host Vercel serves (the
  bare domain 308-redirects to it). Canonical, hreflang and sitemap URLs must be the final URL or
  search engines discount them. If the primary domain is ever flipped in Vercel, flip `SITE` too.
- Long words: translated hero headlines size to their column and card headings hyphenate (the
  "translated pages: longer words" block at the end of `site.css`). QA loads every translated page at
  390, 1100 and 1440px and fails on clipped or overflowing text.
- No automatic redirect by browser language (bad for crawlers and for people abroad). `site.js` shows
  one dismissible hint when the browser prefers another available language and remembers the choice
  in `localStorage` (`lang`).
- The switcher is three sets of plain links per page (nav `<details class="lang">`, chips in the phone
  menu, a footer row), filled in after link rewriting via the `<!--LANG…-->` slots in `nav()` / `FOOT`.
- The mini-OS inside the monitor is English only; its page links still point at the visitor's language.
- To add a language: add it to `LANGS` in `i18n.py` (and `LANG_WORD` in `build.py`, the allow-list in
  `api/contact.js`), export, translate, merge, rebuild, run QA.
- The translations were written by Claude, not a native speaker; a native proofread of the homepage
  and service pages is still worth doing before leaning on them.

## The studio homepage (`studio/`)

The home hero is a three.js room modelled on Anowar's real desk at dusk. Lighting is baked in
Blender Cycles and drawn with unlit shaders; the left monitor opens a DOM mini-OS.

| Path | What's in it |
| --- | --- |
| `studio/blender/scene.py` | Builds the whole room in code. `blender -b -P scene.py -- preview \| bake only=0\|1 res=2048 spp=128 \| env \| export` |
| `studio/blender/denoise.py` | OIDN pass over the raw bakes (`raw/lm*_*.npy`) |
| `studio/tools/post.py` | Encodes the bakes to `baked/lm{0,1}_{W,P,B}.webp` (W = window, P = lamps, B = monitors) |
| `studio/tools/make_textures.py` | Procedural source textures (`tex/`) and OS wallpapers (`baked/wall_*.jpg`) |
| `studio/tools/shot.py` | Headless Chromium on the real GPU: screenshots, input, frame rate. Blocks analytics |
| `studio/src/app.js` | The room: shaders, screens, hotspots and cards, camera, fly-in |
| `studio/src/os.js`, `apps.js` | Window manager and the thirteen programs |
| `studio/data.json` | Written by `build/pages3.py` from the same lists the HTML pages use. Never hand-edit |
| `studio/vendor/` | three.js r186, local. **No CDN** — the page may only reach Google Fonts and analytics |

Rules that are easy to break:
- Object names in `scene.py` drive the page (`screen_main`, `glow_*`, `sway_*`, hotspot prefixes in
  `HOT` in `app.js`). Rename in both places.
- Any geometry change needs both lightmap groups rebaked, then denoise, then `post.py` — the
  lightmap UVs are re-unwrapped on every bake, so an old lightmap with a new `studio.glb` is garbage.
- Everything under `/studio/baked/` is cached `immutable`; that is only safe because every URL
  carries `?v={STUDIO_VER}` (hash of the studio files, `build.py`). Never reference one without it.
- The room's hero text and object cards are translated (see "Languages"); wrap any new visible string
  in `T('…')`, or `N('…')` when it is only declared there, or it stays English everywhere.
- `?t=<seconds>` freezes time, `?view=os[&app=<id>]` opens the OS, `?view=card-<key>` opens a card.
- No city name, address or person inside the room or the OS (`_nocity()` in `pages3.py` scrubs
  `data.json`). Sound stays off until "Enable sound". Sentence-case copy, no emoji icons.
- `studio/raw/` is scratch (bakes, screenshots) and is git-ignored.
