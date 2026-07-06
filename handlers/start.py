from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import SUPER_ADMIN_ID
from keyboards.main_menu import (
    super_admin_menu,
    employee_menu,
)

router = Router()


@router.message(CommandStart())
async def start(message: Message):

    if message.from_user.id == SUPER_ADMIN_ID:

        await message.answer(
            "👑 Assalomu alaykum!\n\n"
            "TaskFlow tizimiga xush kelibsiz.",
            reply_markup=super_admin_menu(),
        )

    else:

        await message.answer(
            "Assalomu alaykum.",
            reply_markup=employee_menu(),
        )