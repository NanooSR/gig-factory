document.getElementById('lead-form').addEventListener('submit', function (e) {
  e.preventDefault();
  document.getElementById('form-status').textContent = 'Thanks — your request has been captured. Connect this form to email, Tally, Formspree, or your backend.';
  this.reset();
});
