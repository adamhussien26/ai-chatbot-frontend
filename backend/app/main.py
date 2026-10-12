"""
main.py — نقطة انطلاق الـ Backend (FastAPI)
يجمع جميع المسارات + CORS + معالجة الأخطاء + Health Check.
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.database.connection import init_db
from app.utils.exceptions import register_exception_handlers

logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("ust")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API نظام المساعد الذكي لجامعة العلوم والتقانة (Authentication, Students, Chatbot, RAG, Admin)",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS: السماح للـ Frontend الحالي بالاتصال ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,          # نستخدم Authorization header وليس كوكيز
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- معالجات الأخطاء الموحدة ---
register_exception_handlers(app)

# --- المسارات ---
from app.routes import (  # noqa: E402
    academic_routes, admin_routes, auth_routes, chatbot_routes,
    kb_routes, notification_routes, students_routes,
)

API = settings.API_PREFIX
app.include_router(auth_routes.router, prefix=API)
app.include_router(students_routes.router, prefix=API)
app.include_router(academic_routes.router, prefix=API)
app.include_router(notification_routes.router, prefix=API)
app.include_router(chatbot_routes.router, prefix=API)
app.include_router(kb_routes.router, prefix=API)
app.include_router(admin_routes.router, prefix=API)


# --- Health / Root ---
@app.get(f"{API}/health", tags=["System"])
def health():
    return {
        "success": True,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "llm_available": bool(settings.OPENAI_API_KEY),
        "embeddings_provider": settings.EMBEDDINGS_PROVIDER,
    }


@app.on_event("startup")
def on_startup():
    init_db()
    logger.info("%s v%s started (LLM: %s)", settings.APP_NAME, settings.APP_VERSION,
                "ON" if settings.OPENAI_API_KEY else "OFFLINE MODE")
