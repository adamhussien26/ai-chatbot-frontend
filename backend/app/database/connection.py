"""
database/connection.py — محرك قاعدة البيانات والجلسات (SQLAlchemy)
يدعم MySQL عبر pymysql (الإنتاج) و SQLite (التطوير والاختبار).
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config.settings import settings

engine_kwargs: dict = {}

if settings.DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs.update({
        "pool_pre_ping": True,   # يعيد الاتصال تلقائيًا عند انقطاع MySQL
        "pool_recycle": 1800,
    })

engine = create_engine(settings.DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """الأساس لجميع نماذج ORM."""
    pass


def get_db():
    """FastAPI dependency: جلسة قاعدة بيانات لكل طلب."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """إنشاء الجداول (مناسب للتطوير؛ في الإنتاج استخدم database/schema.sql)."""
    from app.models import user, student, academic, notification, chat, knowledge, otp  # noqa: F401
    Base.metadata.create_all(bind=engine)
