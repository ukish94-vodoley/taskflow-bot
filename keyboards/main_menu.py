from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def super_admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="👥 Rahbarlar"),
                KeyboardButton(text="👷 Xodimlar"),
            ],
            [
                KeyboardButton(text="📋 Vazifalar"),
                KeyboardButton(text="📊 Hisobot"),
            ],
            [
                KeyboardButton(text="📥 Tekshirilayotgan vazifalar"),
                KeyboardButton(text="🔍 Qidiruv"),
            ],
            [
                KeyboardButton(text="⚙️ Sozlamalar"),
            ],
        ],
        resize_keyboard=True,
    )


def employee_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📋 Mening vazifalarim"),
            ],
            [
                KeyboardButton(text="✅ Vazifani yakunlash"),
            ],
            [
                KeyboardButton(text="📊 Hisobotim"),
            ],
        ],
        resize_keyboard=True,
    )