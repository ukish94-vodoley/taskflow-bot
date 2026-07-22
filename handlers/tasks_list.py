from aiogram import Router, F
from aiogram.types import Message

from sqlalchemy import select

from database.database import SessionLocal
from models.task import Task
from models.user import User

router = Router()


@router.message(F.text == "📋 Vazifalar ro'yxati")
async def tasks_list(message: Message):

    async with SessionLocal() as session:

        result = await session.execute(
            select(Task).order_by(Task.id.desc())
        )

        tasks = result.scalars().all()

        if not tasks:

            await message.answer(
                "📭 Vazifalar mavjud emas."
            )

            return

        text = "📋 Vazifalar ro'yxati\n\n"

        for task in tasks:

            employee = await session.get(
                User,
                task.employee_id,
            )

            leader = await session.get(
                User,
                task.leader_id,
            )

            employee_name = (
                employee.full_name
                if employee
                else "Noma'lum"
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
                f"👷 Xodim: {employee_name}\n"
                f"📅 Muddat: {task.deadline}\n"
                f"⚠️ Muhimlik: {task.priority}\n"
                f"📌 Holati: {task.status}\n"
                f"\n━━━━━━━━━━━━━━━━━━\n\n"
            )

        await message.answer(text)