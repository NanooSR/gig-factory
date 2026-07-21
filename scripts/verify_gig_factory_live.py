from pathlib import Path
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
import json
import urllib.request

BASE = 'https://gig-factory-navy.vercel.app'
ROOT = Path(__file__).resolve().parents[1]
OUTDIR = ROOT / 'runtime' / 'live_verification_20260721_cfff642'
OUTDIR.mkdir(parents=True, exist_ok=True)
ROUTES = [
    '/',
    '/gigs/lead-value-roi-calculator/',
    '/gigs/local-service-quote-calculator/',
    '/gigs/website-audit-scorecard/',
]
ASSETS = [
    '/assets/screenshots/gigs/lead-value-roi-calculator-desktop-output.png',
    '/assets/screenshots/gigs/lead-value-roi-calculator-mobile-output.png',
    '/assets/screenshots/gigs/local-service-quote-calculator-desktop-output.png',
    '/assets/screenshots/gigs/local-service-quote-calculator-mobile-output.png',
    '/assets/screenshots/gigs/website-audit-scorecard-desktop-output.png',
    '/assets/screenshots/gigs/website-audit-scorecard-mobile-output.png',
]
BAD_TERMS = [
    'LIVE DEMO MINI-SITE', 'hello@example.com', 'Quote-Intake', 'tax/contingency',
    'weighted bands', 'Open live demo', 'Preview quote email', 'Get your custom quote'
]


def expect(condition, message):
    if not condition:
        raise AssertionError(message)


def fetch_head(path):
    req = urllib.request.Request(BASE + path + '?live_check=cfff642', method='GET', headers={'User-Agent': 'HermesLiveGigVerifier/1.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        return {'url': BASE + path, 'status': r.status, 'content_type': r.headers.get('content-type',''), 'bytes': len(body), 'text_head': body[:1000].decode('utf-8', 'ignore')}


def check_layout(page, label):
    overflow = page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
    expect(overflow <= 2, f'{label}: horizontal overflow {overflow}px')
    bad_images = page.evaluate("""() => [...document.images].filter(img => !img.complete || img.naturalWidth === 0).map(img => img.src)""")
    expect(not bad_images, f'{label}: broken images {bad_images}')


def test_lead(page):
    page.goto(BASE + '/gigs/lead-value-roi-calculator/?live_check=cfff642', wait_until='networkidle')
    page.screenshot(path=str(OUTDIR / 'lead-live.png'), full_page=True)
    page.click('#calculate')
    expect(page.locator('#results:not(.hidden)').count() == 1, 'lead valid results hidden')
    href = unquote(page.locator('#cta').get_attribute('href') or '')
    for token in ['Average revenue', 'Gross margin', 'Monthly ad spend', 'Break-even clients', 'Additional customer value']:
        expect(token in href, f'lead mailto missing {token}')
    page.fill('#qualification-rate', '150')
    page.fill('#monthly-leads', '-1')
    page.click('#calculate')
    expect(page.locator('#validation-summary:not(.hidden)').count() == 1, 'lead validation summary missing')
    expect(page.locator('#results.hidden').count() == 1, 'lead invalid should hide results')
    expect('Each percentage must remain within the range shown' in page.locator('#validation-summary').inner_text(), 'lead refined validation copy missing')
    page.click('#reset-sample')
    expect(page.locator('#validation-summary.hidden').count() == 1, 'lead reset validation not cleared')


def test_quote(page):
    page.goto(BASE + '/gigs/local-service-quote-calculator/?live_check=cfff642', wait_until='networkidle')
    page.screenshot(path=str(OUTDIR / 'quote-live.png'), full_page=True)
    page.fill('#customer-name', 'Ada Buyer')
    page.fill('#customer-contact', 'ada@example.ca')
    page.fill('#service-location', 'N1R 1A1')
    page.fill('#project-notes', 'Back entrance, two pets, confirm parking.')
    page.select_option('#team-size', '1.2')
    page.select_option('#urgency', '1.12')
    page.check('.addon[data-cost="95"]')
    page.click('#calculate')
    expect(page.locator('#breakdown:not(.hidden)').count() == 1, 'quote valid breakdown hidden')
    expect(page.locator('#allowance').count() == 1, 'quote allowance id missing')
    href = unquote(page.locator('#cta').get_attribute('href') or '')
    for token in ['Ada Buyer', 'N1R 1A1', '2 technicians', 'Priority', 'materials', 'planning allowance']:
        expect(token in href, f'quote mailto missing {token}')
    body = page.locator('body').inner_text().lower()
    expect('pricing configuration transparency' in body, 'quote transparency block missing')
    expect('get your custom estimate' in body, 'quote estimate CTA label missing')
    expect('get your custom quote' not in body, 'quote stale custom quote CTA present')
    expect('tax/contingency' not in body, 'quote stale tax/contingency text present')
    page.fill('#hours', '0')
    page.click('#calculate')
    expect(page.locator('#breakdown.hidden').count() == 1, 'quote invalid should hide result')
    page.click('#reset-sample')
    expect(page.locator('#breakdown:not(.hidden)').count() == 1, 'quote reset did not recalculate')


def test_scorecard(page):
    page.goto(BASE + '/gigs/website-audit-scorecard/?live_check=cfff642', wait_until='networkidle')
    page.screenshot(path=str(OUTDIR / 'scorecard-live.png'), full_page=True)
    expect(page.locator('#score-output.hidden').count() == 1, 'scorecard should start hidden')
    expect('No score has been assigned yet.' in page.locator('#score-text').inner_text(), 'scorecard initial copy missing')
    page.fill('#website-name', 'Ada Studio')
    page.fill('#website-url', 'https://adastudio.example')
    page.fill('#reviewer-notes', 'Test review notes')
    page.locator("input[data-label='value-prop']").evaluate("el => { el.value = 1; el.dispatchEvent(new Event('input', {bubbles:true})); }")
    page.click('#score-btn')
    expect(page.locator('#score-output:not(.hidden)').count() == 1, 'scorecard result missing')
    href = unquote(page.locator('#cta').get_attribute('href') or '')
    for token in ['Ada Studio', 'Criterion scores', 'Readiness band']:
        expect(token in href, f'scorecard mailto missing {token}')
    page.click('#reset-sample')
    expect(page.locator('#score-output.hidden').count() == 1, 'scorecard reset should hide result')


def main():
    report = {'base': BASE, 'expected_commit': '1302081a0b78170bba10072cfb50b32db048f0d7', 'http': [], 'assets': [], 'viewports': []}
    for route in ROUTES:
        got = fetch_head(route)
        expect(got['status'] == 200, f'{route}: HTTP {got["status"]}')
        expect('text/html' in got['content_type'], f'{route}: bad content type {got["content_type"]}')
        report['http'].append(got)
    for asset in ASSETS:
        got = fetch_head(asset)
        expect(got['status'] == 200, f'{asset}: HTTP {got["status"]}')
        expect(got['bytes'] > 10000, f'{asset}: image too small/broken')
        report['assets'].append({k:v for k,v in got.items() if k != 'text_head'})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for label, viewport in [
            ('desktop', {'width': 1440, 'height': 1000}),
            ('tablet', {'width': 820, 'height': 1180}),
            ('mobile', {'width': 390, 'height': 844}),
            ('narrow320', {'width': 320, 'height': 760}),
        ]:
            page = browser.new_page(viewport=viewport)
            console_errors = []
            failed = []
            page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)
            page.on('pageerror', lambda exc: console_errors.append(str(exc)))
            page.on('requestfailed', lambda req: failed.append(req.url))
            for route in ROUTES:
                page.goto(BASE + route + '?live_check=cfff642', wait_until='networkidle')
                text = page.locator('body').inner_text()
                for term in BAD_TERMS:
                    expect(term not in text, f'{label} {route}: stale term {term}')
                check_layout(page, f'{label} {route}')
                expect('What a buyer receives' in text or route == '/', f'{label} {route}: buyer deliverables missing')
            test_lead(page)
            test_quote(page)
            test_scorecard(page)
            # Basic keyboard focus check on homepage and zoom-ish layout check.
            page.goto(BASE + '/?live_check=cfff642', wait_until='networkidle')
            page.keyboard.press('Tab')
            active = page.evaluate('document.activeElement && (document.activeElement.href || document.activeElement.tagName)')
            expect(active, f'{label}: keyboard focus missing')
            page.evaluate("document.body.style.zoom='200%' ")
            check_layout(page, f'{label} zoom200 home')
            expect(not console_errors, f'{label}: console/page errors {console_errors}')
            expect(not failed, f'{label}: failed requests {failed}')
            report['viewports'].append({'label': label, 'ok': True})
            page.close()
        browser.close()
    out = OUTDIR / 'live_verification_report.json'
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('LIVE_VERIFICATION_OK', out)

if __name__ == '__main__':
    main()
