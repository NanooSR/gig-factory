from pathlib import Path
from playwright.sync_api import sync_playwright
import http.server
import json
import os
import socketserver
import threading

ROOT = Path(__file__).resolve().parents[1]
LANDING = ROOT / 'templates' / 'landing-page'
ROUTES = [
    '/',
    '/gigs/lead-value-roi-calculator/',
    '/gigs/local-service-quote-calculator/',
    '/gigs/website-audit-scorecard/',
]

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

class Server(socketserver.TCPServer):
    allow_reuse_address = True


def start_server():
    old = os.getcwd()
    os.chdir(LANDING)
    server = Server(('127.0.0.1', 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, old, f'http://127.0.0.1:{server.server_address[1]}'


def money_to_float(text):
    return float(text.replace('$', '').replace(',', '').strip())


def expect(condition, message):
    if not condition:
        raise AssertionError(message)


def test_lead(page, base):
    page.goto(base + '/gigs/lead-value-roi-calculator/', wait_until='networkidle')
    page.click('#calculate')
    expect(page.locator('#results:not(.hidden)').count() == 1, 'lead results should show after valid calculation')
    expect(page.locator('#validation-summary.hidden').count() == 1, 'lead validation should be hidden for valid input')
    expect(page.locator('#qualified-leads').inner_text() == '26.4', 'lead qualified leads mismatch')
    expect(page.locator('#new-clients').inner_text() == '2.11', 'lead new clients mismatch')
    expect('$1,111.97' in page.locator('#monthly-profit').inner_text(), 'lead gross profit mismatch')
    href = page.locator('#cta').get_attribute('href') or ''
    decoded = href.replace('%20', ' ')
    for token in ['Average revenue', 'Gross margin', 'Monthly ad spend', 'Break-even clients', 'Additional customer value']:
        expect(token.replace(' ', '%20') in href or token in decoded, f'lead email missing {token}')
    page.fill('#qualification-rate', '150')
    page.fill('#monthly-leads', '-10')
    page.click('#calculate')
    expect(page.locator('#validation-summary:not(.hidden)').count() == 1, 'lead invalid summary should show')
    expect(page.locator('#results.hidden').count() == 1, 'lead invalid should hide results')
    page.click('#reset-sample')
    expect(page.locator('#validation-summary.hidden').count() == 1, 'lead reset should clear validation')


def test_quote(page, base):
    page.goto(base + '/gigs/local-service-quote-calculator/', wait_until='networkidle')
    page.fill('#customer-name', 'Ada Buyer')
    page.fill('#customer-contact', 'ada@example.ca')
    page.fill('#service-location', 'N1R 1A1')
    page.fill('#project-notes', 'Back entrance, two pets, confirm parking.')
    page.select_option('#team-size', '1.2')
    page.select_option('#urgency', '1.12')
    page.check('.addon[data-cost="95"]')
    page.click('#calculate')
    expect(page.locator('#breakdown:not(.hidden)').count() == 1, 'quote breakdown should show')
    href = page.locator('#cta').get_attribute('href') or ''
    for token in ['Ada%20Buyer', 'N1R%201A1', '2%20technicians', 'Priority', 'materials', 'planning%20allowance']:
        expect(token.lower() in href.lower(), f'quote email missing {token}')
    expect('2–4 business days' in page.locator('#eta').inner_text(), 'quote urgency window mismatch')
    body = page.locator('body').inner_text().lower()
    expect('pricing configuration transparency' in body, 'quote transparency block missing')
    expect('tax/contingency' not in body, 'quote should not claim tax/contingency')
    expect(page.locator('#allowance').count() == 1, 'quote should use allowance id for sample planning allowance')
    page.fill('#hours', '0')
    page.click('#calculate')
    expect(page.locator('#breakdown.hidden').count() == 1, 'quote invalid hours should hide result')
    page.click('#reset-sample')
    expect(page.locator('#breakdown:not(.hidden)').count() == 1, 'quote reset should recalculate')


def test_scorecard(page, base):
    page.goto(base + '/gigs/website-audit-scorecard/', wait_until='networkidle')
    expect(page.locator('#score-output.hidden').count() == 1, 'scorecard should start hidden')
    expect('No score has been assigned yet.' in page.locator('#score-text').inner_text(), 'scorecard initial state copy missing')
    page.fill('#website-name', 'Ada Studio')
    page.fill('#website-url', 'https://adastudio.example')
    page.fill('#reviewer-notes', 'Test review notes')
    page.locator("input[data-label='value-prop']").evaluate("el => { el.value = 1; el.dispatchEvent(new Event('input', {bubbles:true})); }")
    page.click('#score-btn')
    expect(page.locator('#score-output:not(.hidden)').count() == 1, 'scorecard result should show after click')
    expect('Readiness band' in page.locator('body').inner_text(), 'readiness band label missing')
    href = page.locator('#cta').get_attribute('href') or ''
    for token in ['Ada%20Studio', 'Criterion%20scores', 'Readiness%20band']:
        expect(token in href, f'scorecard email missing {token}')
    page.click('#reset-sample')
    expect(page.locator('#score-output.hidden').count() == 1, 'scorecard reset should hide result')


def test_routes(page, base):
    for route in ROUTES:
        page.goto(base + route, wait_until='networkidle')
        body = page.locator('body').inner_text()
        lower = body.lower()
        expect(page.evaluate('document.documentElement.scrollWidth <= document.documentElement.clientWidth + 2'), f'{route} horizontal overflow')
        expect('live demo mini-site' not in lower, f'{route} old demo framing')
        expect('hello@example.com' not in lower, f'{route} placeholder email visible')
        if route != '/':
            expect('what a buyer receives' in lower, f'{route} buyer deliverables missing')
            expect(page.locator('.live-preview-gallery img').count() == 2, f'{route} screenshot gallery missing')


def main():
    server, old, base = start_server()
    report = {'base': base, 'routes': ROUTES, 'tests': []}
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            for name, viewport in [('desktop', {'width': 1440, 'height': 1000}), ('mobile', {'width': 390, 'height': 844})]:
                page = browser.new_page(viewport=viewport)
                errors = []
                page.on('pageerror', lambda exc: errors.append(str(exc)))
                test_routes(page, base)
                test_lead(page, base)
                test_quote(page, base)
                test_scorecard(page, base)
                expect(not errors, f'{name} page errors: {errors}')
                report['tests'].append({'viewport': name, 'ok': True})
                page.close()
            browser.close()
    finally:
        server.shutdown(); server.server_close(); os.chdir(old)
    out = ROOT / 'runtime' / 'vercel_gig_factory_regression_latest.json'
    out.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print('REGRESSION_OK', out)

if __name__ == '__main__':
    main()
