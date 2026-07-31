from database.database import engine
from models.base import Base

# Modellarni import qilish
from models.user import User
from models.task import Task
from models.task_attachment import TaskAttachment
from models.finance import Finance


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await migrate_finance()

from sqlalchemy import text


async def migrate_finance():
    async with engine.begin() as conn:
        columns = [
            ("status", "ALTER TABLE finance ADD COLUMN status VARCHAR(20) DEFAULT 'approved'"),
            ("edited", "ALTER TABLE finance ADD COLUMN edited INTEGER DEFAULT 0"),
            ("old_amount", "ALTER TABLE finance ADD COLUMN old_amount INTEGER"),
            ("edit_reason", "ALTER TABLE finance ADD COLUMN edit_reason VARCHAR(1000) DEFAULT ''"),
            ("approved_by", "ALTER TABLE finance ADD COLUMN approved_by INTEGER"),
            ("approved_at", "ALTER TABLE finance ADD COLUMN approved_at DATETIME"),
            ("edited_at", "ALTER TABLE finance ADD COLUMN edited_at DATETIME"),
        ]

        result = await conn.execute(text("PRAGMA table_info(finance)"))
        existing = {row[1] for row in result.fetchall()}

        for name, sql in columns:
            if name not in existing:
                await conn.execute(text(sql))
