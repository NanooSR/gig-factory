const leadForm = document.getElementById('lead-form');
const formStatus = document.getElementById('form-status');

if (leadForm && formStatus) {
  leadForm.addEventListener('submit', function (e) {
    e.preventDefault();
    formStatus.textContent = 'Thanks — your request has been captured. Connect this form to email, Tally, Formspree, or your backend.';
    this.reset();
  });
}
