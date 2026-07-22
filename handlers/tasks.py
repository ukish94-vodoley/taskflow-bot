from aiogram import Router, F
from aiogram.types import Message

from keyboards.tasks import tasks_menu
from keyboards.main_menu import super_admin_menu

router = Router()


@router.message(F.text == "📋 Vazifalar")
async def tasks(message: Message):
    await message.answer(
        "📋 Vazifalar bo'limi",
        reply_markup=tasks_menu(),
    )


