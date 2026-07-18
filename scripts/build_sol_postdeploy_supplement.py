from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(r"C:\Users\TWETrade\gig-factory")
TWE = Path(r"C:\PROJECTS\TWEStore")
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_UTC")
OUT = ROOT / "runtime" / f"sol_vercel_postdeploy_supplement_{RUN_ID}"
TEXT = OUT / "text_evidence"
IMAGES = OUT / "images"
SUMMARY = OUT / "summary"
BASE = "https://gig-factory-navy.vercel.app"
ROUTES = {
    "home": BASE + "/",
    "lead-value-roi-calculator": BASE + "/gigs/lead-value-roi-calculator/",
    "local-service-quote-calculator": BASE + "/gigs/local-service-quote-calculator/",
    "website-audit-scorecard": BASE + "/gigs/website-audit-scorecard/",
}
SLUGS = [k for k in ROUTES if k != "home"]
FULL_PACKAGE = ROOT / "runtime" / "sol_vercel_gig_audit_v2_20260718_235037_UTC" / "SOL_INPUT_ZIP_vercel_gig_service_listings_v2_20260718_235037_UTC.zip"
FULL_PACKAGE_INFO = ROOT / "runtime" / "sol_vercel_gig_audit_v2_20260718_235037_UTC" / "ZIP_INFO.json"
MONITOR = TWE / "runtime" / "vercel_gig_factory_monitor_latest.json"
CONTACT = "thewatchersedgestore@gmail.com"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str) -> dict:
    with urlopen(Request(url + "?solsupplement=" + RUN_ID, headers={"User-Agent": "Hermes SOL supplement"}), timeout=30) as resp:
        body = resp.read().decode("utf-8", "replace")
        return {"status": resp.status, "final_url": resp.geturl(), "html": body}


def copy_text(rel: str):
    src = ROOT / rel
    if src.exists():
        dest = TEXT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        return {"path": rel, "bytes": dest.stat().st_size, "sha256": sha256(dest)}
    return {"path": rel, "missing": True}


def compress_image(src: Path, dest: Path, max_width=1200, quality=76):
    if not src.exists():
        return {"source": str(src), "missing": True}
    dest.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if im.width > max_width:
        ratio = max_width / im.width
        im = im.resize((max_width, int(im.height * ratio)))
    im.save(dest, quality=quality, optimize=True)
    return {"source": str(src), "path": str(dest.relative_to(OUT)), "bytes": dest.stat().st_size, "sha256": sha256(dest), "size": [im.width, im.height]}


def main():
    for d in [TEXT, IMAGES, SUMMARY]:
        d.mkdir(parents=True, exist_ok=True)
    live = {}
    for key, url in ROUTES.items():
        rec = fetch(url)
        live[key] = {k: v for k, v in rec.items() if k != "html"}
        (TEXT / f"live_{key}.html").write_text(rec["html"], encoding="utf-8")
        stripped = rec["html"].replace("<", "\n<")
        (TEXT / f"live_{key}_html_excerpt.txt").write_text(stripped[:50000], encoding="utf-8")

    copied = []
    copied.append(copy_text("templates/landing-page/index.html"))
    copied.append(copy_text("templates/landing-page/styles.css"))
    copied.append(copy_text("templates/landing-page/script.js"))
    for slug in SLUGS:
        for base in ["gigs", "templates/landing-page/gigs"]:
            for ext in ["index.html", "styles.css", "script.js"]:
                copied.append(copy_text(f"{base}/{slug}/{ext}"))

    image_records = []
    image_sources = [ROOT / "docs/assets/screenshots/gigs/gig-factory-desktop-contact-sheet.jpg", ROOT / "docs/assets/screenshots/gigs/gig-factory-mobile-contact-sheet.jpg"]
    for slug in SLUGS:
        image_sources.append(ROOT / "docs/assets/screenshots/gigs" / f"{slug}-desktop-output.png")
        image_sources.append(ROOT / "docs/assets/screenshots/gigs" / f"{slug}-mobile-output.png")
    for src in image_sources:
        image_records.append(compress_image(src, IMAGES / (src.stem + ".jpg")))

    monitor = json.loads(MONITOR.read_text(encoding="utf-8")) if MONITOR.exists() else {"missing": str(MONITOR)}
    full_info = json.loads(FULL_PACKAGE_INFO.read_text(encoding="utf-8")) if FULL_PACKAGE_INFO.exists() else {"missing": str(FULL_PACKAGE_INFO)}
    status = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Small supplemental post-deploy data package for SOL when full ZIP upload is unavailable in ChatGPT environment.",
        "full_package_path": str(FULL_PACKAGE),
        "full_package_exists_locally": FULL_PACKAGE.exists(),
        "full_package_sha256": sha256(FULL_PACKAGE) if FULL_PACKAGE.exists() else None,
        "full_package_info": full_info,
        "deployed_commit": "ad3caa7",
        "public_routes": ROUTES,
        "live_fetch_summary": live,
        "monitor_latest": monitor,
        "text_files": copied,
        "image_files": image_records,
        "post_deploy_assertions_verified_by_hermes_tools": [
            "All four public URLs returned HTTP 200 after deployment.",
            "Public HTML contained no href=\"#\", no placeholder text, no yourbrand.com, and no yourdomain.com.",
            "Full post-deploy package has 15 behavior states and zero error records.",
            "TWEStore DB has 3 Vercel channel_listings and monitored source vercel-gig-factory-public.",
        ],
        "safe_improvements_already_deployed": [
            "Removed internal/placeholder wording from gig pages.",
            "Changed demo fields to example/demo labels and neutral hello@example.com values.",
            f"Changed public fallback CTAs to real mailto/contact flow for {CONTACT}.",
            "Clarified quote planning buffer wording instead of tax/placeholder wording.",
            "Fixed ROI zero-ad-spend display to avoid misleading 999% ROI.",
            "Improved blank/zero input status messages.",
            "Adjusted scorecard low-score handling and contradictory messaging.",
            "Added hard pre-ZIP validation to the evidence builder.",
        ],
        "known_owner_gated_items": [
            "Final price/package promise and checkout setup require Ryan approval.",
            "Paid ads/boosting require Ryan approval.",
            "Payment, tax, billing, terms, or account-secret actions are out of scope.",
        ],
    }
    (SUMMARY / "POSTDEPLOY_SUPPLEMENT_STATUS.json").write_text(json.dumps(status, indent=2), encoding="utf-8")
    md = [
        "# SOL Post-Deploy Vercel Gig Factory Supplement",
        "",
        "This smaller package supplements the full post-deploy ZIP when ChatGPT/SOL cannot access the larger uploaded archive.",
        "",
        f"Full package SHA-256: `{status['full_package_sha256']}`",
        f"Deployed commit: `{status['deployed_commit']}`",
        "",
        "## Public routes",
    ]
    for k, u in ROUTES.items():
        md.append(f"- {k}: {u}")
    md += ["", "## Verified safe improvements deployed"] + [f"- {x}" for x in status["safe_improvements_already_deployed"]]
    md += ["", "## Remaining owner-gated items"] + [f"- {x}" for x in status["known_owner_gated_items"]]
    md += ["", "## Files", "- `text_evidence/`: public HTML plus current source HTML/CSS/JS.", "- `images/`: compressed contact sheets and live screenshot examples.", "- `summary/POSTDEPLOY_SUPPLEMENT_STATUS.json`: machine-readable status and verification summary."]
    (OUT / "README_SOL_POSTDEPLOY_SUPPLEMENT.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    zip_path = OUT / f"SOL_SUPPLEMENT_POSTDEPLOY_VERCEL_GIG_FACTORY_{RUN_ID}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT.rglob("*")):
            if f == zip_path or f.is_dir():
                continue
            z.write(f, f.relative_to(OUT))
    zip_info = {"zip_path": str(zip_path), "zip_name": zip_path.name, "bytes": zip_path.stat().st_size, "sha256": sha256(zip_path), "members": len(zipfile.ZipFile(zip_path).namelist())}
    (OUT / "ZIP_INFO.json").write_text(json.dumps(zip_info, indent=2), encoding="utf-8")
    print(json.dumps({"out": str(OUT), **zip_info}, indent=2))


if __name__ == "__main__":
    main()
