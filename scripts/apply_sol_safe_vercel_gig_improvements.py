from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTACT = 'thewatchersedgestore@gmail.com'

def patch_file(rel, replacements):
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    if text != original:
        path.write_text(text, encoding='utf-8')
        print('patched', rel)

# Make public demos clearer and less internal/placeholder-looking.
patch_file('gigs/lead-value-roi-calculator/index.html', [
    ('CUSTOMIZATION READY MINI-SITE', 'LIVE DEMO MINI-SITE'),
    ('Built for freelancers and small businesses to quickly estimate campaign profitability before spending ad dollars.', 'A working lead-value and ROI calculator mini-site for agencies, freelancers, and service businesses that want to show campaign value before spending ad dollars.'),
    ('Brand Name\n            <input id="brand-name" value="Your Agency" />', 'Demo brand name\n            <input id="brand-name" value="TWE Growth Studio" />'),
    ('Contact Email\n            <input id="brand-email" type="email" value="hello@yourbrand.com" />', 'Demo contact email\n            <input id="brand-email" type="email" value="hello@example.com" />'),
    ('CTA Text\n            <input id="cta-text" value="Book a growth call" />', 'Demo CTA text\n            <input id="cta-text" value="Book a growth call" />'),
    ('<a id="cta" class="cta" href="#">Book a campaign audit</a>', f'<a id="cta" class="cta" href="mailto:{CONTACT}?subject=Lead%20Value%20%26%20ROI%20Calculator%20mini-site">Ask about this mini-site</a>'),
    ('Tip: this is best used in sales calls to quickly test price, conversion, and margin scenarios.', 'Buyer note: this is a live static demo. The delivered mini-site can be customized with your brand, contact email, CTA wording, and calculator assumptions.'),
])

patch_file('gigs/local-service-quote-calculator/index.html', [
    ('CUSTOMIZATION READY MINI-SITE', 'LIVE DEMO MINI-SITE'),
    ('Turn service details into an instant, client-ready estimate for cleaners, landscapers, movers,\n          electricians, and other local businesses.', 'A working quote-builder mini-site for cleaners, landscapers, movers, electricians, and other local service businesses that need faster client estimates.'),
    ('<h2>Editable branding</h2>', '<h2>Demo settings</h2>'),
    ('Brand Name\n              <input id="brand-name" type="text" value="Your Service Business" />', 'Demo brand name\n              <input id="brand-name" type="text" value="TWE Local Services" />'),
    ('Contact Email\n              <input id="brand-email" type="email" value="hello@yourdomain.com" />', 'Demo contact email\n              <input id="brand-email" type="email" value="hello@example.com" />'),
    ('Primary CTA\n              <input id="brand-cta" type="text" value="Get your custom quote" />', 'Demo CTA\n              <input id="brand-cta" type="text" value="Get your custom quote" />'),
    ('<p class="brand-note">Change these fields and copy in <code>index.html</code> to match your client brand.</p>', '<p class="brand-note">These fields demonstrate how the delivered static mini-site can be customized for a buyer\'s own brand, contact email, and offer.</p>'),
    ('<p><strong>Taxes / contingency (placeholder):</strong> <span id="tax">$0</span></p>', '<p><strong>Estimated planning buffer:</strong> <span id="tax">$0</span></p>'),
    ('<a id="cta" class="cta-button" href="#">Email estimate to lead</a>', f'<a id="cta" class="cta-button" href="mailto:{CONTACT}?subject=Local%20Service%20Quote%20Calculator%20mini-site">Ask about this mini-site</a>'),
])

patch_file('gigs/website-audit-scorecard/index.html', [
    ('CUSTOMIZATION READY MINI-SITE', 'LIVE DEMO MINI-SITE'),
    ('Help clients identify the 5 biggest improvement areas in under 90 seconds.', 'A working website audit scorecard mini-site that helps agencies and freelancers show prospects what to fix before a larger web project starts.'),
    ('Brand Name\n            <input id="brand-name" value="Your Brand" />', 'Demo brand name\n            <input id="brand-name" value="TWE Web Review" />'),
    ('Contact Email\n            <input id="brand-email" type="email" value="hello@yourbrand.com" />', 'Demo contact email\n            <input id="brand-email" type="email" value="hello@example.com" />'),
    ('Offer CTA Text\n            <input id="cta-text" value="Order my website cleanup" />', 'Demo CTA text\n            <input id="cta-text" value="Order my website cleanup" />'),
    ('<a id="cta" class="cta" href="#">Take the website audit offer</a>', f'<a id="cta" class="cta" href="mailto:{CONTACT}?subject=Website%20Audit%20Scorecard%20mini-site">Ask about this mini-site</a>'),
])

# Safer ROI calculation wording.
patch_file('gigs/lead-value-roi-calculator/script.js', [
    ("  const breakEvenClients = adSpend > 0 && (margin > 0)\n    ? Math.max(1, adSpend / (revenuePerClient * (1 + ltvUplift) * margin))\n    : 0;\n  const roi = adSpend > 0 ? ((grossProfit - adSpend) / adSpend) * 100 : (grossProfit > 0 ? 999 : 0);\n",
     "  const effectiveProfitPerClient = revenuePerClient * (1 + ltvUplift) * margin;\n  const breakEvenClients = adSpend > 0 && effectiveProfitPerClient > 0\n    ? adSpend / effectiveProfitPerClient\n    : 0;\n  const roi = adSpend > 0 ? ((grossProfit - adSpend) / adSpend) * 100 : null;\n"),
    ("  roiLine.textContent = `${fmtPercent(roi)}`;\n", "  roiLine.textContent = roi === null ? 'Not applicable without ad spend' : `${fmtPercent(roi)}`;\n"),
    ("  if (roi >= 0) {\n", "  if (roi === null) {\n    roiLine.className = '';\n    interpretation.textContent = 'ROI needs a non-zero ad spend. Profit and client estimates are still shown above.';\n    interpretation.className = '';\n  } else if (roi >= 0) {\n"),
    ("    `- ROI: ${fmtPercent(roi)} / month`,\n", "    `- ROI: ${roi === null ? 'not applicable without ad spend' : fmtPercent(roi) + ' / month'}`,\n"),
])

# More accurate quote wording: this is a planning buffer, not a tax claim.
patch_file('gigs/local-service-quote-calculator/script.js', [
    ("const taxRate = 0.072;", "const planningBufferRate = 0.072;"),
    ("  const taxes = subtotalBeforeTax * taxRate;\n  const total = subtotalBeforeTax + taxes;", "  const planningBuffer = subtotalBeforeTax * planningBufferRate;\n  const total = subtotalBeforeTax + planningBuffer;"),
    ("  taxEl.textContent = currency.format(Math.round(taxes));", "  taxEl.textContent = currency.format(Math.round(planningBuffer));"),
    ("    `Estimated tax/contingency: ${currency.format(Math.round(taxes))}`,", "    `Estimated planning buffer: ${currency.format(Math.round(planningBuffer))}`,"),
])

# Keep deployed template in sync by re-running the publisher after originals are patched.
print('done')
