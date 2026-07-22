from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext

from services.user_service import get_user

from keyboards.main_menu import (
    super_admin_menu,
    employee_menu,
)

router = Router()


phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📱 Kirish",
            )
        ]
    ],
    resize_keyboard=True,
)


@router.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext,
):

    await state.clear()

    user = await get_user(
        message.from_user.id,
    )

    if user is None:

        await message.answer(
            "Assalomu alaykum.\n\n"
            "Tizimga kirish uchun tugmani bosing.",
            reply_markup=phone_keyboard,
        )

        return

    if user.role in (
        "super_admin",
        "leader",
    ):

        await message.answer(
            f"👋 Xush kelibsiz, {user.full_name}",
            reply_markup=super_admin_menu(),
        )

        return

    await message.answer(
        f"👋 Xush kelibsiz, {user.full_name}",
        reply_markup=employee_menu(),
    )