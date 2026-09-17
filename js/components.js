/**
 * ==========================================================================
 * Reusable Components & UI Utility Logic - المساعد الذكي
 * Handles password visibility toggles, form field error states, validation.
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  setupPasswordVisibilityToggles();
});

/**
 * Sets up password toggle visibility handlers for all buttons with .toggle-pass
 */
function setupPasswordVisibilityToggles() {
  const toggleButtons = document.querySelectorAll('.toggle-pass');

  toggleButtons.forEach((btn) => {
    let isVisible = false;

    btn.addEventListener('click', () => {
      isVisible = !isVisible;
      const targetId = btn.dataset.target || 'password';
      const input = document.getElementById(targetId);

      if (input) {
        input.type = isVisible ? 'text' : 'password';

        // SVG icon swap if eyeIcon or SVG exists inside
        const eyeIcon = btn.querySelector('svg');
        if (eyeIcon) {
          if (isVisible) {
            eyeIcon.innerHTML = `
              <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a21.6 21.6 0 0 1 5.06-6.06M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a21.6 21.6 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
              <line x1="1" y1="1" x2="23" y2="23"></line>
            `;
          } else {
            eyeIcon.innerHTML = `
              <path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7-11-7-11-7z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            `;
          }
        }
      }
    });
  });
}

/**
 * Validates email pattern.
 * @param {string} email
 * @returns {boolean}
 */
function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

/**
 * Sets or clears error state on a field container element.
 * @param {HTMLElement} fieldElement
 * @param {boolean} hasError
 */
function setFieldError(fieldElement, hasError) {
  if (fieldElement) {
    fieldElement.classList.toggle('has-error', hasError);
  }
}
