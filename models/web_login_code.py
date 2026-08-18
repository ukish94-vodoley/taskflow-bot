from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Sequence, String

from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class WebLoginCode(Base):
    __tablename__ = "web_login_codes"

    id: Mapped[int] = mapped_column(
        Integer,
        Sequence("web_login_codes_id_seq"),
        primary_key=True,
    )    
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    code_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
