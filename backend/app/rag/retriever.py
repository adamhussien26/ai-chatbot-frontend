"""
rag/retriever.py — خط الاسترجاع: سؤال → متجه → أفضل المقاطع → سياق جاهز للـ LLM
"""
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.rag.embeddings import embed_single
from app.rag.store import search_chunks


def retrieve(db: Session, question: str, top_k: int | None = None) -> list[dict]:
    """إرجاع أفضل المقاطع المطابقة للسؤال."""
    k = top_k or settings.RAG_TOP_K
    query_vector = embed_single(question)
    if not query_vector:
        return []
    return search_chunks(db, query_vector, top_k=k)


def build_context(hits: list[dict], max_chars: int = 3500) -> str:
    """بناء نص السياق من المقاطع المسترجعة (مع ذكر المصادر)."""
    parts = []
    total = 0
    for hit in hits:
        piece = f"[{hit['document_title']}]\n{hit['content']}"
        if total + len(piece) > max_chars:
            break
        parts.append(piece)
        total += len(piece)
    return "\n\n---\n\n".join(parts)


def best_score(hits: list[dict]) -> float:
    return hits[0]["score"] if hits else 0.0


def is_reliable(hits: list[dict]) -> bool:
    """هل نتائج الاسترجاع موثوقة بدرجة كافية؟"""
    return best_score(hits) >= settings.RAG_SIMILARITY_THRESHOLD
