/* ==========================================
   js/app.js — أقسام لوحة التحكم (صفحة واحدة)
   نظرة عامة | قاعدة المعرفة | التقارير
   (الكود المشترك موجود في js/main.js)
   ========================================== */

// ===== الحالة العامة =====
let usageChart = null;
let currentChartPeriod = 'week';
let docPage = 1, activityPage = 1;
const DOCS_PER_PAGE = 5, ACTIVITIES_PER_PAGE = 5;

// ===== تهيئة الأقسام =====
document.addEventListener('DOMContentLoaded', () => {
  renderDashboard();
  renderDocuments();
  renderReportTables();
  renderChart(currentChartPeriod);
  renderActivities();
});

// ==========================================
// الشاشة الرئيسية (Dashboard)
// ==========================================
function renderDashboard() {
  const d = getDashboardData();
  animateNumber('statConversations', d.conversationsToday);
  animateNumber('statUsers', d.activeUsers);
  animateNumber('statDocs', d.totalDocuments);
}

// ==========================================
// التقارير: جداول الأسئلة + الرسم البياني
// ==========================================
function renderReportTables() {
  const d = getDashboardData();

  const freqBody = document.getElementById('frequentQuestionsBody');
  if (freqBody) {
    freqBody.innerHTML = d.frequentQuestions.map((q, i) => `
      <tr class="transition-colors">
        <td class="py-3 px-3 text-on-surface-variant">${i + 1}</td>
        <td class="py-3 px-3 font-table-b text-on-surface">${q.question}</td>
        <td class="py-3 px-3"><span class="px-2.5 py-0.5 rounded-full font-label-sm bg-secondary-fixed text-on-secondary-fixed-variant font-medium">${q.count} تكرار</span></td>
      </tr>
    `).join('');
  }

  const failBody = document.getElementById('failedQuestionsBody');
  if (failBody) {
    const fails = d.failedQuestions;
    if (fails.length === 0) {
      failBody.innerHTML = '<tr><td colspan="3"><div class="text-center py-8 text-on-surface-variant"><span class="material-symbols-outlined text-[48px] text-outline-variant block mb-2">check_circle</span><p class="font-body">لا توجد أسئلة فاشلة</p></div></td></tr>';
    } else {
      failBody.innerHTML = fails.map(q => `
        <tr class="transition-colors">
          <td class="py-3 px-3 font-table-b text-on-surface">${q.question}</td>
          <td class="py-3 px-3">${q.answers.length === 0 ? '<span class="text-error font-medium">بدون ردود</span>' : q.answers.length + ' رد'}</td>
          <td class="py-3 px-3 text-end"><button class="px-3 py-1 rounded-lg bg-surface-container-high hover:bg-surface-container text-on-surface font-label-sm transition-all" onclick="showToast('تم مراجعة السؤال','success')">مراجعة</button></td>
        </tr>
      `).join('');
    }
  }
}

function switchChartPeriod(period) {
  currentChartPeriod = period;
  renderChart(period);
  const activeClass = 'px-3 py-1 rounded-lg bg-primary text-on-primary font-btn';
  const idleClass = 'px-3 py-1 rounded-lg bg-surface-container text-on-surface-variant font-btn';
  document.getElementById('chartWeekBtn').className = period === 'week' ? activeClass : idleClass;
  document.getElementById('chartMonthBtn').className = period === 'month' ? activeClass : idleClass;
}

function renderChart(period) {
  const canvas = document.getElementById('usageChart');
  if (!canvas || !window.Chart) return;
  const usage = getDashboardData();
  const data = period === 'week' ? usage.weeklyUsage : usage.monthlyUsage;

  // ألوان الرسم تتبع الوضع الليلي
  const isDark = document.body.classList.contains('dark-demo');
  const lineColor = isDark ? '#39b8fd' : '#006591';
  const fillColor = isDark ? 'rgba(57, 184, 253, 0.12)' : 'rgba(0, 101, 145, 0.1)';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.05)';
  const tickColor = isDark ? '#9aa0a6' : '#666666';

  if (usageChart) usageChart.destroy();
  usageChart = new Chart(canvas.getContext('2d'), {
    type: 'line',
    data: {
      labels: data.labels,
      datasets: [{
        label: 'عدد المحادثات',
        data: data.values,
        borderColor: lineColor,
        backgroundColor: fillColor,
        fill: true,
        tension: 0.4,
        pointBackgroundColor: lineColor,
        pointRadius: 5,
        pointHoverRadius: 7
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: gridColor }, ticks: { color: tickColor } },
        x: { grid: { display: false }, ticks: { color: tickColor } }
      }
    }
  });
}

// إعادة رسم الرسم البياني عند تبديل الوضع الليلي
window.addEventListener('adminthemechange', () => {
  if (usageChart) renderChart(currentChartPeriod);
});

// ==========================================
// قاعدة المعرفة (المستندات)
// ==========================================
function renderDocuments() {
  const docs = getDocuments();
  const searchEl = document.getElementById('docSearch');
  const search = searchEl ? searchEl.value.toLowerCase() : '';
  const catEl = document.getElementById('docCategory');

  // تعبئة قائمة التصنيفات مرة واحدة
  if (catEl && catEl.options.length <= 1) {
    [...new Set(docs.map(d => d.category))].forEach(c => {
      const opt = document.createElement('option');
      opt.value = c; opt.textContent = c;
      catEl.appendChild(opt);
    });
  }
  const category = catEl ? catEl.value : '';

  const filtered = docs.filter(d =>
    (!category || d.category === category) &&
    (d.name.toLowerCase().includes(search) || d.type.toLowerCase().includes(search) || d.category.toLowerCase().includes(search))
  );
  const totalPages = Math.ceil(filtered.length / DOCS_PER_PAGE);
  if (docPage > totalPages) docPage = 1;
  const start = (docPage - 1) * DOCS_PER_PAGE;
  const pageDocs = filtered.slice(start, start + DOCS_PER_PAGE);

  const body = document.getElementById('documentsBody');
  if (pageDocs.length === 0) {
    body.innerHTML = '<tr><td colspan="5"><div class="text-center py-8 text-on-surface-variant"><span class="material-symbols-outlined text-[48px] text-outline-variant block mb-2">folder_off</span><p class="font-body">لا توجد مستندات</p></div></td></tr>';
  } else {
    body.innerHTML = pageDocs.map(d => `
      <tr class="transition-colors">
        <td class="py-3 px-3">
          <div class="flex items-center gap-2">
            <div class="w-8 h-8 rounded-lg bg-secondary-container text-on-secondary-container flex items-center justify-center font-bold text-[10px]">${d.type}</div>
            <div>
              <div class="font-body text-on-surface">${d.name}</div>
              <div class="font-caption text-on-surface-variant">${d.category}</div>
            </div>
          </div>
        </td>
        <td class="py-3 px-3 font-table-b text-on-surface whitespace-nowrap">${d.type} · ${d.size}</td>
        <td class="py-3 px-3 font-table-b text-on-surface whitespace-nowrap">${d.date}</td>
        <td class="py-3 px-3">${statusLabel(d.status)}</td>
        <td class="py-3 px-3 text-end">
          <div class="flex items-center justify-end gap-1">
            <button class="p-1.5 rounded-lg hover:bg-surface-container text-on-surface-variant transition-all" title="إعادة الفهرسة" onclick="showToast('تم إعادة فهرسة ${d.name}','info')"><span class="material-symbols-outlined text-[18px]">refresh</span></button>
            <button class="p-1.5 rounded-lg hover:bg-surface-container text-on-surface-variant transition-all" title="عرض الأجزاء" onclick="showToast('عرض أجزاء ${d.name}','info')"><span class="material-symbols-outlined text-[18px]">visibility</span></button>
            <button class="p-1.5 rounded-lg hover:bg-error-container text-error transition-all" title="حذف" onclick="confirmDelete('document', ${d.id}, '${d.name}')"><span class="material-symbols-outlined text-[18px]">delete</span></button>
          </div>
        </td>
      </tr>
    `).join('');
  }
  renderPagination('docPagination', totalPages, docPage, (p) => { docPage = p; renderDocuments(); });
}

function statusLabel(s) {
  const labels = { indexed: 'مفهرس', processing: 'قيد المعالجة', failed: 'فشل' };
  const colors = { indexed: 'bg-tertiary-container text-tertiary-fixed', processing: 'bg-secondary-container text-on-secondary-container', failed: 'bg-error-container text-error' };
  return `<span class="px-2.5 py-0.5 rounded-full font-label-sm font-semibold whitespace-nowrap ${colors[s] || ''}">${labels[s] || s}</span>`;
}

function filterDocuments() { docPage = 1; renderDocuments(); }

// رفع الملفات (سحب وإفلات + محاكاة شريط التقدم)
function handleDragOver(e) { e.preventDefault(); e.currentTarget.classList.add('border-secondary'); }
function handleDragLeave(e) { e.currentTarget.classList.remove('border-secondary'); }
function handleDrop(e) {
  e.preventDefault(); e.currentTarget.classList.remove('border-secondary');
  if (e.dataTransfer.files.length) simulateUpload(e.dataTransfer.files[0].name);
}
function handleFileSelect(e) { if (e.target.files.length) simulateUpload(e.target.files[0].name); }

function simulateUpload(fileName) {
  const progressDiv = document.getElementById('uploadProgress');
  progressDiv.classList.remove('hidden');
  document.getElementById('uploadFileName').textContent = fileName;
  const fill = document.getElementById('uploadProgressFill');
  const percentEl = document.getElementById('uploadPercent');
  let percent = 0;
  const interval = setInterval(() => {
    percent += Math.random() * 15;
    if (percent >= 100) { percent = 100; clearInterval(interval); showToast('تم رفع وفهرسة الملف بنجاح', 'success'); setTimeout(() => progressDiv.classList.add('hidden'), 2000); }
    fill.style.width = percent + '%';
    percentEl.textContent = Math.round(percent) + '%';
  }, 300);
}

// ==========================================
// سجل النشاط
// ==========================================
function renderActivities() {
  const filter = document.getElementById('activityUserFilter');
  if (filter && filter.options.length <= 1) {
    const uniqueUsers = [...new Set(getActivities().map(a => a.user))];
    uniqueUsers.forEach(u => {
      const opt = document.createElement('option');
      opt.value = u; opt.textContent = u;
      filter.appendChild(opt);
    });
  }

  let activities = getActivities();
  const dateFilter = document.getElementById('activityDateFilter')?.value || '';
  const userFilter = filter?.value || '';
  if (dateFilter) activities = activities.filter(a => a.time.startsWith(dateFilter));
  if (userFilter) activities = activities.filter(a => a.user === userFilter);

  const totalPages = Math.ceil(activities.length / ACTIVITIES_PER_PAGE);
  if (activityPage > totalPages) activityPage = 1;
  const start = (activityPage - 1) * ACTIVITIES_PER_PAGE;
  const pageActivities = activities.slice(start, start + ACTIVITIES_PER_PAGE);

  const body = document.getElementById('activityBody');
  if (pageActivities.length === 0) {
    body.innerHTML = '<tr><td colspan="4"><div class="text-center py-8 text-on-surface-variant"><span class="material-symbols-outlined text-[48px] text-outline-variant block mb-2">history</span><p class="font-body">لا توجد أنشطة مطابقة للفلاتر</p></div></td></tr>';
  } else {
    body.innerHTML = pageActivities.map(a => `
      <tr class="transition-colors">
        <td class="py-3 px-3 font-table-b text-on-surface">${a.user}</td>
        <td class="py-3 px-3 font-table-b text-on-surface">${a.action}</td>
        <td class="py-3 px-3 font-small text-on-surface-variant whitespace-nowrap">${a.time}</td>
        <td class="py-3 px-3"><code class="font-code-sm text-on-surface-variant">${a.ip}</code></td>
      </tr>
    `).join('');
  }
  renderPagination('activityPagination', totalPages, activityPage, (p) => { activityPage = p; renderActivities(); });
}

function filterActivities() { activityPage = 1; renderActivities(); }

function exportCSV() {
  const activities = getActivities();
  const rows = [['المستخدم', 'الإجراء', 'الوقت', 'IP']];
  activities.forEach(a => rows.push([a.user, a.action, a.time, a.ip]));
  const csv = rows.map(r => r.join(',')).join('\n');
  const blob = new Blob(['\ufeff' + csv], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = 'activity_log.csv';
  link.click();
  showToast('تم تصدير سجل النشاط بنجاح', 'success');
}

// ==========================================
// تأكيد الحذف (الحوار في js/main.js)
// ==========================================
function doDelete(type, id, name) {
  showToast(`تم حذف ${name} بنجاح`, 'success');
  closeModal();
  if (type === 'document') renderDocuments();
}
