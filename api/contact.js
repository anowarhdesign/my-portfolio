// Vercel serverless function — receives the quick-brief form from the CTA
// band and emails it via Resend. Needs a RESEND_API_KEY environment
// variable set in the Vercel project (Settings -> Environment Variables);
// without it this responds 500 and the form falls back to telling the
// visitor to email hello@anowarhdesign.com directly. See CLAUDE.md.

const TO_EMAIL = "anowarhdesign@gmail.com";
const FROM_EMAIL = "Portfolio contact <onboarding@resend.dev>";
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const body = req.body || {};
  const name = String(body.name || "").trim();
  const email = String(body.email || "").trim();
  const budget = String(body.budget || "Not specified").trim();
  const details = String(body.details || "").trim();
  const company = String(body.company || "").trim(); // honeypot

  if (company) {
    // looks like a bot — pretend success, do nothing
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
