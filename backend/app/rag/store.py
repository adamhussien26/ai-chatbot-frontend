"""
rag/store.py — تخزين واسترجاع المقاطع مع المتجهات من قاعدة البيانات
المتجهات مخزنة JSON في knowledge_chunks؛ التشابه يُحسب في بايثون
(مناسب لحجم الجامعة؛ يمكن الترقية لقاعدة متجهات مخصصة لاحقًا).
"""
from sqlalchemy.orm import Session

from app.models import KnowledgeChunk, KnowledgeDocument
from app.rag.embeddings import cosine_similarity, decode_vector


def search_chunks(db: Session, query_vector: list[float], top_k: int = 4) -> list[dict]:
    """البحث الدلالي في جميع مقاطع المستندات النشطة."""
    rows = (
        db.query(KnowledgeChunk, KnowledgeDocument)
        .join(KnowledgeDocument, KnowledgeChunk.document_id == KnowledgeDocument.id)
        .filter(KnowledgeDocument.is_active.is_(True))
        .all()
    )

    scored = []
    for chunk, document in rows:
        try:
            vector = decode_vector(chunk.embedding)
        except (ValueError, TypeError):
            continue
        score = cosine_similarity(query_vector, vector)
        scored.append({
            "chunk_id": chunk.id,
            "document_id": document.id,
            "document_title": document.title,
            "content": chunk.content,
            "score": round(score, 4),
        })

    scored.sort(key=lambda item: item["score"], reverse=True)
    return scored[:top_k]
