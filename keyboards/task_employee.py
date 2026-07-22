from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from services.user_service import get_employees


async def employees_keyboard():

    employees = await get_employees()

    keyboard = []

    for employee in employees:

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"👤 {employee.full_name}",
                    callback_data=f"employee:{employee.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="👥 Barcha xodimlarga",
                callback_data="employee:all",
            )
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="➡️ Davom etish",
                callback_data="employee:next",
            )
        ]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=keyboard
    )