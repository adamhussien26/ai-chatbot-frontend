# المساعد الذكي - جامعة العلوم والتقانة (Clean Frontend Architecture)

مشروع الواجهة الأمامية (Frontend) المنظم والمحدث وفق أعلى معايير البرمجة النظيفة (**Professional Clean Code Architecture**).

---

## 📁 هيكلية المشروع (Directory Structure)

```text
g:/Desktop/design/
│
├── 01-welcome.html          # صفحة الترحب الهبوطية
├── 02-signup.html           # صفحة إنشاء حساب طالب جديد
├── 03-login.html            # صفحة تسجيل الدخول
├── 04-forgot-password.html  # صفحة استعادة كلمة المرور
├── 05-reset-password.html   # صفحة إعادة تعيين كلمة المرور
├── 06-chat.html             # صفحة المحادثة التفاعلية مع المساعد الذكي
├── 07-settings.html         # صفحة الملف الشخصي وإعدادات الحساب
│
├── css/                     # ملفات التنسيق والنظام الجمالي
│   ├── style.css            # CSS Variables, Resets, Base Typography, Utilities
│   ├── components.css       # Reusable Components (Buttons, Cards, Inputs, Topbar)
│   ├── responsive.css       # Media Queries الموحدة للتجاوب مع كافة الشاشات
│   └── pages/               # التنسيقات الخاصة بكل صفحة فقط
│       ├── welcome.css
│       ├── signup.css
│       ├── login.css
│       ├── forgot-password.css
│       ├── reset-password.css
│       ├── chat.css
│       └── settings.css
│
├── js/                      # ملفات الجافاسكريبت والسلوك
│   ├── main.js              # التهيئة العامة، إدارة RTL/LTR، والثيم الداكن
│   ├── components.js        # وظائف المكونات التفاعلية (تبديل كلمة المرور، الـ Validation)
│   └── pages/               # المنطق البرمجي الخاص بكل صفحة فقط
│       ├── welcome.js
│       ├── signup.js
│       ├── login.js
│       ├── forgot-password.js
│       ├── reset-password.js
│       ├── chat.js
│       └── settings.js
│
├── assets/                  # الصور والشعارات والوسائط
│   └── logo.png
│
└── README.md                # توثيق المشروع
```

---

## 🎨 النظام الجمالي (Global Design System)

تم بناء كافة ألوان وأبعاد المشروع باستخدام **CSS Custom Properties (`:root`)** في `css/style.css`:

```css
:root {
  --navy-900: #0f1b3d;
  --gold-500: #c9a24a;
  --teal-btn: #1c4d55;
  --bg: #f4f5f8;
  --panel: #ffffff;
  --text-dark: #14203f;
  --text-muted: #6b7280;
  --border: #e6e8ee;
  --radius-md: 12px;
  --radius-lg: 18px;
  --shadow-sm: 0 4px 12px rgba(15, 27, 61, 0.06);
}
```

---

## 🚀 المبادئ المطبقة (Clean Code Principles)

1. **Separation of Concerns (فصل المسؤوليات)**:
   - **HTML**: مسؤول عن الـ Semantic Structure فقط. خالي تماماً من وسوم `<style>`, `<script>`, أو السمتين `style="..."` و `onclick="..."`.
   - **CSS**: مسؤول عن التصميم والتجاوب، مقسم إلى Global Variables, Reusable Components, و Page-Specific CSS.
   - **JS**: مسؤول عن السلوك والتفاعلات، مقسم إلى Main App Handler, Component Utils, و Page-Specific Logic.
2. **DRY (Don't Repeat Yourself)**: إعادة استخدام أنماط الأزرار والنماذج والكروت ومبدلات اللغة والكلمة المرورية بدلاً من تكرارها.
3. **Arabic RTL + English LTR Support**: دعم كامل ومتناسق للاتجاهين مع استخدام CSS Logical Properties.
4. **Single Responsibility**: كل ملف وFunction يؤدي غرضاً واحداً واضحاً ومحدد المسؤولية.
5. **Accessibility & SEO**: استخدام Semantic HTML5 tags (`<header>`, `<main>`, `<aside>`, `<nav>`, `<form>`, `<label>`) وسمات ARIA الأساسية.
