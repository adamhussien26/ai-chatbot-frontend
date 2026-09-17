/**
 * ==========================================================================
 * Main Global Application Manager - المساعد الذكي
 * Handles global theme, language direction (RTL/LTR), and app initialization.
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initLanguageSupport();
  initThemeSupport();
});

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

/**
 * Initializes Dark / Light theme toggle support.
 */
function initThemeSupport() {
  const themeToggleBtns = document.querySelectorAll('#themeToggle, .theme-toggle');
  const darkModeCheckbox = document.getElementById('darkModeToggle');

  const storedTheme = localStorage.getItem('app_theme');
  if (storedTheme === 'dark') {
    document.body.classList.add('dark-demo');
    if (darkModeCheckbox) darkModeCheckbox.checked = true;
  }

  themeToggleBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      toggleDarkTheme();
    });
  });

  if (darkModeCheckbox) {
    darkModeCheckbox.addEventListener('change', (e) => {
      setDarkTheme(e.target.checked);
    });
  }
}

/**
 * Toggles dark theme mode on the body element.
 */
function toggleDarkTheme() {
  const isDark = document.body.classList.toggle('dark-demo');
  localStorage.setItem('app_theme', isDark ? 'dark' : 'light');
  const darkModeCheckbox = document.getElementById('darkModeToggle');
  if (darkModeCheckbox) darkModeCheckbox.checked = isDark;
}

/**
 * Sets dark theme state explicitly.
 * @param {boolean} isDark
 */
function setDarkTheme(isDark) {
  document.body.classList.toggle('dark-demo', isDark);
  localStorage.setItem('app_theme', isDark ? 'dark' : 'light');
}
