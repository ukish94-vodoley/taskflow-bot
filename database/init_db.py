from database.database import engine
from models.base import Base

# Modellarni import qilish
from models.user import User


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)