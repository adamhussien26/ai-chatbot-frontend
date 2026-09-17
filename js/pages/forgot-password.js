/**
 * ==========================================================================
 * Page Specific Logic: 04-forgot-password.html (نسيت كلمة المرور)
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initForgotPasswordForm();
});

function initForgotPasswordForm() {
  const form = document.getElementById('resetForm');
  if (!form) return;

  const emailField = document.getElementById('emailField');
  const emailInput = document.getElementById('email');
  const submitBtn = document.getElementById('submitBtn');
  const submitText = document.getElementById('submitText');
  const formBox = document.getElementById('formBox');
  const successBox = document.getElementById('successBox');
  const sentEmail = document.getElementById('sentEmail');
  const resendBtn = document.getElementById('resendBtn');

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const value = emailInput.value.trim();

    if (!isValidEmail(value)) {
      setFieldError(emailField, true);
      return;
    }
    setFieldError(emailField, false);

    submitBtn.classList.add('loading');
    if (submitText) submitText.textContent = 'جارٍ الإرسال...';

    setTimeout(() => {
      submitBtn.classList.remove('loading');
      if (submitText) submitText.textContent = 'إرسال رابط إعادة التعيين';
      if (sentEmail) sentEmail.textContent = value;
      if (formBox) formBox.classList.add('hide');
      if (successBox) successBox.classList.add('show');
      startResendCooldown(resendBtn);
    }, 900);
  });

  if (resendBtn) {
    resendBtn.addEventListener('click', () => {
      if (resendBtn.disabled) return;
      startResendCooldown(resendBtn);
    });
  }
}

/**
 * Starts a 30-second cooldown timer for resending password reset link.
 * @param {HTMLButtonElement} resendBtn
 */
function startResendCooldown(resendBtn) {
  if (!resendBtn) return;

  let seconds = 30;
  resendBtn.disabled = true;
  resendBtn.textContent = `إعادة الإرسال (${seconds})`;

  const interval = setInterval(() => {
    seconds--;
    if (seconds <= 0) {
      clearInterval(interval);
      resendBtn.disabled = false;
      resendBtn.textContent = 'إعادة الإرسال';
    } else {
      resendBtn.textContent = `إعادة الإرسال (${seconds})`;
    }
  }, 1000);
}
