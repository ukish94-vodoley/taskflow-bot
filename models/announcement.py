from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    Text,
)

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("announcements_id_seq"),
        primary_key=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
    )

    body: Mapped[str] = mapped_column(
        Text,
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )