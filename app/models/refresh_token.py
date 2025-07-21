import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config import JWT_REFRESH_TOKEN_EXPIRE_MINUTES, JWT_REFRESH_TOKEN_LENGTH

from .base import Base


def generate_expiration_date() -> datetime:
    return datetime.now(tz=timezone.utc) + timedelta(
        minutes=JWT_REFRESH_TOKEN_EXPIRE_MINUTES
    )


# def generate_token() -> str:
#     return secrets.token_urlsafe(JWT_REFRESH_TOKEN_LENGTH)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    hash: Mapped[str] = mapped_column(Text, primary_key=True)
    expiry: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=generate_expiration_date
    )
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE")
    )
    user: Mapped["User"] = relationship(back_populates="refresh_tokens", lazy="joined")
