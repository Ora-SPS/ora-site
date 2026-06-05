const form = document.querySelector('#waitlist-form');
const emailInput = document.querySelector('#email');
const companyInput = document.querySelector('#company');
const submitButton = document.querySelector('#waitlist-submit');
const statusEl = document.querySelector('#waitlist-status');

const supportEmail = 'support@oracoach.app';
const allowedGoals = new Set(['training', 'nutrition', 'coach', 'all-in-one']);

const getPrimaryGoal = () => {
  const selected = document.querySelector('input[name="primary_goal"]:checked');
  if (!selected || !allowedGoals.has(selected.value)) return 'not selected';
  return selected.value;
};

const setStatus = (message, type) => {
  if (!statusEl) return;
  statusEl.textContent = message;
  statusEl.className = `form-status ${type || ''}`.trim();
};

if (form && emailInput && companyInput && submitButton) {
  form.addEventListener('submit', (event) => {
    event.preventDefault();

    const email = emailInput.value.trim().toLowerCase();
    if (!email || !emailInput.validity.valid) {
      setStatus('Enter a valid email address.', 'error');
      emailInput.focus();
      return;
    }

    if (companyInput.value) {
      setStatus(`Email ${supportEmail} to join the beta.`, 'success');
      return;
    }

    const subject = 'Ora beta access request';
    const body = [
      'I would like to join the Ora beta.',
      '',
      `Email: ${email}`,
      `Primary goal: ${getPrimaryGoal()}`,
      `Page: ${window.location.href}`,
    ].join('\n');

    window.location.href = `mailto:${supportEmail}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    setStatus(`Opening your email app. If nothing opens, email ${supportEmail}.`, 'success');
  });
}
