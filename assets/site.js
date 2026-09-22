/* ══════════════════════════════════════════════════════════
   site.js — no dependencies. Spring cursor, elastic preview,
   line reveals, counters, magnetic buttons.
   ══════════════════════════════════════════════════════════ */
(function () {
  "use strict";
  var reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = matchMedia("(pointer: fine)").matches;
  var doc = document.documentElement;

  /* ─── reveal on scroll ─── */
  var revealables = document.querySelectorAll("[data-reveal], .lines");
  if (!("IntersectionObserver" in window) || reduced) {
    revealables.forEach(function (el) { el.classList.add("in"); });
  } else {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.06 });
    revealables.forEach(function (el) { io.observe(el); });
  }

  /* ─── count-up stats ─── */
  var nums = document.querySelectorAll("[data-count]");
  if (nums.length && !reduced && "IntersectionObserver" in window) {
    var cio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        cio.unobserve(e.target);
        var el = e.target;
        var target = parseFloat(el.dataset.count);
        var suffix = el.dataset.suffix || "";
        var t0 = performance.now(), dur = 1500;
        (function step(now) {
          var p = Math.min(1, (now - t0) / dur);
          var eased = 1 - Math.pow(1 - p, 4);
          var v = Math.round(target * eased);
          el.textContent = v.toLocaleString("en-US") + suffix;
          if (p < 1) requestAnimationFrame(step);
        })(t0);
      });
    }, { threshold: 0.4 });
    nums.forEach(function (n) { cio.observe(n); });
  }

  /* ─── wordmark wink: a reusable trigger, since three separate things
     now ask the logo to wink (scroll-into-mini, first-visit peek, idle) ─── */
  function wink(el, ms) {
    if (!el || reduced) return;
    el.classList.add("wink");
    clearTimeout(el._winkT);
    el._winkT = setTimeout(function () { el.classList.remove("wink"); }, ms || 650);
  }
  function currentWordmark() {
    if (nav && nav.classList.contains("hide") && navMiniMark) return navMiniMark;
    return nav ? nav.querySelector(".wordmark") : null;
  }

  /* ─── nav: hide on scroll down, dock reveal, progress ─── */
  var nav = document.querySelector(".nav");
  var navMini = document.querySelector(".nav-mini");
  var navMiniMark = navMini && navMini.querySelector(".wordmark");
  var dock = document.querySelector(".dock");
  var bar = document.querySelector(".progress i");
  var last = 0, wasHidden = false;
  function onScroll() {
    var y = scrollY;
    if (nav) {
      nav.classList.toggle("stuck", y > 20);
      var hidden = y > 420 && y > last;
      nav.classList.toggle("hide", hidden);
      if (navMini) {
        navMini.classList.toggle("show", hidden);
        // the full nav slides away in its place, so the mini pill is most
        // visitors' only chance to see the logo's face at all — wink it
        // once, the instant it appears, rather than leaving it static
        if (hidden && !wasHidden) wink(navMiniMark);
      }
      wasHidden = hidden;
    }
    // tied to the same "hidden" state as the nav, not a separate scroll
    // threshold — otherwise the dock and the full nav can both be on
    // screen at once (e.g. scroll down past 640, then back up a little:
    // the full nav returns immediately, but the old y > 640 check kept
    // the dock up regardless of direction)
    if (dock) dock.classList.toggle("up", nav ? nav.classList.contains("hide") : y > 640);
    if (bar) {
      var h = document.body.scrollHeight - innerHeight;
      bar.style.width = (h > 0 ? (y / h) * 100 : 0) + "%";
    }
    last = y;
  }
  addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ─── logo, three more ways to see it wink without hovering ─── */
  if (!reduced) {
    // 1. first-visit peek — most visitors never scroll far enough to
    // trigger the mini-pill wink, and touch devices never hover at all,
    // so give everyone one unprompted look shortly after landing
    setTimeout(function () { wink(currentWordmark(), 700); }, 2200);

    // 2. idle wink — a small "still here" beat after a stretch of no
    // activity at all; pauses while the tab isn't in focus and resets
    // on any real interaction so it never fires mid-read or mid-scroll
    var idleT;
    function scheduleIdleWink() {
      clearTimeout(idleT);
      idleT = setTimeout(function () {
        if (!document.hidden) wink(currentWordmark(), 700);
        scheduleIdleWink();
      }, 26000);
    }
    ["mousemove", "touchstart", "keydown", "scroll", "click"].forEach(function (evt) {
      addEventListener(evt, scheduleIdleWink, { passive: true });
    });
    scheduleIdleWink();

    // 3. click-wink — every click on any logo winks it once, held for one
    // short beat before navigating so the wink actually gets seen instead
    // of firing into a page that's already gone.
    var NAV_DELAY = 320;
    document.querySelectorAll(".wordmark").forEach(function (wm) {
      wm.addEventListener("click", function (e) {
        e.preventDefault();
        wink(wm, 700);
        var href = wm.getAttribute("href");
        setTimeout(function () { location.href = href; }, NAV_DELAY);
      });
    });
  }

  /* ─── section theme awareness for the cursor ─── */
  if (!reduced && "IntersectionObserver" in window) {
    var inkio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.intersectionRatio > 0.5) doc.classList.add("on-ink");
        else if (e.intersectionRatio < 0.2) doc.classList.remove("on-ink");
      });
    }, { threshold: [0.2, 0.5, 0.8] });
    document.querySelectorAll(".sec-ink").forEach(function (s) { inkio.observe(s); });
  }

  /* ─── spring helper ─── */
  function spring(stiffness) {
    var cur = { x: 0, y: 0 }, tgt = { x: 0, y: 0 };
    return {
      to: function (x, y) { tgt.x = x; tgt.y = y; },
      tick: function () {
        cur.x += (tgt.x - cur.x) * stiffness;
        cur.y += (tgt.y - cur.y) * stiffness;
        return cur;
      },
      jump: function (x, y) { cur.x = tgt.x = x; cur.y = tgt.y = y; }
    };
  }

  var ring = document.querySelector(".cursor");
  var dot = document.querySelector(".cursor-dot");
  var peek = document.getElementById("peek");
  var label = ring && ring.querySelector(".lbl");

  if (fine && !reduced && ring && dot) {
    var sRing = spring(0.16), sDot = spring(0.42), sPeek = spring(0.11);
    var mx = innerWidth / 2, my = innerHeight / 2, peekOn = false, prevX = mx;

    addEventListener("pointermove", function (e) {
      mx = e.clientX; my = e.clientY;
      doc.classList.add("has-cursor");
      sRing.to(mx, my); sDot.to(mx, my);
      sPeek.to(mx + 28, my - 110);
    }, { passive: true });

    (function frame() {
      var r = sRing.tick(), d = sDot.tick();
      ring.style.transform = "translate3d(" + r.x + "px," + r.y + "px,0)";
      dot.style.transform = "translate3d(" + d.x + "px," + d.y + "px,0)";
      if (peek) {
        var p = sPeek.tick();
        /* velocity → skew + rotation, the elastic feel */
        var vx = p.x - prevX; prevX = p.x;
        var rot = Math.max(-14, Math.min(14, vx * 0.42));
        var squash = 1 + Math.min(0.13, Math.abs(vx) * 0.004);
        peek.style.transform = "translate3d(" + p.x + "px," + p.y + "px,0) rotate(" + rot + "deg)" +
          " scale(" + (peekOn ? squash : 0.86) + "," + (peekOn ? 2 - squash : 0.86) + ")";
      }
      requestAnimationFrame(frame);
    })();

    /* cursor states: quiet ring on links, labelled disc only where a label is declared */
    var quiet = ".nav a, .dock a, .foot a, .navlinks a, .wordmark, summary";
    document.querySelectorAll("a,button,summary,[data-cursor]").forEach(function (el) {
      var labelled = el.dataset.cursor;
      var small = el.matches(quiet) || el.closest(".nav,.dock,.foot") !== null;
      el.addEventListener("pointerenter", function () {
        if (labelled && !small) {
          ring.classList.add("hot");
          doc.classList.add("hide-dot");
          if (label) label.textContent = labelled;
        } else if (!small) {
          ring.classList.add("hover");
        } else {
          /* the ring stays out of the way here so it never sits over dense nav/footer
             text, but the dot still gives a small ember pulse instead of doing nothing */
          dot.classList.add("pulse");
        }
      });
      el.addEventListener("pointerleave", function () {
        ring.classList.remove("hot", "hover");
        dot.classList.remove("pulse");
        doc.classList.remove("hide-dot");
        if (label) label.textContent = "";
      });
    });

    /* elastic project preview */
    if (peek) {
      var host = peek.querySelector(".host");
      var shot = peek.querySelector(".shot");
      var pname = peek.querySelector(".name");
      document.querySelectorAll("[data-peek]").forEach(function (el) {
        el.addEventListener("pointerenter", function () {
          peek.style.background = el.dataset.peek;
          if (host) host.textContent = el.dataset.host || "";
          if (pname) pname.textContent = el.dataset.peekName || "";
          var src = el.dataset.peekImg;
          peek.classList.toggle("has-shot", !!src);
          if (shot) { shot.src = src || ""; shot.alt = src ? (el.dataset.peekName || "") + " website" : ""; }
          peekOn = true; peek.classList.add("on");
          sPeek.jump(mx + 28, my - 110);
        });
        el.addEventListener("pointerleave", function () {
          peekOn = false; peek.classList.remove("on");
        });
      });
    }

    /* magnetic buttons, plus a gentler version on the dock links so that quiet strip
       of nav isn't the one place on the site the cursor has zero effect on anything */
    document.querySelectorAll(".btn[data-magnet], .dock a").forEach(function (el) {
      var isDock = el.closest(".dock") !== null;
      var pull = isDock ? 0.16 : 0.28, pullY = isDock ? 0.22 : 0.42;
      var raf = null;
      el.addEventListener("pointermove", function (e) {
        var b = el.getBoundingClientRect();
        var dx = (e.clientX - (b.left + b.width / 2)) * pull;
        var dy = (e.clientY - (b.top + b.height / 2)) * pullY;
        cancelAnimationFrame(raf);
        raf = requestAnimationFrame(function () {
          el.style.transform = "translate(" + dx + "px," + dy + "px)";
        });
      });
      el.addEventListener("pointerleave", function () {
        cancelAnimationFrame(raf);
        el.style.transform = "";
      });
    });
  }

  /* ─── card spotlight follows the pointer ─── */
  if (fine && !reduced) {
    document.querySelectorAll(".card,.quote").forEach(function (el) {
      el.addEventListener("pointermove", function (e) {
        var b = el.getBoundingClientRect();
        el.style.setProperty("--mx", (e.clientX - b.left) + "px");
        el.style.setProperty("--my", (e.clientY - b.top) + "px");
      });
    });
  }

  /* ─── cta band: budget chips + quick-brief form (POSTs to /api/contact) ─── */
  document.querySelectorAll(".bf-chips").forEach(function (group) {
    var chips = group.querySelectorAll("[data-chip]");
    chips.forEach(function (chip) {
      chip.addEventListener("click", function () {
        chips.forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
        chip.setAttribute("aria-pressed", "true");
      });
    });
  });
  document.querySelectorAll("[data-brief-form]").forEach(function (form) {
    var note = form.querySelector("[data-bf-note]");
    var noteDefault = note ? note.textContent : "";
    var submitBtn = form.querySelector('button[type="submit"]');
    var submitDefault = submitBtn ? submitBtn.innerHTML : "";
    // when the form became interactive — the server rejects submissions that
    // arrive implausibly soon after this, a cheap but effective bot filter
    var loadedAt = Date.now();

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var name = (form.querySelector('[name="name"]') || {}).value || "";
      var email = (form.querySelector('[name="email"]') || {}).value || "";
      var whatsapp = (form.querySelector('[name="whatsapp"]') || {}).value || "";
      var details = (form.querySelector('[name="details"]') || {}).value || "";
      var company = (form.querySelector('[name="company"]') || {}).value || "";
      var chip = form.querySelector('[data-chip][aria-pressed="true"]');
      var budget = chip ? chip.textContent.trim() : "";

      if (!email.trim() || !details.trim()) return;

      if (submitBtn) { submitBtn.setAttribute("disabled", "disabled"); submitBtn.textContent = "Sending…"; }
      if (note) { note.textContent = noteDefault; note.classList.remove("is-ok", "is-err"); }

      fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name, email: email, whatsapp: whatsapp, budget: budget, details: details,
          company: company, loadedAt: loadedAt
        })
      }).then(function (res) {
        if (!res.ok) throw new Error("bad status");
        return res.json();
      }).then(function () {
        if (note) { note.textContent = "Sent — I’ll reply within 24 hours."; note.classList.add("is-ok"); }
        form.reset();
        form.querySelectorAll("[data-chip]").forEach(function (c) { c.setAttribute("aria-pressed", "false"); });
      }).catch(function () {
        if (note) {
          note.textContent = "Couldn’t send — email hello@anowarhdesign.com directly instead.";
          note.classList.add("is-err");
        }
      }).finally(function () {
        if (submitBtn) { submitBtn.removeAttribute("disabled"); submitBtn.innerHTML = submitDefault; }
      });
    });
  });

  /* ─── copy email button ─── */
  document.querySelectorAll(".copy-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var text = btn.dataset.copy;
      var done = function () {
        btn.classList.add("copied");
        btn.setAttribute("aria-label", "Copied");
        clearTimeout(btn._t);
        btn._t = setTimeout(function () {
          btn.classList.remove("copied");
          btn.setAttribute("aria-label", "Copy email address");
        }, 1600);
      };
      var legacyCopy = function () {
        var ta = document.createElement("textarea");
        ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
        document.body.appendChild(ta); ta.select();
        try { if (document.execCommand("copy")) done(); } catch (e) {}
        document.body.removeChild(ta);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, legacyCopy);
      } else {
        legacyCopy();
      }
    });
  });

  /* ─── mobile nav ─── */
  var toggle = document.querySelector(".navtoggle");
  var links = document.querySelector(".navlinks");
  if (toggle && links) {
    toggle.addEventListener("click", function () {
      var open = links.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "Close" : "Menu";
    });
  }

  /* ─── Dhaka clock + year ─── */
  var clocks = document.querySelectorAll("[id='clock']");
  if (clocks.length) {
    var tick = function () {
      var t;
      try {
        t = new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit",
          hour12: false, timeZone: "Asia/Dhaka" }).format(new Date());
      } catch (err) { t = "--:--"; }
      clocks.forEach(function (c) { c.textContent = t; });
    };
    tick(); setInterval(tick, 30000);
  }
  var y = document.getElementById("cpyear");
  if (y) y.textContent = new Date().getFullYear();

  /* ─── old single-page anchors → their new homes ─── */
  var moved = { "#work": "/work", "#protocol": "/services", "#channel": "/contact",
                "#deploys": "/work", "#record": "/about", "#operator": "/about" };
  if (location.pathname === "/" && moved[location.hash] && !document.querySelector(location.hash)) {
    location.replace(moved[location.hash]);
  }
})();
