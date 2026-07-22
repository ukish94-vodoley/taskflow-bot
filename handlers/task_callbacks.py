from email import message

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.database import SessionLocal
from models.task import Task
from states.task import ReviewTask

from services.task_service import complete_task, get_task
from services.user_service import get_user_by_id
from services.notification_service import bot

router = Router()


@router.callback_query(F.data.startswith("approve_"))
async def approve_task(callback: CallbackQuery):

    try:
        task_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Xato.")
        return

    task = await get_task(task_id)

    if task is None:
        await callback.answer("❌ Vazifa topilmadi.", show_alert=True)
        return

    await complete_task(task_id)

    employee = await get_user_by_id(task.employee_id)

    if employee and employee.telegram_id:
        try:
            await bot.send_message(
                employee.telegram_id,
                "🎉 Vazifangiz rahbar tomonidan tasdiqlandi.\n\n"
                f"🆔 Vazifa №{task.id}"
            )
        except Exception:
            pass

    await callback.answer("✅ Tasdiqlandi.")

    await callback.message.edit_reply_markup(
        reply_markup=None,
    )

    await callback.message.answer(
        "✅ Vazifa muvaffaqiyatli tasdiqlandi."
    )


@router.callback_query(F.data.startswith("return_"))
async def return_task(callback: CallbackQuery, state: FSMContext):

    try:
        task_id = int(callback.data.split("_")[1])
    except (IndexError, ValueError):
        await callback.answer("❌ Xato.")
        return

    await state.update_data(task_id=task_id)
    await state.set_state(ReviewTask.waiting_reason)

    await callback.answer("🔄 Qayta ishlash.")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer(
    "💬 Qaytarish sababini yuboring.\n\n"
    "✍️ Matn\n"
    "🎤 Ovozli xabar\n"
    "🎥 Video xabar\n"
    "📹 Video\n"
    "🖼 Rasm\n"
    "📄 Hujjat"
)

@router.message(
    ReviewTask.waiting_reason,
    F.text | F.voice | F.video_note | F.video | F.photo | F.document,
)
@router.message(
    ReviewTask.waiting_reason,
    F.text | F.voice | F.video_note | F.video | F.photo | F.document,
)
async def process_return_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    task = await get_task(data["task_id"])

    if task is None:
        await state.clear()
        await message.answer("❌ Vazifa topilmadi.")
        return

    async with SessionLocal() as session:
        db_task = await session.get(Task, task.id)
        db_task.status = "Qayta ishlashda"
        await session.commit()

    employee = await get_user_by_id(task.employee_id)

    if employee and employee.telegram_id:
        try:
            await bot.send_message(
                employee.telegram_id,
                f"❌ Vazifa №{task.id} qayta ishlashga yuborildi."
            )

            if message.text:
                await bot.send_message(
                    employee.telegram_id,
                    f"💬 Sabab:\n\n{message.text}"
                )

            elif message.voice:
                await bot.send_message(
                    employee.telegram_id,
                    "🎤 Rahbar ovozli izoh qoldirdi."
                )
                await bot.send_voice(
                    employee.telegram_id,
                    voice=message.voice.file_id,
                )

            elif message.video_note:
                await bot.send_message(
                    employee.telegram_id,
                    "🎥 Rahbar video xabar qoldirdi."
                )
                await bot.send_video_note(
                    employee.telegram_id,
                    video_note=message.video_note.file_id,
                )

            elif message.video:
                await bot.send_video(
                    employee.telegram_id,
                    video=message.video.file_id,
                    caption="📹 Rahbarning video izohi"
                )

            elif message.photo:
                await bot.send_photo(
                    employee.telegram_id,
                    photo=message.photo[-1].file_id,
                    caption="🖼 Rahbarning izohi"
                )

            elif message.document:
                await bot.send_document(
                    employee.telegram_id,
                    document=message.document.file_id,
                    caption="📄 Rahbarning izohi"
                )

        except Exception as e:
            print("Return error:", e)

    await state.clear()

    await message.answer(
        "✅ Qayta ishlashga yuborildi."
    )
