/**
 * ==========================================================================
 * Page Specific Logic: 02-signup.html (صفحة إنشاء حساب)
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initSignupForm();
  initGoogleAuth();
});

/**
 * Handles signup form submission, validation and redirect logic.
 */
function initSignupForm() {
  const form = document.getElementById('signupForm');
  if (!form) return;

  const idField = document.getElementById('idField');
  const nameField = document.getElementById('nameField');
  const emailField = document.getElementById('emailField');
  const passField = document.getElementById('passField');
  const confirmField = document.getElementById('confirmField');

  const uniId = document.getElementById('uniId');
  const fullName = document.getElementById('fullName');
  const email = document.getElementById('email');
  const password = document.getElementById('password');
  const confirm = document.getElementById('confirm');

  const submitBtn = document.getElementById('submitBtn');
  const submitText = document.getElementById('submitText');

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let valid = true;

    if (uniId.value.trim() === '') { setFieldError(idField, true); valid = false; } else setFieldError(idField, false);
    if (fullName.value.trim() === '') { setFieldError(nameField, true); valid = false; } else setFieldError(nameField, false);
    if (!isValidEmail(email.value.trim())) { setFieldError(emailField, true); valid = false; } else setFieldError(emailField, false);
    if (password.value.length < 8) { setFieldError(passField, true); valid = false; } else setFieldError(passField, false);
    if (confirm.value !== password.value || confirm.value === '') { setFieldError(confirmField, true); valid = false; } else setFieldError(confirmField, false);

    if (!valid) return;

    // Loading state simulation
    submitBtn.classList.add('loading');
    if (submitText) submitText.textContent = 'جارٍ إنشاء الحساب...';

    setTimeout(() => {
      submitBtn.classList.remove('loading');
      if (submitText) submitText.textContent = 'إنشاء الحساب';
      window.location.href = '03-login.html';
    }, 1000);
  });
}

/**
 * Initializes Google OAuth button simulation.
 */
function initGoogleAuth() {
  const googleBtn = document.getElementById('googleBtn');
  if (googleBtn) {
    googleBtn.addEventListener('click', () => {
      alert('سيتم تفعيل التسجيل عبر Google هنا.');
    });
  }
}
