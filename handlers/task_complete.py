from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database.database import SessionLocal
from models.task import Task
from models.user import User

from services.user_service import get_user
from services.task_service import save_task_result
from services.notification_service import (
    bot,
    send_completed_notification,
)

from states.task import CompleteTask

router = Router()


@router.message(F.text == "✅ Vazifani yakunlash")
async def complete_menu(
    message: Message,
    state: FSMContext,
):

    user = await get_user(message.from_user.id)

    if user is None:
        return

    async with SessionLocal() as session:

        result = await session.execute(
            select(Task)
            .where(
                Task.employee_id == user.id,
                Task.status != "Bajarildi",
            )
            .order_by(Task.id.desc())
        )

        tasks = result.scalars().all()

        if not tasks:

            await message.answer(
                "📭 Yakunlanadigan vazifalar yo'q."
            )

            return

        keyboard = []

        for task in tasks:

            keyboard.append(
                [
                    KeyboardButton(
                        text=f"{task.id} | {task.object_name}"
                    )
                ]
            )

        keyboard.append(
            [
                KeyboardButton(
                    text="⬅️ Orqaga"
                )
            ]
        )

        await state.set_state(
            CompleteTask.waiting_task
        )

        await state.update_data(
            tasks=[task.id for task in tasks]
        )

        await message.answer(
            "✅ Vazifani tanlang:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
            ),
        )


@router.message(CompleteTask.waiting_task)
async def selected_task(
    message: Message,
    state: FSMContext,
):

    if message.text == "⬅️ Orqaga":

        await state.clear()

        return

    task_id = int(
        message.text.split("|")[0].strip()
    )

    data = await state.get_data()

    if task_id not in data["tasks"]:

        await message.answer(
            "❌ Vazifani tugmadan tanlang."
        )

        return

    await state.update_data(
        task_id=task_id
    )

    await state.set_state(
        CompleteTask.waiting_photo
    )

    await message.answer(
        "📎 Hisobot faylini yuboring.\n\n🖼 Rasm\n🎥 Video\n🎤 Ovoz\n🎬 Video message\n📄 PDF yoki boshqa hujjat\n\n(Hozircha bir dona fayl yuboring.)"
    )


@router.message(
    CompleteTask.waiting_photo,
    F.photo | F.video | F.voice | F.video_note | F.document,
)
async def get_photo(
    message: Message,
    state: FSMContext,
):

    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.voice:
        file_id = message.voice.file_id
        file_type = "voice"
    elif message.video_note:
        file_id = message.video_note.file_id
        file_type = "video_note"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
    else:
        await message.answer("❌ Qo'llab-quvvatlanmaydigan fayl.")
        return

    await state.update_data(
        photo=file_id,
        file_type=file_type,
    )

    await state.set_state(
        CompleteTask.waiting_comment
    )

    await message.answer(
        "📝 Izoh yozing."
    )


@router.message(
    CompleteTask.waiting_comment
)
async def get_comment(
    message: Message,
    state: FSMContext,
):

    data = await state.get_data()

    await save_task_result(
        task_id=data["task_id"],
        photo=data["photo"],
        comment=message.text,
    )

    async with SessionLocal() as session:

        task = await session.get(
            Task,
            data["task_id"],
        )

        employee = await session.get(
            User,
            task.employee_id,
        )

        leader = await session.get(
            User,
            task.leader_id,
        )

    if leader and leader.telegram_id:

        await send_completed_notification(
            telegram_id=leader.telegram_id,
            task_id=task.id,
            employee_name=employee.full_name,
            object_name=task.object_name,
            task_name=task.task_name,
        )

        caption = f"💬 Izoh:\n\n{message.text}"
        file_type = data.get("file_type","photo")

        if file_type == "photo":
            await bot.send_photo(
                leader.telegram_id,
                photo=data["photo"],
                caption=caption,
            )
        elif file_type == "video":
            await bot.send_video(
                leader.telegram_id,
                video=data["photo"],
                caption=caption,
            )
        elif file_type == "voice":
            await bot.send_voice(
                leader.telegram_id,
                voice=data["photo"],
                caption=caption,
            )
        elif file_type == "video_note":
            await bot.send_video_note(
                leader.telegram_id,
                video_note=data["photo"],
            )
            await bot.send_message(
                leader.telegram_id,
                caption,
            )
        elif file_type == "document":
            await bot.send_document(
                leader.telegram_id,
                document=data["photo"],
                caption=caption,
            )

    await state.clear()

    await message.answer(
        "✅ Hisobot rahbarga yuborildi."
    )