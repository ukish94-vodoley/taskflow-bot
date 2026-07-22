from datetime import datetime

from sqlalchemy import (
    String,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.base import Base


class TaskAttachment(Base):
    __tablename__ = "task_attachments"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    task_id: Mapped[int] = mapped_column(
        ForeignKey("tasks.id"),
    )

    file_id: Mapped[str] = mapped_column(
        String(300),
    )

    file_name: Mapped[str] = mapped_column(
        String(300),
        default="",
    )

    file_type: Mapped[str] = mapped_column(
        String(30),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )