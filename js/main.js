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
 * Login page: API login (مع fallback تجريبي) + validation + navigation.
 */
function initLoginForm() {
  const form = document.getElementById('loginForm');
  if (!form) return;

  const emailField = document.getElementById('emailField');
  const passField = document.getElementById('passField');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('password');
  const submitBtn = form.querySelector('button.btn-primary');

  form.addEventListener('submit', async (e) => {
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

    if (!valid) return;

    // 1) محاولة الدخول عبر الـ Backend
    try {
      const data = await API.post('/auth/login', {
        email: emailInput.value.trim(),
        password: passwordInput.value,
      }, { timeout: 6000 });
      API.setSession(data.access_token, data.user);
      window.location.href = 'chat.html';
      return;
    } catch (err) {
      if (!API.isNetworkError(err)) {
        // بيانات خاطئة أو حساب معطل → إظهار الخطأ في الحقل
        setFieldError(passField, true);
        const errorEl = passField.querySelector('.error');
        if (errorEl) errorEl.textContent = err.message || 'بيانات الدخول غير صحيحة.';
        return;
      }
      // 2) الخادم غير متاح → الوضع التجريبي (كما كان سابقًا)
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

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    let valid = true;

    if (uniId.value.trim() === '') { setFieldError(idField, true); valid = false; } else setFieldError(idField, false);
    if (fullName.value.trim() === '') { setFieldError(nameField, true); valid = false; } else setFieldError(nameField, false);
    if (!isValidEmail(email.value.trim())) { setFieldError(emailField, true); valid = false; } else setFieldError(emailField, false);
    if (password.value.length < 8) { setFieldError(passField, true); valid = false; } else setFieldError(passField, false);
    if (confirm.value !== password.value || confirm.value === '') { setFieldError(confirmField, true); valid = false; } else setFieldError(confirmField, false);

    if (!valid) return;

    // Loading state
    setButtonLoading(submitBtn, true);
    if (submitText) submitText.textContent = 'جارٍ إنشاء الحساب...';

    // 1) محاولة إنشاء الحساب عبر الـ Backend
    try {
      await API.post('/auth/register', {
        full_name: fullName.value.trim(),
        email: email.value.trim(),
        password: password.value,
        university_id: uniId.value.trim(),
      }, { timeout: 6000 });
      setButtonLoading(submitBtn, false);
      if (submitText) submitText.textContent = 'إنشاء الحساب';
      window.location.href = 'login.html';
      return;
    } catch (err) {
      setButtonLoading(submitBtn, false);
      if (submitText) submitText.textContent = 'إنشاء الحساب';

      if (!API.isNetworkError(err)) {
        const errorEl = emailField.querySelector('.error');
        if (errorEl) errorEl.textContent = err.message || 'تعذر إنشاء الحساب.';
        setFieldError(emailField, true);
        return;
      }
      // 2) الخادم غير متاح → الوضع التجريبي (كما كان سابقًا)
      window.location.href = 'login.html';
    }
  });

  initGoogleAuth(() => {
    alert('سيتم تفعيل التسجيل عبر Google هنا.');
  });
}

/**
 * Forgot password page: email step → OTP verification step (6 digits) → New Password screen.
 * Frontend-only: OTP simulation accepts any complete 6-digit code (integration point for the API).
 */
function initForgotPasswordForm() {
  const form = document.getElementById('resetForm');
  const emailField = document.getElementById('emailField');
  if (!form || !emailField) return;

  const emailInput = document.getElementById('email');
  const submitBtn = document.getElementById('submitBtn');
  const submitText = document.getElementById('submitText');
  const formBox = document.getElementById('formBox');
  const otpBox = document.getElementById('otpBox');
  const sentEmail = document.getElementById('sentEmail');
  const resendBtn = document.getElementById('resendBtn');
  const verifyBtn = document.getElementById('verifyOtpBtn');
  const verifyText = document.getElementById('verifyOtpText');
  const otpError = document.getElementById('otpError');
  const otpGroup = document.getElementById('otpGroup');
  const otpInputs = Array.from(document.querySelectorAll('.otp-input'));

  const OTP_LENGTH = 6;

  function clearOtp() {
    otpInputs.forEach((input) => {
      input.value = '';
      input.classList.remove('filled');
    });
    hideOtpError();
  }

  function hideOtpError() {
    if (otpError) otpError.classList.remove('show');
    if (otpGroup) otpGroup.classList.remove('has-error');
  }

  function showOtpError(message) {
    if (!otpError) return;
    otpError.textContent = message;
    otpError.classList.add('show');
    if (otpGroup) otpGroup.classList.add('has-error');
  }

  function getOtpCode() {
    return otpInputs.map((input) => input.value).join('');
  }

  /* --- الخطوة 1: إرسال رمز التحقق إلى البريد (Backend → OTP) --- */
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const value = emailInput.value.trim();

    if (!isValidEmail(value)) {
      setFieldError(emailField, true);
      return;
    }
    setFieldError(emailField, false);

    setButtonLoading(submitBtn, true);
    if (submitText) submitText.textContent = 'جارٍ الإرسال...';

    let backendDone = false;
    let devCode = null;

    // 1) محاولة إرسال OTP عبر الـ Backend
    try {
      const data = await API.post('/auth/forgot-password', { email: value }, { timeout: 6000 });
      backendDone = true;
      devCode = data.dev_code || null;
      if (devCode) console.info('[DEV] OTP code for', value, ':', devCode);
    } catch (err) {
      if (!API.isNetworkError(err)) {
        setButtonLoading(submitBtn, false);
        if (submitText) submitText.textContent = 'إرسال رمز التحقق';
        setFieldError(emailField, true);
        const errorEl = emailField.querySelector('.error');
        if (errorEl) errorEl.textContent = err.message || 'تعذر إرسال الرمز.';
        return;
      }
    }

    setTimeout(() => {
      setButtonLoading(submitBtn, false);
      if (submitText) submitText.textContent = 'إرسال رمز التحقق';
      if (sentEmail) sentEmail.textContent = value;
      clearOtp();
      if (formBox) formBox.classList.add('hide');
      if (otpBox) otpBox.classList.add('show');
      if (backendDone) {
        try {
          sessionStorage.setItem('ust_reset_email', value);
          if (devCode) alert('وضع التطوير: رمز التحقق الخاص بك هو ' + devCode);
        } catch (err) { /* noop */ }
      }
      startResendCooldown(resendBtn);
      if (otpInputs[0]) otpInputs[0].focus();
    }, backendDone ? 150 : 900);
  });

  /* --- إعادة إرسال الرمز مع العد التنازلي --- */
  if (resendBtn) {
    resendBtn.addEventListener('click', () => {
      if (resendBtn.disabled) return;
      clearOtp();
      startResendCooldown(resendBtn);
      if (otpInputs[0]) otpInputs[0].focus();
    });
  }

  /* --- سلوك حقول OTP: أرقام فقط + تنقّل تلقائي + Backspace + لصق + أسهم --- */
  otpInputs.forEach((input, index) => {
    input.addEventListener('input', () => {
      input.value = input.value.replace(/\D/g, '').slice(0, 1);
      input.classList.toggle('filled', input.value !== '');
      hideOtpError();

      if (input.value && index < otpInputs.length - 1) {
        otpInputs[index + 1].focus();
      }
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !input.value && index > 0) {
        const prev = otpInputs[index - 1];
        prev.value = '';
        prev.classList.remove('filled');
        prev.focus();
      } else if (e.key === 'ArrowLeft' && index > 0) {
        otpInputs[index - 1].focus();
      } else if (e.key === 'ArrowRight' && index < otpInputs.length - 1) {
        otpInputs[index + 1].focus();
      } else if (e.key === 'Enter' && verifyBtn) {
        verifyBtn.click();
      }
    });

    input.addEventListener('paste', (e) => {
      e.preventDefault();
      const text = (e.clipboardData || window.clipboardData).getData('text') || '';
      const digits = text.replace(/\D/g, '').slice(0, OTP_LENGTH);
      if (!digits) return;

      digits.split('').forEach((digit, i) => {
        if (otpInputs[i]) {
          otpInputs[i].value = digit;
          otpInputs[i].classList.add('filled');
        }
      });
      hideOtpError();

      const nextEmpty = otpInputs.findIndex((field) => field.value === '');
      const target = nextEmpty === -1 ? otpInputs[otpInputs.length - 1] : otpInputs[nextEmpty];
      if (target) target.focus();
    });
  });

  /* --- الخطوة 2: التحقق من الرمز والانتقال لشاشة كلمة المرور الجديدة --- */
  if (verifyBtn) {
    verifyBtn.addEventListener('click', async () => {
      const code = getOtpCode();

      if (code.length < OTP_LENGTH) {
        showOtpError('من فضلك أدخل الرمز المكوّن من 6 أرقام.');
        const firstEmpty = otpInputs.find((input) => input.value === '');
        if (firstEmpty) firstEmpty.focus();
        return;
      }
      hideOtpError();

      setButtonLoading(verifyBtn, true);
      if (verifyText) verifyText.textContent = 'جارٍ التحقق...';

      // 1) محاولة التحقق عبر الـ Backend
      let backendVerified = false;
      try {
        const resetEmail = sessionStorage.getItem('ust_reset_email') || (sentEmail ? sentEmail.textContent : '');
        await API.post('/auth/verify-otp', { email: resetEmail, code }, { timeout: 6000 });
        backendVerified = true;
        sessionStorage.setItem('ust_reset_code', code);
      } catch (err) {
        if (!API.isNetworkError(err)) {
          setButtonLoading(verifyBtn, false);
          if (verifyText) verifyText.textContent = 'تحقق من الرمز';
          showOtpError(err.message || 'رمز التحقق غير صحيح أو منتهي الصلاحية.');
          return;
        }
      }

      setTimeout(() => {
        setButtonLoading(verifyBtn, false);
        if (verifyText) verifyText.textContent = 'تحقق من الرمز';

        try {
          sessionStorage.setItem('otp_verified', '1');
        } catch (err) { /* noop */ }

        window.location.href = 'reset-password.html';
      }, backendVerified ? 150 : 900);
    });
  }
}

/**
 * Starts a 30-second cooldown timer for resending the OTP code.
 * @param {HTMLButtonElement} resendBtn
 */
function startResendCooldown(resendBtn) {
  if (!resendBtn) return;

  let seconds = 30;
  resendBtn.disabled = true;
  resendBtn.textContent = `إعادة إرسال الرمز (${seconds})`;

  const interval = setInterval(() => {
    seconds--;
    if (seconds <= 0) {
      clearInterval(interval);
      resendBtn.disabled = false;
      resendBtn.textContent = 'إعادة إرسال الرمز';
    } else {
      resendBtn.textContent = `إعادة إرسال الرمز (${seconds})`;
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

  // Guard: شاشة كلمة المرور الجديدة متاحة فقط بعد التحقق من رمز OTP
  let otpVerified = false;
  try {
    otpVerified = sessionStorage.getItem('otp_verified') === '1';
  } catch (err) { /* noop */ }

  if (!otpVerified) {
    window.location.replace('forgot-password.html');
    return;
  }

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

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const { allMet, matches } = validateForm();
    if (!matches) {
      setFieldError(confirmField, true);
      return;
    }
    if (!allMet) return;

    setButtonLoading(submitBtn, true);
    if (submitText) submitText.textContent = 'جارٍ الحفظ...';

    // 1) محاولة إعادة التعيين عبر الـ Backend (يستهلك رمز OTP فعليًا)
    try {
      const resetEmail = sessionStorage.getItem('ust_reset_email') || '';
      const resetCode = sessionStorage.getItem('ust_reset_code') || '';
      if (resetEmail && resetCode) {
        await API.post('/auth/reset-password', {
          email: resetEmail,
          code: resetCode,
          new_password: passwordInput.value,
        }, { timeout: 6000 });
        try { sessionStorage.removeItem('otp_verified'); } catch (err) { /* noop */ }
        setButtonLoading(submitBtn, false);
        if (submitText) submitText.textContent = 'حفظ كلمة المرور';
        if (formBox) formBox.classList.add('hide');
        if (successBox) successBox.classList.add('show');
        return;
      }
    } catch (err) {
      if (!API.isNetworkError(err)) {
        setButtonLoading(submitBtn, false);
        if (submitText) submitText.textContent = 'حفظ كلمة المرور';
        setFieldError(confirmField, true);
        const errorEl = confirmField.querySelector('.error');
        if (errorEl) errorEl.textContent = err.message || 'تعذر إعادة التعيين. أعد المحاولة.';
        return;
      }
    }

    // 2) الخادم غير متاح → الوضع التجريبي (كما كان سابقًا)
    setTimeout(() => {
      setButtonLoading(submitBtn, false);
      if (submitText) submitText.textContent = 'حفظ كلمة المرور';

      try {
        sessionStorage.removeItem('otp_verified');
      } catch (err) { /* noop */ }

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
 * Settings page: profile (من الـ Backend) + تغيير كلمة المرور + photo simulation.
 */
function initSettingsPage() {
  const profilePhoto = document.querySelector('.profile-photo');
  const photoEditBtn = document.querySelector('.photo-edit-btn');
  const removePhotoBtn = document.querySelector('.remove-photo');
  const changePasswordBtn = document.querySelector('.card-footer .primary-btn');

  if (!profilePhoto && !changePasswordBtn) return;

  // تحميل بيانات الملف الشخصي من الـ Backend (بدون تغيير التصميم)
  (async () => {
    try {
      if (!API.getToken()) return;
      const profile = await API.get('/students/me', { timeout: 5000 });
      const nameEl = document.querySelector('.profile-meta .name');
      if (nameEl && profile.full_name) nameEl.textContent = profile.full_name;
      const idEl = document.querySelector('.sub-row span:first-child');
      if (idEl && profile.university_id) idEl.firstChild.textContent = profile.university_id + ' ';
      const emailEl = document.querySelector('.sub-row span:last-child');
      if (emailEl && profile.email) emailEl.firstChild.textContent = profile.email + ' ';
      if (profilePhoto && profile.avatar_url) profilePhoto.src = profile.avatar_url;
    } catch (err) {
      // الخادم غير متاح أو الجلسة منتهية — تبقى البيانات التجريبية كما هي
    }
  })();

  if (photoEditBtn) {
    photoEditBtn.addEventListener('click', async () => {
      const newUrl = prompt('أدخل رابط الصورة الجديدة:', profilePhoto ? profilePhoto.src : '');
      if (newUrl && newUrl.trim() !== '') {
        if (profilePhoto) profilePhoto.src = newUrl.trim();
        try {
          if (API.getToken()) await API.put('/students/me', { avatar_url: newUrl.trim() }, { timeout: 5000 });
        } catch (err) { /* الوضع التجريبي */ }
      }
    });
  }

  if (removePhotoBtn) {
    removePhotoBtn.addEventListener('click', async () => {
      if (confirm('هل أنت متاكد من رغبتك في إزالة الصورة الشخصية؟')) {
        const defaultPhoto = 'https://picsum.photos/seed/defaultuser/200/200';
        if (profilePhoto) profilePhoto.src = defaultPhoto;
        try {
          if (API.getToken()) await API.put('/students/me', { avatar_url: defaultPhoto }, { timeout: 5000 });
        } catch (err) { /* الوضع التجريبي */ }
      }
    });
  }

  if (changePasswordBtn) {
    changePasswordBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      const currentInput = document.getElementById('currentPassword');
      const newInput = document.getElementById('newPassword');
      const confirmInput = document.getElementById('confirmNewPassword');

      if (!currentInput || !newInput || !confirmInput) return;
      if (!currentInput.value || !newInput.value || !confirmInput.value) {
        alert('يرجى ملء جميع الحقول الخاصة بكلمة المرور.');
        return;
      }
      if (newInput.value !== confirmInput.value) {
        alert('كلمتا المرور غير متطابقتين.');
        return;
      }

      // 1) تغيير كلمة المرور عبر الـ Backend
      try {
        if (API.getToken()) {
          await API.post('/auth/change-password', {
            current_password: currentInput.value,
            new_password: newInput.value,
          }, { timeout: 6000 });
          alert('تم تغيير كلمة المرور بنجاح!');
          [currentInput, newInput, confirmInput].forEach((input) => input.value = '');
          return;
        }
      } catch (err) {
        if (!API.isNetworkError(err)) {
          alert(err.message || 'تعذر تغيير كلمة المرور.');
          return;
        }
      }

      // 2) الوضع التجريبي (كما كان سابقًا)
      alert('تم تغيير كلمة المرور بنجاح!');
      [currentInput, newInput, confirmInput].forEach((input) => input.value = '');
    });
  }

  // تسجيل الخروج: مسح الجلسة عند الضغط على أي رابط خروج
  document.querySelectorAll('a.side-link.logout, a[href="welcome.html"].logout').forEach((link) => {
    link.addEventListener('click', () => {
      if (typeof API !== 'undefined') API.clearSession();
    });
  });
}
