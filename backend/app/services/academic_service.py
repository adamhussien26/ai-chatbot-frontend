"""
services/academic_service.py — استعلامات البيانات الأكاديمية
تُستخدم من مسارات REST ومن محرك الـ Chatbot (مصدر DATABASE).
"""
from sqlalchemy.orm import Session

from app.models import (
    Course, Enrollment, Exam, Faculty, Notification, Result, Schedule, Student,
)

ARABIC_DAYS = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]

CURRENT_SEMESTER = "2025-2026 الفصل الأول"


# ---------------------------------------------------------------- helpers
def get_student_by_user(db: Session, user_id: int) -> Student | None:
    return db.query(Student).filter(Student.user_id == user_id).first()


def student_course_ids(db: Session, student_id: int, semester: str | None = None) -> list[int]:
    q = db.query(Enrollment.course_id).filter(Enrollment.student_id == student_id)
    if semester:
        q = q.filter(Enrollment.semester == semester)
    return [row[0] for row in q.all()]


def grade_from_total(total: float) -> tuple[str, float]:
    """يحوّل العلامة إلى تقدير ونقاط GPA."""
    if total >= 90:
        return "A+", 4.0
    if total >= 80:
        return "A", 4.0
    if total >= 70:
        return "B", 3.0
    if total >= 60:
        return "C", 2.0
    if total >= 50:
        return "D", 1.0
    return "F", 0.0


# ---------------------------------------------------------------- Results
def get_student_results(db: Session, student_id: int, semester: str | None = None) -> list[dict]:
    q = (
        db.query(Result, Course)
        .join(Course, Result.course_id == Course.id)
        .filter(Result.student_id == student_id)
    )
    if semester:
        q = q.filter(Result.semester == semester)
    rows = q.order_by(Result.id.desc()).all()

    results = []
    for result, course in rows:
        results.append({
            "id": result.id,
            "course_id": course.id,
            "course_code": course.code,
            "course_name": course.name,
            "semester": result.semester,
            "midterm": float(result.midterm) if result.midterm is not None else None,
            "final_exam": float(result.final_exam) if result.final_exam is not None else None,
            "practical": float(result.practical) if result.practical is not None else None,
            "total": float(result.total),
            "grade": result.grade,
            "gpa_points": float(result.gpa_points),
        })
    return results


def get_student_gpa(db: Session, student_id: int) -> dict:
    rows = (
        db.query(Result, Course.credit_hours)
        .join(Course, Result.course_id == Course.id)
        .filter(Result.student_id == student_id)
        .all()
    )
    if not rows:
        return {"gpa": None, "credits_earned": 0, "courses_count": 0}

    total_points = 0.0
    total_credits = 0
    earned = 0
    for result, credits in rows:
        total_points += float(result.gpa_points) * credits
        total_credits += credits
        if float(result.gpa_points) > 0:
            earned += credits

    gpa = round(total_points / total_credits, 2) if total_credits else None
    return {"gpa": gpa, "credits_earned": earned, "courses_count": len(rows)}


# ---------------------------------------------------------------- Courses
def get_student_courses(db: Session, student_id: int, semester: str | None = None) -> list[dict]:
    q = (
        db.query(Enrollment, Course)
        .join(Course, Enrollment.course_id == Course.id)
        .filter(Enrollment.student_id == student_id)
    )
    if semester:
        q = q.filter(Enrollment.semester == semester)
    rows = q.all()
    return [
        {
            "id": course.id,
            "code": course.code,
            "name": course.name,
            "credit_hours": course.credit_hours,
            "semester": enrollment.semester,
            "description": course.description,
        }
        for enrollment, course in rows
    ]


def find_course_by_hint(db: Session, hint: str) -> Course | None:
    """بحث مرن عن مقرر عبر اسم/كلمة من سؤال المستخدم."""
    hint = (hint or "").strip()
    if not hint:
        return None
    courses = db.query(Course).all()
    hint_lower = hint.lower()

    # مطابقة بالكود أولًا
    for course in courses:
        if course.code.lower() == hint_lower or course.code.lower() in hint_lower:
            return course
    # ثم بالاسم الكامل أو الجزئي
    for course in courses:
        if course.name in hint or hint in course.name:
            return course
    for course in courses:
        words = [w for w in course.name.split() if len(w) > 2]
        if words and any(w in hint for w in words):
            return course
    return None


# ---------------------------------------------------------------- Schedule
def get_student_schedule(db: Session, student_id: int, semester: str | None = None) -> list[dict]:
    """جدول الطالب: صفوف خاصة به + صفوف عامة (student_id NULL) لمقرراته المسجلة."""
    course_ids = student_course_ids(db, student_id, semester)

    from sqlalchemy import or_
    q = (
        db.query(Schedule, Course)
        .join(Course, Schedule.course_id == Course.id)
        .filter(or_(Schedule.student_id == student_id, Schedule.student_id.is_(None)))
    )
    if semester:
        q = q.filter(Schedule.semester == semester)
    elif course_ids:
        q = q.filter(or_(Schedule.student_id == student_id, Schedule.course_id.in_(course_ids)))
    else:
        q = q.filter(Schedule.student_id == student_id)

    rows = q.order_by(Schedule.day_of_week, Schedule.start_time).all()
    return [
        {
            "id": schedule.id,
            "course_code": course.code,
            "course_name": course.name,
            "day": ARABIC_DAYS[schedule.day_of_week] if 0 <= schedule.day_of_week < 7 else str(schedule.day_of_week),
            "day_of_week": schedule.day_of_week,
            "start_time": schedule.start_time.strftime("%H:%M"),
            "end_time": schedule.end_time.strftime("%H:%M"),
            "room": schedule.room,
            "lecturer": schedule.lecturer,
            "semester": schedule.semester,
        }
        for schedule, course in rows
    ]


# ---------------------------------------------------------------- Exams
def get_student_exams(db: Session, student_id: int, semester: str | None = None) -> list[dict]:
    """امتحانات مقررات الطالب المسجلة."""
    course_ids = student_course_ids(db, student_id)
    if not course_ids:
        return []

    q = db.query(Exam, Course).join(Course, Exam.course_id == Course.id).filter(Exam.course_id.in_(course_ids))
    if semester:
        q = q.filter(Exam.semester == semester)
    rows = q.order_by(Exam.exam_date, Exam.start_time).all()

    from datetime import date
    today = date.today()
    return [
        {
            "id": exam.id,
            "course_code": course.code,
            "course_name": course.name,
            "title": exam.title,
            "exam_date": exam.exam_date.isoformat(),
            "days_left": (exam.exam_date - today).days,
            "start_time": exam.start_time.strftime("%H:%M"),
            "end_time": exam.end_time.strftime("%H:%M"),
            "room": exam.room,
            "semester": exam.semester,
            "is_past": exam.exam_date < today,
        }
        for exam, course in rows
    ]


# ---------------------------------------------------------------- Notifications
def get_user_notifications(db: Session, user_id: int) -> list[Notification]:
    from sqlalchemy import or_
    return (
        db.query(Notification)
        .filter(or_(Notification.user_id == user_id, Notification.user_id.is_(None)))
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )


# ---------------------------------------------------------------- Profile
def get_student_profile(db: Session, user_id: int) -> dict | None:
    student = get_student_by_user(db, user_id)
    if student is None:
        return None
    user = student.user
    faculty = db.get(Faculty, student.faculty_id) if student.faculty_id else None
    department = student.department

    return {
        "id": student.id,
        "user_id": user.id,
        "university_id": student.university_id,
        "full_name": user.full_name,
        "email": user.email,
        "faculty_id": student.faculty_id,
        "faculty_name": faculty.name if faculty else None,
        "department_id": student.department_id,
        "department_name": department.name if department else None,
        "level": student.level,
        "phone": student.phone,
        "avatar_url": student.avatar_url,
        "enrollment_year": student.enrollment_year,
    }
