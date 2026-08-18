from datetime import datetime

from sqlalchemy import (
    ForeignKey,
    String,
    Integer,
    DateTime,
    Sequence,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from models.base import Base


class Finance(Base):
    __tablename__ = "finance"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("finance_id_seq"),
        primary_key=True,
    )

    employee_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    leader_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=True,
    )

    type: Mapped[str] = mapped_column(
        String(20),
    )

    amount: Mapped[int] = mapped_column(
        Integer,
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        default=None,
    )

    photo: Mapped[str] = mapped_column(
        String(500),
        default="",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="approved",
    )

    edited: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    old_amount: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    edit_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        default=None,
    )

    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )

    approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    edited_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
