/**
 * ==========================================================================
 * Page Specific Logic: 07-settings.html (صفحة الإعدادات والملف الشخصي)
 * Handles profile picture simulation, password update form submission.
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  initProfilePhotoActions();
  initPasswordChangeForm();
});

/**
 * Handles profile photo edit / remove interactions.
 */
function initProfilePhotoActions() {
  const photoEditBtn = document.querySelector('.photo-edit-btn');
  const removePhotoBtn = document.querySelector('.remove-photo');
  const profilePhoto = document.querySelector('.profile-photo');

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
}

/**
 * Handles security card password update action.
 */
function initPasswordChangeForm() {
  const changePasswordBtn = document.querySelector('.card-footer .primary-btn');
  if (!changePasswordBtn) return;

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
