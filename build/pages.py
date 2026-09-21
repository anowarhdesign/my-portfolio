#!/usr/bin/env python3
from build import *   # noqa
from graphics import hero_visual   # noqa

S = SITE

def svc_schema(name, desc, price):
    return {"@type": "Service", "name": name, "description": desc,
            "serviceType": name, "provider": {"@id": S + "/#person"},
            "areaServed": ["US", "GB", "CA", "AU", "DE", "NL"],
            "offers": {"@type": "Offer", "priceCurrency": "USD", "description": price}}

# ─────────────────────────── HOME ───────────────────────────
home_faq = [
 ("Who is Anowar Hossain?",
  "Anowar Hossain is a UI/UX designer and Webflow &amp; Framer developer based in Dhaka, Bangladesh, working with SaaS, AI, healthcare and enterprise teams across the US, UK and Europe. He is Top Rated on Upwork with 100% job success and 2,237 hours logged, and he designs and builds every project himself &#8212; no agency layer, no outsourcing."),
 ("Can one person really design and build a whole site?",
  "Yes, and that is the point. A single operator holds the goals from the first call to launch, so nothing is lost between a strategist, a designer and a dev shop. It means faster decisions, one person accountable for the result, and a build where the design intent actually survives."),
 ("What does a project cost?",
  "A landing page starts at $450, a 6&#8211;12 page marketing site with CMS runs $1,250&#8211;$3,000, and a product design engagement runs $1,500&#8211;$3,500. Every project is a fixed quote agreed after the discovery call &#8212; no hourly meters."),
]

home_body = f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      {BADGE}
      <h1 data-reveal>Design that<br>earns trust.<span class="serif">Built to keep it.</span></h1>
      <p class="lead" data-reveal>UI/UX design and Webflow &amp; Framer development for SaaS, AI and enterprise
        teams &#8212; one operator, no handoffs, fixed quotes. Working with companies across the US, UK and Europe.</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book the discovery call</a>
        <a class="btn btn-ghost" href="/work">See the work</a>
      </div>
      {LOGOWALL}
    </div>
    <aside class="hero-aside">{hero_visual("home")}</aside>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div>
      <span class="mono">What I do</span>
      <h2>One operator.<br><span class="serif ember">No handoffs.</span></h2>
    </div>
    <a class="btn btn-ghost" href="/services">All services</a></div>
    <p class="answer" data-reveal>I design and build digital products end to end: UX and interface design in Figma,
      then production development in Webflow or Framer. You brief one person, that person designs the interface,
      builds it, and answers for the result &#8212; which is why founders come to me instead of an agency.</p>
    <div class="grid g-4" style="margin-top:36px">
      {"".join(service_card(s, ember=(s[2] == "04")) for s in SERVICES)}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div>
      <span class="mono">Selected work</span>
      <h2>Real briefs.<br><span class="serif ember">Shipped to production.</span></h2>
    </div>
    <a class="btn btn-ghost" href="/work">All work</a></div>
    <div class="grid g-3">{"".join(case_card(c) for c in CASES[:3])}</div>
  </div>
</section>

<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div>
      <span class="mono">The record</span>
      <h2>Don&#8217;t take the site&#8217;s<br>word for it.</h2>
    </div></div>
    <div class="stats" data-reveal>
      <div class="stat"><div class="n">399+</div><div class="l">Projects completed</div></div>
      <div class="stat"><div class="n">100%</div><div class="l">Job success, Top Rated on Upwork</div></div>
      <div class="stat"><div class="n">2,237</div><div class="l">Hours logged with clients</div></div>
      <div class="stat"><div class="n">6+</div><div class="l">Years doing this work</div></div>
      <div class="stat"><div class="n">US &#183; EU</div><div class="l">Where most clients are</div></div>
    </div>
    <div class="grid g-3" style="margin-top:32px">
      {quote("webflow")}{quote("rigor")}{quote("listen")}
    </div>
    <p class="mono" style="margin-top:24px">All quotes are public Upwork reviews, verbatim</p>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div>
      <span class="mono">Working together</span>
      <h2>Predictable, on<br>two continents.</h2>
    </div>
    <a class="btn btn-ghost" href="/process">The full process</a></div>
    <div class="steps">
      <div class="step" data-reveal><span class="k">01</span><h3>Discovery call</h3>
        <p>Your goals, constraints, and an honest answer about whether I am the right fit.</p></div>
      <div class="step" data-reveal><span class="k">02</span><h3>Fixed quote</h3>
        <p>Scope, timeline and price agreed up front. No hourly meter, no scope surprises.</p></div>
      <div class="step" data-reveal><span class="k">03</span><h3>Weekly demos</h3>
        <p>You see progress every week in your own time zone, not a silent month.</p></div>
      <div class="step" data-reveal><span class="k">04</span><h3>Launch &amp; handover</h3>
        <p>QA on every breakpoint, analytics wired in, docs so your team can run it.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div>
      <span class="mono">Straight answers</span>
      <h2>The questions buyers<br>actually ask.</h2>
    </div></div>
    {faq_html(home_faq)}
  </div>
</section>

<section style="padding-block:0">{band("Ready when you are.", "One call. Your goals, your constraints, and an honest answer about whether I am the right fit. No pitch, no obligation.")}</section>
'''

page("index.html",
     "Anowar Hossain | UI/UX Designer &amp; Webflow Developer",
     "UI/UX designer and Webflow &amp; Framer developer for SaaS, AI and enterprise teams in the US and Europe. Top Rated on Upwork. Fixed quotes, one operator.",
     home_body,
     [{"@type": "ProfessionalService", "@id": S + "/#business", "name": "Anowar Hossain",
       "description": "UI/UX design and Webflow & Framer development for SaaS, AI and enterprise teams.",
       "url": S + "/", "founder": {"@id": S + "/#person"},
       "priceRange": "$450-$6,000",
       "areaServed": ["US", "GB", "CA", "AU", "DE", "NL"]},
      {"@type": "WebSite", "@id": S + "/#website", "url": S + "/",
       "name": "Anowar Hossain", "publisher": {"@id": S + "/#person"}},
      faq_schema(home_faq),
      *review_schema(["webflow", "rigor", "listen"])],
     current="/")

# ─────────────────────────── SERVICES HUB ───────────────────────────
hub_faq = [
 ("Do you design and develop, or only one?",
  "Both, in one engagement. Most projects run design straight into build, which removes the handoff where intent usually gets lost. I also take build-only work from an existing Figma file, and design-only work that another team will implement."),
 ("Which platform should I choose &#8212; Webflow or Framer?",
  "Framer wins on speed to launch and motion: a marketing site or landing page live in three to seven days. Webflow wins when a marketing team owns the content, the site grows past twenty pages, or you need structured CMS collections and integrations."),
 ("Can you work with my existing team?",
  "Yes. I join at whatever stage needs the hands &#8212; designing against a developer&#8217;s constraints, building from your designer&#8217;s file, or taking a stalled project the rest of the way."),
]

hub_body = f'''
<section class="hero">
  <div class="wrap hero-in">
    <div class="hero-copy">
      <span class="eyebrow" data-reveal>Services</span>
      <h1 data-reveal>Design and build,<span class="serif">under one roof.</span></h1>
      <p class="answer" data-reveal>Four ways to work together: product design in Figma, Webflow development,
        Framer development, and finishing AI-built prototypes. Every engagement is a fixed quote agreed after a
        discovery call, run by one person from brief to launch, typically in two to three weeks.</p>
      <div class="cta-row" data-reveal>
        <a class="btn btn-primary" href="https://cal.com/anowarhdesign/discovery" target="_blank" rel="noopener">Book the discovery call</a>
        <a class="btn btn-ghost" href="/pricing">See pricing</a>
      </div>
    </div>
    <aside class="hero-aside">{hero_visual("services")}</aside>
  </div>
</section>

<section style="padding-top:0">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">The four</span>
      <h2>What I&#8217;m hired for.</h2></div></div>
    <div class="grid g-2">{"".join(service_card(s, ember=(s[2] == "04")) for s in SERVICES)}</div>
  </div>
</section>

<section class="sec-ink">
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Choosing</span>
      <h2>Which one do you<br>actually need?</h2></div></div>
    <div class="grid g-3">
      <div class="card" data-reveal><h3>You have a design already</h3>
        <p style="margin-top:10px">Webflow or Framer development. Send the Figma file; you get a production build
          that matches it and a CMS your team can run.</p></div>
      <div class="card" data-reveal><h3>You have a product, not a design</h3>
        <p style="margin-top:10px">Product design first. Research, flows and interface work, then the build &#8212;
          or a developer-ready Figma file if your engineers take it from there.</p></div>
      <div class="card" data-reveal><h3>You have an AI-built prototype</h3>
        <p style="margin-top:10px">AI product builds. The Lovable or v0 output works but looks generic; this is the
          design and production pass that makes it shippable.</p></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="sec-head"><div><span class="mono">Straight answers</span><h2>Common questions.</h2></div></div>
    {faq_html(hub_faq)}
  </div>
</section>

<section style="padding-block:0">{band("Not sure which fits?", "Book the call and describe the problem &#8212; I will tell you which of the four it is, or that it is none of them.")}</section>
'''

page("services/index.html",
     "Services | Design &amp; Webflow Development | Anowar Hossain",
     "Product design, Webflow and Framer development, and AI product builds. One operator, fixed quotes, two to three weeks, for teams in the US and Europe.",
     hub_body,
     [faq_schema(hub_faq)],
     current="/services",
     trail=[("Home", "/"), ("Services", "/services")])

print("home + services hub built")
