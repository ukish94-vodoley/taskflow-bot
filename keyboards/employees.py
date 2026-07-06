from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def employees_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Xodim qo'shish")],
            [KeyboardButton(text="📋 Xodimlar ro'yxati")],
            [KeyboardButton(text="❌ Xodimni o'chirish")],
            [KeyboardButton(text="⬅️ Orqaga")],
        ],
        resize_keyboard=True,
    )