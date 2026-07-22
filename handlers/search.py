from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import super_admin_menu
from services.task_service import search_tasks
from states.search import SearchState

router = Router()


@router.message(F.text == "🔍 Qidiruv")
async def search_start(message: Message, state: FSMContext):

    await state.clear()
    await state.set_state(SearchState.waiting_query)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True,
    )

    await message.answer(
        "🔍 Nimani qidirmoqchisiz?\n\n"
        "Masalan:\n"
        "• DOC-000021\n"
        "• Shahobiddin\n"
        "• kamera\n"
        "• bugun\n"
        "• shoshilinch",
        reply_markup=keyboard,
    )


@router.message(SearchState.waiting_query)
async def search_query(message: Message, state: FSMContext):

    if message.text == "⬅️ Orqaga":
        await state.clear()
        await message.answer(
            "🏠 Bosh menyu",
            reply_markup=super_admin_menu(),
        )
        return

    tasks = await search_tasks(message.text)

    if not tasks:
        await message.answer("❌ Hech narsa topilmadi.")
        return

    keyboard = []

    for item in tasks:
        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"{item['doc']} | {item['employee']}",
                    callback_data=f"task_{item['task_id']}",
                )
            ]
        )

    await message.answer(
        f"🔍 Topildi: {len(tasks)} ta vazifa",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        ),
    )