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


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    object_name: Mapped[str] = mapped_column(
        String(255),
    )

    task_name: Mapped[str] = mapped_column(
        String(1000),
    )

    leader_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    deadline: Mapped[str] = mapped_column(
        String(100),
    )

    priority: Mapped[str] = mapped_column(
        String(30),
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="Yangi",
    )

    comment: Mapped[str] = mapped_column(
        String(1000),
        default="",
    )

    photo: Mapped[str] = mapped_column(
        String(500),
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )