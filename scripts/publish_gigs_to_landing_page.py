from __future__ import annotations

import shutil
import textwrap
import threading
import http.server
import socketserver
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / "templates" / "landing-page"
ASSETS = LANDING / "assets" / "screenshots" / "gigs"
RUNTIME = ROOT / "docs" / "assets" / "screenshots" / "gigs"

GIGS = [
    {
        "slug": "lead-value-roi-calculator",
        "title": "Lead Value & ROI Calculator",
        "eyebrow": "Lead value scenario planning",
        "description": "A scenario-planning calculator for agencies, consultants, and service businesses that want clearer lead-value and ad-assumption conversations without guaranteed outcomes.",
    },
    {
        "slug": "local-service-quote-calculator",
        "title": "Custom Service Estimate & Intake Calculator",
        "eyebrow": "Fast quoting for service businesses",
        "description": "A planning-estimate preview for one approved service niche, with buyer-supplied rates, modifiers, exclusions, and non-binding estimate language.",
    },
    {
        "slug": "website-audit-scorecard",
        "title": "Website Audit Scorecard",
        "eyebrow": "Client-ready diagnostic offer",
        "description": "A manual scorecard preview that helps consultants structure a first-pass conversation about offer clarity, conversion flow, trust, content, and tracking.",
    },
]


def copy_gig_pages() -> None:
    for gig in GIGS:
        src = ROOT / "gigs" / gig["slug"]
        dst = LANDING / "gigs" / gig["slug"]
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)


def start_server(directory: Path):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    class ReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = ReuseTCPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    old_cwd = Path.cwd()

    def run():
        import os
        os.chdir(directory)
        try:
            server.serve_forever()
        finally:
            os.chdir(old_cwd)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return server, port


def prepare_demo_state(page, slug: str) -> None:
    page.wait_for_load_state("domcontentloaded")
    if slug == "lead-value-roi-calculator":
        page.locator("#brand-name").fill("TWE Growth Studio")
        page.locator("#brand-email").fill("thewatchersedgestore@gmail.com")
        page.locator("#calculate").click()
    elif slug == "local-service-quote-calculator":
        page.locator("#brand-name").fill("TWE Local Services")
        page.locator("#brand-email").fill("thewatchersedgestore@gmail.com")
        page.locator("#hours").fill("6")
        page.locator("#calculate").click()
    elif slug == "website-audit-scorecard":
        page.locator("#brand-name").fill("TWE Web Review")
        page.locator("#brand-email").fill("thewatchersedgestore@gmail.com")
        # Move a few sliders so the output is visibly not a blank/template-only state.
        for slider in page.locator("input[type='range']").all()[:4]:
            slider.evaluate("el => { el.value = 4; el.dispatchEvent(new Event('input', {bubbles:true})); }")
        page.locator("button[type='submit'], #calculate, button").first.click()
    page.wait_for_timeout(500)


def capture_screenshots() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    server, port = start_server(LANDING)
    base = f"http://127.0.0.1:{port}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for gig in GIGS:
                slug = gig["slug"]
                for name, viewport in [("desktop-output", {"width": 1440, "height": 1000}), ("mobile-output", {"width": 390, "height": 844})]:
                    page = browser.new_page(viewport=viewport, device_scale_factor=1)
                    page.goto(f"{base}/gigs/{slug}/", wait_until="networkidle")
                    prepare_demo_state(page, slug)
                    path = ASSETS / f"{slug}-{name}.png"
                    page.screenshot(path=str(path), full_page=True)
                    shutil.copy2(path, RUNTIME / path.name)
                    page.close()
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


def patch_gig_pages() -> None:
    for gig in GIGS:
        slug = gig["slug"]
        index = LANDING / "gigs" / slug / "index.html"
        html = index.read_text(encoding="utf-8")
        if "live-preview-gallery" not in html:
            preview = f'''
      <section class="card live-preview-gallery" aria-label="Actual product screenshots">
        <p class="eyebrow">Actual product screenshots</p>
        <h2>See the mini-site in use before you buy</h2>
        <p>These are real captured states from the working static deliverable: desktop output and mobile output, not a generic title card.</p>
        <div class="preview-grid">
          <figure>
            <img src="../../assets/screenshots/gigs/{slug}-desktop-output.png" alt="Desktop screenshot of {gig['title']} showing the live output state" />
            <figcaption>Desktop output state</figcaption>
          </figure>
          <figure>
            <img src="../../assets/screenshots/gigs/{slug}-mobile-output.png" alt="Mobile screenshot of {gig['title']} showing the live output state" />
            <figcaption>Mobile output state</figcaption>
          </figure>
        </div>
      </section>
'''
            if "\n      <section class=\"card\">" in html:
                html = html.replace("\n      <section class=\"card\">", preview + "\n      <section class=\"card\">", 1)
            elif "\n      <main" in html:
                html = html.replace("\n      <main", preview + "\n      <main", 1)
            elif "</header>" in html:
                html = html.replace("</header>", "</header>" + preview, 1)
            else:
                html = html.replace("</body>", preview + "</body>", 1)
            index.write_text(html, encoding="utf-8")
        css = LANDING / "gigs" / slug / "styles.css"
        css_text = css.read_text(encoding="utf-8")
        if "live-preview-gallery" not in css_text:
            css_text += textwrap.dedent('''

            .live-preview-gallery {
              margin-top: 1.5rem;
            }

            .preview-grid {
              display: grid;
              grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
              gap: 1rem;
              margin-top: 1rem;
            }

            .preview-grid figure {
              margin: 0;
              padding: 0.75rem;
              border: 1px solid rgba(148, 163, 184, 0.28);
              border-radius: 18px;
              background: rgba(15, 23, 42, 0.72);
            }

            .preview-grid img {
              width: 100%;
              height: auto;
              border-radius: 12px;
              display: block;
              border: 1px solid rgba(255,255,255,0.12);
            }

            .preview-grid figcaption {
              margin-top: 0.55rem;
              color: #cbd5e1;
              font-size: 0.92rem;
            }
            ''')
            css.write_text(css_text, encoding="utf-8")


def write_landing_page() -> None:
    cards = []
    for gig in GIGS:
        slug = gig["slug"]
        cards.append(f'''
        <article class="gig-card">
          <a class="screenshot-link" href="gigs/{slug}/">
            <img src="assets/screenshots/gigs/{slug}-desktop-output.png" alt="Actual desktop screenshot of {gig['title']}" />
          </a>
          <div class="gig-card-body">
            <p class="eyebrow">{gig['eyebrow']}</p>
            <h3>{gig['title']}</h3>
            <p>{gig['description']}</p>
            <div class="card-actions">
              <a class="cta" href="gigs/{slug}/">Open working preview</a>
              <a class="link-btn" href="assets/screenshots/gigs/{slug}-mobile-output.png">Mobile screenshot</a>
            </div>
          </div>
        </article>''')
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Gig Factory | Live Mini-Site Demos</title>
  <link rel="stylesheet" href="styles.css" />
</head>
<body>
  <header class="hero">
    <nav class="nav">
      <div class="brand">Gig Factory</div>
      <a class="cta secondary" href="#gigs">View Gigs</a>
    </nav>
    <div class="hero-content">
      <p class="eyebrow">Complete working base products for custom delivery</p>
      <h1>Three interactive calculators and scorecards, ready to tailor to your brand and approved business rules.</h1>
      <p class="sub">Try each complete working base product, review real desktop and mobile output, and request a scoped version using your approved copy, formulas, pricing rules, contact flow, and brand. Final scope, price, timeline, integrations, and support terms are confirmed in writing before delivery.</p>
      <div class="hero-actions">
        <a class="cta" href="#gigs">See the gigs</a>
        <a class="link-btn" href="mailto:thewatchersedgestore@gmail.com?subject=Customization%20request%20-%20Vercel%20Gig%20Factory">Ask about customization</a>
        <a class="link-btn" href="https://github.com/NanooSR/gig-factory">View source repo</a>
      </div>
    </div>
  </header>

  <main>
    <section id="gigs" class="section gig-grid" aria-label="Live gig demos">
      {''.join(cards)}
    </section>

    <section class="section grid-3">
      <article class="card"><h2>Actual screenshots</h2><p>Every gig card uses a captured output state, not a generic title-only graphic.</p></article>
      <article class="card"><h2>Public preview URLs</h2><p>Each mini-site is linked from this Vercel deployment and can be opened directly.</p></article>
      <article class="card"><h2>Custom delivery</h2><p>Approved projects can be delivered as static HTML/CSS/JS packages with setup notes and agreed test cases. Hosting, integrations, data collection, and maintenance are included only when written into scope.</p></article>
    </section>
  </main>

  <script src="script.js"></script>
</body>
</html>
'''
    (LANDING / "index.html").write_text(html, encoding="utf-8")

    css = (LANDING / "styles.css").read_text(encoding="utf-8")
    if ".gig-grid" not in css:
        css += textwrap.dedent('''

        .gig-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(290px, 1fr));
          gap: 1.25rem;
        }

        .gig-card {
          border: 1px solid rgba(148, 163, 184, 0.28);
          border-radius: 24px;
          background: rgba(15, 23, 42, 0.76);
          overflow: hidden;
          box-shadow: 0 24px 70px rgba(15, 23, 42, 0.28);
        }

        .screenshot-link {
          display: block;
          background: linear-gradient(135deg, rgba(14,165,233,0.18), rgba(20,184,166,0.16));
          padding: 0.75rem;
        }

        .screenshot-link img {
          display: block;
          width: 100%;
          height: auto;
          border-radius: 16px;
          border: 1px solid rgba(255,255,255,0.16);
        }

        .gig-card-body {
          padding: 1.25rem;
        }

        .gig-card h3 {
          margin: 0.25rem 0 0.75rem;
          font-size: clamp(1.35rem, 2vw, 1.8rem);
        }

        .card-actions {
          display: flex;
          flex-wrap: wrap;
          align-items: center;
          gap: 0.8rem;
          margin-top: 1rem;
        }
        ''')
        (LANDING / "styles.css").write_text(css, encoding="utf-8")


def verify_local() -> None:
    server, port = start_server(LANDING)
    base = f"http://127.0.0.1:{port}"
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1440, "height": 1000})
            page.goto(base + "/", wait_until="networkidle")
            assert page.locator(".gig-card").count() == 3
            assert page.locator(".gig-card img").count() == 3
            for gig in GIGS:
                slug = gig["slug"]
                page.goto(f"{base}/gigs/{slug}/", wait_until="networkidle")
                assert page.locator(".live-preview-gallery img").count() == 2
                dims = page.locator(".live-preview-gallery img").evaluate_all("imgs => imgs.map(img => [img.naturalWidth, img.naturalHeight])")
                assert all(w > 300 and h > 300 for w, h in dims), (slug, dims)
            browser.close()
    finally:
        server.shutdown()
        server.server_close()


def main() -> None:
    copy_gig_pages()
    capture_screenshots()
    patch_gig_pages()
    write_landing_page()
    verify_local()
    print("published-gig-static-assets-ready", LANDING)


if __name__ == "__main__":
    main()
