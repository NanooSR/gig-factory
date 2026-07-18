from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def patch(rel, old, new):
    p=ROOT/rel; s=p.read_text(encoding='utf-8')
    if old not in s:
        raise SystemExit(f'missing pattern in {rel}: {old[:80]}')
    p.write_text(s.replace(old,new),encoding='utf-8')
    print('patched',rel)

# ROI: make blank/zero state explicit instead of silently looking like a meaningful forecast.
patch('gigs/lead-value-roi-calculator/script.js',
"  status.textContent = 'Forecast is ready. Use this to compare offer quality against ad spend.';\n\n  if (roi === null) {",
"  const hasEnoughInputs = monthlyLeads > 0 && revenuePerClient > 0 && margin > 0;\n  status.textContent = hasEnoughInputs\n    ? 'Forecast is ready. Use this to compare offer quality against ad spend.'\n    : 'Add lead volume, revenue, and margin assumptions to make this forecast meaningful.';\n\n  if (roi === null) {")

# Quote calculator: clamp unrealistic blank/zero values and label buffer clearly.
patch('gigs/local-service-quote-calculator/script.js',
"  const laborHours = Number(hours.value || 0);\n  const laborRate = Number(hourlyRate.value || 0);",
"  const laborHours = Math.max(0, Number(hours.value || 0));\n  const laborRate = Math.max(0, Number(hourlyRate.value || 0));")
patch('gigs/local-service-quote-calculator/script.js',
"  messageEl.textContent = `${brandName} quote generated. Paste this in a proposal email.`;",
"  const estimateIsUsable = laborHours > 0 && laborRate > 0;\n  messageEl.textContent = estimateIsUsable\n    ? `${brandName} quote generated. Paste this in a proposal email.`\n    : 'Add positive labor hours and hourly rate before treating this as a usable quote.';")
patch('gigs/local-service-quote-calculator/script.js',
"    `Generated with Local Service Quote Calculator mini-site.'",
"    `Generated with Local Service Quote Calculator mini-site. Final tax, permit, and travel rules should be confirmed by the service provider.'")

# Website audit: avoid contradictory 'Good/fix gaps' band with 'Great job all strong' when all sliders are merely 3.
patch('gigs/website-audit-scorecard/script.js',
"    if (value <= 2) {\n      lowScorers.push(key);\n    }",
"    if (value <= 3) {\n      lowScorers.push(key);\n    }")
patch('gigs/website-audit-scorecard/script.js',
"    li.textContent = 'Great job — all core areas are strong. Consider A/B testing hero variants for growth.';",
"    li.textContent = total >= 40\n      ? 'Great job — all core areas are strong. Consider A/B testing hero variants for growth.'\n      : 'No severe single-area failure detected, but the total score still needs stronger proof, clearer CTA flow, and trust signals before calling the page launch-ready.';")
print('done')
