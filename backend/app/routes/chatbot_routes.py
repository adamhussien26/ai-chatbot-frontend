"""
routes/chatbot_routes.py — محادثة الطالب مع المساعد الذكي
POST /api/chat        → سؤال → إجابة (يُحفظ في السجل)
GET  /api/chat/history → سجل محادثات الطالب
DELETE /api/chat/history → مسح سجل الطالب
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.router import process_question
from app.auth.dependencies import get_current_user
from app.database.connection import get_db
from app.models import ChatHistory, User
from app.schemas.chat import ChatAnswer, ChatHistoryOut, ChatQuestion
from app.services.academic_service import get_student_by_user
from app.utils.exceptions import PermissionDeniedError

router = APIRouter(prefix="/chat", tags=["Chatbot"])


@router.post("", response_model=ChatAnswer)
def ask(
    payload: ChatQuestion,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    استقبال سؤال الطالب → تحليل → توجيه (DB/RAG/LLM) → إجابة.
    تحفظ المحادثة تلقائيًا في chat_history.
    """
    student = get_student_by_user(db, user.id)
    student_id = student.id if student else None

    result = process_question(db, payload.question.strip(), student_id, user.id)

    history = ChatHistory(
        user_id=user.id,
        question=payload.question.strip(),
        answer=result["answer"],
        source=result["source"],
        source_ref=result.get("source_ref"),
    )
    db.add(history)
    db.commit()

    return ChatAnswer(**result)


@router.get("/history", response_model=list[ChatHistoryOut])
def my_history(limit: int = 50, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """سجل محادثات المستخدم الحالي فقط (خصوصية كاملة)."""
    logs = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user.id)
        .order_by(ChatHistory.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )
    return list(reversed(logs))


@router.delete("/history")
def clear_history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    count = db.query(ChatHistory).filter(ChatHistory.user_id == user.id).delete()
    db.commit()
    return {"success": True, "message": f"تم مسح {count} رسالة من سجل محادثاتك."}


@router.get("/history/{history_id}", response_model=ChatHistoryOut)
def history_item(history_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """رسالة واحدة من السجل — الطالب لا يرى إلا رسائله."""
    log = db.get(ChatHistory, history_id)
    if log is None or log.user_id != user.id:
        raise PermissionDeniedError("هذه الرسالة غير موجودة في سجل محادثاتك.")
    return log
