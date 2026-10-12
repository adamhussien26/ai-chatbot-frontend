/* ==========================================
   js/main.js — الكود المشترك بين كل الأقسام
   الثيم | التنبيهات | النوافذ |
   تأكيد الحذف | ترقيم الصفحات | عدّاد الأرقام
   ========================================== */

// ===== 1) الوضع الليلي =====
// نفس المفتاح app_theme مشترك مع باقي صفحات الموقع
const THEME_KEY = 'app_theme';

function applyTheme(isDark, persist) {
  document.body.classList.toggle('dark-demo', isDark);
  if (persist) localStorage.setItem(THEME_KEY, isDark ? 'dark' : 'light');
  // إشعار الشاشات (مثل الرسم البياني) لإعادة تلوين نفسها
  window.dispatchEvent(new CustomEvent('adminthemechange', { detail: { isDark } }));
}

function initTheme() {
  applyTheme(localStorage.getItem(THEME_KEY) === 'dark', false);
  document.querySelectorAll('#themeToggle, .theme-toggle').forEach((btn) => {
    btn.addEventListener('click', () => {
      applyTheme(!document.body.classList.contains('dark-demo'), true);
    });
  });
}

// ===== 2) التنبيهات (Toast) =====
function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  const colors = {
    success: 'bg-tertiary-container text-on-tertiary',
    error: 'bg-error text-on-error',
    info: 'bg-secondary text-on-secondary',
    warning: 'bg-secondary-container text-on-secondary-container'
  };
  const icons = { success: 'check_circle', error: 'error', info: 'info', warning: 'warning' };
  toast.className = `px-5 py-3 rounded-xl font-btn font-semibold ${colors[type] || colors.info} transition-all`;
  toast.style.cssText = 'animation:slideDown 0.3s ease;min-width:280px;';
  toast.innerHTML = `<span class="material-symbols-outlined text-[18px] me-2" style="vertical-align:middle;">${icons[type] || icons.info}</span>${message}`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(-10px)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// ===== 3) النوافذ (Modal) =====
// نافذة واحدة مشتركة: كل شاشة تملأ المحتوى الذي تحتاجه
function openModal(title, bodyHtml, footerHtml) {
  document.getElementById('modalTitle').textContent = title;
  document.getElementById('modalBody').innerHTML = bodyHtml;
  document.getElementById('modalFooter').innerHTML = footerHtml || '';
  const overlay = document.getElementById('modalOverlay');
  overlay.classList.remove('hidden');
  overlay.classList.add('flex');
}

function closeModal() {
  const overlay = document.getElementById('modalOverlay');
  overlay.classList.add('hidden');
  overlay.classList.remove('flex');
}

// ===== 4) تأكيد الحذف =====
// حوار موحد؛ إعادة تحميل البيانات تتم في doDelete (js/app.js)
function confirmDelete(type, id, name) {
  openModal('تأكيد الحذف', `
    <div class="text-center">
      <span class="material-symbols-outlined text-[48px] text-error block mb-3">warning</span>
      <p class="font-body text-on-surface mb-1">هل أنت متأكد من حذف <strong>${name}</strong>؟</p>
      <p class="font-label-sm text-on-surface-variant">لا يمكن التراجع عن هذا الإجراء</p>
    </div>
  `, `
    <button class="px-4 py-2 rounded-lg bg-surface-container-high text-on-surface font-btn hover:bg-surface-container-highest transition-all" onclick="closeModal()">إلغاء</button>
    <button class="px-4 py-2 rounded-lg bg-error text-on-error font-btn hover:bg-error/80 transition-all" onclick="doDelete('${type}', '${id}', '${name}')">حذف</button>
  `);
}

// ===== 5) ترقيم الصفحات (Pagination) =====
// مكوّن واحد لأي جدول: تمرير دالة callback تُستدعى عند تغيير الصفحة
const paginationCallbacks = {};

function renderPagination(containerId, totalPages, currentPage, callback) {
  const container = document.getElementById(containerId);
  if (!container) return;
  paginationCallbacks[containerId] = callback;
  if (totalPages <= 1) { container.innerHTML = ''; return; }

  const navBtn = (icon, page, disabled) => `
    <button class="w-9 h-9 rounded-lg border border-surface-container text-on-surface-variant hover:bg-surface-container hover:text-primary transition-all flex items-center justify-center"
            onclick="goPage('${containerId}', ${page})"
            ${disabled ? 'disabled style="opacity:0.3;cursor:not-allowed"' : ''}>
      <span class="material-symbols-outlined text-[18px]">${icon}</span>
    </button>`;

  let html = navBtn('chevron_right', currentPage - 1, currentPage <= 1);
  for (let i = 1; i <= totalPages; i++) {
    const isActive = i === currentPage;
    html += `
      <button class="w-9 h-9 rounded-lg border font-label-sm font-medium transition-all flex items-center justify-center ${isActive ? 'bg-primary text-on-primary border-primary' : 'bg-surface-container-lowest text-on-surface-variant border-surface-container hover:bg-surface-container hover:text-primary'}"
              onclick="goPage('${containerId}', ${i})">${i}</button>`;
  }
  html += navBtn('chevron_left', currentPage + 1, currentPage >= totalPages);

  container.innerHTML = html;
}

function goPage(containerId, page) {
  const callback = paginationCallbacks[containerId];
  if (callback) callback(page);
}

// ===== 6) عدّاد أرقام متحرك (بطاقات الإحصائيات) =====
function animateNumber(id, target) {
  const el = document.getElementById(id);
  if (!el) return;
  let current = 0;
  const increment = Math.max(1, Math.floor(target / 30));
  const timer = setInterval(() => {
    current += increment;
    if (current >= target) { current = target; clearInterval(timer); }
    el.textContent = current;
  }, 30);
}

// ===== 7) تسجيل الخروج (بدون شاشة دخول) =====
function logout() {
  showToast('تم تسجيل الخروج بنجاح', 'success');
}

// ===== تهيئة المشترك =====
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
});
