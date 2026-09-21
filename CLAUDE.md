# anowarhdesign.com

Personal site for Anowar Hossain — UI/UX designer and Webflow / Framer developer, Dhaka (GMT+6),
working with US, UK and EU clients. Static HTML, no framework, deployed on Vercel from this repo.

## How this site is built

**The HTML is generated. Do not hand-edit the page files** — `index.html`, `services/…`, `work/…`
etc. are all output. Edit the generators in `build/`, then rebuild:

```bash
build/build_all.sh                       # regenerates all 11 pages + sitemap.xml + llms.txt
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
Design Professional Certificate. Price bands: landing page from $900, marketing site $2,500–$6,000,
product design $3,000–$7,000, AI product build $1,500–$4,000, care plan $300–$900/mo.

"399+ projects completed" (2026-09-21, confirmed by Anowar as accurate across all platforms, not
just the 50 completed Upwork contracts) replaces the old site's unverified "398+ projects" claim,
which had been deliberately dropped for lacking that confirmation. Don't revert this without a
fresh confirmation — the number is only as good as the last person who checked it.

## State

Eleven pages: home, services hub, four service pages, work, pricing, process, about, contact.
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
