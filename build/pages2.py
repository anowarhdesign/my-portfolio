#!/usr/bin/env python3
from build import *   # noqa
from pages import svc_schema   # noqa
from graphics import hero_visual   # noqa

S = SITE
case_by = {c[0]: c for c in CASES}

def service_page(slug, nav_title, h1_a, h1_b, answer, fits, not_fits, included, steps,
                 quote_key, case_names, price_line, price_notes, faq, desc, title, service_name):
    body = f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow" data-reveal>{nav_title}</span>
      <h1 data-reveal>{h1_a}<span class="serif">{h1_b}</span></h1>
      <p class="answer" data-reveal>{answer}</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book the discovery call</a>
        <a class="btn btn-ghost" href="mailto:hello@anowarhdesign.com?subject=Project%20enquiry">Email a brief</a>
      </div>
    </div>
    <aside class="hero-aside">{hero_visual(slug)}</aside>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap grid g-2">
    <div class="card" data-reveal>
      <span class="mono">A good fit when</span>
      <ul style="margin-top:14px;list-style:none;display:flex;flex-direction:column;gap:12px">
        {"".join(f'<li style="display:flex;gap:10px"><span style="color:var(--ember)">&#10003;</span><span>{x}</span></li>' for x in fits)}
      </ul>
    </div>
    <div class="card" data-reveal>
      <span class="mono">Probably not for you if</span>
      <ul style="margin-top:14px;list-style:none;display:flex;flex-direction:column;gap:12px">
        {"".join(f'<li style="display:flex;gap:10px"><span style="color:var(--ash-2)">&#8212;</span><span>{x}</span></li>' for x in not_fits)}
      </ul>
    </div>
  </div>
</section>

<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">What&#8217;s included</span>
      <h2>Everything in<br>the fixed quote.</h2></div></div>
    <div style="display:flex;flex-wrap:wrap;gap:10px" data-reveal>
      {"".join(f'<span class="chip">{x}</span>' for x in included)}
    </div>
    <div class="steps" style="margin-top:44px">
      {"".join(f'<div class="step" data-reveal><span class="k">{i+1:02d}</span><h3>{t}</h3><p>{d}</p></div>' for i, (t, d) in enumerate(steps))}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Proof</span>
      <h2>Work of this<br><span class="serif ember">exact kind.</span></h2></div>
    <a class="btn btn-ghost" href="/work">All work</a></div>
    <div class="grid g-2">{"".join(case_card(case_by[n]) for n in case_names)}</div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Price</span><h2>{price_line}</h2></div>
    <a class="btn btn-ghost" href="/pricing">Full pricing</a></div>
    <div class="grid g-2">
      <div class="card" data-reveal><span class="mono">What moves the number</span>
        <ul style="margin-top:14px;list-style:none;display:flex;flex-direction:column;gap:10px">
          {"".join(f'<li style="display:flex;gap:10px"><span style="color:var(--ember)">&#8226;</span><span>{x}</span></li>' for x in price_notes)}
        </ul></div>
      <div class="card" data-reveal><span class="mono">What is never extra</span>
        <ul style="margin-top:14px;list-style:none;display:flex;flex-direction:column;gap:10px">
          <li style="display:flex;gap:10px"><span style="color:var(--ember)">&#8226;</span><span>Revisions inside the agreed scope</span></li>
          <li style="display:flex;gap:10px"><span style="color:var(--ember)">&#8226;</span><span>Weekly demos and progress calls</span></li>
          <li style="display:flex;gap:10px"><span style="color:var(--ember)">&#8226;</span><span>Post-launch support and handover docs</span></li>
          <li style="display:flex;gap:10px"><span style="color:var(--ember)">&#8226;</span><span>Straight answers about what will not work</span></li>
        </ul></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Straight answers</span><h2>Questions about {nav_title.lower()}.</h2></div></div>
    {faq_html(faq)}
  </div>
</section>

<section style="padding-block:0">{band("Tell me what you&#8217;re building.", "A 30-minute call, a fixed quote, and an honest answer about whether this is the right service for the problem.")}</section>
'''
    page(f"services/{slug}/index.html", title, desc, body,
         [svc_schema(service_name, desc, price_line), faq_schema(faq)],
         current="/services",
         trail=[("Home", "/"), ("Services", "/services"), (nav_title, f"/services/{slug}")])

# ─────────────────── product design ───────────────────
service_page(
 "product-design", "Product design",
 "Find where users<br>struggle. ", "Fix why.",
 "Product design for SaaS and mobile teams: UX research, flows, wireframes and high-fidelity interface design in Figma, delivered developer-ready with a component system. A typical engagement runs two to four weeks and costs $1,500&#8211;$3,500, designed against your business goals rather than a moodboard.",
 ["You have a product and a goal but no design team",
  "Your interface grew feature by feature and now confuses users",
  "Engineering is ready and needs a file they can build from",
  "You need a design system, not another one-off screen"],
 ["You want pixel art or brand identity only",
  "You need a 24-hour turnaround on a full product",
  "You want a designer to execute without asking why"],
 ["UX audit", "User research", "Information architecture", "User flows", "Wireframes",
  "High-fidelity UI", "Responsive design", "Design system", "Interactive prototype", "Developer handoff"],
 [("Understand", "Your goals, your users, your constraints, and what the current interface gets wrong."),
  ("Structure", "Flows and wireframes agreed before a single pixel gets styled."),
  ("Design", "High-fidelity interface built on a component system, reviewed with you weekly."),
  ("Hand off", "Developer-ready Figma, documented components, and answers during the build.")],
 "design", ["0xBow", "SecureCDP"],
 "$1,500&#8211;$3,500",
 ["Number of screens and states", "Research depth &#8212; interviews or desk research",
  "Whether a design system exists already", "Prototype fidelity"],
 [("How long does a product design engagement take?",
   "Two to four weeks for most SaaS and mobile projects. A focused audit and redesign of an existing flow can run one to one-and-a-half weeks; a full product with research, a design system and a prototype runs closer to four."),
  ("Do you do user research?",
   "Yes, scaled to the project. That may be interviews with your existing users, a heuristic audit against usability principles, analytics review, or competitor teardowns. I will tell you which is worth paying for and which is not."),
  ("Will my developers be able to build it?",
   "That is the deliverable. Files ship with a component library, documented spacing and type scales, states and responsive behaviour, and I stay reachable during the build to answer questions."),
  ("Can you build the design as well?",
   "Yes &#8212; most clients run design straight into a Webflow or Framer build with me, which removes the handoff entirely. If your engineers are building it, the file is made for them instead."),
  ("Do you work in Figma?",
   "Always. Every file is yours, organised, and editable by whoever comes after me.")],
 "UX and interface design for SaaS and mobile products, delivered developer-ready in Figma. Two to four weeks, $1,500-$3,500, fixed quote.",
 "Product Design for SaaS &amp; Mobile | Anowar Hossain",
 "Product design")

# ─────────────────── webflow ───────────────────
service_page(
 "webflow-development", "Webflow development",
 "A site your team<br>can run ", "without me.",
 "Production Webflow development for marketing sites: pixel-perfect builds from your design or mine, with an editor-proof CMS your marketing team runs alone. A 6&#8211;12 page site with CMS runs $1,250&#8211;$3,000 and takes two to three weeks, including migration, QA on every breakpoint and launch support.",
 ["You have a Figma file and need it built properly",
  "Your marketing team is blocked on a developer for every edit",
  "You are moving off WordPress and want to stop patching plugins",
  "Your current site is slow and fails Core Web Vitals"],
 ["You need a web app with authentication and complex logic",
  "You want the cheapest possible template swap",
  "You need a platform other than Webflow"],
 ["Pixel-perfect development", "CMS setup", "Custom interactions", "Responsive optimization",
  "SEO basics", "Finsweet attributes", "Memberstack", "Zapier / Make", "Migration", "QA &amp; testing", "Launch support"],
 [("Structure", "Page inventory, CMS collections and the editing model your team will actually use."),
  ("Build", "Pixel-perfect development with clean classes, reusable components and real interactions."),
  ("Test", "Every breakpoint, browser and interaction, plus a page-speed pass before launch."),
  ("Hand over", "Editor training, documentation, and support after you go live.")],
 "webflow", ["Stratus Neuro", "Assistments"],
 "$1,250&#8211;$3,000",
 ["Page count and template variety", "CMS collections and their relationships",
  "Custom animation and interaction work", "Content migration volume", "Integrations &#8212; Memberstack, Zapier, analytics"],
 [("How much does a Webflow website cost?",
   "A 6&#8211;12 page marketing site with a CMS runs $1,250&#8211;$3,000. A single landing page starts at $450. An enterprise site with many templates, heavy migration and integrations runs higher; you get a fixed quote after the discovery call, not an hourly meter."),
  ("How long does a Webflow build take?",
   "Two to three weeks for a typical marketing site from an agreed design. A landing page is three to seven days. Content readiness is usually what moves the date, not the build."),
  ("Can my team edit the site afterwards?",
   "Yes &#8212; that is the point of the CMS structure. Collections are built so a non-technical editor can add a post, a case study or a team member without touching layout, and I train the editors before handover. One client asked me to teach him instead of doing the task, which is on the record in my Upwork reviews."),
  ("Do you migrate from WordPress?",
   "Yes. Content, URLs and redirects are mapped before anything moves, so rankings survive the switch. Migration volume is one of the variables in the quote."),
  ("Will the site pass Core Web Vitals?",
   "That is part of QA, not an upsell. Images are sized and served in modern formats, scripts are deferred, and the build is checked against Lighthouse before launch.")],
 "Production Webflow development with an editor-proof CMS. 6-12 page marketing sites, $1,250-$3,000, two to three weeks. Migration, QA and launch support included.",
 "Webflow Developer for SaaS &amp; B2B Teams | Anowar Hossain",
 "Webflow development")

# ─────────────────── framer ───────────────────
service_page(
 "framer-development", "Framer development",
 "Launch-ready at<br>startup ", "speed.",
 "Framer development for landing pages and marketing sites that have to ship on a date: a launch page live in three to seven days from $450, a full marketing site in one-and-a-half to two weeks. Built for fundraises, product launches and announcements, with real motion, a working CMS and performance that holds up.",
 ["You have a launch date and it is close",
  "You want motion and polish without a custom front-end build",
  "You are raising and the site has to look funded",
  "You want to edit and publish without a developer"],
 ["Your site needs deep CMS relationships or heavy integrations",
  "You have 50+ pages of structured content",
  "You need self-hosted infrastructure"],
 ["Landing pages", "Marketing websites", "Custom components", "Framer CMS", "Advanced animation",
  "GSAP integrations", "Responsive optimization", "Performance", "Launch support"],
 [("Scope in a call", "What has to be true on launch day, and what can follow the week after."),
  ("Design or adapt", "From your Figma file, or designed here first &#8212; whichever is faster for the date."),
  ("Build with motion", "Components, CMS and interactions built in Framer, demoed as they land."),
  ("Ship", "Domain, analytics, QA on every breakpoint, and support through launch week.")],
 "framer", ["0xBow", "Eric Kanigan"],
 "From $450",
 ["Page count and section variety", "How much custom motion is involved",
  "Whether a design exists or starts here", "CMS needs", "How compressed the timeline is"],
 [("Framer or Webflow &#8212; which should I choose?",
   "Framer wins on speed to launch and motion: it is the right call for a launch page, a fundraise site or an announcement with a fixed date. Webflow wins when a marketing team owns growing content, you need structured CMS relationships, or the site will pass twenty pages. If Framer is the wrong tool for your case, I will say so on the call."),
  ("How fast can a Framer site go live?",
   "A focused landing page can be live in three to seven days from an agreed design, a full marketing site in one-and-a-half to two weeks. The bottleneck is almost always copy and assets, so we agree those first."),
  ("Can I edit the site myself afterwards?",
   "Yes. Framer&#8217;s editor is genuinely usable by non-developers, the CMS is set up for your content model, and I walk your team through it at handover."),
  ("Can you fix or finish an existing Framer site?",
   "Yes, and it is regular work &#8212; responsive bugs, broken interactions, half-finished templates, performance problems. Several of my public reviews are exactly this."),
  ("Do you work with GSAP inside Framer?",
   "Where the built-in motion cannot do it. Custom code components are fine; they just need to survive a client editing the page afterwards, which shapes how they are built.")],
 "Framer development for landing pages and marketing sites. Live in three to seven days, from $450. Custom motion, CMS, launch support for startups and fundraises.",
 "Framer Developer for Hire | Anowar Hossain",
 "Framer development")

# ─────────────────── ai product builds ───────────────────
service_page(
 "ai-product-builds", "AI product builds",
 "AI got you 70%.<br>", "The rest is the job.",
 "Design and production work on apps built with Lovable, v0, Bolt or Claude Code. AI tools produce a working prototype in a weekend; what they do not produce is a considered interface, a real component system, working responsive behaviour or something a paying customer trusts. That pass runs $750&#8211;$2,000 and takes one to two-and-a-half weeks.",
 ["Your Lovable or v0 app works but looks like a template",
  "You want an MVP designed properly, then built fast",
  "You shipped to users and the interface is the complaint",
  "You need an internal tool that your team will actually use"],
 ["You need a security audit or penetration testing",
  "You want backend architecture rebuilt from scratch",
  "You expect AI tools to make the project free"],
 ["Interface redesign", "Component system", "Responsive pass", "Accessibility pass",
  "Brand application", "Marketing site around the app", "Design-led MVP build", "Handover documentation"],
 [("Audit", "What the prototype gets right, what breaks under real use, and what is worth keeping."),
  ("Design", "A real interface and component system &#8212; in Figma or straight in the code, whichever is faster."),
  ("Rebuild the surface", "Layout, states, responsive behaviour and accessibility, applied across the app."),
  ("Hand over", "Documented components and a build your next developer can read.")],
 "startup", ["SecureCDP", "0xBow"],
 "$750&#8211;$2,000",
 ["How many screens the app has", "Whether the underlying code is salvageable",
  "How much of the design system already exists", "Whether a marketing site is included"],
 [("Can you fix an app built with Lovable?",
   "Yes &#8212; it is the most common version of this work. Typically the logic works and the interface does not: generic layout, no design system, broken responsive behaviour, no empty or error states. I redesign the surface and rebuild it properly, keeping what works underneath."),
  ("Do you build MVPs with AI tools?",
   "Yes, design-led. The design is decided first, then built with Claude Code, Lovable or Cursor, which is far faster than hand-coding and far better than prompting your way to a layout. You get something maintainable with a written handover."),
  ("Is AI-built code safe to ship?",
   "Not automatically. Published research in 2026 found a large share of AI-generated code samples carrying common security flaws, and AI app builders have shipped apps with exposed user data. I handle design, front-end and production polish; anything touching authentication, payments or personal data gets reviewed by a security specialist I bring in. I will not pretend that is my discipline."),
  ("Which tools do you actually use?",
   "Claude Code and Cursor for building, Lovable and v0 for rapid prototypes, Figma for design. Tools change every few months; the judgment about what to keep and what to throw away does not."),
  ("Is this cheaper than a normal build?",
   "Often, because the prototype already answers what the product should do. It is not free: the last 30% &#8212; the part your customers judge you on &#8212; is the part that takes real time.")],
 "Design and production work on AI-built apps: Lovable, v0, Bolt and Claude Code prototypes taken to something you can ship. $750-$2,000, one to two-and-a-half weeks.",
 "AI Product Builds | Finish Your Lovable App | Anowar Hossain",
 "AI product builds")

print("service pages built")
