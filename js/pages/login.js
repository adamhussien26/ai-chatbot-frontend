/**
 * ==========================================================================
 * Page Specific Logic: 03-login.html (صفحة تسجيل الدخول)
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initLoginForm();
  initGoogleLogin();
});

/**
 * Initializes login form validation and navigation logic.
 */
function initLoginForm() {
  const form = document.getElementById('loginForm');
  if (!form) return;

  const emailField = document.getElementById('emailField');
  const passField = document.getElementById('passField');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    let valid = true;

    if (!isValidEmail(emailInput.value.trim())) {
      setFieldError(emailField, true);
      valid = false;
    } else {
      setFieldError(emailField, false);
    }

    if (passwordInput.value.trim() === '') {
      setFieldError(passField, true);
      valid = false;
    } else {
      setFieldError(passField, false);
    }

    if (valid) {
      window.location.href = '06-chat.html';
    }
  });
}

/**
 * Handles Google Login button interaction.
 */
function initGoogleLogin() {
  const googleBtn = document.getElementById('googleBtn');
  if (googleBtn) {
    googleBtn.addEventListener('click', () => {
      window.location.href = '06-chat.html';
    });
  }
}
