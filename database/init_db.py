from database.database import engine
from models.base import Base

# Modellarni import qilish
from models.user import User
from models.task import Task
from models.task_attachment import TaskAttachment
from models.finance import Finance
from models.announcement import Announcement
from models.web_login_code import WebLoginCode


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Oracle Database: jadvallar yaratildi.")