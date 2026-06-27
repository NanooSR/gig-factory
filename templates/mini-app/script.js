const result = document.getElementById('result');
document.getElementById('calculateBtn').addEventListener('click', () => {
  const base = Number(document.getElementById('projectType').value);
  const rush = Number(document.getElementById('rush').value);
  const revisions = Number(document.getElementById('revisions').value || 0) * 25;
  const total = base + rush + revisions;
  result.textContent = `Estimate: $${total}`;
});
