"""
utils/exceptions.py — استثناءات مخصصة + معالجات أخطاء موحدة
تضمن رسائل واضحة للواجهة دون كشف تفاصيل داخلية، ودون توقف النظام.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse

from app.config.settings import settings


class AppError(Exception):
    """استثناء أساس عام للتطبيق."""

    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "العنصر المطلوب غير موجود."):
        super().__init__(message, status.HTTP_404_NOT_FOUND)


class AuthError(AppError):
    def __init__(self, message: str = "بيانات الدخول غير صحيحة."):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)


class PermissionDeniedError(AppError):
    def __init__(self, message: str = "ليس لديك صلاحية للوصول إلى هذا المورد."):
        super().__init__(message, status.HTTP_403_FORBIDDEN)


class ValidationError(AppError):
    def __init__(self, message: str = "البيانات المدخلة غير صحيحة."):
        super().__init__(message, status.HTTP_422_UNPROCESSABLE_ENTITY)


def _error_payload(message: str, error_type: str) -> dict:
    return {"success": False, "error": {"type": error_type, "message": message}}


def register_exception_handlers(app) -> None:
    """تسجيل معالجات الأخطاء الموحدة على التطبيق."""

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(exc.message, "app_error"),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception):
        # آخر خط دفاع: لا نكشف التفاصيل للمستخدم لكن نسجّل الخطأ
        import logging
        logging.getLogger("ust").exception("Unhandled error: %s", exc)
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        message = "حدث خطأ غير متوقع في الخادم. حاول مرة أخرى لاحقًا."
        if settings.DEBUG:
            message = f"{message} [{type(exc).__name__}: {exc}]"
        return JSONResponse(
            status_code=status_code,
            content=_error_payload(message, "internal_error"),
        )
