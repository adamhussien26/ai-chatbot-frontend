"""
schemas/academic.py — مخططات الطلاب والمقررات والنتائج والجداول والامتحانات والإشعارات
"""
from datetime import date, datetime, time

from pydantic import BaseModel, Field


# ---------------------------------------------------------------- Students
class StudentCreate(BaseModel):
    full_name: str = Field(min_length=3, max_length=190)
    email: str
    password: str = Field(min_length=8, max_length=128)
    university_id: str = Field(min_length=3, max_length=20)
    faculty_id: int | None = None
    department_id: int | None = None
    level: int | None = Field(default=None, ge=1, le=7)
    phone: str | None = Field(default=None, max_length=30)


class StudentUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=3, max_length=190)
    faculty_id: int | None = None
    department_id: int | None = None
    level: int | None = Field(default=None, ge=1, le=7)
    phone: str | None = Field(default=None, max_length=30)
    avatar_url: str | None = Field(default=None, max_length=500)


class StudentOut(BaseModel):
    id: int
    user_id: int
    university_id: str
    full_name: str
    email: str
    faculty_id: int | None
    department_id: int | None
    faculty_name: str | None = None
    department_name: str | None = None
    level: int | None
    phone: str | None
    avatar_url: str | None
    enrollment_year: int | None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------- Courses
class CourseCreate(BaseModel):
    code: str = Field(min_length=2, max_length=20)
    name: str = Field(min_length=2, max_length=190)
    credit_hours: int = Field(default=3, ge=1, le=6)
    description: str | None = None
    department_id: int | None = None


class CourseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=190)
    credit_hours: int | None = Field(default=None, ge=1, le=6)
    description: str | None = None
    department_id: int | None = None


class CourseOut(BaseModel):
    id: int
    code: str
    name: str
    credit_hours: int
    description: str | None

    model_config = {"from_attributes": True}


class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
    semester: str = Field(min_length=3, max_length=30)


# ---------------------------------------------------------------- Results
class ResultCreate(BaseModel):
    student_id: int
    course_id: int
    semester: str = Field(min_length=3, max_length=30)
    midterm: float | None = Field(default=None, ge=0, le=100)
    final_exam: float | None = Field(default=None, ge=0, le=100)
    practical: float | None = Field(default=None, ge=0, le=100)
    total: float = Field(ge=0, le=100)


class ResultUpdate(BaseModel):
    midterm: float | None = Field(default=None, ge=0, le=100)
    final_exam: float | None = Field(default=None, ge=0, le=100)
    practical: float | None = Field(default=None, ge=0, le=100)
    total: float | None = Field(default=None, ge=0, le=100)


class ResultOut(BaseModel):
    id: int
    course_id: int
    course_code: str | None = None
    course_name: str | None = None
    semester: str
    midterm: float | None
    final_exam: float | None
    practical: float | None
    total: float
    grade: str
    gpa_points: float

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------- Schedules
class ScheduleCreate(BaseModel):
    student_id: int | None = None
    course_id: int
    day_of_week: int = Field(ge=0, le=6)
    start_time: time
    end_time: time
    room: str | None = Field(default=None, max_length=60)
    lecturer: str | None = Field(default=None, max_length=190)
    semester: str = Field(min_length=3, max_length=30)


class ScheduleOut(BaseModel):
    id: int
    course_id: int
    course_code: str | None = None
    course_name: str | None = None
    day_of_week: int
    start_time: time
    end_time: time
    room: str | None
    lecturer: str | None
    semester: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------- Exams
class ExamCreate(BaseModel):
    course_id: int
    title: str = Field(min_length=2, max_length=190)
    exam_date: date
    start_time: time
    end_time: time
    room: str | None = Field(default=None, max_length=60)
    semester: str = Field(min_length=3, max_length=30)


class ExamOut(BaseModel):
    id: int
    course_id: int
    course_code: str | None = None
    course_name: str | None = None
    title: str
    exam_date: date
    start_time: time
    end_time: time
    room: str | None
    semester: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------- Notifications
class NotificationCreate(BaseModel):
    user_id: int | None = None   # None = بث عام
    title: str = Field(min_length=2, max_length=190)
    body: str = Field(min_length=2)


class NotificationOut(BaseModel):
    id: int
    user_id: int | None
    title: str
    body: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------- Faculties / Departments
class FacultyOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class DepartmentOut(BaseModel):
    id: int
    name: str
    faculty_id: int

    model_config = {"from_attributes": True}
