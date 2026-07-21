const CONFIG = {
  planningBufferRate: 0.072,
  depositRate: 0.35,
  services: {
    '260': { label: 'Standard residential cleaning visit', baseFee: 260 },
    '420': { label: 'Deep cleaning / move-out cleaning', baseFee: 420 },
    '180': { label: 'Kitchen or bathroom add-on block', baseFee: 180 },
    '95': { label: 'Inside-fridge or inside-oven add-on', baseFee: 95 }
  },
  crewMultipliers: {
    '1': { label: '1 technician — 1.00× labour', multiplier: 1 },
    '1.2': { label: '2 technicians — 1.20× labour sample', multiplier: 1.2 },
    '1.35': { label: '3–4 technicians — 1.35× labour sample', multiplier: 1.35 }
  },
  urgencyRules: {
    '1': { label: 'Standard (4–7 business days)', multiplier: 1, window: '4–7 business days' },
    '1.12': { label: 'Priority (2–4 business days)', multiplier: 1.12, window: '2–4 business days' },
    '1.22': { label: 'Rush (2 business days)', multiplier: 1.22, window: '2 business days' }
  }
};

const serviceType = document.getElementById('service-type');
const hours = document.getElementById('hours');
const hourlyRate = document.getElementById('hourly-rate');
const teamSize = document.getElementById('team-size');
const urgency = document.getElementById('urgency');
const materials = document.getElementById('materials');
const addonInputs = Array.from(document.querySelectorAll('.addon'));
const resultCard = document.getElementById('breakdown');
const laborSubtotalEl = document.getElementById('labor-subtotal');
const fixedSubtotalEl = document.getElementById('fixed-subtotal');
const subtotalEl = document.getElementById('subtotal');
const allowanceEl = document.getElementById('allowance');
const totalEl = document.getElementById('total');
const bandEl = document.getElementById('band');
const ctaEl = document.getElementById('cta');
const ctaTextEl = document.getElementById('brand-cta');
const depositEl = document.getElementById('deposit');
const etaEl = document.getElementById('eta');
const brandNameEl = document.getElementById('brand-name');
const brandEmailEl = document.getElementById('brand-email');
const gigTitle = document.getElementById('gig-title');
const messageEl = document.getElementById('client-message');
const customerNameEl = document.getElementById('customer-name');
const customerContactEl = document.getElementById('customer-contact');
const serviceLocationEl = document.getElementById('service-location');
const projectNotesEl = document.getElementById('project-notes');
const currency = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' });
let lastEstimate = null;

function isUsablePreviewEmail(value) {
  const email = value.trim().toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    && !email.endsWith('@example.com')
    && !email.includes('yourbrand')
    && !email.includes('yourdomain');
}

function updateOptionLabels() {
  Array.from(teamSize.options).forEach((option) => { option.textContent = CONFIG.crewMultipliers[option.value]?.label || option.textContent; });
  Array.from(urgency.options).forEach((option) => { option.textContent = CONFIG.urgencyRules[option.value]?.label || option.textContent; });
}

function selectedAddons() {
  return addonInputs.filter((input) => input.checked).map((input) => ({ label: input.parentElement.textContent.trim(), cost: Number(input.dataset.cost) }));
}

function readEstimate() {
  const service = CONFIG.services[serviceType.value] || { label: serviceType.options[serviceType.selectedIndex].text, baseFee: Number(serviceType.value) };
  const crew = CONFIG.crewMultipliers[teamSize.value] || { label: teamSize.options[teamSize.selectedIndex].text, multiplier: Number(teamSize.value) };
  const urgencyRule = CONFIG.urgencyRules[urgency.value] || { label: urgency.options[urgency.selectedIndex].text, multiplier: Number(urgency.value), window: 'Confirm with provider' };
  const laborHours = Number(hours.value || 0);
  const laborRate = Number(hourlyRate.value || 0);
  const materialsCost = Number(materials.value || 0);
  const addons = selectedAddons();
  const addOnsTotal = addons.reduce((sum, addon) => sum + addon.cost, 0);
  const laborCost = laborHours * laborRate;
  const adjustedLaborCost = laborCost * crew.multiplier * urgencyRule.multiplier;
  const fixedAndPassThroughCosts = service.baseFee + materialsCost + addOnsTotal;
  const subtotalBeforeBuffer = adjustedLaborCost + fixedAndPassThroughCosts;
  const planningBuffer = subtotalBeforeBuffer * CONFIG.planningBufferRate;
  const total = subtotalBeforeBuffer + planningBuffer;
  const deposit = Math.round(total * CONFIG.depositRate);
  const band = total >= 800 ? 'Illustrative high-scope band — replace before customer use' : total >= 450 ? 'Illustrative mid-scope band — replace before customer use' : 'Illustrative starter band — replace before customer use';
  return { service, crew, urgencyRule, laborHours, laborRate, materialsCost, addons, addOnsTotal, adjustedLaborCost, fixedAndPassThroughCosts, subtotalBeforeBuffer, planningBuffer, total, deposit, band, customerName: customerNameEl.value.trim(), customerContact: customerContactEl.value.trim(), serviceLocation: serviceLocationEl.value.trim(), projectNotes: projectNotesEl.value.trim() };
}

function isEstimateUsable(estimate) {
  return hours.checkValidity() && hourlyRate.checkValidity() && materials.checkValidity()
    && estimate.laborHours >= 1 && estimate.laborRate >= 20 && estimate.materialsCost >= 0;
}

function estimateLines(estimate) {
  const addonLine = estimate.addons.length ? estimate.addons.map((addon) => `${addon.label} (${currency.format(addon.cost)})`).join('; ') : 'None selected';
  return [
    `Customer/project: ${estimate.customerName || 'Not provided'}`,
    `Reply contact: ${estimate.customerContact || 'Not provided'}`,
    `Service location/postal code: ${estimate.serviceLocation || 'Not provided'}`,
    `Project details/access notes: ${estimate.projectNotes || 'Not provided'}`,
    `Selected service: ${estimate.service.label}`,
    `Sample base service fee: ${currency.format(estimate.service.baseFee)}`,
    `Labour: ${estimate.laborHours}h @ ${currency.format(estimate.laborRate)}/h`,
    `Approved crew-size labour multiplier: ${estimate.crew.label}`,
    `Urgency/completion rule: ${estimate.urgencyRule.label}`,
    `Selected add-ons: ${addonLine}`,
    `Materials/pass-through input: ${currency.format(estimate.materialsCost)}`,
    `Labour subtotal after crew/urgency: ${currency.format(Math.round(estimate.adjustedLaborCost))}`,
    `Fixed service/add-on/pass-through costs: ${currency.format(Math.round(estimate.fixedAndPassThroughCosts))}`,
    `Subtotal: ${currency.format(Math.round(estimate.subtotalBeforeBuffer))}`,
    `Illustrative planning allowance (7.2% sample — replace with approved rule): ${currency.format(Math.round(estimate.planningBuffer))}`,
    `Total non-binding estimate: ${currency.format(Math.round(estimate.total))}`,
    `Illustrative deposit (${Math.round(CONFIG.depositRate * 100)}% sample): ${currency.format(estimate.deposit)}`,
    `Illustrative completion window: ${estimate.urgencyRule.window}`
  ];
}

function calculateTotal() {
  const estimate = readEstimate();
  const brandEmail = brandEmailEl.value.trim();
  const brandName = brandNameEl.value.trim() || 'Your Business';
  if (!isEstimateUsable(estimate)) {
    resultCard.classList.add('hidden');
    ctaEl.removeAttribute('href');
    messageEl.textContent = 'Enter labor hours of at least 1, an hourly rate of at least $20, and non-negative materials to generate an estimate preview.';
    lastEstimate = null;
    return;
  }
  lastEstimate = estimate;
  laborSubtotalEl.textContent = currency.format(Math.round(estimate.adjustedLaborCost));
  fixedSubtotalEl.textContent = currency.format(Math.round(estimate.fixedAndPassThroughCosts));
  subtotalEl.textContent = currency.format(Math.round(estimate.subtotalBeforeBuffer));
  allowanceEl.textContent = currency.format(Math.round(estimate.planningBuffer));
  totalEl.textContent = currency.format(Math.round(estimate.total));
  depositEl.textContent = currency.format(estimate.deposit);
  bandEl.textContent = estimate.band;
  etaEl.textContent = estimate.urgencyRule.window;
  messageEl.textContent = `${brandName} estimate preview generated. Replace and test the service rules, deposits, completion windows, materials, travel, and contract language before customer use.`;

  const subjectName = estimate.customerName || estimate.service.label;
  const subject = `Estimate review — ${estimate.service.label} — ${subjectName}`;
  const body = [
    `Estimate review for ${brandName}`,
    '',
    ...estimateLines(estimate),
    '',
    'Generated with Custom Service Estimate & Intake Calculator preview. Planning estimate only; not a binding quote. Final scope, taxes, permits, travel, materials, availability, and contract terms must be confirmed by the service provider.'
  ].join('\n');
  if (isUsablePreviewEmail(brandEmail)) {
    ctaEl.href = `mailto:${encodeURIComponent(brandEmail)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    ctaEl.textContent = ctaTextEl.value.trim() || 'Preview estimate email';
  } else {
    ctaEl.removeAttribute('href');
    ctaEl.textContent = 'Enter a real email to preview estimate email';
  }
  resultCard.classList.remove('hidden');
}

function updateBrand() {
  const brandName = brandNameEl.value.trim() || 'Your Service Business';
  gigTitle.textContent = `${brandName} Estimate & Intake Calculator`;
  ctaTextEl.value = ctaTextEl.value || 'Get your custom estimate';
}

function quoteSummaryText() {
  const estimate = lastEstimate || readEstimate();
  return [
    'Custom Service Estimate & Intake Calculator summary',
    ...estimateLines(estimate),
    'Planning estimate only. Final quote requires provider approval.'
  ].join('\n');
}

async function copyQuoteSummary() {
  const estimate = lastEstimate || readEstimate();
  if (!isEstimateUsable(estimate)) {
    messageEl.textContent = 'Enter valid estimate details before copying the summary.';
    return;
  }
  const text = quoteSummaryText();
  try {
    await navigator.clipboard.writeText(text);
    messageEl.textContent = 'Estimate and intake summary copied. Confirm final scope, taxes, materials, travel, permits, and contract terms before customer use.';
  } catch (error) {
    messageEl.textContent = text;
  }
}

function resetSampleEstimate() {
  brandNameEl.value = 'TWE Local Services';
  brandEmailEl.value = 'thewatchersedgestore@gmail.com';
  ctaTextEl.value = 'Get your custom estimate';
  customerNameEl.value = 'Sample Customer';
  customerContactEl.value = 'customer@example.ca';
  serviceLocationEl.value = 'Cambridge, ON';
  projectNotesEl.value = 'Three-bedroom home; confirm parking, pets, and access before final quote.';
  serviceType.value = '260';
  hours.value = '4';
  hourlyRate.value = '85';
  teamSize.value = '1';
  urgency.value = '1';
  materials.value = '40';
  addonInputs.forEach(input => { input.checked = false; });
  updateBrand();
  calculateTotal();
}

updateOptionLabels();
document.getElementById('calculate').addEventListener('click', calculateTotal);
brandNameEl.addEventListener('input', updateBrand);
[serviceType, hours, hourlyRate, teamSize, urgency, materials, customerNameEl, customerContactEl, serviceLocationEl, projectNotesEl, ctaTextEl, brandEmailEl].forEach((el) => el.addEventListener('input', calculateTotal));
addonInputs.forEach((el) => el.addEventListener('change', calculateTotal));
document.getElementById('copy-summary').addEventListener('click', copyQuoteSummary);
document.getElementById('reset-sample').addEventListener('click', resetSampleEstimate);
updateBrand();
calculateTotal();
