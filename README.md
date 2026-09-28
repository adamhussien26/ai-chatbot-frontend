# المساعد الذكي - جامعة العلوم والتقانة (Frontend)

واجهة أمامية بسيطة ومنظمة مبنية على **HTML + CSS + JavaScript فقط** (بدون أي Framework).

المبدأ الأساسي: **"Write once, reuse everywhere"** — كل ما هو مشترك بين أكثر من شاشة موجود في ملف واحد مشترك.

---

## 📁 هيكلية المشروع (Directory Structure)

```text
fronend/
│
├── pages/                     # جميع صفحات المشروع
│   ├── welcome.html           # صفحة الترحب الهبوطية
│   ├── signup.html            # صفحة إنشاء حساب طالب جديد
│   ├── login.html             # صفحة تسجيل الدخول
│   ├── forgot-password.html   # صفحة استعادة كلمة المرور
│   ├── reset-password.html    # صفحة إعادة تعيين كلمة المرور
│   ├── chat.html              # صفحة المحادثة مع المساعد الذكي
│   └── settings.html          # صفحة الملف الشخصي
│
├── css/
│   └── style.css              # ملف CSS واحد مشترك لجميع الصفحات
│
├── js/
│   ├── main.js                # JavaScript مشترك (المظهر، الاتجاه، المكونات، النماذج)
│   └── chat.js                # منطق خاص بصفحة المحادثة فقط
│
├── assets/
│   └── images/                # الصور والشعارات
│
└── README.md                  # توثيق المشروع
```

---

## 🎨 نظام التصميم (css/style.css)

ملف واحد منظم بأقسام مرقّمة واضحة:

| القسم | المحتوى |
|---|---|
| 1. Design Tokens | الألوان، الخطوط، الظلال، الزوايا (CSS Variables) |
| 2. Reset & Base | تصفير CSS، الخطوط الأساسية، RTL/LTR، شريط التمرير |
| 3. Utilities | أدوات مساعدة (`.hidden`, `.hide`, `.show`) |
| 4. Shared Keyframes | حركات مشتركة |
| 5. Components | `.btn`, `.btn-primary`, `.btn-google`, `.field`, `.input-wrap`, `.toggle-pass`, `.error`, `.card`, `.card-header`, `.badge`, `.topbar`, `.strength`, `.rules` |
| 6. Auth Layouts | عناصر مشتركة لصفحات المصادقة: `body.auth-page`, `.auth-split`, `.auth-card`, `.back-link`, `.divider`, `.success-box` |
| 7-12. Page Sections | الأنماط الخاصة بكل صفحة في قسم واضح (Welcome, Signup, Login, Forgot/Reset, Chat, Settings) |
| 13. Responsive | كل Media Queries موحدة في مكان واحد |
| 14. Theme Layer | طبقة Glassmorphism النهائية |

> **ملاحظة**: لا يوجد ملف CSS منفصل لأي شاشة — كل شيء في `style.css`.

---

## ⚡ نظام JavaScript

| الملف | المحتوى |
|---|---|
| `js/main.js` | **مشترك لكل الصفحات**: اتجاه اللغة RTL/LTR، رسم Topbar تلقائياً، إظهار/إخفاء كلمة المرور، التحقق من النماذج (Login / Signup / Forgot / Reset)، صفحة الملف الشخصي |
| `js/chat.js` | **خاص بصفحة المحادثة فقط**: محرك الرسائل، الردود الذكية، الاقتراحات، أرشيف المحادثات، قائمة الجوال |

كل دالة في `main.js` محمية بفحص وجود عناصر الصفحة — لذا تحميل `main.js` في كل صفحة آمن ولا يسبب أخطاء.

---

## 🚀 التشغيل

افتح `pages/welcome.html` مباشرة في المتصفح، أو استخدم إضافة Live Server في VS Code.

---

## 🧭 التنقل بين الصفحات

```
welcome → login → chat ⇄ settings
login ⇄ signup
login → forgot-password → reset-password → login
```

---

## ✅ مبادئ مطبقة

1. **DRY**: لا تكرار — Topbar وزر المظهر يُرسمون مرة واحدة في `main.js` لجميع الصفحات.
2. **ملف CSS واحد** منظم بأقسام بدلاً من ملف لكل شاشة.
3. **ملفا JS فقط**: مشترك + ملف خاص بالمحادثة (حاجة حقيقية فقط).
4. **RTL/LTR**: دعم كامل للاتجاهين محفوظ في المتصفح (localStorage).
5. **Semantic HTML + ARIA**: وسوم دلالية وسمات وصول أساسية.
