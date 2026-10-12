"""
models/__init__.py — تصدير جميع النماذج في مكان واحد
"""
from app.models.user import User, ROLE_ADMIN, ROLE_STUDENT
from app.models.student import Faculty, Department, Student
from app.models.academic import Course, Enrollment, Result, Schedule, Exam
from app.models.notification import Notification
from app.models.chat import ChatHistory, SOURCE_DATABASE, SOURCE_LLM, SOURCE_RAG
from app.models.knowledge import KnowledgeDocument, KnowledgeChunk
from app.models.otp import OTPCode

__all__ = [
    "User", "ROLE_ADMIN", "ROLE_STUDENT",
    "Faculty", "Department", "Student",
    "Course", "Enrollment", "Result", "Schedule", "Exam",
    "Notification",
    "ChatHistory", "SOURCE_DATABASE", "SOURCE_LLM", "SOURCE_RAG",
    "KnowledgeDocument", "KnowledgeChunk",
    "OTPCode",
]
