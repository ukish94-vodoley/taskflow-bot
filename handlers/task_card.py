from aiogram import Router, F
from aiogram.types import CallbackQuery

from database.database import SessionLocal
from models.task import Task
from models.user import User

from services.notification_service import bot

router = Router()


@router.callback_query(F.data.startswith("task_"))
async def open_task_card(callback: CallbackQuery):

    try:
        task_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Xato.")
        return

    async with SessionLocal() as session:

        task = await session.get(Task, task_id)

        if task is None:
            await callback.answer("❌ Vazifa topilmadi.", show_alert=True)
            return

        employee = await session.get(User, task.employee_id)
        leader = await session.get(User, task.leader_id)

    text = (
        f"🆔 DOC-{task.id:06d}\n\n"
        f"🏢 Obyekt: {task.object_name}\n"
        f"📝 Vazifa: {task.task_name}\n\n"
        f"👷 Xodim: {employee.full_name if employee else '-'}\n"
        f"👨‍💼 Rahbar: {leader.full_name if leader else '-'}\n\n"
        f"📅 Muddat: {task.deadline}\n"
        f"⚠️ Muhimlik: {task.priority}\n"
        f"📌 Holati: {task.status}\n\n"
        f"💬 Izoh:\n{task.comment or '-'}"
    )

    await callback.message.answer(text)

    if task.photo:

        try:
            await bot.send_photo(
                callback.message.chat.id,
                task.photo,
            )
        except Exception:
            try:
                await bot.send_document(
                    callback.message.chat.id,
                    task.photo,
                )
            except Exception:
                try:
                    await bot.send_video(
                        callback.message.chat.id,
                        task.photo,
                    )
                except Exception:
                    try:
                        await bot.send_voice(
                            callback.message.chat.id,
                            task.photo,
                        )
                    except Exception:
                        try:
                            await bot.send_video_note(
                                callback.message.chat.id,
                                task.photo,
                            )
                        except Exception:
                            pass

    await callback.answer()