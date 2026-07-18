from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen, Request

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
TWE_ROOT = Path('C:/PROJECTS/TWEStore')
RUN_ID = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_UTC')
OUT = ROOT / 'runtime' / f'sol_vercel_gig_audit_{RUN_ID}'
RAW = OUT / 'raw_evidence'
PUBLIC = RAW / 'public_live'
SOURCE = RAW / 'source_files'
SUPPORT = RAW / 'supporting_files'
SCREEN = RAW / 'screenshots'
SUMMARY = OUT / 'summaries'
ZIP_NAME = f'SOL_INPUT_ZIP_vercel_gig_service_listings_{RUN_ID}.zip'
ZIP_PATH = OUT / ZIP_NAME

BASE_URL = 'https://gig-factory-navy.vercel.app'
SLUGS = [
    'lead-value-roi-calculator',
    'local-service-quote-calculator',
    'website-audit-scorecard',
]
ROUTES = [{'name': 'home', 'slug': 'home', 'url': BASE_URL + '/'}] + [
    {'name': slug.replace('-', ' ').title(), 'slug': slug, 'url': f'{BASE_URL}/gigs/{slug}/'}
    for slug in SLUGS
]

SUPPORTING_PATHS = [
    'README.md',
    '.hermes.md',
    'docs/profit-shortlist.md',
    'docs/sales-listings.md',
    'docs/sell-next-steps.md',
    'docs/continuity/latest-handoff.md',
    'docs/assets/screenshots/gigs/gig-factory-desktop-contact-sheet.jpg',
    'docs/assets/screenshots/gigs/gig-factory-mobile-contact-sheet.jpg',
    'templates/landing-page/index.html',
    'templates/landing-page/styles.css',
    'scripts/publish_gigs_to_landing_page.py',
]
for slug in SLUGS:
    SUPPORTING_PATHS.extend([
        f'gigs/{slug}/index.html',
        f'gigs/{slug}/styles.css',
        f'templates/landing-page/gigs/{slug}/index.html',
        f'templates/landing-page/gigs/{slug}/styles.css',
        f'templates/landing-page/assets/screenshots/gigs/{slug}-desktop-output.png',
        f'templates/landing-page/assets/screenshots/gigs/{slug}-mobile-output.png',
    ])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], cwd: Path = ROOT) -> dict:
    proc = subprocess.run(cmd, cwd=str(cwd), text=True, capture_output=True, timeout=180)
    return {'cmd': cmd, 'cwd': str(cwd), 'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr}


def safe_get(url: str) -> dict:
    req = Request(url + ('?v=sol-audit-package' if '?' not in url else '&v=sol-audit-package'), headers={'User-Agent':'Hermes SOL audit evidence builder'})
    try:
        with urlopen(req, timeout=30) as resp:
            body = resp.read()
            return {'url': url, 'status': resp.status, 'headers': dict(resp.headers), 'body': body.decode('utf-8', 'replace'), 'bytes': len(body)}
    except Exception as exc:
        return {'url': url, 'error': repr(exc)}


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def copy_supporting_files() -> list[dict]:
    copied = []
    for rel in SUPPORTING_PATHS:
        src = ROOT / rel
        rec = {'relative_path': rel, 'exists': src.exists()}
        if src.exists() and src.is_file():
            dest = SOURCE / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            rec.update({'copied_to': str(dest.relative_to(OUT)), 'bytes': dest.stat().st_size, 'sha256': sha256(dest)})
        copied.append(rec)
    return copied


def capture_browser() -> list[dict]:
    captures = []
    SCREEN.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for route in ROUTES:
            for viewport_name, viewport in [('desktop', {'width':1440,'height':1200}), ('mobile', {'width':430,'height':1100})]:
                page = browser.new_page(viewport=viewport)
                url = route['url'] + '?v=sol-audit-package'
                rec = {'route': route, 'viewport': viewport_name, 'url': url}
                try:
                    resp = page.goto(url, wait_until='networkidle', timeout=45000)
                    page.wait_for_timeout(700)
                    png = SCREEN / f"{route['slug']}_{viewport_name}.png"
                    html = PUBLIC / f"{route['slug']}_{viewport_name}.rendered.html"
                    text = PUBLIC / f"{route['slug']}_{viewport_name}.visible_text.txt"
                    page.screenshot(path=str(png), full_page=True)
                    html.write_text(page.content(), encoding='utf-8')
                    text.write_text(page.locator('body').inner_text(timeout=5000), encoding='utf-8')
                    links = page.eval_on_selector_all('a', "els => els.map(a => ({text:a.innerText.trim(), href:a.href, aria:a.getAttribute('aria-label'), target:a.target}))")
                    imgs = page.eval_on_selector_all('img', "els => els.map(i => ({alt:i.alt, src:i.src, width:i.naturalWidth, height:i.naturalHeight, clientWidth:i.clientWidth, clientHeight:i.clientHeight}))")
                    buttons = page.eval_on_selector_all('button, input, select, textarea', "els => els.map(e => ({tag:e.tagName, text:e.innerText || e.value || e.getAttribute('aria-label') || '', type:e.type || '', name:e.name || '', id:e.id || ''}))")
                    forms = page.eval_on_selector_all('form', "els => els.map(f => ({action:f.action, method:f.method, text:f.innerText.slice(0,1000)}))")
                    rec.update({
                        'status': resp.status if resp else None,
                        'final_url': page.url,
                        'screenshot': str(png.relative_to(OUT)),
                        'rendered_html': str(html.relative_to(OUT)),
                        'visible_text': str(text.relative_to(OUT)),
                        'links': links,
                        'images': imgs,
                        'controls': buttons,
                        'forms': forms,
                    })
                except Exception as exc:
                    rec['error'] = repr(exc)
                finally:
                    page.close()
                captures.append(rec)
        browser.close()
    return captures


def infer_listing_matrix(captures: list[dict]) -> list[dict]:
    out = []
    for slug in SLUGS:
        html_path = ROOT / 'templates' / 'landing-page' / 'gigs' / slug / 'index.html'
        css_path = ROOT / 'templates' / 'landing-page' / 'gigs' / slug / 'styles.css'
        source_path = ROOT / 'gigs' / slug / 'index.html'
        public_url = f'{BASE_URL}/gigs/{slug}/'
        desktop = next((c for c in captures if c.get('route',{}).get('slug')==slug and c.get('viewport')=='desktop'), {})
        text = ''
        if desktop.get('visible_text'):
            p = OUT / desktop['visible_text']
            if p.exists(): text = p.read_text(encoding='utf-8', errors='replace')
        image_assets = [f'templates/landing-page/assets/screenshots/gigs/{slug}-desktop-output.png', f'templates/landing-page/assets/screenshots/gigs/{slug}-mobile-output.png']
        out.append({
            'slug': slug,
            'public_url': public_url,
            'current_status': 'published on Vercel production URL and source pushed to origin/main' if desktop.get('status') == 200 else 'needs verification',
            'source_files': [str(source_path.relative_to(ROOT)), str(css_path.relative_to(ROOT)), str(html_path.relative_to(ROOT))],
            'image_assets': image_assets,
            'listing_visible_text': text,
            'links': desktop.get('links', []),
            'images': desktop.get('images', []),
            'customer_flow_observed': {
                'public_page_loads': desktop.get('status') == 200,
                'has_inputs_or_calculator_controls': bool(desktop.get('controls')),
                'forms': desktop.get('forms', []),
                'primary_cta_links': [l for l in desktop.get('links', []) if any(w in (l.get('text') or '').lower() for w in ['start', 'buy', 'order', 'request', 'contact', 'preview'])],
                'pricing_detected_in_text': any(marker in text for marker in ['$', 'USD', 'CAD', 'price', 'Price', 'package', 'Package']),
            }
        })
    return out


def make_markdown(manifest, listing_matrix, public_fetches, commands) -> str:
    lines = [
        '# Vercel Gig Factory SOL Audit Evidence Package',
        '',
        f'Generated UTC: {manifest["generated_utc"]}',
        f'Live base URL: {BASE_URL}',
        f'Git commit: {manifest["git"]["head"]}',
        '',
        '## Scope',
        'This package contains raw evidence for every currently identified Vercel-hosted Gig Factory public page/service listing: homepage plus three gig routes.',
        '',
        '## Listings',
    ]
    for item in listing_matrix:
        lines += [
            f'### {item["slug"]}',
            f'- Public URL: {item["public_url"]}',
            f'- Status: {item["current_status"]}',
            f'- Source files: {", ".join(item["source_files"])}',
            f'- Image assets: {", ".join(item["image_assets"])}',
            f'- Pricing detected in visible text: {item["customer_flow_observed"]["pricing_detected_in_text"]}',
            f'- Controls detected: {item["customer_flow_observed"]["has_inputs_or_calculator_controls"]}',
            '',
            'Visible text excerpt:',
            '```text',
            item['listing_visible_text'][:3000],
            '```',
            '',
        ]
    lines += [
        '## Raw Evidence Map',
        '- `raw_evidence/public_live/`: rendered HTML, visible text, HTTP bodies and browser-capture metadata.',
        '- `raw_evidence/screenshots/`: desktop and mobile full-page screenshots for each route.',
        '- `raw_evidence/source_files/`: copied source/templates/CSS/screenshots/support docs.',
        '- `summaries/listing_matrix.json`: listing text, links, image references, customer flow, pricing detection, status.',
        '- `summaries/manifest.json`: ZIP/file inventory and hashes.',
        '',
        '## SOL Review Ask',
        'Audit accuracy, clarity, professionalism, customer appeal, trust, visual quality, sales readiness, screenshot/example quality, and internal-note/unfinished-wording risks. Recommend only evidence-based improvements that are safe to implement without account/payment/terms changes.',
    ]
    return '\n'.join(lines) + '\n'


def main() -> None:
    for d in [RAW, PUBLIC, SOURCE, SUPPORT, SCREEN, SUMMARY]:
        d.mkdir(parents=True, exist_ok=True)
    commands = {
        'git_status': run(['git', 'status', '--short']),
        'git_head': run(['git', 'rev-parse', 'HEAD']),
        'git_remote_head': run(['bash', '-lc', 'git ls-remote origin main | cut -f1']),
        'git_log': run(['git', 'log', '--oneline', '-5']),
    }
    # Refresh generated pages/screenshots before capture.
    commands['publish_refresh'] = run(['python', 'scripts/publish_gigs_to_landing_page.py'])
    copied = copy_supporting_files()
    public_fetches = [safe_get(r['url']) for r in ROUTES]
    for fetch in public_fetches:
        name = fetch['url'].rstrip('/').split('/')[-1] or 'home'
        if fetch.get('body'):
            (PUBLIC / f'{name}_http_body.html').write_text(fetch['body'], encoding='utf-8')
    captures = capture_browser()
    listing_matrix = infer_listing_matrix(captures)
    write_json(SUMMARY / 'public_fetches.json', public_fetches)
    write_json(SUMMARY / 'browser_captures.json', captures)
    write_json(SUMMARY / 'listing_matrix.json', listing_matrix)
    write_json(SUMMARY / 'commands.json', commands)
    manifest = {
        'package': ZIP_NAME,
        'generated_utc': datetime.now(timezone.utc).isoformat(),
        'base_url': BASE_URL,
        'routes': ROUTES,
        'slugs': SLUGS,
        'git': {
            'head': commands['git_head']['stdout'].strip(),
            'origin_main': commands['git_remote_head']['stdout'].strip(),
            'status_short': commands['git_status']['stdout'],
        },
        'raw_evidence_policy': 'No credentials/tokens/cookies/session data intentionally collected. Public pages/source/support files only.',
        'copied_files': copied,
    }
    write_json(SUMMARY / 'manifest.json', manifest)
    (OUT / 'EVIDENCE_README.md').write_text(make_markdown(manifest, listing_matrix, public_fetches, commands), encoding='utf-8')
    # Build zip and then append final manifest with zip hash sidecar outside zip.
    with zipfile.ZipFile(ZIP_PATH, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for file in sorted(OUT.rglob('*')):
            if file == ZIP_PATH or file.is_dir():
                continue
            zf.write(file, file.relative_to(OUT))
    zip_hash = sha256(ZIP_PATH)
    zip_info = {'zip_path': str(ZIP_PATH), 'zip_name': ZIP_NAME, 'sha256': zip_hash, 'bytes': ZIP_PATH.stat().st_size, 'members': len(zipfile.ZipFile(ZIP_PATH).namelist())}
    write_json(OUT / 'ZIP_INFO.json', zip_info)
    print(json.dumps({'out': str(OUT), 'zip': str(ZIP_PATH), 'sha256': zip_hash, 'members': zip_info['members'], 'routes': len(ROUTES), 'listings': len(SLUGS)}, indent=2))

if __name__ == '__main__':
    main()
