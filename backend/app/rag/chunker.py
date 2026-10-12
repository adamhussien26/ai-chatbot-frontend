"""
rag/chunker.py — تقسيم النص إلى مقاطع (Chunks) مناسبة للاسترجاع
تقسيم بالفقرات أولًا ثم دمج حتى الطول الأقصى مع تداخل بسيط.
"""
CHUNK_SIZE = 800       # الحرف الأقصى للمقطع
CHUNK_OVERLAP = 120    # التداخل بين المقاطع


def split_into_chunks(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    if not text or not text.strip():
        return []

    # تقسيم أولي على الفقرات
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[str] = []
    buffer = ""

    for paragraph in paragraphs:
        # فقرة أطول من الحد → تقسم بالجُمل
        if len(paragraph) > chunk_size:
            if buffer:
                chunks.append(buffer.strip())
                buffer = ""
            chunks.extend(_split_long_paragraph(paragraph, chunk_size, overlap))
            continue

        if len(buffer) + len(paragraph) + 2 <= chunk_size:
            buffer = f"{buffer}\n{paragraph}".strip()
        else:
            if buffer:
                chunks.append(buffer.strip())
            buffer = paragraph

    if buffer.strip():
        chunks.append(buffer.strip())

    return [c for c in chunks if len(c) > 20]


def _split_long_paragraph(paragraph: str, chunk_size: int, overlap: int) -> list[str]:
    pieces: list[str] = []
    start = 0
    length = len(paragraph)

    while start < length:
        end = min(start + chunk_size, length)
        # محاولة القطع عند نهاية جملة
        if end < length:
            sentence_end = paragraph.rfind(".", start, end)
            newline_end = paragraph.rfind("\n", start, end)
            cut = max(sentence_end, newline_end)
            if cut > start + chunk_size // 2:
                end = cut + 1
        pieces.append(paragraph[start:end].strip())
        start = end - overlap if end < length else end

    return [p for p in pieces if p]
