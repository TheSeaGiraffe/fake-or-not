from typing import List

from sqlalchemy import Identity, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer, Identity(), primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship(
        back_populates="user", passive_deletes=True
    )
