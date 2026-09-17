/**
 * ==========================================================================
 * Page Specific Logic: 05-reset-password.html (إعادة تعيين كلمة المرور)
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initResetPasswordForm();
});

function initResetPasswordForm() {
  const form = document.getElementById('resetForm');
  if (!form) return;

  const passwordInput = document.getElementById('password');
  const confirmInput = document.getElementById('confirm');
  const confirmField = document.getElementById('confirmField');
  const submitBtn = document.getElementById('submitBtn');
  const submitText = document.getElementById('submitText');
  const formBox = document.getElementById('formBox');
  const successBox = document.getElementById('successBox');
  const goLoginBtn = document.getElementById('goLoginBtn');

  const bars = [
    document.getElementById('bar1'),
    document.getElementById('bar2'),
    document.getElementById('bar3'),
    document.getElementById('bar4')
  ];
  const strengthLabel = document.getElementById('strengthLabel');

  const ruleLength = document.getElementById('rule-length');
  const ruleUpper = document.getElementById('rule-upper');
  const ruleNumber = document.getElementById('rule-number');

  function checkRules(value) {
    const hasLength = value.length >= 8;
    const hasUpperLower = /[a-z]/.test(value) && /[A-Z]/.test(value);
    const hasNumber = /[0-9]/.test(value);

    if (ruleLength) ruleLength.classList.toggle('met', hasLength);
    if (ruleUpper) ruleUpper.classList.toggle('met', hasUpperLower);
    if (ruleNumber) ruleNumber.classList.toggle('met', hasNumber);

    const score = [hasLength, hasUpperLower, hasNumber].filter(Boolean).length;
    return { hasLength, hasUpperLower, hasNumber, score };
  }

  function updateStrengthBar(value, score) {
    const colors = ['', 'var(--danger)', 'var(--warning)', 'var(--success)', 'var(--success)'];
    const labels = ['', 'ضعيفة', 'متوسطة', 'قوية', 'قوية جدًا'];
    const activeCount = value.length === 0 ? 0 : Math.max(1, score + (value.length >= 12 ? 1 : 0));

    bars.forEach((bar, i) => {
      if (bar) {
        bar.style.background = i < activeCount ? colors[Math.min(activeCount, 4)] : 'var(--border)';
      }
    });

    if (strengthLabel) {
      strengthLabel.textContent = value.length === 0 ? '\u00A0' : labels[Math.min(activeCount, 4)];
    }
  }

  function validateForm() {
    const { hasLength, hasUpperLower, hasNumber } = checkRules(passwordInput.value);
    const allMet = hasLength && hasUpperLower && hasNumber;
    const matches = confirmInput.value.length > 0 && confirmInput.value === passwordInput.value;

    submitBtn.disabled = !(allMet && matches);
    return { allMet, matches };
  }

  passwordInput.addEventListener('input', () => {
    const { score } = checkRules(passwordInput.value);
    updateStrengthBar(passwordInput.value, score);
    validateForm();
  });

  confirmInput.addEventListener('input', () => {
    if (confirmInput.value.length > 0 && confirmInput.value !== passwordInput.value) {
      setFieldError(confirmField, true);
    } else {
      setFieldError(confirmField, false);
    }
    validateForm();
  });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const { allMet, matches } = validateForm();
    if (!matches) {
      setFieldError(confirmField, true);
      return;
    }
    if (!allMet) return;

    submitBtn.classList.add('loading');
    if (submitText) submitText.textContent = 'جارٍ الحفظ...';

    setTimeout(() => {
      submitBtn.classList.remove('loading');
      if (submitText) submitText.textContent = 'حفظ كلمة المرور';
      if (formBox) formBox.classList.add('hide');
      if (successBox) successBox.classList.add('show');
    }, 900);
  });

  if (goLoginBtn) {
    goLoginBtn.addEventListener('click', () => {
      window.location.href = '03-login.html';
    });
  }
}
