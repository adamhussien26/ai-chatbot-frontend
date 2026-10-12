"""
routes/admin_routes.py — لوحة الإدارة: إحصائيات + إدارة المستخدمين + سجل المحادثات
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.auth.security import hash_password
from app.database.connection import get_db
from app.models import (
    ChatHistory, Course, KnowledgeDocument, Result, Student, User,
)
from app.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/admin", tags=["Admin"])


# ---------------------------------------------------------------- Stats
@router.get("/stats")
def stats(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    return {
        "users_count": db.query(func.count(User.id)).scalar(),
        "students_count": db.query(func.count(Student.id)).scalar(),
        "courses_count": db.query(func.count(Course.id)).scalar(),
        "results_count": db.query(func.count(Result.id)).scalar(),
        "chat_messages_count": db.query(func.count(ChatHistory.id)).scalar(),
        "kb_documents_count": db.query(func.count(KnowledgeDocument.id)).scalar(),
    }


# ---------------------------------------------------------------- Users management
@router.get("/users")
def list_users(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    users = db.query(User).order_by(User.id).all()
    return [
        {
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None,
        }
        for u in users
    ]


@router.patch("/users/{user_id}")
def update_user(
    user_id: int,
    role: str | None = None,
    is_active: bool | None = None,
    full_name: str | None = None,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("المستخدم غير موجود.")

    if user.id == admin.id and is_active is False:
        raise ValidationError("لا يمكنك تعطيل حسابك الخاص.")

    if role is not None:
        if role not in ("student", "admin"):
            raise ValidationError("الدور يجب أن يكون 'student' أو 'admin'.")
        user.role = role
    if is_active is not None:
        user.is_active = is_active
    if full_name is not None and full_name.strip():
        user.full_name = full_name.strip()

    db.commit()
    return {"success": True, "message": "تم تحديث المستخدم."}


@router.post("/users/{user_id}/reset-password")
def admin_reset_password(
    user_id: int,
    new_password: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if len(new_password) < 8:
        raise ValidationError("كلمة المرور يجب أن تكون 8 أحرف على الأقل.")
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("المستخدم غير موجود.")
    user.password_hash = hash_password(new_password)
    db.commit()
    return {"success": True, "message": "تم تعيين كلمة مرور جديدة."}


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    if user_id == admin.id:
        raise ValidationError("لا يمكنك حذف حسابك الخاص.")
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError("المستخدم غير موجود.")
    db.delete(user)  # CASCADE يحذف سجلات الطالب والمحادثات المرتبطة
    db.commit()
    return {"success": True, "message": "تم حذف المستخدم."}


# ---------------------------------------------------------------- Chat logs
@router.get("/chat-logs")
def chat_logs(
    user_id: int | None = None,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = db.query(ChatHistory)
    if user_id is not None:
        query = query.filter(ChatHistory.user_id == user_id)
    logs = query.order_by(ChatHistory.created_at.desc()).limit(min(limit, 500)).all()

    users = {u.id: u.email for u in db.query(User).filter(User.id.in_({l.user_id for l in logs})).all()} if logs else {}
    return [
        {
            "id": log.id,
            "user_id": log.user_id,
            "user_email": users.get(log.user_id),
            "question": log.question,
            "answer": log.answer,
            "source": log.source,
            "source_ref": log.source_ref,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log in logs
    ]
