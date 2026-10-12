"""
routes/auth_routes.py — المصادقة: تسجيل، دخول، خروج، الملف الشخصي،
نسيت كلمة المرور (OTP)، إعادة التعيين، تغيير كلمة المرور.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.otp import issue_otp, verify_otp
from app.auth.security import create_access_token, hash_password, verify_password
from app.config.settings import settings
from app.database.connection import get_db
from app.models import ROLE_STUDENT, Faculty, Student, User
from app.schemas.auth import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
    UserOut,
    VerifyOTPRequest,
)
from app.utils.exceptions import AppError, AuthError, NotFoundError, ValidationError

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ------------------------------------------------------------------ Register
@router.post("/register", response_model=TokenResponse, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    """إنشاء حساب طالب جديد."""
    exists = db.query(User).filter(User.email == payload.email.lower()).first()
    if exists:
        raise ValidationError("البريد الإلكتروني مستخدم بالفعل.")

    uni_id_taken = db.query(Student).filter(Student.university_id == payload.university_id).first()
    if uni_id_taken:
        raise ValidationError("الرقم الجامعي مستخدم بالفعل.")

    user = User(
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        full_name=payload.full_name.strip(),
        role=ROLE_STUDENT,
    )
    db.add(user)
    db.flush()

    student = Student(
        user_id=user.id,
        university_id=payload.university_id,
        faculty_id=payload.faculty_id,
        department_id=payload.department_id,
        level=payload.level,
        enrollment_year=payload.university_id[:4] if payload.university_id[:4].isdigit() else None,
    )
    db.add(student)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


# ------------------------------------------------------------------ Login
@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise AuthError("البريد الإلكتروني أو كلمة المرور غير صحيحة.")
    if not user.is_active:
        raise AuthError("هذا الحساب معطّل. تواصل مع إدارة النظام.")

    token = create_access_token(user.id, user.role)
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


# ------------------------------------------------------------------ Logout
@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    """
    الخروج عديم الحالة (Stateless): الواجهة تحذف الرمز محليًا.
    نقطة النهاية موجودة للتوحيد وتأكيد الهوية.
    """
    return {"success": True, "message": "تم تسجيل الخروج بنجاح."}


# ------------------------------------------------------------------ Me
@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return UserOut.model_validate(user)


# ------------------------------------------------------------------ Change password
@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.current_password, user.password_hash):
        raise AuthError("كلمة المرور الحالية غير صحيحة.")

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"success": True, "message": "تم تغيير كلمة المرور بنجاح."}


# ------------------------------------------------------------------ Forgot password (OTP)
@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    الخطوة 1 من استعادة الحساب: إنشاء رمز OTP وإرساله (يُرسل عبر البريد في الإنتاج).
    في وضع التطوير يعاد الرمز في الاستجابة (dev_code) لاختبار التدفق.
    """
    user = db.query(User).filter(User.email == payload.email.lower()).first()

    # لا نكشف إن كان البريد مسجلًا أم لا (حماية من تعداد الحسابات)
    if user is None:
        return {"success": True, "message": "إذا كان البريد مسجلًا فسيصلك رمز التحقق."}

    code = issue_otp(db, user.id, purpose="password_reset")

    response = {
        "success": True,
        "message": "تم إرسال رمز التحقق إلى بريدك الإلكتروني.",
        "expires_in_minutes": settings.OTP_EXPIRE_MINUTES,
    }
    if settings.DEBUG:
        response["dev_code"] = code  # للتطوير فقط — يُحذف في الإنتاج
    return response


# ------------------------------------------------------------------ Verify OTP
@router.post("/verify-otp")
def verify_otp_endpoint(payload: VerifyOTPRequest, db: Session = Depends(get_db)):
    """الخطوة 2: التحقق من الرمز قبل السماح بإعادة التعيين."""
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None:
        raise NotFoundError("الحساب غير موجود.")

    if not verify_otp(db, user.id, payload.code, purpose="password_reset"):
        raise ValidationError("رمز التحقق غير صحيح أو منتهي الصلاحية.")

    return {"success": True, "message": "تم التحقق من الرمز بنجاح.", "email": payload.email.lower()}


# ------------------------------------------------------------------ Reset password
@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """الخطوة 3: تعيين كلمة مرور جديدة بعد التحقق من OTP (يستهلك الرمز)."""
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user is None:
        raise NotFoundError("الحساب غير موجود.")

    if not verify_otp(db, user.id, payload.code, purpose="password_reset", consume=True):
        raise ValidationError("رمز التحقق غير صحيح أو منتهي الصلاحية.")

    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {"success": True, "message": "تم تغيير كلمة المرور بنجاح. يمكنك تسجيل الدخول الآن."}


# ------------------------------------------------------------------ Faculties (public-ish, للنماذج)
@router.get("/faculties")
def list_faculties(db: Session = Depends(get_db)):
    """قائمة الكليات والأقسام لنماذج التسجيل."""
    faculties = db.query(Faculty).all()
    return {
        "success": True,
        "faculties": [
            {
                "id": f.id,
                "name": f.name,
                "departments": [{"id": d.id, "name": d.name} for d in f.departments],
            }
            for f in faculties
        ],
    }
