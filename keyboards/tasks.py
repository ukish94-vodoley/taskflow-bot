from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def tasks_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Vazifa yaratish")],
            [KeyboardButton(text="📋 Vazifalar ro'yxati")],
            [KeyboardButton(text="❌ Vazifani o'chirish")],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True,
    )