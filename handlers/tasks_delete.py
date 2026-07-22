from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext

from states.task import DeleteTask

from services.task_service import (
    get_tasks,
    delete_task,
)

router = Router()


@router.message(F.text == "❌ Vazifani o'chirish")
async def delete_task_menu(
    message: Message,
    state: FSMContext,
):

    tasks = await get_tasks()

    if not tasks:
        await message.answer(
            "📭 Vazifalar mavjud emas."
        )
        return

    keyboard = []

    for task in tasks:
        keyboard.append(
            [
                KeyboardButton(
                    text=f"{task.id} | {task.object_name} | {task.task_name}"
                )
            ]
        )

    keyboard.append(
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    )

    await state.set_state(
        DeleteTask.waiting_task
    )

    await state.update_data(
        tasks=tasks
    )

    await message.answer(
        "🗑 O'chiriladigan vazifani tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        ),
    )


@router.message(DeleteTask.waiting_task)
async def delete_selected_task(
    message: Message,
    state: FSMContext,
):

    data = await state.get_data()

    if message.text == "⬅️ Orqaga":
        await state.clear()
        return

    tasks = data["tasks"]

    selected = None

    for task in tasks:
        if message.text == f"{task.id} | {task.object_name} | {task.task_name}":
            selected = task
            break

    if selected is None:
        await message.answer(
            "❌ Vazifani tugmadan tanlang."
        )
        return

    # Vazifani o'chirish
    await delete_task(selected.id)

    await message.answer(
        "✅ Vazifa muvaffaqiyatli o'chirildi."
    )

    # Yangilangan ro'yxat
    tasks = await get_tasks()

    if not tasks:
        await state.clear()
        await message.answer(
            "📭 O'chiriladigan vazifalar qolmadi."
        )
        return

    keyboard = []

    for task in tasks:
        keyboard.append(
            [
                KeyboardButton(
                    text=f"{task.id} | {task.object_name} | {task.task_name}"
                )
            ]
        )

    keyboard.append(
        [
            KeyboardButton(text="⬅️ Orqaga")
        ]
    )

    await state.update_data(
        tasks=tasks
    )

    await message.answer(
        "🗑 Keyingi o'chiriladigan vazifani tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        ),
    )