"""
rag/extractor.py — استخراج النصوص من الملفات (PDF / DOCX / TXT / MD) + تنظيفها
"""
import io
import re

from app.utils.exceptions import ValidationError

SUPPORTED_TYPES = {".pdf": "pdf", ".docx": "docx", ".txt": "txt", ".md": "txt"}


def detect_doc_type(filename: str) -> str:
    dot = filename.rfind(".")
    ext = filename[dot:].lower() if dot != -1 else ""
    if ext not in SUPPORTED_TYPES:
        raise ValidationError(
            f"نوع الملف غير مدعوم ({ext or 'بدون امتداد'}). الأنواع المدعومة: PDF, DOCX, TXT, MD."
        )
    return SUPPORTED_TYPES[ext]


def _extract_pdf(data: bytes) -> str:
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(data))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n".join(pages)


def _extract_docx(data: bytes) -> str:
    import docx

    document = docx.Document(io.BytesIO(data))
    parts = [p.text for p in document.paragraphs]
    for table in document.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            parts.append(" | ".join(cells))
    return "\n".join(parts)


def _extract_txt(data: bytes) -> str:
    for encoding in ("utf-8", "utf-16", "cp1256"):  # cp1256 لعربي Windows القديم
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return data.decode("utf-8", errors="ignore")


def extract_text(filename: str, data: bytes) -> str:
    doc_type = detect_doc_type(filename)
    if doc_type == "pdf":
        raw = _extract_pdf(data)
    elif doc_type == "docx":
        raw = _extract_docx(data)
    else:
        raw = _extract_txt(data)

    cleaned = clean_text(raw)
    if len(cleaned.strip()) < 10:
        raise ValidationError("لم يتمكن النظام من استخراج نص كافٍ من الملف.")
    return cleaned


def clean_text(text: str) -> str:
    """تنظيف النص: توحيد المسافات والأسطر وإزالة الرموز الضارة."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    # إزالة محارف تحكم غير مرئية (تحافظ على الحروف العربية)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text.strip()
