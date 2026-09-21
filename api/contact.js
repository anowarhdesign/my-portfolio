// Vercel serverless function — receives the quick-brief form from the CTA
// band and emails it via Resend. Needs a RESEND_API_KEY environment
// variable set in the Vercel project (Settings -> Environment Variables);
// without it this responds 500 and the form falls back to telling the
// visitor to email hello@anowarhdesign.com directly. See CLAUDE.md.
//
// Spam defenses, layered (each one alone is beatable, together they filter
// out virtually all automated submissions without a CAPTCHA):
//   1. Honeypot field ("company") — real visitors never see or fill it.
//   2. Time-trap — site.js records when the form became interactive and
//      sends it as `loadedAt`; anything submitted in under ~2.5s, or with
//      no loadedAt at all (i.e. not submitted through the real JS path),
//      is almost certainly scripted.
//   3. Origin/Referer check — rejects requests that didn't originate from
//      this site (direct API abuse from elsewhere).
//   4. Content heuristics — too many links in the message is the single
//      most common signal for link-spam.
//   5. Best-effort per-IP rate limit, in-memory. This resets on cold start
//      and isn't shared across concurrent instances, so it's not a hard
//      guarantee — but it stops naive burst/loop scripts, which is most of
//      them. A durable limit would need Vercel KV or similar; not worth the
//      extra infrastructure unless the lighter defenses above prove
//      insufficient.

const TO_EMAIL = "anowarhdesign@gmail.com";
const FROM_EMAIL = "Portfolio contact <onboarding@resend.dev>";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const ALLOWED_HOSTS = new Set([
  "anowarhdesign.com",
  "www.anowarhdesign.com",
]);
const MIN_FILL_MS = 2500;
const RATE_LIMIT_MAX = 5;
const RATE_LIMIT_WINDOW_MS = 15 * 60 * 1000;
const MAX_LINKS = 3;

// module-scope Map survives across warm invocations of the same instance
const hits = new Map();

function clientIp(req) {
  const fwd = req.headers["x-forwarded-for"];
  if (fwd) return String(fwd).split(",")[0].trim();
  return req.socket && req.socket.remoteAddress ? req.socket.remoteAddress : "unknown";
}

function isRateLimited(ip) {
  const now = Date.now();
  const recent = (hits.get(ip) || []).filter((t) => now - t < RATE_LIMIT_WINDOW_MS);
  recent.push(now);
  hits.set(ip, recent);
  // opportunistic cleanup so the map doesn't grow unbounded
  if (hits.size > 500) {
    for (const [key, times] of hits) {
      if (!times.some((t) => now - t < RATE_LIMIT_WINDOW_MS)) hits.delete(key);
    }
  }
  return recent.length > RATE_LIMIT_MAX;
}

function hostFromHeader(value) {
  if (!value) return null;
  try {
    return new URL(value).host;
  } catch {
    return null;
  }
}

function looksLikeLinkSpam(text) {
  const matches = text.match(/https?:\/\/|www\./gi);
  return !!matches && matches.length > MAX_LINKS;
}

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const ip = clientIp(req);
  if (isRateLimited(ip)) {
    return res.status(429).json({ error: "Too many requests" });
  }

  const originHost = hostFromHeader(req.headers.origin) || hostFromHeader(req.headers.referer);
  if (originHost && !ALLOWED_HOSTS.has(originHost)) {
    return res.status(403).json({ error: "Forbidden" });
  }

  const body = req.body || {};
  const name = String(body.name || "").trim();
  const email = String(body.email || "").trim();
  const budget = String(body.budget || "Not specified").trim();
  const details = String(body.details || "").trim();
  const company = String(body.company || "").trim(); // honeypot
  const loadedAt = Number(body.loadedAt);

  if (company) {
    // looks like a bot — pretend success, do nothing
    return res.status(200).json({ ok: true });
  }

  if (!Number.isFinite(loadedAt) || Date.now() - loadedAt < MIN_FILL_MS) {
    // submitted implausibly fast (or the JS path was skipped entirely) —
    // pretend success so a scripted client doesn't learn to adjust its timing
    return res.status(200).json({ ok: true });
  }

  if (!name || !email || !details) {
    return res.status(400).json({ error: "Missing required fields" });
  }
  if (!EMAIL_RE.test(email)) {
    return res.status(400).json({ error: "Invalid email address" });
  }
  if (name.length > 200 || email.length > 200 || budget.length > 100 || details.length > 5000) {
    return res.status(400).json({ error: "Field too long" });
  }
  if (looksLikeLinkSpam(name) || looksLikeLinkSpam(details)) {
    return res.status(200).json({ ok: true }); // same "pretend success" treatment
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) {
    console.error("contact form: RESEND_API_KEY is not set");
    return res.status(500).json({ error: "Email service not configured" });
  }

  const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

  try {
    const resp = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: FROM_EMAIL,
        to: [TO_EMAIL],
        reply_to: email,
        subject: `Project enquiry from ${name}`,
        text: `Name: ${name}\nEmail: ${email}\nRough budget: ${budget}\n\n${details}`,
        html:
          `<p><strong>Name:</strong> ${esc(name)}</p>` +
          `<p><strong>Email:</strong> ${esc(email)}</p>` +
          `<p><strong>Rough budget:</strong> ${esc(budget)}</p>` +
          `<p><strong>What they're building:</strong></p><p>${esc(details).replace(/\n/g, "<br>")}</p>`,
      }),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      console.error("Resend error:", resp.status, errText);
      return res.status(502).json({ error: "Failed to send" });
    }

    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error("contact form error:", err);
    return res.status(500).json({ error: "Server error" });
  }
}
