// ==========================================
// js/mock-data.js
// جميع البيانات التجريبية مخزنة هنا
// يسهل استبدالها بـ API لاحقاً
// ==========================================

const MOCK_DATA = {
  // ===== إحصائيات لوحة التحكم =====
  dashboard: {
    conversationsToday: 1247,
    activeUsers: 389,
    totalDocuments: 56,
    weeklyUsage: {
      labels: ['السبت', 'الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة'],
      values: [320, 450, 510, 480, 620, 710, 590]
    },
    monthlyUsage: {
      labels: ['الأسبوع 1', 'الأسبوع 2', 'الأسبوع 3', 'الأسبوع 4'],
      values: [2100, 2800, 3200, 3600]
    },
    frequentQuestions: [
      { question: 'ما أوقات الدوام الجامعي؟', count: 234 },
      { question: 'كيف أتسجل في البرامج التدريبية؟', count: 189 },
      { question: 'ما موعد امتحانات الفصل الثاني؟', count: 156 },
      { question: 'أين يقع مكتبة الجامعة؟', count: 142 },
      { question: 'كيف أتجدد بطاقة الطالب؟', count: 98 }
    ],
    failedQuestions: [
      { question: 'ما رسوم الالتحاق بالبرنامج الدولية؟', answers: [] },
      { question: 'هل يوجد مقرر عن الذكاء الاصطناعي؟', answers: ['لا يوجد مقرر حالياً'] },
      { question: 'كيف أحصل على منحة دراسية؟', answers: [] }
    ]
  },

  // ===== المستندات =====
  documents: [
    { id: 1, name: 'منهج علم النفس الأساسي.pdf', type: 'PDF', size: '15.2 MB', date: '2026-09-15', status: 'indexed', category: 'كتب' },
    { id: 2, name: 'محاضرات البرمجة 1.pptx', type: 'PPTX', size: '48.7 MB', date: '2026-09-14', status: 'processing', category: 'محاضرات' },
    { id: 3, name: 'دليل الطالب 2026.pdf', type: 'PDF', size: '8.3 MB', date: '2026-09-13', status: 'indexed', category: 'أدلة' },
    { id: 4, name: 'بحث تخرج عن التعلم الآلي.pdf', type: 'PDF', size: '22.1 MB', date: '2026-09-12', status: 'failed', category: 'أبحاث' },
    { id: 5, name: 'كتيب الأنشطة الطلابية.docx', type: 'DOCX', size: '5.6 MB', date: '2026-09-11', status: 'indexed', category: 'كتيبات' },
    { id: 6, name: 'امتحان سنة 2025.pdf', type: 'PDF', size: '3.1 MB', date: '2026-09-10', status: 'processing', category: 'امتحانات' },
    { id: 7, name: 'جدول المقررات.xlsx', type: 'XLSX', size: '2.4 MB', date: '2026-09-09', status: 'indexed', category: 'جداول' },
    { id: 8, name: 'سياسات الجامعة 2026.pdf', type: 'PDF', size: '12 MB', date: '2026-09-08', status: 'failed', category: 'سياسات' },
    { id: 9, name: 'محاضرات الشبكات.part1.zip', type: 'ZIP', size: '150 MB', date: '2026-09-07', status: 'processing', category: 'محاضرات' },
    { id: 10, name: 'نشرة الجامعة الإلكترونية.pdf', type: 'PDF', size: '4.8 MB', date: '2026-09-06', status: 'indexed', category: 'نشرات' }
  ],

  // ===== سجلات النشاط =====
  activities: [
    { user: 'المسؤول العام', action: 'أضاف مستند جديد', time: '2026-09-20 15:30', ip: '192.168.1.10' },
    { user: 'محمد العلي', action: 'عدّل خدمة التسجيل', time: '2026-09-20 14:45', ip: '192.168.1.25' },
    { user: 'أحمد محمد الشيخ', action: 'تسجيل دخول', time: '2026-09-20 14:30', ip: '192.168.1.45' },
    { user: 'المسؤول العام', action: 'غيّر إعدادات البوت', time: '2026-09-20 13:15', ip: '192.168.1.10' },
    { user: 'فاطمة علي عمران', action: 'رفع مستند', time: '2026-09-20 12:00', ip: '192.168.1.60' },
    { user: 'خالد عبدالله حسن', action: 'تعديل بيانات شخصية', time: '2026-09-20 11:30', ip: '192.168.1.33' },
    { user: 'سارة الفهد', action: 'عرض التقارير', time: '2026-09-20 10:15', ip: '192.168.1.77' },
    { user: 'المسؤول العام', action: 'أنشئ مستخدم جديد', time: '2026-09-20 09:00', ip: '192.168.1.10' },
    { user: 'عمر راشد النوبي', action: 'تقديم طلب', time: '2026-09-19 17:00', ip: '192.168.2.15' },
    { user: 'محمد العلي', action: 'حذف مستند قديم', time: '2026-09-19 16:45', ip: '192.168.1.25' },
    { user: 'نورة سعد المري', action: 'تسجيل دخول', time: '2026-09-19 15:30', ip: '192.168.1.88' },
    { user: 'المسؤول العام', action: 'أطلق تحديث النظام', time: '2026-09-19 14:00', ip: '192.168.1.10' }
  ],

};

// ===== البيانات المجمعة =====
function getDashboardData() { return MOCK_DATA.dashboard; }
function getDocuments() { return MOCK_DATA.documents; }
function getActivities() { return MOCK_DATA.activities; }