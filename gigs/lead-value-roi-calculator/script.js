const currency = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' });

function round2(n) { return Number(n.toFixed(2)); }

function fmtPercent(value, digits = 1) {
  return `${round2(value).toFixed(digits)}%`;
}

function isUsablePreviewEmail(value) {
  const email = value.trim().toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    && !email.endsWith('@example.com')
    && !email.includes('yourbrand')
    && !email.includes('yourdomain');
}

function readNumber(id) {
  const input = document.getElementById(id);
  const value = Number(input.value || 0);
  const min = input.min !== '' ? Number(input.min) : -Infinity;
  const max = input.max !== '' ? Number(input.max) : Infinity;
  return Math.min(max, Math.max(min, Number.isFinite(value) ? value : 0));
}

function run() {
  const monthlyLeads = readNumber('monthly-leads');
  const qualificationRate = readNumber('qualification-rate') / 100;
  const closeRate = readNumber('close-rate') / 100;
  const revenuePerClient = readNumber('revenue-per-client');
  const margin = readNumber('gross-margin') / 100;
  const adSpend = readNumber('ad-spend');
  const ltvUplift = readNumber('ltv-uplift') / 100;

  const qualifiedLeads = Math.max(0, monthlyLeads * qualificationRate);
  const newClients = Math.max(0, qualifiedLeads * closeRate);
  const effectiveRevenuePerClient = revenuePerClient * (1 + ltvUplift);
  const grossRevenue = newClients * effectiveRevenuePerClient;
  const grossProfit = grossRevenue * margin;

  const effectiveProfitPerClient = revenuePerClient * (1 + ltvUplift) * margin;
  const breakEvenClients = adSpend > 0 && effectiveProfitPerClient > 0
    ? adSpend / effectiveProfitPerClient
    : 0;
  const roi = adSpend > 0 ? ((grossProfit - adSpend) / adSpend) * 100 : null;
  const costPerLead = monthlyLeads > 0 ? adSpend / monthlyLeads : 0;

  const status = document.getElementById('status-line');
  const results = document.getElementById('results');
  const interpretation = document.getElementById('interpretation');
  const roiLine = document.getElementById('roi');

  document.getElementById('qualified-leads').textContent = round2(qualifiedLeads).toLocaleString();
  document.getElementById('new-clients').textContent = round2(newClients).toLocaleString();
  document.getElementById('monthly-profit').textContent = currency.format(grossProfit);
  document.getElementById('break-even').textContent = round2(breakEvenClients) > 0
    ? `${round2(breakEvenClients)} clients / ${Math.ceil(breakEvenClients)} whole-client target`
    : 'n/a';
  document.getElementById('cost-per-lead').textContent = currency.format(costPerLead);

  roiLine.textContent = roi === null ? 'Not applicable without ad spend' : `${fmtPercent(roi)}`;
  const hasEnoughInputs = monthlyLeads > 0 && revenuePerClient > 0 && margin > 0;
  status.textContent = hasEnoughInputs
    ? 'Illustrative scenario is ready. Verify conversion, margin, timing, retention, and cost assumptions before using this in a budget decision.'
    : 'Add lead volume, revenue, and margin assumptions to make this forecast meaningful.';

  if (roi === null) {
    roiLine.className = '';
    interpretation.textContent = 'Estimated ROI needs a non-zero ad spend. Client and gross-profit estimates are still shown above.';
    interpretation.className = '';
  } else if (roi >= 0) {
    roiLine.className = 'good';
    interpretation.textContent = 'Positive scenario under the entered assumptions. Verify the conversion, margin, timing, retention, and cost inputs before using this estimate in a budget decision.';
    interpretation.className = 'good';
  } else {
    roiLine.className = 'bad';
    interpretation.textContent = 'Negative scenario under the entered assumptions. Review lead quality, conversion, margin, customer value, and acquisition cost. No single adjustment guarantees a profitable result.';
    interpretation.className = 'bad';
  }

  const brandEmail = document.getElementById('brand-email').value.trim();
  const brandName = document.getElementById('brand-name').value.trim() || 'Your Agency';
  const ctaText = document.getElementById('cta-text').value.trim() || 'Book a growth call';

  const subject = `${brandName} - Lead ROI strategy review`;
  const body = [
    `Assumptions used:`,
    `- Monthly leads: ${monthlyLeads}`,
    `- Qualified leads (${fmtPercent(qualificationRate * 100)}): ${round2(qualifiedLeads)}`,
    `- New clients (${fmtPercent(closeRate * 100)}): ${round2(newClients)}`,
    `- Estimated gross profit from projected new clients: ${currency.format(grossProfit)}`,
    `- Estimated gross-profit ROI after ad spend: ${roi === null ? 'not applicable without ad spend' : fmtPercent(roi)}`,
    `- Estimated cost/lead: ${currency.format(costPerLead)}`
  ].join('\n');

  const cta = document.getElementById('cta');
  if (isUsablePreviewEmail(brandEmail)) {
    cta.textContent = ctaText || 'Preview results email';
    cta.href = `mailto:${encodeURIComponent(brandEmail)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  } else {
    cta.textContent = 'Enter a real email to preview results email';
    cta.removeAttribute('href');
  }

  results.classList.remove('hidden');
}

document.getElementById('calculate').addEventListener('click', run);
run();
