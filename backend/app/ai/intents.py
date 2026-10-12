"""
ai/intents.py — تحليل السؤال: كشف النية (Intent Detection) + استخراج الكيانات (Entity Extraction)
يعتمد على قواعد لغوية عربية سريعة ومحددة (بدون LLM) لضمان الدقة والسرعة،
ويُستخدم LLM فقط كطبقة ثانوية اختيارية للنوايا الغامضة.

أولويات التوجيه:
1. كلمات شخصية مملوكة (نتيجتي، موادي، جدولي...) → قاعدة البيانات
2. كلمات معلومات رسمية (تسجيل، رسوم، شروط...) → RAG / قاعدة المعرفة
3. غير ذلك (مفاهيم عامة) → LLM
"""
import re
from dataclasses import dataclass, field


# ---------------------------------------------------------------- النوايا المدعومة
INTENT_RESULTS = "results"            # ما نتيجتي / درجاتي
INTENT_GPA = "gpa"                    # معدلي / GPA
INTENT_COURSES = "courses"            # ما موادي / مقرراتي
INTENT_SCHEDULE = "schedule"          # ما جدولي / محاضراتي
INTENT_EXAMS = "exams"                # مواعيد امتحاناتي
INTENT_NOTIFICATIONS = "notifications"  # إشعاراتي
INTENT_STUDENT_INFO = "student_info"  # رقم الطالب / بياناتي الشخصية
INTENT_UNIVERSITY_INFO = "university_info"  # معلومات رسمية → RAG
INTENT_GENERAL = "general"            # مفاهيم ومعرفة عامة → LLM

# النوايا التي تُجاب حصرًا من قاعدة البيانات (لا LLM ولا تخمين)
DATABASE_INTENTS = {
    INTENT_RESULTS, INTENT_GPA, INTENT_COURSES,
    INTENT_SCHEDULE, INTENT_EXAMS, INTENT_NOTIFICATIONS, INTENT_STUDENT_INFO,
}

# ---------------------------------------------------------------- 1) كلمات شخصية (أولوية قصوى)
# كل نية مع كلماتها الشخصية (صيغ الملكية/الضمير)
_PERSONAL_INTENT_KEYWORDS: list[tuple[str, list[str]]] = [
    (INTENT_GPA, ["معدلي", "معدل التراكمي", "المعدل التراكمي", "المعدل", "معدل", "gpa"]),
    (INTENT_RESULTS, ["نتيجتي", "نتائجي", "نتيجت", "نتيجة", "نتائج", "درجاتي", "درجتي", "درجات",
                      "علاماتي", "علامتي", "علامات", "كشف الدرجات", "كشف درجاتي"]),
    (INTENT_SCHEDULE, ["جدولي", "جدول محاضراتي", "جدولي هذا", "محاضراتي", "جدول", "محاضرات", "محاضرة"]),
    (INTENT_EXAMS, ["امتحاناتي", "اختباراتي", "امتحانات", "امتحان", "اختبار", "اختبارات", "نهائي"]),
    (INTENT_NOTIFICATIONS, ["إشعاراتي", "اشعاراتي", "إشعارات", "اشعارات", "إشعار", "اشعار", "تنبيهاتي", "تنبيه"]),
    (INTENT_STUDENT_INFO, ["رقمي الجامعي", "رقم الطالب", "الرقم الجامعي", "رقمي", "بياناتي", "ملفي", "معلوماتي"]),
    (INTENT_COURSES, ["موادي", "مقرراتي", "ساعاتي", "مواد هذا الفصل", "مقررات هذا الفصل", "مواد", "مقررات", "ساعة معتمدة"]),
]

# ---------------------------------------------------------------- 2) كلمات معلومات رسمية (RAG)
_UNIVERSITY_KEYWORDS: list[tuple[str, int]] = [
    ("تسجيل", 2), ("التسجيل", 2), ("شروط", 2), ("شروط القبول", 3), ("القبول", 2), ("قبول", 2),
    ("الرسوم", 2), ("رسوم", 2), ("سداد", 2), ("قسط", 2), ("منح", 1), ("خصم", 1),
    ("شهادة", 2), ("شهادات", 2), ("إفادة", 2), ("افادة", 2), ("كشف درجات", 2),
    ("التقويم", 2), ("تقويم", 2), ("عطلة", 1), ("إجازة", 1), ("اجازة", 1),
    ("لوائح", 2), ("لائحة", 2), ("أنظمة", 2), ("انظمة", 2), ("انسحاب", 2), ("التحويل", 2),
    ("تقديم", 1), ("معاملة", 1), ("سكن", 2), ("نقل جامعي", 2), ("مكتبة", 1),
    ("العام الجامعي", 1), ("الفصل الدراسي", 1), ("الترم", 1), ("الحرم", 1),
]

# ---------------------------------------------------------------- كيانات
_COURSE_EXTRACT_PATTERNS = [
    re.compile(r"(?:في|بمادة|مادة|من)\s+(?:مادة\s+)?([A-Za-z\u0600-\u06FF][A-Za-z\u0600-\u06FF\s\d]{1,40}?)(?:\s*(?:\?|؟|$|،|,))"),
    re.compile(r"نتيجتي\s+(?:في\s+)?(?:مادة\s+)?([A-Za-z\u0600-\u06FF][A-Za-z\u0600-\u06FF\s\d]{1,40}?)(?:\s*(?:\?|؟|$|،|,))"),
]
_CODE_PATTERN = re.compile(r"\b([A-Z]{2,4}\s?\d{3,4})\b", re.IGNORECASE)

_STOPWORDS = {"في", "من", "على", "عن", "ما", "اي", "أي", "هو", "هي", "المادة", "مادة", "كل", "عند", "هذا", "هذه"}


@dataclass
class QuestionAnalysis:
    """نتيجة تحليل السؤال."""
    raw: str
    intent: str
    is_personal: bool = False          # هل تُجاب من قاعدة البيانات؟
    entities: dict = field(default_factory=dict)  # course_hint, course_code, semester_part


def detect_intent(question: str) -> str:
    q = question.lower().strip()

    # ---- 1) الكلمات الشخصية أولاً (صيغ الملكية)
    personal_score = 0
    intent_scores: dict[str, int] = {}
    for intent, keywords in _PERSONAL_INTENT_KEYWORDS:
        score = sum(1 for kw in keywords if kw in q)
        if score > 0:
            intent_scores[intent] = score
            personal_score += score

    # ---- 2) كلمات المعلومات الرسمية
    university_score = sum(weight for kw, weight in _UNIVERSITY_KEYWORDS if kw in q)

    # ---- القرار
    if intent_scores and personal_score >= university_score:
        # أعد النية الأكثر تحديدًا (أعلى كلمات مطابقة، مع تفضيل الأكثر خصوصية)
        return max(intent_scores.items(), key=lambda kv: kv[1])[0]

    if university_score > 0:
        return INTENT_UNIVERSITY_INFO

    if intent_scores:
        return max(intent_scores.items(), key=lambda kv: kv[1])[0]

    return INTENT_GENERAL


def extract_entities(question: str) -> dict:
    entities: dict = {}

    # كود مقرر صريح مثل CS201 أو "cs 201"
    code_match = _CODE_PATTERN.search(question)
    if code_match:
        entities["course_code"] = code_match.group(1).replace(" ", "").upper()

    # اسم مقرر بعد أدوات الربط
    for pattern in _COURSE_EXTRACT_PATTERNS:
        match = pattern.search(question)
        if match:
            candidate = match.group(1).strip()
            words = [w for w in candidate.split() if w.lower() not in _STOPWORDS and len(w) > 1]
            if words:
                entities["course_hint"] = " ".join(words)
            break

    # فصل دراسي إن ذُكر
    semester_match = re.search(r"(فصل\s+)?(الأول|الثاني|الصيف|اول|ثاني)", question)
    if semester_match:
        part = semester_match.group(2)
        mapping = {"الأول": "الأول", "اول": "الأول", "الثاني": "الثاني", "ثاني": "الثاني", "الصيف": "الصيف"}
        entities["semester_part"] = mapping.get(part, part)

    return entities


def analyze_question(question: str) -> QuestionAnalysis:
    """تحليل كامل للسؤال: نية + كيانات + هل هو شخصي (DB)؟"""
    intent = detect_intent(question)
    entities = extract_entities(question)

    is_personal = intent in DATABASE_INTENTS
    return QuestionAnalysis(raw=question, intent=intent, is_personal=is_personal, entities=entities)
