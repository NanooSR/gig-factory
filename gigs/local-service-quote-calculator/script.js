const BRAND_EMAIL_DEFAULT = 'hello@yourdomain.com';

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
  const subtotalBeforeTax = (base + laborCost + materialsCost + addOns) * team * urgencyMultiplier;
  const planningBuffer = subtotalBeforeTax * planningBufferRate;
  const total = subtotalBeforeTax + planningBuffer;

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

  const brandEmail = brandEmailEl.value.trim() || BRAND_EMAIL_DEFAULT;
  const brandName = brandNameEl.value.trim() || 'Your Business';

  subtotalEl.textContent = currency.format(Math.round(subtotalBeforeTax));
  taxEl.textContent = currency.format(Math.round(planningBuffer));
  totalEl.textContent = currency.format(Math.round(total));
  depositEl.textContent = currency.format(deposit);
  bandEl.textContent = band;
  etaEl.textContent = eta;
  const estimateIsUsable = laborHours > 0 && laborRate > 0;
  messageEl.textContent = estimateIsUsable
    ? `${brandName} quote generated. Paste this in a proposal email.`
    : 'Add positive labor hours and hourly rate before treating this as a usable quote.';

  const subject = `Quote request from ${brandName}`;
  const body = [
    `Estimated service: ${serviceType.options[serviceType.selectedIndex].text}`,
    `Labor: ${laborHours}h @ $${laborRate}/h`,
    `Subtotal before tax: ${currency.format(Math.round(subtotalBeforeTax))}`,
    `Estimated planning buffer: ${currency.format(Math.round(planningBuffer))}`,
    `Total: ${currency.format(Math.round(total))}`,
    `Suggested deposit: ${currency.format(deposit)}`,
    `Projected turnaround: ${eta}`,
    'Generated with Local Service Quote Calculator mini-site. Final tax, permit, and travel rules should be confirmed by the service provider.'
  ].join('\n');

  ctaEl.href = `mailto:${encodeURIComponent(brandEmail)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  ctaEl.textContent = ctaTextEl.value.trim() || 'Get your custom quote';

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
