from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

from sqlalchemy import (
    BigInteger,
    Integer,
    Sequence,
    String,
    DateTime,
    Boolean,
    ForeignKey,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("users_id_seq"),
        primary_key=True,
    )

    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        unique=True,
        nullable=True,
    )

    full_name: Mapped[str] = mapped_column(String(255))

    phone: Mapped[str] = mapped_column(
        String(20),
        unique=True,
    )

    role: Mapped[str] = mapped_column(
        String(30),
        default="employee",
    )

    leader_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )