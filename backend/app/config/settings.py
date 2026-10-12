"""
config/settings.py — إعدادات التطبيق المركزية
تُقرأ من ملف .env الموجود في مجلد backend/ (أو من متغيرات البيئة).
"""
from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- App ---
    APP_NAME: str = "UST University Chatbot API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_PREFIX: str = "/api"

    # --- Security / JWT ---
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    # --- OTP ---
    OTP_EXPIRE_MINUTES: int = 10
    OTP_LENGTH: int = 6

    # --- Database ---
    # MySQL:  mysql+pymysql://user:password@localhost:3306/ust_chatbot?charset=utf8mb4
    # SQLite (تطوير/اختبار): sqlite:///./ust_dev.db
    DATABASE_URL: str = f"sqlite:///{(BASE_DIR / 'ust_dev.db').as_posix()}"

    # --- CORS ---
    CORS_ORIGINS: str = "*"  # مفصولة بفواصل في الإنتاج

    # --- LLM (OpenAI-Compatible REST API) ---
    OPENAI_API_KEY: str = ""       # فارغ = وضع Offline (بدون LLM خارجي)
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    LLM_MODEL: str = "gpt-4o-mini"
    LLM_TIMEOUT_SECONDS: int = 25

    # --- Embeddings / RAG ---
    EMBEDDINGS_PROVIDER: str = "local"   # "openai" أو "local" (مدمج بدون خدمات خارجية)
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    RAG_TOP_K: int = 4
    RAG_SIMILARITY_THRESHOLD: float = 0.15   # ارفعها إلى ~0.30 عند استخدام OpenAI embeddings

    # --- Files ---
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_UPLOAD_SIZE_MB: int = 20

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
