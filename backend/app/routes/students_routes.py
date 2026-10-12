"""
routes/students_routes.py — ملف الطالب (للطالب نفسه + إدارة للأدمن)
ضمانة الخصوصية: الطالب لا يرى إلا ملفه؛ الأدمن يرى الجميع.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_student, get_current_user, require_admin
from app.database.connection import get_db
from app.models import ROLE_STUDENT, Faculty, Student, User
from app.schemas.academic import StudentCreate, StudentOut, StudentUpdate
from app.services.academic_service import get_student_profile
from app.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/students", tags=["Students"])


# ---------------------------------------------------------------- Student: ملفي
@router.get("/me")
def my_profile(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """ملف الطالب الحالي (أو ملف الأدمن الأساسي إن لم يكن طالبًا)."""
    profile = get_student_profile(db, user.id)
    if profile is None:
        # حساب أدمن بدون ملف طالب — نعيد بيانات المستخدم الأساسية
        return {
            "id": None,
            "user_id": user.id,
            "university_id": None,
            "full_name": user.full_name,
            "email": user.email,
            "faculty_id": None,
            "faculty_name": None,
            "department_id": None,
            "department_name": None,
            "level": None,
            "phone": None,
            "avatar_url": None,
            "enrollment_year": None,
            "role": user.role,
        }
    return profile


@router.put("/me")
def update_my_profile(
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    student: Student = Depends(get_current_student),
):
    """تحديث بيانات الطالب لنفسه (حقول محدودة)."""
    allowed = {"phone", "avatar_url"}
    data = payload.model_dump(exclude_unset=True)

    if "phone" in data and data["phone"] is not None:
        student.phone = data["phone"]
    if "avatar_url" in data:
        student.avatar_url = data["avatar_url"]
    if "level" in data and data["level"] is not None:
        student.level = data["level"]

    db.commit()
    return {"success": True, "message": "تم تحديث الملف الشخصي."}


# ---------------------------------------------------------------- Admin: إدارة الطلاب
@router.get("/meta/faculties")
def faculties(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    faculties = db.query(Faculty).all()
    return [
        {"id": f.id, "name": f.name, "departments": [{"id": d.id, "name": d.name} for d in f.departments]}
        for f in faculties
    ]


@router.get("", response_model=list[StudentOut])
def list_students(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    students = db.query(Student).all()
    return [StudentOut(**get_student_profile(db, s.user_id)) for s in students]


@router.post("", response_model=StudentOut, status_code=201)
def create_student(payload: StudentCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    from app.auth.security import hash_password

    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise ValidationError("البريد الإلكتروني مستخدم بالفعل.")
    if db.query(Student).filter(Student.university_id == payload.university_id).first():
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
        phone=payload.phone,
    )
    db.add(student)
    db.commit()
    return StudentOut(**get_student_profile(db, user.id))


@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    الوصول لملف طالب:
    - الطالب يرى ملفه فقط (أي معرف آخر → 403).
    - الأدمن يرى الجميع.
    """
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError("الطالب غير موجود.")

    if not user.is_admin:
        own = db.query(Student).filter(Student.user_id == user.id, Student.id == student_id).first()
        if own is None:
            raise NotFoundError("لا تملك صلاحية الاطلاع على ملف هذا الطالب.")

    return get_student_profile(db, student.user_id)


@router.put("/{student_id}")
def update_student(
    student_id: int,
    payload: StudentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError("الطالب غير موجود.")

    data = payload.model_dump(exclude_unset=True)
    if "full_name" in data and data["full_name"]:
        student.user.full_name = data["full_name"].strip()
    for field in ("faculty_id", "department_id", "level", "phone", "avatar_url"):
        if field in data:
            setattr(student, field, data[field])

    db.commit()
    return {"success": True, "message": "تم تحديث بيانات الطالب."}


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    student = db.get(Student, student_id)
    if student is None:
        raise NotFoundError("الطالب غير موجود.")

    user = student.user
    db.delete(student)
    db.delete(user)  # ON DELETE CASCADE يحذف السجلات المرتبطة
    db.commit()
    return {"success": True, "message": "تم حذف الطالب وجميع بياناته."}
