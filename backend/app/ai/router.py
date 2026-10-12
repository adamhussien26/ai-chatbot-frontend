"""
ai/router.py — موجّه الأسئلة (Question Router) وخط المعالجة الكامل

User Question
→ Question Processing (analyze_question)
→ Intent Detection + Entity Extraction
→ تحديد المصدر: DATABASE / RAG / LLM
→ Generate Response
→ ChatAnswer (answer, source, source_ref, intent)

قاعدة صارمة: أسئلة بيانات الطلاب تُجاب من قاعدة البيانات فقط ولا يلمسها الـ LLM.
"""
import logging

from sqlalchemy.orm import Session

from app.ai import intents as intent_module
from app.ai.intents import (
    DATABASE_INTENTS,
    INTENT_COURSES,
    INTENT_EXAMS,
    INTENT_GENERAL,
    INTENT_GPA,
    INTENT_NOTIFICATIONS,
    INTENT_RESULTS,
    INTENT_SCHEDULE,
    INTENT_STUDENT_INFO,
    INTENT_UNIVERSITY_INFO,
    analyze_question,
)
from app.ai.llm_client import (
    LLM_OFFLINE_MESSAGE,
    NO_INFO_MESSAGE,
    chat_completion,
    is_llm_available,
)
from app.ai.prompts import GENERAL_PROMPT, RAG_ANSWER_PROMPT
from app.rag.retriever import best_score, build_context, is_reliable, retrieve
from app.services.academic_service import (
    find_course_by_hint,
    get_student_courses,
    get_student_exams,
    get_student_gpa,
    get_student_profile,
    get_student_results,
    get_student_schedule,
    get_user_notifications,
)

logger = logging.getLogger("ust.router")

# أسئلة تعريفية/مفاهيمية → LLM مباشرة دون المرور على RAG
_DEFINITIONAL_PREFIXES = (
    "ما هو مفهوم", "ما هي مفهوم", "مفهوم", "تعريف", "ما تعريف", "شرح", "اشرح",
    "فرق بين", "ما الفرق", "كيف تعمل", "أمثلة على", "امثلة على",
)


def is_definitional(question: str) -> bool:
    q = question.strip()
    return any(q.startswith(p) or p in q[:30] for p in _DEFINITIONAL_PREFIXES)


# ================================================================ DATABASE answers
def _format_results(results: list[dict], course_hint: str | None, db, student_id: int) -> str:
    if course_hint:
        course = find_course_by_hint(db, course_hint)
        if course:
            filtered = [r for r in results if r["course_id"] == course.id or r["course_code"] == course.code]
            if filtered:
                r = filtered[0]
                return (
                    f"نتيجتك في مقرر {r['course_name']} ({r['course_code']}) لفصل {r['semester']}:\n"
                    f"- الدرجة الكلية: {r['total']}\n"
                    f"- التقدير: {r['grade']}"
                )
            return f"لم أجد نتيجة مسجلة لك في مقرر مطابق لـ «{course_hint}» حتى الآن."

    if not results:
        return "لا توجد نتائج مسجلة لك حتى الآن. ستظهر نتائجك هنا فور اعتمادها من العمادة."

    lines = ["نتائجك المسجلة:"]
    for r in results[:10]:
        lines.append(f"- {r['course_name']} ({r['course_code']}): {r['total']} — تقدير {r['grade']} ({r['semester']})")

    gpa_info = get_student_gpa(db, student_id)
    if gpa_info["gpa"] is not None:
        lines.append(f"\nمعدلك التراكمي الحالي: {gpa_info['gpa']} من 4.00")
    return "\n".join(lines)


def _format_courses(courses: list[dict]) -> str:
    if not courses:
        return "أنت غير مسجل في أي مقررات حاليًا."
    lines = [f"أنت مسجل في {len(courses)} مقررات:"]
    total_credits = 0
    for c in courses:
        lines.append(f"- {c['name']} ({c['code']}) — {c['credit_hours']} ساعة ({c['semester']})")
        total_credits += c["credit_hours"]
    lines.append(f"\nإجمالي الساعات المسجلة: {total_credits} ساعة.")
    return "\n".join(lines)


def _format_schedule(schedule: list[dict]) -> str:
    if not schedule:
        return "لا يوجد جدول محاضرات مسجل لك في هذا الفصل."
    lines = ["جدول محاضراتك:"]
    current_day = None
    for item in schedule:
        if item["day"] != current_day:
            current_day = item["day"]
            lines.append(f"\n{current_day}:")
        lines.append(
            f"- {item['course_name']} ({item['course_code']}) | {item['start_time']}-{item['end_time']}"
            + (f" | {item['room']}" if item["room"] else "")
        )
    return "\n".join(lines)


def _format_exams(exams: list[dict]) -> str:
    upcoming = [e for e in exams if not e["is_past"]]
    if not upcoming:
        return "لا توجد امتحانات قادمة مسجلة لمقرراتك حاليًا."
    if len(upcoming) == 1:
        header = "لديك امتحان واحد قادم:"
    elif len(upcoming) == 2:
        header = "لديك امتحانان قادمان:"
    else:
        header = f"لديك {len(upcoming)} امتحانات قادمة:"
    lines = [header]
    for e in upcoming[:10]:
        days = f" (بعد {e['days_left']} يوم)" if e["days_left"] >= 0 else ""
        lines.append(
            f"- {e['course_name']} ({e['course_code']}): {e['title']} يوم {e['exam_date']} الساعة {e['start_time']}"
            + (f" في قاعة {e['room']}" if e["room"] else "")
            + days
        )
    return "\n".join(lines)


def _format_notifications(notifications) -> str:
    if not notifications:
        return "لا توجد إشعارات جديدة لديك حاليًا."
    lines = [f"أحدث {min(len(notifications), 5)} إشعارات:"]
    for n in notifications[:5]:
        lines.append(f"- {n.title}: {n.body[:120]}")
    return "\n".join(lines)


def _format_student_info(profile: dict | None) -> str:
    if profile is None or profile.get("university_id") is None:
        return "لا يوجد ملف طالب مرتبط بحسابك."
    lines = ["بياناتك الجامعية:"]
    lines.append(f"- الاسم: {profile['full_name']}")
    lines.append(f"- الرقم الجامعي: {profile['university_id']}")
    lines.append(f"- البريد: {profile['email']}")
    if profile.get("faculty_name"):
        lines.append(f"- الكلية: {profile['faculty_name']}")
    if profile.get("department_name"):
        lines.append(f"- القسم: {profile['department_name']}")
    if profile.get("level"):
        lines.append(f"- المستوى: {profile['level']}")
    return "\n".join(lines)


def answer_from_database(db: Session, analysis, student_id: int, user_id: int) -> tuple[str, str]:
    """إجابة حتمية من قاعدة البيانات — بلا تخمين وبلا LLM."""
    intent = analysis.intent
    course_hint = analysis.entities.get("course_hint")

    if intent == INTENT_RESULTS:
        results = get_student_results(db, student_id)
        return _format_results(results, course_hint, db, student_id), "results"

    if intent == INTENT_GPA:
        gpa_info = get_student_gpa(db, student_id)
        if gpa_info["gpa"] is None:
            return "لا يمكن حساب معدلك التراكمي لأنه لا توجد نتائج معتمدة لك بعد.", "gpa"
        return (
            f"معدلك التراكمي الحالي هو {gpa_info['gpa']} من 4.00، "
            f"مسجل في {gpa_info['courses_count']} مقررات بإجمالي {gpa_info['credits_earned']} ساعة معتمدة."
        ), "gpa"

    if intent == INTENT_COURSES:
        courses = get_student_courses(db, student_id)
        if course_hint:
            course = find_course_by_hint(db, course_hint)
            if course:
                mine = [c for c in courses if c["id"] == course.id]
                if mine:
                    c = mine[0]
                    return (f"نعم، أنت مسجل في مقرر {c['name']} ({c['code']}) — {c['credit_hours']} ساعة ({c['semester']})."), "courses"
                return f"أنت غير مسجل في مقرر مطابق لـ «{course_hint}» هذا الفصل.", "courses"
        return _format_courses(courses), "courses"

    if intent == INTENT_SCHEDULE:
        return _format_schedule(get_student_schedule(db, student_id)), "schedule"

    if intent == INTENT_EXAMS:
        return _format_exams(get_student_exams(db, student_id)), "exams"

    if intent == INTENT_NOTIFICATIONS:
        return _format_notifications(get_user_notifications(db, user_id)), "notifications"

    if intent == INTENT_STUDENT_INFO:
        return _format_student_info(get_student_profile(db, user_id)), "student_info"

    return NO_INFO_MESSAGE, "unknown"


# ================================================================ RAG answer
def answer_from_rag(db: Session, question: str) -> tuple[str | None, str | None, float]:
    """
    يحاول الإجابة من قاعدة المعرفة.
    يعيد (answer, document_title, best_score) — answer=None إن لم يجد شيئًا موثوقًا.
    """
    hits = retrieve(db, question)
    score = best_score(hits)

    if not hits or not is_reliable(hits):
        return None, None, score

    title = hits[0]["document_title"]

    if is_llm_available():
        context = build_context(hits)
        llm_answer = chat_completion(question, system_extra=RAG_ANSWER_PROMPT, context=context)
        if llm_answer:
            return llm_answer, title, score

    # وضع Offline: إجابة استخلاصية حرفية من المستندات (بدون اختراع)
    top = hits[0]["content"].strip()
    extra = f"\n\nمعلومات إضافية: {hits[1]['content'].strip()}" if len(hits) > 1 and hits[1]["score"] > score * 0.9 else ""
    return f"وفق المصادر الرسمية للجامعة ({title}):\n{top}{extra}", title, score


# ================================================================ General (LLM)
def answer_general(question: str) -> str:
    """أسئلة المفاهيم العامة — LLM فقط دون أي ادعاء بمعرفة بيانات الجامعة."""
    if is_llm_available():
        llm_answer = chat_completion(question, system_extra=GENERAL_PROMPT)
        if llm_answer:
            return llm_answer
        return "حدث خطأ أثناء الاتصال بخدمة النموذج اللغوي. حاول مرة أخرى بعد قليل."
    return LLM_OFFLINE_MESSAGE


# ================================================================ Pipeline الكامل
def process_question(db: Session, question: str, student_id: int | None, user_id: int) -> dict:
    """
    خط معالجة السؤال الكامل مع معالجة أخطاء محكمة:
    أي فشل داخلي في RAG/LLM لا يُسقط النظام بل يُجاب برسالة واضحة.
    """
    analysis = analyze_question(question)

    # 1) نية شخصية → قاعدة البيانات حصريًا
    if analysis.is_personal and student_id is not None:
        try:
            answer, ref = answer_from_database(db, analysis, student_id, user_id)
            return {"answer": answer, "source": "database", "source_ref": ref, "intent": analysis.intent}
        except Exception as exc:
            logger.exception("Database answer failed: %s", exc)
            return {
                "answer": "حدث خطأ أثناء الوصول إلى بياناتك من قاعدة البيانات. حاول مرة أخرى بعد قليل.",
                "source": "database", "source_ref": "error", "intent": analysis.intent,
            }

    if analysis.is_personal and student_id is None:
        return {
            "answer": "هذه الخدمة متاحة لحسابات الطلاب المسجلين فقط. إن كنت طالبًا فأكمل ملفك الشخصي أو تواصل مع الإدارة.",
            "source": "database", "source_ref": "no_student", "intent": analysis.intent,
        }

    # 2) مفاهيم عامة (تعريف/شرح) → LLM مباشرة
    if is_definitional(question):
        answer = answer_general(question)
        return {"answer": answer, "source": "llm", "source_ref": None, "intent": analysis.intent}

    # 3) معلومات جامعية → RAG (قاعدة المعرفة)
    try:
        rag_answer, doc_title, score = answer_from_rag(db, question)
        if rag_answer:
            return {"answer": rag_answer, "source": "rag", "source_ref": doc_title, "intent": analysis.intent}
    except Exception as exc:
        logger.exception("RAG answer failed: %s", exc)

    # 4) لم يوجد شيء موثوق → LLM (أو رسالة الاعتذار)
    answer = answer_general(question)
    source = "llm" if is_llm_available() else "llm_offline"
    return {"answer": answer, "source": source, "source_ref": None, "intent": analysis.intent}
