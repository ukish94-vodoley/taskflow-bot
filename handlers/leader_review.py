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

from services.user_service import get_user

from states.task import ReviewTask

router = Router()


@router.message(F.text == "📥 Tekshirilayotgan vazifalar")
async def review_menu(
    message: Message,
    state: FSMContext,
):

    user = await get_user(
        message.from_user.id,
    )

    if user is None:
        return

    async with SessionLocal() as session:

        result = await session.execute(
            select(Task)
            .where(
                Task.leader_id == user.id,
                Task.status == "Tekshirilmoqda",
            )
            .order_by(Task.id.desc())
        )

        tasks = result.scalars().all()

        if not tasks:

            await message.answer(
                "📭 Tekshirilayotgan vazifalar yo'q."
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
            ReviewTask.waiting_task
        )

        await state.update_data(
            tasks=[task.id for task in tasks]
        )

        await message.answer(
            "📥 Vazifani tanlang:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=keyboard,
                resize_keyboard=True,
            ),
        )

@router.message(ReviewTask.waiting_task)
async def review_selected(
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
        task_id=task_id,
    )

    async with SessionLocal() as session:
        task = await session.get(Task, task_id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="✅ Tasdiqlash"
                )
            ],
            [
                KeyboardButton(
                    text="🔄 Qayta ishlashga yuborish"
                )
            ],
            [
                KeyboardButton(
                    text="⬅️ Orqaga"
                )
            ],
        ],
        resize_keyboard=True,
    )

    await state.set_state(
        ReviewTask.waiting_action
    )

    await message.answer(
        f"📋 Vazifa: {task.object_name}\n\nAmalni tanlang:",
        reply_markup=keyboard,
    )


@router.message(ReviewTask.waiting_action)
async def review_action(
    message: Message,
    state: FSMContext,
):

    if message.text == "⬅️ Orqaga":

        await state.clear()

        return

    data = await state.get_data()

    async with SessionLocal() as session:

        task = await session.get(
            Task,
            data["task_id"],
        )

        if task is None:

            await state.clear()

            await message.answer(
                "❌ Vazifa topilmadi."
            )

            return

        if message.text == "✅ Tasdiqlash":

            task.status = "Bajarildi"

        elif message.text == "🔄 Qayta ishlashga yuborish":

            task.status = "Qayta ishlashda"

        else:

            await message.answer(
                "❌ Tugmadan tanlang."
            )

            return

        await session.commit()

    await state.clear()

    await message.answer(
        "✅ Vazifa holati yangilandi."
    )