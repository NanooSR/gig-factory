const currency = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' });
const fieldIds = ['monthly-leads', 'qualification-rate', 'close-rate', 'revenue-per-client', 'gross-margin', 'ad-spend', 'ltv-uplift'];
let lastScenario = null;

function round2(n) { return Number(n.toFixed(2)); }
function fmtPercent(value, digits = 1) { return `${round2(value).toFixed(digits)}%`; }
function isUsablePreviewEmail(value) {
  const email = value.trim().toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    && !email.endsWith('@example.com')
    && !email.includes('yourbrand')
    && !email.includes('yourdomain');
}

function readRawNumber(id) {
  const input = document.getElementById(id);
  const value = Number(input.value);
  return { input, value };
}

function validateInputs() {
  const errors = [];
  fieldIds.forEach((id) => {
    const { input, value } = readRawNumber(id);
    const label = input.closest('label')?.textContent.trim().replace(/\s+/g, ' ') || id;
    const min = input.min !== '' ? Number(input.min) : -Infinity;
    const max = input.max !== '' ? Number(input.max) : Infinity;
    const valid = Number.isFinite(value) && value >= min && value <= max;
    input.classList.toggle('field-error', !valid);
    input.setAttribute('aria-invalid', valid ? 'false' : 'true');
    if (!valid) {
      errors.push(`${label} must be ${Number.isFinite(min) ? `at least ${min}` : 'a number'}${Number.isFinite(max) ? ` and no more than ${max}` : ''}.`);
    }
  });
  return errors;
}

function showValidation(errors) {
  const summary = document.getElementById('validation-summary');
  if (!summary) return;
  if (!errors.length) {
    summary.classList.add('hidden');
    summary.innerHTML = '';
    return;
  }
  summary.classList.remove('hidden');
  summary.innerHTML = `<strong>Correct the highlighted fields before calculating.</strong><ul>${errors.map((error) => `<li>${error}</li>`).join('')}</ul><p>Each percentage must remain within the range shown for that field; money and lead values cannot be negative; the values shown will be the values used.</p>`;
}

function readNumber(id) { return Number(document.getElementById(id).value); }

function buildScenario() {
  const monthlyLeads = readNumber('monthly-leads');
  const qualificationRatePct = readNumber('qualification-rate');
  const closeRatePct = readNumber('close-rate');
  const revenuePerClient = readNumber('revenue-per-client');
  const marginPct = readNumber('gross-margin');
  const adSpend = readNumber('ad-spend');
  const ltvUpliftPct = readNumber('ltv-uplift');
  const qualificationRate = qualificationRatePct / 100;
  const closeRate = closeRatePct / 100;
  const margin = marginPct / 100;
  const ltvUplift = ltvUpliftPct / 100;
  const qualifiedLeads = monthlyLeads * qualificationRate;
  const newClients = qualifiedLeads * closeRate;
  const effectiveRevenuePerClient = revenuePerClient * (1 + ltvUplift);
  const grossRevenue = newClients * effectiveRevenuePerClient;
  const grossProfit = grossRevenue * margin;
  const profitPerClient = effectiveRevenuePerClient * margin;
  const breakEvenClients = adSpend > 0 && profitPerClient > 0 ? adSpend / profitPerClient : 0;
  const roi = adSpend > 0 ? ((grossProfit - adSpend) / adSpend) * 100 : null;
  const costPerLead = monthlyLeads > 0 ? adSpend / monthlyLeads : 0;
  return { monthlyLeads, qualificationRatePct, closeRatePct, revenuePerClient, marginPct, adSpend, ltvUpliftPct, qualifiedLeads, newClients, effectiveRevenuePerClient, grossRevenue, grossProfit, profitPerClient, breakEvenClients, roi, costPerLead };
}

function scenarioLines(scenario) {
  return [
    `- Monthly leads: ${scenario.monthlyLeads}`,
    `- Qualification rate: ${fmtPercent(scenario.qualificationRatePct)}`,
    `- Qualified leads: ${round2(scenario.qualifiedLeads)}`,
    `- Client conversion rate: ${fmtPercent(scenario.closeRatePct)}`,
    `- New clients/month: ${round2(scenario.newClients)}`,
    `- Average revenue/client: ${currency.format(scenario.revenuePerClient)}`,
    `- Additional customer value included: ${fmtPercent(scenario.ltvUpliftPct)}`,
    `- Effective revenue/client: ${currency.format(scenario.effectiveRevenuePerClient)}`,
    `- Gross margin: ${fmtPercent(scenario.marginPct)}`,
    `- Monthly ad spend: ${currency.format(scenario.adSpend)}`,
    `- Estimated gross profit: ${currency.format(scenario.grossProfit)}`,
    `- Break-even clients needed: ${scenario.breakEvenClients > 0 ? `${round2(scenario.breakEvenClients)} clients / ${Math.ceil(scenario.breakEvenClients)} whole-client target` : 'n/a'}`,
    `- Estimated gross-profit ROI after ad spend: ${scenario.roi === null ? 'not applicable without ad spend' : fmtPercent(scenario.roi)}`,
    `- Estimated cost/lead: ${currency.format(scenario.costPerLead)}`
  ];
}

function run() {
  const errors = validateInputs();
  showValidation(errors);
  const status = document.getElementById('status-line');
  const results = document.getElementById('results');
  const cta = document.getElementById('cta');
  if (errors.length) {
    results.classList.add('hidden');
    cta.removeAttribute('href');
    cta.textContent = 'Correct inputs to preview results email';
    status.textContent = 'Correct the highlighted fields before calculating. No hidden clamping is used.';
    lastScenario = null;
    return;
  }

  const scenario = buildScenario();
  lastScenario = scenario;
  document.getElementById('qualified-leads').textContent = round2(scenario.qualifiedLeads).toLocaleString();
  document.getElementById('new-clients').textContent = round2(scenario.newClients).toLocaleString();
  document.getElementById('monthly-profit').textContent = currency.format(scenario.grossProfit);
  document.getElementById('break-even').textContent = scenario.breakEvenClients > 0
    ? `${round2(scenario.breakEvenClients)} clients / ${Math.ceil(scenario.breakEvenClients)} whole-client target`
    : 'n/a';
  document.getElementById('cost-per-lead').textContent = currency.format(scenario.costPerLead);

  const roiLine = document.getElementById('roi');
  const interpretation = document.getElementById('interpretation');
  roiLine.textContent = scenario.roi === null ? 'Not applicable without ad spend' : fmtPercent(scenario.roi);
  const hasEnoughInputs = scenario.monthlyLeads > 0 && scenario.revenuePerClient > 0 && scenario.marginPct > 0;
  status.textContent = hasEnoughInputs
    ? 'Illustrative scenario is ready. Verify conversion, margin, timing, retention, and cost assumptions before using this in a budget decision.'
    : 'Add lead volume, revenue, and margin assumptions to make this forecast meaningful.';

  if (scenario.roi === null) {
    roiLine.className = '';
    interpretation.textContent = 'Estimated ROI needs a non-zero ad spend. Client and gross-profit estimates are still shown above.';
    interpretation.className = '';
  } else if (scenario.roi >= 0) {
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
  const ctaText = document.getElementById('cta-text').value.trim() || 'Preview results email';
  const subject = `${brandName} - Lead ROI strategy review`;
  const body = [
    'Assumptions used:',
    ...scenarioLines(scenario),
    '',
    'Scenario estimate only. Confirm lead quality, conversion timing, revenue, margin, retention, attribution, ad spend, and other costs before making a budget decision.'
  ].join('\n');

  if (isUsablePreviewEmail(brandEmail)) {
    cta.textContent = ctaText;
    cta.href = `mailto:${encodeURIComponent(brandEmail)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  } else {
    cta.textContent = 'Enter a real email to preview results email';
    cta.removeAttribute('href');
  }
  results.classList.remove('hidden');
}

function currentSummaryText() {
  const scenario = lastScenario || buildScenario();
  return [
    'Lead Value & Campaign Economics Calculator summary',
    ...scenarioLines(scenario),
    'Planning preview only. Verify all assumptions before budget decisions.'
  ].join('\n');
}

async function copySummary() {
  const errors = validateInputs();
  showValidation(errors);
  if (errors.length) {
    document.getElementById('status-line').textContent = 'Correct inputs before copying the summary.';
    return;
  }
  const text = currentSummaryText();
  try {
    await navigator.clipboard.writeText(text);
    document.getElementById('status-line').textContent = 'Result summary copied. Review the assumptions before sharing with a buyer or stakeholder.';
  } catch (error) {
    document.getElementById('status-line').textContent = text;
  }
}

function resetSample() {
  const sample = { 'brand-name': 'TWE Growth Studio', 'brand-email': 'thewatchersedgestore@gmail.com', 'cta-text': 'Book a growth call', 'monthly-leads': 120, 'qualification-rate': 22, 'close-rate': 8, 'revenue-per-client': 900, 'gross-margin': 45, 'ad-spend': 1800, 'ltv-uplift': 30 };
  Object.entries(sample).forEach(([id, value]) => { document.getElementById(id).value = value; });
  run();
}

document.getElementById('calculate').addEventListener('click', run);
document.getElementById('copy-summary').addEventListener('click', copySummary);
document.getElementById('reset-sample').addEventListener('click', resetSample);
fieldIds.forEach((id) => document.getElementById(id).addEventListener('input', () => showValidation(validateInputs())));
run();
