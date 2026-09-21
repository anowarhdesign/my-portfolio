#!/usr/bin/env python3
from build import *   # noqa
from graphics import hero_visual   # noqa

S = SITE

DEPLOYS = [
 ("Assistments", "assistments.org", "Webflow &#183; Edtech &#183; Nonprofit", "2025"),
 ("UberStrategist", "uberstrategist.com", "Webflow &#183; Gaming &#183; PR agency", "2024"),
 ("Stratus Neuro", "stratusneuro.com", "Webflow &#183; Medtech &#183; Healthcare", "2025"),
 ("CADDi", "us.caddi.com", "Webflow &#183; Enterprise &#183; Manufacturing", "2024"),
 ("SecureCDP", "securecdp.com", "Webflow &#183; Cybersecurity &#183; SaaS", "2026"),
 ("Fit3D", "fit3d.com", "Webflow &#183; Healthtech &#183; Enterprise", "2025"),
 ("UserVoice", "uservoice.com", "Webflow &#183; B2B SaaS &#183; Product", "2024"),
 ("Spiritus", "spiritus.com", "Webflow &#183; Enterprise &#183; SaaS", "2024"),
 ("Spoiler Alert", "spoileralert.com", "Webflow &#183; Climatetech &#183; SaaS", "2025"),
 ("Gym Insight", "gyminsight.com", "Webflow &#183; Fitness &#183; SaaS", "2024"),
]

# ─────────────────────────── WORK ───────────────────────────
GRADS = ["linear-gradient(140deg,#16150F,#3A1D10)", "linear-gradient(140deg,#10161A,#12303A)",
         "linear-gradient(140deg,#0F1614,#123A2E)", "linear-gradient(140deg,#12131A,#1E2A4A)",
         "linear-gradient(140deg,#14101A,#2E1A46)", "linear-gradient(140deg,#17140F,#3A3123)"]
_seen = {c[0] for c in CASES}
DEPLOY_ROWS = ([(c[0], c[1], c[2], c[3], c[4], "") for c in CASES] +
               [(n, h, tg, GRADS[i % len(GRADS)], "#FFB48F", "")
                for i, (n, h, tg, y) in enumerate(DEPLOYS) if n not in _seen])

work_body = f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow" data-reveal>Work</span>
      <h1 data-reveal>Real clients.<span class="serif">Shipped to production.</span></h1>
      <p class="answer" data-reveal>Six years of client work across enterprise manufacturing, edtech, medtech,
        cybersecurity, Web3 and fine art &#8212; most of it for teams in the US and Europe. Every site below is
        live, and every one was designed, built, or both, by one person.</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book the discovery call</a>
        <a class="btn btn-ghost" href="/services">See services</a>
      </div>
    </div>
    <aside class="hero-aside">{hero_visual("work")}</aside>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Case studies</span>
      <h2>Eight builds,<br><span class="serif ember">in detail.</span></h2></div></div>
    <div class="grid g-3">{"".join(case_card(c) for c in CASES)}</div>
  </div>
</section>

<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Latest deployments</span>
      <h2>Every site,<br>shipped &amp; live.</h2></div></div>
    {work_rows(DEPLOY_ROWS)}
  </div>
</section>

<section>
  <div class="wrap grid g-3">{quote("teach")}{quote("startup")}{quote("rigor")}</div>
</section>

<section style="padding-block:0">{band("Want something like these?", "Bring the brief. You will get a fixed quote, a timeline, and a straight answer about what is realistic.")}</section>
'''
page("work/index.html", "Work | Webflow &amp; Framer Case Studies | Anowar Hossain",
     "Live Webflow and Framer sites for CADDi, Assistments, Stratus Neuro, SecureCDP, 0xBow and more - enterprise, SaaS, medtech and Web3 clients across the US and Europe.",
     work_body, [], current="/work", trail=[("Home", "/"), ("Work", "/work")])

# ─────────────────────────── PRICING ───────────────────────────
BANDS = [
 ("Landing page", "Framer or Webflow", "From $900", "1&#8211;2 weeks"),
 ("Marketing site", "6&#8211;12 pages with CMS", "$2,500&#8211;$6,000", "4&#8211;6 weeks"),
 ("Product design", "UX + UI engagement", "$3,000&#8211;$7,000", "4&#8211;8 weeks"),
 ("AI product build", "Prototype to production", "$1,500&#8211;$4,000", "2&#8211;5 weeks"),
 ("Care plan", "Ongoing edits and support", "$300&#8211;$900/mo", "Rolling"),
]
band_rows = "".join(f'''<div class="card" data-reveal style="display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap">
  <div style="min-width:220px"><h3>{n}</h3><p style="font-size:14.5px;color:var(--ash);margin-top:4px">{sub}</p></div>
  <div style="font-size:24px;font-weight:600;letter-spacing:-.02em;color:var(--ember-deep)">{price}</div>
  <div class="mono" style="min-width:110px;text-align:right">{dur}</div>
</div>''' for n, sub, price, dur in BANDS)

pricing_faq = [
 ("How much does a Webflow website cost in 2026?",
  "A 6&#8211;12 page marketing site with a CMS runs $2,500&#8211;$6,000 and takes four to six weeks. A single landing page starts at $900. Page count, CMS complexity, custom animation and content migration are what move the number. Every project is quoted as a fixed price after a discovery call."),
 ("Why don&#8217;t you charge hourly?",
  "Because it punishes speed. Six years of practice means a build takes less time, not less skill, and an hourly meter would bill you less for better work. A fixed quote also means you know the number before anything starts."),
 ("What happens if the scope changes?",
  "Small changes inside the agreed scope are included &#8212; revisions are not an upsell. A genuinely new requirement gets its own small quote before any work happens, so nothing appears on an invoice you did not agree to."),
 ("How does payment work for US and European clients?",
  "Fixed projects run on milestones, typically 50% to start and 50% at launch, with larger projects split into three. Invoices are in USD; EUR and GBP can be arranged. I can sign your standard contract and provide a W-8BEN for US companies."),
 ("Do you offer ongoing support after launch?",
  "Post-launch support is included in every project, and I stay reachable after that. If you want a standing arrangement for edits, new pages and small features, the care plan runs $300&#8211;$900 a month depending on volume."),
]

pricing_body = f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow" data-reveal>Pricing</span>
      <h1 data-reveal>Fixed quotes.<span class="serif">No hourly meters.</span></h1>
      <p class="answer" data-reveal>A landing page starts at $900. A 6&#8211;12 page marketing site with a CMS runs
        $2,500&#8211;$6,000 over four to six weeks. A product design engagement runs $3,000&#8211;$7,000. Every
        project is quoted as a fixed price after a 30-minute discovery call, and revisions inside that scope are
        included.</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Get a fixed quote</a>
      </div>
      {BADGE}
    </div>
    <aside class="hero-aside">{hero_visual("pricing")}</aside>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">The bands</span>
      <h2>What things cost.</h2></div></div>
    <div style="display:flex;flex-direction:column;gap:14px">{band_rows}</div>
  </div>
</section>

<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">The variables</span>
      <h2>What moves<br>the number.</h2></div></div>
    <div class="grid g-4">
      <div class="card" data-reveal><h3>Page count</h3><p style="margin-top:8px;font-size:14.5px">Unique templates matter more than total pages &#8212; twenty CMS-driven pages cost less than five bespoke ones.</p></div>
      <div class="card" data-reveal><h3>CMS complexity</h3><p style="margin-top:8px;font-size:14.5px">One blog collection is simple. Related collections with filtering and permissions are not.</p></div>
      <div class="card" data-reveal><h3>Custom motion</h3><p style="margin-top:8px;font-size:14.5px">Considered interaction work takes time to build and more time to make survive a client edit.</p></div>
      <div class="card" data-reveal><h3>Migration</h3><p style="margin-top:8px;font-size:14.5px">Moving 200 posts with their URLs and redirects is a project inside the project.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Working with US &amp; EU teams</span>
      <h2>The procurement<br><span class="serif ember">questions, answered.</span></h2></div></div>
    <div class="grid g-3">
      <div class="card" data-reveal><h3>Currency &amp; invoicing</h3><p style="margin-top:8px;font-size:14.5px">Invoiced in USD; EUR and GBP arranged on request. Bank transfer, Wise or Upwork if your procurement prefers a platform.</p></div>
      <div class="card" data-reveal><h3>Contracts</h3><p style="margin-top:8px;font-size:14.5px">I can sign your MSA, NDA and standard vendor paperwork, and provide a W-8BEN for US companies.</p></div>
      <div class="card" data-reveal><h3>Milestones</h3><p style="margin-top:8px;font-size:14.5px">50/50 on smaller projects, three milestones on larger ones. Nothing is billed in advance of the work it covers.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Straight answers</span><h2>Pricing questions.</h2></div></div>
    {faq_html(pricing_faq)}
  </div>
</section>

<section style="padding-block:0">{band("Get the number before you commit.", "Thirty minutes on a call is enough for a fixed quote and an honest view of the timeline.", cta="Get a fixed quote")}</section>
'''
page("pricing/index.html", "Pricing | What a Webflow or Framer Site Costs | Anowar Hossain",
     "Webflow and Framer pricing: landing pages from $900, marketing sites $2,500-$6,000, product design $3,000-$7,000. Fixed quotes, no hourly meters.",
     pricing_body, [faq_schema(pricing_faq)], current="/pricing",
     trail=[("Home", "/"), ("Pricing", "/pricing")])

# ─────────────────────────── PROCESS ───────────────────────────
STEPS8 = [
 ("Discovery", "One call. Your goals, constraints, and an honest answer about whether I am the right fit. No pitch."),
 ("Strategy", "Positioning, sitemap, and what the site actually has to achieve &#8212; agreed before design starts."),
 ("UX planning", "Flows and wireframes before any pixels get styled, so structure arguments happen cheaply."),
 ("UI design", "High-fidelity interface built on a component system, reviewed with you as it develops."),
 ("Development", "Pixel-perfect Webflow or Framer build with a demo every week, in your time zone."),
 ("QA", "Every breakpoint, browser and interaction tested, plus a page-speed pass before launch."),
 ("Launch", "Deploy, SEO basics, analytics wired in, redirects mapped, handover docs written."),
 ("Support", "Post-launch support included &#8212; and I stay reachable after it ends."),
]
process_faq = [
 ("How long does a website project take?",
  "Four to six weeks for a typical marketing site, one to two weeks for a landing page, and four to eight weeks for a product design engagement. The timeline is agreed in the quote. In practice content readiness moves dates more often than build time does."),
 ("How does working across time zones actually run?",
  "I am in Dhaka, GMT+6. That overlaps European business hours almost entirely and US East Coast mornings from about 09:00 to 13:00 ET. Messages get a reply within 24 hours, always the same day for European clients, and there is a demo call every week at a time that suits you, not me."),
 ("What do you need from me during a project?",
  "Copy and assets at the agreed points, one decision-maker who can approve, and about an hour a week for the demo. Projects slip when feedback comes from five people with different opinions."),
 ("What if I don&#8217;t like the design?",
  "You see it developing weekly, so there is no reveal moment to dislike. Revisions inside scope are included, and if the direction is wrong we find that out in week one, not week five."),
]
process_body = f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow" data-reveal>Process</span>
      <h1 data-reveal>Same eight steps,<span class="serif">every project.</span></h1>
      <p class="answer" data-reveal>Every engagement runs the same eight stages: discovery, strategy, UX planning,
        UI design, development, QA, launch and support. You get a demo every week, a fixed quote agreed before
        anything starts, and one person answerable for the result from the first call to launch day.</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Start with discovery</a>
        <a class="btn btn-ghost" href="/pricing">See pricing</a>
      </div>
    </div>
    <aside class="hero-aside">{hero_visual("process")}</aside>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">The eight stages</span>
      <h2>How a project runs.</h2></div></div>
    <div class="steps" style="grid-template-columns:repeat(4,minmax(0,1fr))">
    {"".join(f'<div class="step" data-reveal><span class="k">{i+1:02d}</span><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(STEPS8))}
  </div></div>
</section>

<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Time zones</span>
      <h2>Working from GMT+6,<br>for GMT&#8722;5 and GMT+1.</h2></div></div>
    <div class="grid g-3">
      <div class="card" data-reveal><h3>New York</h3><p style="margin-top:8px">Overlap roughly 09:00&#8211;13:00 ET. Demos and calls land in your morning.</p></div>
      <div class="card" data-reveal><h3>London &amp; Berlin</h3><p style="margin-top:8px">Nearly the full working day overlaps. Same-day replies are the norm, not the exception.</p></div>
      <div class="card" data-reveal><h3>Async by default</h3><p style="margin-top:8px">Written updates and recorded walkthroughs, so progress does not wait for a shared hour.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Straight answers</span><h2>Questions about how it runs.</h2></div></div>
    {faq_html(process_faq)}
  </div>
</section>

<section style="padding-block:0">{band("Step one is a call.", "Thirty minutes, no pitch. If I am not the right fit for the project, I will tell you on that call.")}</section>
'''
page("process/index.html", "Process | How a Project Runs | Anowar Hossain",
     "The eight stages of every project: discovery, strategy, UX, UI, build, QA, launch, support. Weekly demos and time-zone overlap with US and EU teams.",
     process_body, [faq_schema(process_faq)], current="/process",
     trail=[("Home", "/"), ("Process", "/process")])

# ─────────────────────────── ABOUT ───────────────────────────
STACK = ["Figma", "Webflow", "Framer", "GSAP", "HTML", "CSS", "JavaScript", "Tailwind CSS", "Relume",
         "Webflow CMS", "Framer CMS", "Finsweet", "Memberstack", "Zapier", "Make", "n8n",
         "Claude Code", "Cursor", "Lovable", "v0"]
about_body = f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow" data-reveal>About</span>
      <h1 data-reveal>A person,<span class="serif">not a vendor.</span></h1>
      <p class="answer" data-reveal>I am Anowar Hossain, a UI/UX designer and Webflow &amp; Framer developer based
        in Dhaka, Bangladesh. For six years I have designed and built digital products for startups and enterprise
        teams across the US, UK, Canada, Australia and Europe &#8212; Top Rated on Upwork with 100% job success
        and 2,237 hours logged. I do the work myself: no agency layer, no outsourcing.</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book a call</a>
        <a class="btn btn-ghost" href="https://www.linkedin.com/in/anowarhdesign/" target="_blank" rel="noopener">Due diligence &#8594; LinkedIn</a>
      </div>
    </div>
    <aside class="hero-aside">
      <img src="/uploads/portrait-760.webp" srcset="/uploads/portrait-380.webp 380w, /uploads/portrait-760.webp 760w"
        sizes="(max-width:1080px) 300px, 400px" width="760" height="760" alt="Anowar Hossain"
        style="border-radius:var(--r-card);width:100%;height:auto" data-reveal>
      {quote("design")}
    </aside>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap grid g-2">
    <div data-reveal>
      <h2 style="font-size:clamp(26px,3vw,36px)">Why one operator</h2>
      <p class="lead" style="margin-top:16px">Most agency work loses something in the handoffs. A strategist hands
        to a designer, a designer hands to a dev shop, and the intent thins out at every step. When the same person
        holds the goal from the first call to launch, decisions are faster, there is nobody to blame, and the design
        that ships is the design that was agreed.</p>
      <p class="lead" style="margin-top:14px">It also means I say no to work I am not right for. That is a feature.
        A project that needs a backend team, a security audit or fifty pages a week of content is not a project
        one person should take, and I will say so on the first call.</p>
    </div>
    <div data-reveal>
      <h2 style="font-size:clamp(26px,3vw,36px)">The teaching habit</h2>
      <p class="lead" style="margin-top:16px">Something shows up repeatedly in my client reviews: I explain the work
        while doing it. One client asked me to teach him Webflow rather than just complete the task, and that became
        the project. Another wrote that I took the time to teach him how Framer works.</p>
      <p class="lead" style="margin-top:14px">That is deliberate. A site your team cannot run without me is a
        liability for you and a support ticket for me. Handover, documentation and editor training are part of
        every build.</p>
    </div>
  </div>
</section>

<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">The record</span><h2>Six years, on the record.</h2></div></div>
    <div class="stats" data-reveal>
      <div class="stat"><div class="n">399+</div><div class="l">Projects completed</div></div>
      <div class="stat"><div class="n">100%</div><div class="l">Job success, Top Rated on Upwork</div></div>
      <div class="stat"><div class="n">2,237</div><div class="l">Hours logged with clients</div></div>
      <div class="stat"><div class="n">6+</div><div class="l">Years designing and building</div></div>
      <div class="stat"><div class="n">5</div><div class="l">Continents worth of clients</div></div>
    </div>
    <div class="grid g-2" style="margin-top:36px">
      <div class="card" data-reveal><span class="mono">Credentials</span>
        <ul style="margin-top:14px;list-style:none;display:flex;flex-direction:column;gap:10px">
          <li>Webflow Experts Certification</li>
          <li>Google UX Design Professional Certificate</li>
          <li>Top Rated on Upwork, 100% job success</li>
        </ul></div>
      <div class="card" data-reveal><span class="mono">Sectors</span>
        <p style="margin-top:14px">AI, SaaS, healthcare and medtech, finance, cybersecurity, Web3, education,
          manufacturing and fine art. Regulated industries are familiar territory, not a surprise.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">The toolkit</span>
      <h2>Tools in active use,<br><span class="serif ember">not collected.</span></h2></div></div>
    <div style="display:flex;flex-wrap:wrap;gap:10px" data-reveal>
      {"".join(f'<span class="chip">{t}</span>' for t in STACK)}
    </div>
  </div>
</section>

<section style="padding-block:0">{band("Let&#8217;s talk about your project.", "Thirty minutes, no pitch, and a straight answer about whether I am the right person for it.")}</section>
'''
page("about/index.html", "About Anowar Hossain | UI/UX Designer &amp; Webflow Developer",
     "Anowar Hossain is a UI/UX designer and Webflow & Framer developer in Dhaka, working with US and European teams. Top Rated on Upwork, 2,237 hours logged.",
     about_body, [{"@type": "AboutPage", "@id": S + "/about#page", "mainEntity": {"@id": S + "/#person"}}],
     current="/about", trail=[("Home", "/"), ("About", "/about")])

# ─────────────────────────── CONTACT ───────────────────────────
contact_body = f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow" data-reveal>Contact</span>
      <h1 data-reveal>Ready when<span class="serif">you are.</span></h1>
      <p class="answer" data-reveal>Book a 30-minute discovery call, or email a brief and get a reply within
        24 hours. Either way you will get an honest read on scope, a timeline, and a fixed quote &#8212; or a
        recommendation to go elsewhere if this is not work I should take.</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book the discovery call</a>
        <a class="btn btn-ghost" href="mailto:hello@anowarhdesign.com?subject=Project%20enquiry">hello@anowarhdesign.com</a>
      </div>
      {BADGE}
    </div>
    <aside class="hero-aside">{hero_visual("contact")}</aside>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Practicalities</span>
      <h2>When and how<br>to reach me.</h2></div></div>
    <div class="grid g-3">
    <div class="card" data-reveal><h3>Overlap hours</h3>
      <ul style="margin-top:12px;list-style:none;display:flex;flex-direction:column;gap:8px;font-size:15px">
        <li>New York &#8212; 09:00&#8211;13:00 ET</li>
        <li>London &#8212; 09:00&#8211;18:00 GMT</li>
        <li>Berlin &#8212; 09:00&#8211;17:00 CET</li>
        <li>Dhaka &#8212; <span id="clock">--:--</span> right now</li>
      </ul></div>
    <div class="card" data-reveal><h3>Response time</h3>
      <p style="margin-top:12px">Within 24 hours, always. Same working day for European clients, next morning for
        the US West Coast.</p></div>
    <div class="card" data-reveal><h3>What to bring</h3>
      <p style="margin-top:12px">What you are building, who it is for, when it has to be live, and roughly what you
        are able to spend. A rough answer to each is enough.</p></div>
  </div></div>
</section>

<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">On the call</span>
      <h2>Thirty minutes,<br>no pitch.</h2></div></div>
    <div class="steps">
      <div class="step" data-reveal><span class="k">01</span><h3>You talk</h3><p>The problem, the product, the constraint you keep hitting.</p></div>
      <div class="step" data-reveal><span class="k">02</span><h3>I ask</h3><p>Enough questions to know whether this is a design problem, a build problem, or neither.</p></div>
      <div class="step" data-reveal><span class="k">03</span><h3>Straight answer</h3><p>Whether I am the right fit, what it would take, and roughly what it costs.</p></div>
      <div class="step" data-reveal><span class="k">04</span><h3>Fixed quote</h3><p>Written up within two working days, with scope and timeline spelled out.</p></div>
    </div>
  </div>
</section>

<section style="padding-top:clamp(48px,6vw,88px);padding-bottom:0">{band("Book the call.", "If I am not the right fit for what you are building, I will say so &#8212; and point you at who is.")}</section>
'''
page("contact/index.html", "Contact | Book a Discovery Call | Anowar Hossain",
     "Book a 30-minute discovery call or email a brief. Replies within 24 hours, overlap hours with New York, London and Berlin, and a fixed quote within two working days.",
     contact_body, [{"@type": "ContactPage", "@id": S + "/contact#page", "mainEntity": {"@id": S + "/#person"}}],
     current="", trail=[("Home", "/"), ("Contact", "/contact")])

# ─────────────────────────── sitemap + llms.txt ───────────────────────────
URLS = ["/", "/services", "/services/product-design", "/services/webflow-development",
        "/services/framer-development", "/services/ai-product-builds", "/work", "/pricing",
        "/process", "/about", "/contact"]
sm = ['<?xml version="1.0" encoding="UTF-8"?>',
      '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in URLS:
    pri = "1.0" if u == "/" else ("0.9" if u.startswith("/services") else "0.7")
    sm.append(f"  <url><loc>{S}{u}</loc><changefreq>monthly</changefreq><priority>{pri}</priority></url>")
sm.append("</urlset>")
(ROOT / "sitemap.xml").write_text("\n".join(sm) + "\n", encoding="utf-8")

(ROOT / "llms.txt").write_text(f"""# Anowar Hossain

> UI/UX designer and Webflow & Framer developer based in Dhaka, Bangladesh, working with SaaS, AI,
> healthcare and enterprise teams across the US, UK, Canada, Australia and Europe. Top Rated on Upwork
> with 100% job success and 2,237 hours logged. One operator: design and development by the same person,
> quoted as a fixed price.

## Services
- Product design (UX + UI in Figma, developer-ready): $3,000-$7,000, 4-8 weeks. {S}/services/product-design
- Webflow development (editor-proof CMS, migration, QA): $2,500-$6,000, 4-6 weeks. {S}/services/webflow-development
- Framer development (landing pages, launch sites, motion): from $900, 1-2 weeks. {S}/services/framer-development
- AI product builds (finishing Lovable / v0 / Claude Code prototypes): $1,500-$4,000, 2-5 weeks. {S}/services/ai-product-builds

## Facts
- Based in Dhaka, Bangladesh (GMT+6); overlaps New York mornings (09:00-13:00 ET) and full European business hours.
- Replies within 24 hours. Weekly demo calls. Fixed quotes, no hourly billing.
- Credentials: Webflow Experts Certification; Google UX Design Professional Certificate; Top Rated on Upwork.
- Clients include CADDi, Assistments, Stratus Neuro, SecureCDP, UberStrategist, Fit3D, 0xBow.

## Pages
- Home: {S}/
- Services: {S}/services
- Work: {S}/work
- Pricing: {S}/pricing
- Process: {S}/process
- About: {S}/about
- Contact: {S}/contact

## Contact
- Email: hello@anowarhdesign.com
- Discovery call: https://cal.com/anowarhdesign/discovery
""", encoding="utf-8")

print("work, pricing, process, about, contact, sitemap, llms.txt built")
