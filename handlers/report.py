from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select

from database.database import SessionLocal
from models.task import Task
from models.user import User

from services.user_service import get_user

router = Router()


@router.message(F.text == "📊 Hisobot")
async def report(
    message: Message,
):

    user = await get_user(
        message.from_user.id,
    )

    if user is None:
        return

    async with SessionLocal() as session:

        tasks = (
            await session.execute(
                select(Task)
            )
        ).scalars().all()

        employees = (
            await session.execute(
                select(User).where(
                    User.role == "employee"
                )
            )
        ).scalars().all()

        leaders = (
            await session.execute(
                select(User).where(
                    User.role == "leader"
                )
            )
        ).scalars().all()

        total = len(tasks)

        new = len(
            [
                x
                for x in tasks
                if x.status == "Yangi"
            ]
        )

        review = len(
            [
                x
                for x in tasks
                if x.status == "Tekshirilmoqda"
            ]
        )

        done = len(
            [
                x
                for x in tasks
                if x.status == "Bajarildi"
            ]
        )

        rework = len(
            [
                x
                for x in tasks
                if x.status == "Qayta ishlashda"
            ]
        )

        text = (
            "📊 HISOBOT\n\n"

            f"👨‍💼 Rahbarlar: {len(leaders)}\n"
            f"👷 Xodimlar: {len(employees)}\n\n"

            f"📋 Jami vazifa: {total}\n\n"

            f"🆕 Yangi: {new}\n"
            f"📥 Tekshirilmoqda: {review}\n"
            f"🔄 Qayta ishlashda: {rework}\n"
            f"✅ Bajarildi: {done}"
        )

        await message.answer(
            text
        )