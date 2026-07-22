from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select

from database.database import SessionLocal
from models.task import Task
from models.user import User

from services.user_service import get_user

router = Router()


@router.message(F.text == "📋 Mening vazifalarim")
async def my_tasks(message: Message):

    user = await get_user(message.from_user.id)

    if user is None:

        await message.answer(
            "❌ Siz tizimga kirmagansiz."
        )

        return

    async with SessionLocal() as session:

        result = await session.execute(
            select(Task)
            .where(Task.employee_id == user.id)
            .order_by(Task.id.desc())
        )

        tasks = result.scalars().all()

        if not tasks:

            await message.answer(
                "📭 Sizga vazifa biriktirilmagan."
            )

            return

        text = "📋 Mening vazifalarim\n\n"

        for task in tasks:

            leader = await session.get(
                User,
                task.leader_id,
            )

            leader_name = (
                leader.full_name
                if leader
                else "Noma'lum"
            )

            text += (
                f"🆔 {task.id}\n"
                f"🏢 Obyekt: {task.object_name}\n"
                f"📝 Vazifa: {task.task_name}\n"
                f"👨‍💼 Rahbar: {leader_name}\n"
                f"📅 Muddat: {task.deadline}\n"
                f"⚠️ Muhimlik: {task.priority}\n"
                f"📌 Holati: {task.status}\n"
                f"\n━━━━━━━━━━━━━━\n\n"
            )

        await message.answer(text)