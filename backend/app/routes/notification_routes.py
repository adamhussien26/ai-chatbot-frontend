"""
routes/notification_routes.py — الإشعارات
- المستخدم يرى إشعاراته + الإشعارات العامة.
- الأدمن ينشئ إشعارات (فردية أو بث عام).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database.connection import get_db
from app.models import Notification, User
from app.schemas.academic import NotificationCreate, NotificationOut
from app.services.academic_service import get_user_notifications
from app.utils.exceptions import NotFoundError

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/my", response_model=list[NotificationOut])
def my_notifications(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return get_user_notifications(db, user.id)


@router.patch("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    notification = db.get(Notification, notification_id)
    if notification is None:
        raise NotFoundError("الإشعار غير موجود.")
    # لا يُسمح بتعديل إشعار مستخدم آخر (الإشعارات العامة يقروها الجميع نسخةً منطقية)
    if notification.user_id is not None and notification.user_id != user.id:
        raise NotFoundError("الإشعار غير موجود.")
    notification.is_read = True
    db.commit()
    db.refresh(notification)
    return notification


@router.post("", response_model=NotificationOut, status_code=201)
def create_notification(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    notification = Notification(**payload.model_dump())
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    notification = db.get(Notification, notification_id)
    if notification is None:
        raise NotFoundError("الإشعار غير موجود.")
    db.delete(notification)
    db.commit()
    return {"success": True, "message": "تم حذف الإشعار."}
