/**
 * ==========================================================================
 * main.js — الملف المشترك لجميع الصفحات (المساعد الذكي - جامعة العلوم والتقانة)
 * ==========================================================================
 * المحتويات:
 * 1. Shared Components  — مكونات واجهة مشتركة تُضاف تلقائياً (Topbar)
 * 2. Language (RTL/LTR) — دعم اتجاه اللغة
 * 3. Common UI          — إظهار/إخفاء كلمة المرور + أدوات مساعدة
 * 4. Page Logic         — منطق صفحات المصادقة والملف الشخصي
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  renderTopbar();

  initLanguageSupport();
  setupPasswordVisibilityToggles();

  initLoginForm();
  initSignupForm();
  initForgotPasswordForm();
  initResetPasswordForm();
  initSettingsPage();
});


/* ==========================================================================
   1. Shared Components — مكونات مشتركة (Write once, reuse everywhere)
   ========================================================================== */

/**
 * روابط شريط التنقل العلوي المشترك بين صفحتي المحادثة والملف الشخصي.
 */
const NAV_TABS = [
  { href: 'chat.html', label: 'المساعد الذكي', key: 'chat' },
  { href: 'settings.html', label: 'الملف الشخصي', key: 'settings' }
];

/**
 * يرسم شريط التنقل العلوي الموحد لصفحتي المحادثة والملف الشخصي.
 */
function renderTopbar() {
  const header = document.querySelector('header.topbar');
  if (!header) return;

  const isChatPage = Boolean(document.getElementById('chatSidebar'));
  const activeKey = isChatPage ? 'chat' : 'settings';

  const tabs = NAV_TABS.map((tab) => {
    const activeClass = tab.key === activeKey ? ' class="active"' : '';
    return `<a href="${tab.href}"${activeClass}>${tab.label}</a>`;
  }).join('');

  header.innerHTML = `
    <div class="topbar-side">
      ${isChatPage ? `
      <button type="button" class="mobile-sidebar-toggle" id="sidebarToggle" title="أرشيف المحادثات" aria-label="أرشيف المحادثات">
        <svg viewBox="0 0 24 24" fill="none" width="22" height="22" aria-hidden="true">
          <path d="M4 6h16M4 12h16M4 18h16" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
      </button>` : ''}
      <img class="avatar" src="https://i.pravatar.cc/80?img=12" alt="${isChatPage ? 'صورة المستخدم' : 'الصورة الشخصية'}">
    </div>
    <nav class="nav-tabs" aria-label="Main Navigation">${tabs}</nav>
    <div class="uni-brand">
      <span>جامعة العلوم والتقانة</span>
      <div class="uni-logo">
        <img src="../assets/images/logo.png" alt="شعار الجامعة">
      </div>
    </div>
  `;
}


/* ==========================================================================
   2. Language Support (RTL / LTR)
   ========================================================================== */

/* ==========================================================================
   2. Language Support (RTL / LTR)
   ========================================================================== */

/**
 * Initializes language toggle buttons (EN / Arabic) across topbars & headers.
 */
function initLanguageSupport() {
  const btnEnList = document.querySelectorAll('#btnEn, .lang-toggle button:first-child, .seg button:first-child');
  const btnArList = document.querySelectorAll('#btnAr, .lang-toggle button:last-child, .seg button:last-child');

  // Check stored direction or default to rtl
  const currentDir = localStorage.getItem('app_dir') || 'rtl';
  applyDirection(currentDir);

  btnEnList.forEach((btnEn) => {
    btnEn.addEventListener('click', (e) => {
      e.preventDefault();
      applyDirection('ltr');
    });
  });

  btnArList.forEach((btnAr) => {
    btnAr.addEventListener('click', (e) => {
      e.preventDefault();
      applyDirection('rtl');
    });
  });
}

/**
 * Applies the requested text direction (rtl / ltr) and updates toggle button states.
 * @param {string} dir - 'rtl' or 'ltr'
 */
function applyDirection(dir) {
  document.documentElement.setAttribute('dir', dir);
  localStorage.setItem('app_dir', dir);

  // Update button active classes across language toggles
  document.querySelectorAll('.lang-toggle, .seg').forEach((toggleContainer) => {
    const buttons = toggleContainer.querySelectorAll('button');
    if (buttons.length >= 2) {
      if (dir === 'ltr') {
        buttons[0].classList.add('active');
        buttons[1].classList.remove('active');
      } else {
        buttons[0].classList.remove('active');
        buttons[1].classList.add('active');
      }
    }
  });
}


/* ==========================================================================
   3. Common UI — أدوات واجهة مشتركة
   ========================================================================== */

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

/**
 * Shows or hides the loading state of a submit button.
 * @param {HTMLElement} btn
 * @param {boolean} isLoading
 */
function setButtonLoading(btn, isLoading) {
  if (btn) btn.classList.toggle('loading', isLoading);
}

/**
 * Google OAuth button simulation (used by login & signup pages).
 */
function initGoogleAuth(onClick) {
  const googleBtn = document.getElementById('googleBtn');
  if (googleBtn && onClick) {
    googleBtn.addEventListener('click', onClick);
  }
}


/* ==========================================================================
   4. Page Logic — منطق الصفحات (كل دالة تعمل فقط إذا وجدت عناصر صفحتها)
   ========================================================================== */

/**
 * Login page: form validation + navigation.
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
      window.location.href = 'chat.html';
    }
  });

  initGoogleAuth(() => {
    window.location.href = 'chat.html';
  });
}

/**
 * Signup page: form validation, loading state and redirect.
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
    setButtonLoading(submitBtn, true);
    if (submitText) submitText.textContent = 'جارٍ إنشاء الحساب...';

    setTimeout(() => {
      setButtonLoading(submitBtn, false);
      if (submitText) submitText.textContent = 'إنشاء الحساب';
      window.location.href = 'login.html';
    }, 1000);
  });

  initGoogleAuth(() => {
    alert('سيتم تفعيل التسجيل عبر Google هنا.');
  });
}

/**
 * Forgot password page: email validation + success view + resend cooldown.
 */
function initForgotPasswordForm() {
  const form = document.getElementById('resetForm');
  const emailField = document.getElementById('emailField');
  const sentEmail = document.getElementById('sentEmail');
  if (!form || !emailField) return;

  const emailInput = document.getElementById('email');
  const submitBtn = document.getElementById('submitBtn');
  const submitText = document.getElementById('submitText');
  const formBox = document.getElementById('formBox');
  const successBox = document.getElementById('successBox');
  const resendBtn = document.getElementById('resendBtn');

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const value = emailInput.value.trim();

    if (!isValidEmail(value)) {
      setFieldError(emailField, true);
      return;
    }
    setFieldError(emailField, false);

    setButtonLoading(submitBtn, true);
    if (submitText) submitText.textContent = 'جارٍ الإرسال...';

    setTimeout(() => {
      setButtonLoading(submitBtn, false);
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

/**
 * Reset password page: strength meter, rules checklist and submit.
 */
function initResetPasswordForm() {
  const form = document.getElementById('resetForm');
  const strengthLabel = document.getElementById('strengthLabel');
  if (!form || !strengthLabel) return;

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

    strengthLabel.textContent = value.length === 0 ? '\u00A0' : labels[Math.min(activeCount, 4)];
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

    setButtonLoading(submitBtn, true);
    if (submitText) submitText.textContent = 'جارٍ الحفظ...';

    setTimeout(() => {
      setButtonLoading(submitBtn, false);
      if (submitText) submitText.textContent = 'حفظ كلمة المرور';
      if (formBox) formBox.classList.add('hide');
      if (successBox) successBox.classList.add('show');
    }, 900);
  });

  if (goLoginBtn) {
    goLoginBtn.addEventListener('click', () => {
      window.location.href = 'login.html';
    });
  }
}

/**
 * Settings page: profile photo simulation + password change form.
 */
function initSettingsPage() {
  const profilePhoto = document.querySelector('.profile-photo');
  const photoEditBtn = document.querySelector('.photo-edit-btn');
  const removePhotoBtn = document.querySelector('.remove-photo');
  const changePasswordBtn = document.querySelector('.card-footer .primary-btn');

  if (!profilePhoto && !changePasswordBtn) return;

  if (photoEditBtn) {
    photoEditBtn.addEventListener('click', () => {
      const newUrl = prompt('أدخل رابط الصورة الجديدة:', profilePhoto ? profilePhoto.src : '');
      if (newUrl && newUrl.trim() !== '') {
        if (profilePhoto) profilePhoto.src = newUrl.trim();
      }
    });
  }

  if (removePhotoBtn) {
    removePhotoBtn.addEventListener('click', () => {
      if (confirm('هل أنت متاكد من رغبتك في إزالة الصورة الشخصية؟')) {
        if (profilePhoto) profilePhoto.src = 'https://picsum.photos/seed/defaultuser/200/200';
      }
    });
  }

  if (changePasswordBtn) {
    changePasswordBtn.addEventListener('click', (e) => {
      e.preventDefault();
      const inputs = document.querySelectorAll('.field-grid input');
      let valid = true;

      inputs.forEach((input) => {
        if (input.value.trim() === '') valid = false;
      });

      if (!valid) {
        alert('يرجى ملء جميع الحقول الخاصة بكلمة المرور.');
        return;
      }

      alert('تم تغيير كلمة المرور بنجاح!');
      inputs.forEach((input) => input.value = '');
    });
  }
}
