from sqlalchemy import select, delete

from database.database import SessionLocal
from models.user import User


async def get_user(telegram_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()




async def get_user_by_id(user_id: int):
    async with SessionLocal() as session:
        return await session.get(User, user_id)

async def get_super_admin():
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.role == "super_admin")
        )
        return result.scalar_one_or_none()


async def create_leader(full_name: str, phone: str):
    async with SessionLocal() as session:
        user = User(
            full_name=full_name,
            phone=phone,
            role="leader",
        )
        session.add(user)
        await session.commit()


async def get_leaders():
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.role == "leader")
        )
        return result.scalars().all()


async def create_employee(full_name: str, phone: str, leader_id: int):
    async with SessionLocal() as session:
        user = User(
            full_name=full_name,
            phone=phone,
            role="employee",
            leader_id=leader_id,
        )
        session.add(user)
        await session.commit()


async def get_employees():
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.role == "employee")
        )
        return result.scalars().all()


async def get_employee_by_name(full_name: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.full_name == full_name,
                User.role == "employee",
            )
        )
        return result.scalar_one_or_none()


async def get_leader_by_telegram(telegram_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.telegram_id == telegram_id,
                User.role == "leader",
            )
        )
        return result.scalar_one_or_none()


async def delete_leader(user_id: int):
    async with SessionLocal() as session:
        await session.execute(
            delete(User).where(User.id == user_id)
        )
        await session.commit()


async def delete_employee(user_id: int):
    async with SessionLocal() as session:
        await session.execute(
            delete(User).where(User.id == user_id)
        )
        await session.commit()


async def get_user_by_phone(phone: str):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()


async def bind_telegram(user_id: int, telegram_id: int):
    async with SessionLocal() as session:

        user = await session.get(User, user_id)

        if user is None:
            return False

        user.telegram_id = telegram_id

        await session.commit()

        return True


async def get_employees_by_leader(leader_id: int):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(
                User.role == "employee",
                User.leader_id == leader_id,
            )
        )
        return result.scalars().all()   


async def get_leader_by_id(user_id: int):
    async with SessionLocal() as session:
        return await session.get(User, user_id)     


async def get_leader_by_id(user_id: int):
    async with SessionLocal() as session:
        return await session.get(User, user_id)    