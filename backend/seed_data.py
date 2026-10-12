"""
seed_data.py — تعبئة قاعدة البيانات ببيانات أولية واقعية
- أدمن:      admin@ust.edu / Admin@1234
- طالب دمو:  student@ust.edu / Student@1234 (الرقم الجامعي 20241056)
- كليات، أقسام، مقررات، تسجيل، نتائج، جدول، امتحانات، إشعارات، مستندات قاعدة معرفة.

الاستخدام:
    cd backend
    python seed_data.py
"""
import sys
from datetime import date, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.database.connection import SessionLocal, init_db
from app.auth.security import hash_password
from app.models import (
    ROLE_ADMIN, ROLE_STUDENT,
    Course, Department, Enrollment, Exam, Faculty,
    KnowledgeChunk, KnowledgeDocument, Notification,
    Result, Schedule, Student, User,
)
from app.rag.chunker import split_into_chunks
from app.rag.embeddings import embed_texts, encode_vector

SEMESTER = "2025-2026 الفصل الأول"


# ---------------------------------------------------------------- Knowledge base docs
KB_DOCUMENTS = [
    ("دليل التسجيل الأكاديمي", """
شروط التسجيل في المقررات بجامعة العلوم والتقانة:
يبدأ التسجيل الإلكتروني للمقررات قبل بداية الفصل الدراسي بأسبوعين، وينتهي في نهاية الأسبوع الأول من الفصل.
الحد الأدنى للساعات المسجلة في الفصل العادي هو 12 ساعة، والحد الأقصى هو 18 ساعة.
يمكن للطالب إضافة أو حذف مقرر خلال الأسبوع الأول من الفصل دون تسجيل رسمي.
بعد انتهاء مدة الإضافة والحذف، يتطلب حذف أي مقرر موافقة العمادة وعبء مالي وقد يترتب عليه تقدير W.
الطالب الذي يرغب بالتخرج مع مرتبة الشرف يجب أن يسجل 15 ساعة على الأقل كل فصل.
للتعذر عن التسجيل في الفصل، يجب تقديم طلب إجازة فصل دراسي عبر البوابة الإلكترونية قبل بداية الفصل.
"""),

    ("الرسوم الدراسية والسداد", """
الرسوم الدراسية بجامعة العلوم والتقانة:
سعر الساعة المعتمدة للطالب السوداني 5000 جنيه، وللطالب الدولي 1500 دولار.
تُقسم الرسوم إلى قسطين: القسط الأول يُسدد قبل بداية الفصل بأسبوع، والقسط الثاني قبل منتصف الفصل.
طرق السداد المتاحة: التطبيقات البنكية (بنكك، فوري)، أو الخزينة المركزية بالجامعة.
يُمنع الطالب من دخول قاعة الامتحان إذا لم يسدد على الأقل 75% من رسوم الفصل.
المنح والخصومات: خصم 20% لأخوة الطلاب، وخصم 15% لمن يحافظ على معدل تراكمي 3.5 فأعلى.
تُمنح إعفاءات كاملة للطلاب المتفوقين في الثانوية العامة (نسبة 95% فأكثر) للفصل الأول فقط.
"""),

    ("التقويم الأكاديمي", """
التقويم الأكاديمي للعام الجامعي:
يبدأ الفصل الدراسي الأول في منتصف شهر سبتمبر وينتهي الامتحانات النهائية في نهاية ديسمبر.
عطلة نهاية الفصل الأول تمتد أسبوعين في يناير.
يبدأ الفصل الثاني في منتصف يناير وتنتهي امتحاناته في منتصف مايو.
العطلات الرسمية: عيد الاستقلال (1 يناير)، عيد الفطر أسبوع، عيد الأضحى أسبوع، عيد الميلاد (25 ديسمبر)،
والذكرى السنوية للثورة (30 يونيو).
تُنشر مواعيد الامتحانات النهائية الرسمية قبل شهر من بدء الامتحانات عبر الموقع الرسمي ولوحة الإعلانات.
"""),

    ("دليل القبول والانتساب", """
شروط القبول بجامعة العلوم والتقانة:
الشهادة المطلوبة: الشهادة السودانية أو ما يعادلها (النجمة، IGCSE، أو غيرها).
الحد الأدنى لقبول كلية الحاسبات وتقانة المعلومات: 60% علمي.
الحد الأدنى لقبول كلية الهندسة: 65% علمي.
الحد الأدنى لقبول كلية الطب: 85% علمي.
المستندات المطلوبة: الشهادة الأصلية، شهادة الميلاد، الصور الشخصية، خطاب حسن السير والسلوك.
يبدأ التقديم للفصل الأول في يوليو وينتهي في منتصف سبتمبر.
يُقبل الطلاب الدوليون عبر مكتب العلاقات الدولية مع شهادة إتقان الإنجليزية IELTS 5.5 فأعلى.
"""),

    ("الأسئلة الشائعة FAQ", """
الأسئلة الشائعة:
س: كيف أستخرج كشف درجات؟ ج: عبر مكتب شؤون الطلاب بعد تقديم طلب وسداد الرسوم، ويصدر خلال ثلاثة أيام عمل.
س: كيف أستخرج إفادة تخرج؟ ج: بتقديم طلب لمكتب شؤون الطلاب مع إرفاق خلو الطرف وإيصال السداد النهائي.
س: هل يوجد سكن جامعي؟ ج: نعم، يتوفر سكن طلابي بتكلفة رمزية، والتقديم في أول أسبوعين من العام الجامعي.
س: كيف أتحول بين التخصصات؟ ج: بنهاية السنة الأولى فقط وبشرط تحقيق معدل 3.0 فأعلى وتوفر مقاعد بالتخصص المقصود.
س: ما هي سياسة الانصراف؟ ج: يُحرم الطالب من دخول الامتحان إذا تجاوز غيابه 25% من محاضرات المقرر.
س: هل توفر الجامعة نقلًا جامعيًا؟ ج: نعم، خطوط نقل مجدولة بتكلفة رمزية تشمل المسارات الرئيسية للمدينة.
"""),
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        # منع التكرار
        if db.query(User).filter(User.email == "admin@ust.edu").first():
            print("Database already seeded — skipping. (delete ust_dev.db to reseed)")
            return

        print("Seeding database...")

        # ---------------- الكليات والأقسام
        cs_faculty = Faculty(name="كلية الحاسبات وتقانة المعلومات")
        eng_faculty = Faculty(name="كلية الهندسة")
        db.add_all([cs_faculty, eng_faculty])
        db.flush()

        cs_dept = Department(name="قسم علوم الحاسب", faculty_id=cs_faculty.id)
        it_dept = Department(name="قسم تقانة المعلومات", faculty_id=cs_faculty.id)
        se_dept = Department(name="قسم الهندسة المدنية", faculty_id=eng_faculty.id)
        db.add_all([cs_dept, it_dept, se_dept])
        db.flush()

        # ---------------- المستخدمون
        admin = User(
            email="admin@ust.edu",
            password_hash=hash_password("Admin@1234"),
            full_name="مدير النظام",
            role=ROLE_ADMIN,
        )
        demo_user = User(
            email="student@ust.edu",
            password_hash=hash_password("Student@1234"),
            full_name="محمد أحمد عبدالله",
            role=ROLE_STUDENT,
        )
        db.add_all([admin, demo_user])
        db.flush()

        demo_student = Student(
            user_id=demo_user.id,
            university_id="20241056",
            faculty_id=cs_faculty.id,
            department_id=cs_dept.id,
            level=2,
            phone="0912345678",
            enrollment_year=2024,
        )
        db.add(demo_student)
        db.flush()

        # ---------------- المقررات
        courses = [
            Course(code="CS201", name="البرمجة الشيئية Java", credit_hours=4, department_id=cs_dept.id,
                   description="مبادئ البرمجة الكائنية بلغة Java"),
            Course(code="CS210", name="هياكل البيانات", credit_hours=3, department_id=cs_dept.id,
                   description="القوائم والأشجار والرسوم البيانية"),
            Course(code="IT205", name="قواعد البيانات", credit_hours=3, department_id=it_dept.id,
                   description="تصميم قواعد البيانات العلائقية و SQL"),
            Course(code="CS220", name="الرياضيات المتقطعة", credit_hours=3, department_id=cs_dept.id),
        ]
        db.add_all(courses)
        db.flush()

        # ---------------- تسجيل الطالب في المقررات
        for course in courses:
            db.add(Enrollment(student_id=demo_student.id, course_id=course.id, semester=SEMESTER))

        # ---------------- النتائج (فصل سابق)
        prev_semester = "2024-2025 الفصل الثاني"
        results_data = [
            (courses[0], 92.0), (courses[1], 78.5), (courses[2], 85.0),
        ]
        for course, total in results_data:
            grade, points = ("A", 4.0) if total >= 80 else (("B", 3.0) if total >= 70 else ("C", 2.0))
            db.add(Result(
                student_id=demo_student.id, course_id=course.id, semester=prev_semester,
                midterm=total * 0.4, final_exam=total * 0.6, total=total, grade=grade, gpa_points=points,
            ))

        # نتيجة فصل حالي لمادة Java (لتجربة سؤال "ما نتيجتي في Java؟")
        db.add(Result(
            student_id=demo_student.id, course_id=courses[0].id, semester=SEMESTER,
            midterm=45.0, final_exam=41.0, practical=8.0, total=94.0, grade="A+", gpa_points=4.0,
        ))

        # ---------------- الجدول
        schedule_rows = [
            Schedule(student_id=None, course_id=courses[0].id, day_of_week=0, start_time=time(9, 0), end_time=time(10, 30), room="قاعة 101", lecturer="د. أحمد سعيد", semester=SEMESTER),
            Schedule(student_id=None, course_id=courses[1].id, day_of_week=0, start_time=time(11, 0), end_time=time(12, 30), room="قاعة 205", lecturer="د. سماء عثمان", semester=SEMESTER),
            Schedule(student_id=None, course_id=courses[2].id, day_of_week=1, start_time=time(9, 0), end_time=time(10, 30), room="مختبر 3", lecturer="د. منى حسن", semester=SEMESTER),
            Schedule(student_id=None, course_id=courses[3].id, day_of_week=2, start_time=time(10, 0), end_time=time(11, 30), room="قاعة 110", lecturer="د. خالد يوسف", semester=SEMESTER),
        ]
        db.add_all(schedule_rows)

        # ---------------- الامتحانات
        from datetime import timedelta
        today = date.today()
        db.add_all([
            Exam(course_id=courses[1].id, title="امتحان منتصف الفصل", exam_date=today + timedelta(days=7), start_time=time(9, 0), end_time=time(11, 0), room="قاعة 205", semester=SEMESTER),
            Exam(course_id=courses[0].id, title="امتحان منتصف الفصل", exam_date=today + timedelta(days=10), start_time=time(12, 0), end_time=time(14, 0), room="قاعة 101", semester=SEMESTER),
            Exam(course_id=courses[2].id, title="امتحان عملي", exam_date=today + timedelta(days=14), start_time=time(9, 0), end_time=time(11, 0), room="مختبر 3", semester=SEMESTER),
        ])

        # ---------------- الإشعارات
        db.add_all([
            Notification(user_id=None, title="بدء فترة الإضافة والحذف", body="تبدأ فترة الإضافة والحذف للمقررات من الأحد القادم وتستمر أسبوعًا واحدًا فقط."),
            Notification(user_id=demo_user.id, title="تنبيه سداد", body="يرجى سداد القسط الثاني قبل نهاية الشهر لتجنب الحرمان من الامتحانات."),
        ])

        # ---------------- قاعدة المعرفة
        for title, body in KB_DOCUMENTS:
            document = KnowledgeDocument(
                title=title, filename=f"seed_{title[:12]}.txt", doc_type="txt",
                size_bytes=len(body.encode("utf-8")), uploaded_by=admin.id,
            )
            db.add(document)
            db.flush()

            chunks = split_into_chunks(body)
            vectors = embed_texts(chunks)
            for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
                db.add(KnowledgeChunk(
                    document_id=document.id, chunk_index=index,
                    content=chunk, embedding=encode_vector(vector),
                ))
            document.chunk_count = len(chunks)

        db.commit()
        print("Seed completed successfully!")
        print("  Admin login : admin@ust.edu / Admin@1234")
        print("  Student     : student@ust.edu / Student@1234 (uni id 20241056)")
        print(f"  KB documents: {len(KB_DOCUMENTS)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
