"""
routes/kb_routes.py — إدارة قاعدة المعرفة (Knowledge Base)
- الأدمن: رفع مستندات (PDF/DOCX/TXT) → استخراج → تقسيم → Embeddings → تخزين
- الأدمن: عرض/حذف المستندات + اختبار البحث الدلالي
"""
import os

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.connection import get_db
from app.models import KnowledgeChunk, KnowledgeDocument, User
from app.auth.dependencies import require_admin
from app.rag.chunker import split_into_chunks
from app.rag.embeddings import embed_single, embed_texts, encode_vector
from app.rag.extractor import detect_doc_type, extract_text
from app.rag.retriever import retrieve
from app.utils.exceptions import NotFoundError, ValidationError

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt", ".md")


def _save_upload(filename: str, data: bytes) -> str:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_name = f"{os.urandom(8).hex()}_{os.path.basename(filename)}"
    path = os.path.join(settings.UPLOAD_DIR, safe_name)
    with open(path, "wb") as f:
        f.write(data)
    return path


@router.post("/documents", status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(None),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    """
    رفع مستند إلى قاعدة المعرفة:
    Extract Text → Clean → Split Chunks → Embeddings → Store
    """
    filename = os.path.basename(file.filename or "document")
    if not filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise ValidationError("الأنواع المدعومة: PDF, DOCX, TXT, MD.")

    data = await file.read()
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(data) > max_bytes:
        raise ValidationError(f"حجم الملف يتجاوز {settings.MAX_UPLOAD_SIZE_MB} ميجابايت.")
    if len(data) == 0:
        raise ValidationError("الملف فارغ.")

    doc_type = detect_doc_type(filename)
    text = extract_text(filename, data)          # Extract + Clean
    chunks = split_into_chunks(text)             # Split
    if not chunks:
        raise ValidationError("لم يتم توليد أي مقاطع من المستند.")

    vectors = embed_texts(chunks)                # Embeddings

    document = KnowledgeDocument(
        title=(title or os.path.splitext(filename)[0]).strip()[:255],
        filename=filename,
        doc_type=doc_type,
        size_bytes=len(data),
        chunk_count=len(chunks),
        uploaded_by=admin.id,
    )
    db.add(document)
    db.flush()

    for index, (chunk, vector) in enumerate(zip(chunks, vectors)):
        db.add(KnowledgeChunk(
            document_id=document.id,
            chunk_index=index,
            content=chunk,
            embedding=encode_vector(vector),
        ))
    db.commit()
    db.refresh(document)

    return {
        "success": True,
        "message": f"تم رفع المستند وفهرسة {len(chunks)} مقطعًا.",
        "document": {
            "id": document.id,
            "title": document.title,
            "doc_type": document.doc_type,
            "chunks": document.chunk_count,
            "size_bytes": document.size_bytes,
        },
    }


@router.get("/documents")
def list_documents(db: Session = Depends(get_db), _: User = Depends(require_admin)):
    documents = db.query(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "filename": d.filename,
            "doc_type": d.doc_type,
            "size_bytes": d.size_bytes,
            "chunk_count": d.chunk_count,
            "is_active": d.is_active,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in documents
    ]


@router.delete("/documents/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    document = db.get(KnowledgeDocument, document_id)
    if document is None:
        raise NotFoundError("المستند غير موجود.")
    db.delete(document)  # CASCADE يحذف المقاطع
    db.commit()
    return {"success": True, "message": "تم حذف المستند وجميع مقاطعه."}


@router.patch("/documents/{document_id}/toggle")
def toggle_document(document_id: int, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    """تفعيل/تعطيل مستند دون حذفه (يُستثنى من البحث عند التعطيل)."""
    document = db.get(KnowledgeDocument, document_id)
    if document is None:
        raise NotFoundError("المستند غير موجود.")
    document.is_active = not document.is_active
    db.commit()
    state = "مُفعّل" if document.is_active else "معطّل"
    return {"success": True, "message": f"تم جعل المستند {state}."}


@router.post("/search")
def search_knowledge(
    query: str = Form(...),
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    """اختبار البحث الدلالي في قاعدة المعرفة (للأدمن)."""
    hits = retrieve(db, query)
    return {"query": query, "results": hits}
