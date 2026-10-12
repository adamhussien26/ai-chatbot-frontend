"""
auth/otp.py — إنشاء رموز OTP والتحقق منها (مجزأة + صلاحية زمنية + استخدام لمرة واحدة)
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.config.settings import settings
from app.models import OTPCode


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def issue_otp(db: Session, user_id: int, purpose: str = "password_reset") -> str:
    """ينشئ رمز OTP جديد (ويعطّل الرموز السابقة لنفس الغرض) ويعيده نصًا صريحًا مرة واحدة."""
    db.query(OTPCode).filter(
        OTPCode.user_id == user_id,
        OTPCode.purpose == purpose,
        OTPCode.is_used.is_(False),
    ).update({"is_used": True})

    code = "".join(secrets.choice("0123456789") for _ in range(settings.OTP_LENGTH))
    otp = OTPCode(
        user_id=user_id,
        code_hash=_hash_code(code),
        purpose=purpose,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.OTP_EXPIRE_MINUTES),
    )
    db.add(otp)
    db.commit()
    return code


def verify_otp(db: Session, user_id: int, code: str, purpose: str = "password_reset", consume: bool = False) -> bool:
    """يتحقق من الرمز. consume=True يستهلك الرمز (يُستخدم عند إعادة التعيين الفعلية)."""
    now = datetime.now(timezone.utc)
    otp = (
        db.query(OTPCode)
        .filter(
            OTPCode.user_id == user_id,
            OTPCode.purpose == purpose,
            OTPCode.is_used.is_(False),
            OTPCode.expires_at > now,
        )
        .order_by(OTPCode.id.desc())
        .first()
    )
    if otp is None:
        return False
    if not secrets.compare_digest(otp.code_hash, _hash_code(code)):
        return False
    if consume:
        otp.is_used = True
        db.commit()
    return True
