"""
auth/dependencies.py — تبعيات الحماية: المستخدم الحالي + الصلاحيات
"""
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.security import decode_access_token
from app.database.connection import get_db
from app.models import ROLE_ADMIN, User
from app.utils.exceptions import AuthError, PermissionDeniedError

_bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """يستخرج المستخدم من رمز Bearer JWT ويتحقق من صلاحيته."""
    if credentials is None:
        raise AuthError("مطلوب تسجيل الدخول للوصول إلى هذا المورد.")

    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise AuthError("جلسة غير صالحة أو منتهية. سجّل الدخول مرة أخرى.")

    user = db.get(User, int(payload.get("sub", "0")))
    if user is None or not user.is_active:
        raise AuthError("الحساب غير موجود أو معطّل.")

    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    """يمنح الوصول للأدمن فقط."""
    if not user.is_admin:
        raise PermissionDeniedError("هذه العملية متاحة لمدير النظام فقط.")
    return user


def require_student(user: User = Depends(get_current_user)) -> User:
    """يمنح الوصول للطلاب فقط."""
    if user.is_admin:
        raise PermissionDeniedError("هذه العملية متاحة للطلاب فقط.")
    return user


def get_current_student(db: Session = Depends(get_db), user: User = Depends(require_student)):
    """يعيد سجل الطالب المرتبط بالمستخدم الحالي."""
    from app.models import Student

    student = db.query(Student).filter(Student.user_id == user.id).first()
    if student is None:
        raise PermissionDeniedError("لا يوجد ملف طالب مرتبط بهذا الحساب.")
    return student
