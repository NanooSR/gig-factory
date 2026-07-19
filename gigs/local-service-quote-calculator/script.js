const serviceType = document.getElementById('service-type');
const hours = document.getElementById('hours');
const hourlyRate = document.getElementById('hourly-rate');
const teamSize = document.getElementById('team-size');
const urgency = document.getElementById('urgency');
const materials = document.getElementById('materials');
const addonInputs = Array.from(document.querySelectorAll('.addon'));

const resultCard = document.getElementById('breakdown');
const subtotalEl = document.getElementById('subtotal');
const taxEl = document.getElementById('tax');
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

const planningBufferRate = 0.072;
const currency = new Intl.NumberFormat('en-CA', { style: 'currency', currency: 'CAD' });

function isUsablePreviewEmail(value) {
  const email = value.trim().toLowerCase();
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
    && !email.endsWith('@example.com')
    && !email.includes('yourbrand')
    && !email.includes('yourdomain');
}

function calculateTotal() {
  const base = Number(serviceType.value);
  const laborHours = Math.max(0, Number(hours.value || 0));
  const laborRate = Math.max(0, Number(hourlyRate.value || 0));
  const team = Number(teamSize.value);
  const urgencyMultiplier = Number(urgency.value);
  const materialsCost = Number(materials.value || 0);

  const addOns = addonInputs
    .filter(input => input.checked)
    .reduce((sum, input) => sum + Number(input.dataset.cost), 0);

  const laborCost = laborHours * laborRate;
  const subtotalBeforeBuffer = (base + laborCost + materialsCost + addOns) * team * urgencyMultiplier;
  const planningBuffer = subtotalBeforeBuffer * planningBufferRate;
  const total = subtotalBeforeBuffer + planningBuffer;

  const deposit = Math.round(total * 0.35);
  const eta = urgencyMultiplier > 1.2
    ? '2 business days'
    : urgencyMultiplier > 1.05
      ? '2-4 business days'
      : '4-7 business days';

  const band = total >= 800
    ? 'Professional package pricing tier'
    : total >= 450
      ? 'Starter-mid package pricing tier'
      : 'Intro package pricing tier';

  const brandEmail = brandEmailEl.value.trim();
  const brandName = brandNameEl.value.trim() || 'Your Business';

  const estimateIsUsable = hours.checkValidity() && hourlyRate.checkValidity() && materials.checkValidity() && laborHours >= 1 && laborRate >= 20 && materialsCost >= 0;
  if (!estimateIsUsable) {
    resultCard.classList.add('hidden');
    ctaEl.removeAttribute('href');
    messageEl.textContent = 'Enter labor hours of at least 1, an hourly rate of at least $20, and non-negative materials to generate a demo estimate.';
    return;
  }

  subtotalEl.textContent = currency.format(Math.round(subtotalBeforeBuffer));
  taxEl.textContent = currency.format(Math.round(planningBuffer));
  totalEl.textContent = currency.format(Math.round(total));
  depositEl.textContent = currency.format(deposit);
  bandEl.textContent = band;
  etaEl.textContent = eta;
  messageEl.textContent = `${brandName} demo estimate generated. Review and replace the default pricing rules before sending this result to a customer.`;

  const subject = `Quote request from ${brandName}`;
  const body = [
    `Estimated service: ${serviceType.options[serviceType.selectedIndex].text}`,
    `Labor: ${laborHours}h @ $${laborRate}/h`,
    `Subtotal before planning buffer: ${currency.format(Math.round(subtotalBeforeBuffer))}`,
    `Estimated planning buffer: ${currency.format(Math.round(planningBuffer))}`,
    `Total: ${currency.format(Math.round(total))}`,
    `Suggested deposit: ${currency.format(deposit)}`,
    `Projected turnaround: ${eta}`,
    'Generated with Local Service Quote Calculator mini-site. Final tax, permit, and travel rules should be confirmed by the service provider.'
  ].join('\n');

  if (isUsablePreviewEmail(brandEmail)) {
    ctaEl.href = `mailto:${encodeURIComponent(brandEmail)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    ctaEl.textContent = ctaTextEl.value.trim() || 'Preview quote email';
  } else {
    ctaEl.removeAttribute('href');
    ctaEl.textContent = 'Enter a real email to preview quote email';
  }

  if (resultCard.classList.contains('hidden')) {
    resultCard.classList.remove('hidden');
  }
}

function updateBrand() {
  const brandName = brandNameEl.value.trim() || 'Your Service Business';
  gigTitle.textContent = `${brandName} Quote Calculator`;
  ctaTextEl.value = ctaTextEl.value || 'Get your custom quote';
}

document.getElementById('calculate').addEventListener('click', calculateTotal);
document.getElementById('brand-name').addEventListener('input', updateBrand);
updateBrand();
calculateTotal();
