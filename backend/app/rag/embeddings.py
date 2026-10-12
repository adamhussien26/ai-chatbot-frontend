"""
rag/embeddings.py — توليد تمثيلات المتجهات (Embeddings)
- مزوّد "openai": يقلب أي واجهة متوافقة مع OpenAI Embeddings عبر httpx.
- مزوّد "local": تمثيل مدمج بدون خدمات خارجية (Hashed Bag-of-Words L2-normalized)
  مناسب للتطوير والاختبار ويحافظ على عمل خط RAG كاملًا دون مفاتيح API.
"""
import hashlib
import json
import math
import re

import httpx

from app.config.settings import settings

EMBED_DIM = 512
_TOKEN_RE = re.compile(r"[\w\u0600-\u06FF]+", re.UNICODE)


# ---------------------------------------------------------------- Normalization
def normalize_arabic(text: str) -> str:
    """توحيد الحروف العربية لتحسين التطابق (أ/إ/آ→ا، ة→ه، ى→ي، إزالة التشكيل)."""
    text = re.sub(r"[\u064B-\u0652\u0670]", "", text)   # تشكيل
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ة", "ه").replace("ى", "ي").replace("ؤ", "و").replace("ئ", "ي")
    return text.lower()


# ---------------------------------------------------------------- Local embeddings
def _local_embed(text: str) -> list[float]:
    vector = [0.0] * EMBED_DIM
    tokens = _TOKEN_RE.findall(normalize_arabic(text))
    for token in tokens:
        # ثلاث هاشات مختلفة لتقليل التصادم
        for salt in ("", "1", "2"):
            digest = hashlib.md5(f"{salt}{token}".encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "little") % EMBED_DIM
            vector[index] += 1.0

    # تطبيع L2
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


# ---------------------------------------------------------------- OpenAI embeddings
def _openai_embed(texts: list[str]) -> list[list[float]]:
    response = httpx.post(
        f"{settings.OPENAI_BASE_URL.rstrip('/')}/embeddings",
        headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
        json={"model": settings.OPENAI_EMBEDDING_MODEL, "input": texts},
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()["data"]
    return [item["embedding"] for item in data]


# ---------------------------------------------------------------- Public API
def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    if settings.EMBEDDINGS_PROVIDER == "openai" and settings.OPENAI_API_KEY:
        return _openai_embed(texts)
    return [_local_embed(t) for t in texts]


def embed_single(text: str) -> list[float]:
    return embed_texts([text])[0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def encode_vector(vector: list[float]) -> str:
    return json.dumps(vector)


def decode_vector(raw: str) -> list[float]:
    return json.loads(raw)
