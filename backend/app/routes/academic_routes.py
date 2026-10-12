"""
routes/academic_routes.py — المقررات والنتائج والجداول والامتحانات
- الطالب يرى بياناته فقط (/my).
- الأدمن يدير البيانات (CRUD).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_student, require_admin
from app.database.connection import get_db
from app.models import Course, Exam, Result, Schedule, User
from app.schemas.academic import (
    CourseCreate, CourseOut, CourseUpdate, EnrollmentCreate,
    ExamCreate, ExamOut, ResultCreate, ResultOut, ResultUpdate,
    ScheduleCreate, ScheduleOut,
)
from app.services.academic_service import (
    CURRENT_SEMESTER, find_course_by_hint, get_student_courses,
    get_student_exams, get_student_gpa, get_student_results,
    get_student_schedule, grade_from_total,
)
from app.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(tags=["Academic"])


# ================================================================ Courses
@router.get("/courses", response_model=list[CourseOut])
def list_courses(q: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """كل المقررات (أدمن) مع بحث اختياري."""
    query = db.query(Course)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter((Course.name.like(like)) | (Course.code.like(like)))
    return query.order_by(Course.code).all()


@router.get("/courses/my")
def my_courses(db: Session = Depends(get_db), student=Depends(get_current_student)):
    """مقررات الطالب المسجلة."""
    return get_student_courses(db, student.id)


@router.get("/courses/hint")
def course_hint(q: str, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """بحث مرن عن مقرر بالاسم/الكود (أدمن)."""
    course = find_course_by_hint(db, q)
    if course is None:
        raise NotFoundError("لا يوجد مقرر مطابق.")
    return {"id": course.id, "code": course.code, "name": course.name, "credit_hours": course.credit_hours}


@router.post("/courses", response_model=CourseOut, status_code=201)
def create_course(payload: CourseCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if db.query(Course).filter(Course.code == payload.code.upper()).first():
        raise ValidationError("كود المقرر مستخدم بالفعل.")
    course = Course(
        code=payload.code.upper(),
        name=payload.name,
        credit_hours=payload.credit_hours,
        description=payload.description,
        department_id=payload.department_id,
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.put("/courses/{course_id}", response_model=CourseOut)
def update_course(
    course_id: int, payload: CourseUpdate,
    db: Session = Depends(get_db), _: User = Depends(require_admin),
):
    course = db.get(Course, course_id)
    if course is None:
        raise NotFoundError("المقرر غير موجود.")
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(course, field, value)
    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    course = db.get(Course, course_id)
    if course is None:
        raise NotFoundError("المقرر غير موجود.")
    db.delete(course)
    db.commit()
    return {"success": True, "message": "تم حذف المقرر."}


@router.post("/enrollments", status_code=201)
def enroll_student(payload: EnrollmentCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    from app.models import Enrollment, Student

    if not db.get(Student, payload.student_id):
        raise NotFoundError("الطالب غير موجود.")
    if not db.get(Course, payload.course_id):
        raise NotFoundError("المقرر غير موجود.")

    exists = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id == payload.student_id,
            Enrollment.course_id == payload.course_id,
            Enrollment.semester == payload.semester,
        )
        .first()
    )
    if exists:
        raise ValidationError("الطالب مسجل في هذا المقرر لنفس الفصل بالفعل.")

    enrollment = Enrollment(**payload.model_dump())
    db.add(enrollment)
    db.commit()
    return {"success": True, "message": "تم تسجيل الطالب في المقرر."}


# ================================================================ Results
@router.get("/results/my")
def my_results(db: Session = Depends(get_db), student=Depends(get_current_student)):
    results = get_student_results(db, student.id)
    gpa = get_student_gpa(db, student.id)
    return {"results": results, "gpa_summary": gpa}


@router.post("/results", response_model=ResultOut, status_code=201)
def create_result(payload: ResultCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    from app.models import Enrollment, Student

    if not db.get(Student, payload.student_id):
        raise NotFoundError("الطالب غير موجود.")
    if not db.get(Course, payload.course_id):
        raise NotFoundError("المقرر غير موجود.")

    grade, points = grade_from_total(payload.total)
    result = Result(
        student_id=payload.student_id,
        course_id=payload.course_id,
        semester=payload.semester,
        midterm=payload.midterm,
        final_exam=payload.final_exam,
        practical=payload.practical,
        total=payload.total,
        grade=grade,
        gpa_points=points,
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    course = db.get(Course, payload.course_id)
    out = ResultOut.model_validate(result)
    out.course_code = course.code
    out.course_name = course.name
    return out


@router.put("/results/{result_id}", response_model=ResultOut)
def update_result(
    result_id: int, payload: ResultUpdate,
    db: Session = Depends(get_db), _: User = Depends(require_admin),
):
    result = db.get(Result, result_id)
    if result is None:
        raise NotFoundError("النتيجة غير موجودة.")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(result, field, value)
    if "total" in data:
        result.grade, result.gpa_points = grade_from_total(data["total"])

    db.commit()
    db.refresh(result)
    return ResultOut.model_validate(result)


@router.delete("/results/{result_id}")
def delete_result(result_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    result = db.get(Result, result_id)
    if result is None:
        raise NotFoundError("النتيجة غير موجودة.")
    db.delete(result)
    db.commit()
    return {"success": True, "message": "تم حذف النتيجة."}


# ================================================================ Schedules
@router.get("/schedules/my")
def my_schedule(db: Session = Depends(get_db), student=Depends(get_current_student)):
    return {"schedule": get_student_schedule(db, student.id), "semester": CURRENT_SEMESTER}


@router.post("/schedules", response_model=ScheduleOut, status_code=201)
def create_schedule(payload: ScheduleCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if not db.get(Course, payload.course_id):
        raise NotFoundError("المقرر غير موجود.")
    if payload.student_id is not None:
        from app.models import Student
        if not db.get(Student, payload.student_id):
            raise NotFoundError("الطالب غير موجود.")

    schedule = Schedule(**payload.model_dump())
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    course = db.get(Course, payload.course_id)
    out = ScheduleOut.model_validate(schedule)
    out.course_code = course.code
    out.course_name = course.name
    return out


@router.delete("/schedules/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    schedule = db.get(Schedule, schedule_id)
    if schedule is None:
        raise NotFoundError("حصة الجدول غير موجودة.")
    db.delete(schedule)
    db.commit()
    return {"success": True, "message": "تم حذف الحصة."}


# ================================================================ Exams
@router.get("/exams/my")
def my_exams(db: Session = Depends(get_db), student=Depends(get_current_student)):
    exams = get_student_exams(db, student.id)
    upcoming = [e for e in exams if not e["is_past"]]
    return {"exams": exams, "upcoming_count": len(upcoming)}


@router.post("/exams", response_model=ExamOut, status_code=201)
def create_exam(payload: ExamCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    if not db.get(Course, payload.course_id):
        raise NotFoundError("المقرر غير موجود.")
    if payload.end_time <= payload.start_time:
        raise ValidationError("وقت النهاية يجب أن يكون بعد وقت البداية.")

    exam = Exam(**payload.model_dump())
    db.add(exam)
    db.commit()
    db.refresh(exam)
    course = db.get(Course, payload.course_id)
    out = ExamOut.model_validate(exam)
    out.course_code = course.code
    out.course_name = course.name
    return out


@router.delete("/exams/{exam_id}")
def delete_exam(exam_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise NotFoundError("الامتحان غير موجود.")
    db.delete(exam)
    db.commit()
    return {"success": True, "message": "تم حذف الامتحان."}
