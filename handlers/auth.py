from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from keyboards.main_menu import (
    super_admin_menu,
    employee_menu,
)

from services.user_service import (
    get_user_by_phone,
    bind_telegram,
)

router = Router()


phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📱 Telefon raqamni yuborish",
                request_contact=True,
            )
        ]
    ],
    resize_keyboard=True,
)


@router.message(F.text == "📱 Kirish")
async def auth_start(message: Message):

    await message.answer(
        "📱 Telefon raqamingizni yuboring.",
        reply_markup=phone_keyboard,
    )


@router.message(F.contact)
async def auth_contact(message: Message):

    phone = message.contact.phone_number

    if phone.startswith("998"):
        phone = "+" + phone

    user = await get_user_by_phone(phone)

    if user is None:

        await message.answer(
            "❌ Siz ushbu tizimda ro'yxatdan o'tmagansiz."
        )

        return

    await bind_telegram(
        user.id,
        message.from_user.id,
    )

    if user.role in (
        "super_admin",
        "leader",
    ):

        await message.answer(
            f"✅ Xush kelibsiz, {user.full_name}",
            reply_markup=super_admin_menu(),
        )

        return

    await message.answer(
        f"✅ Xush kelibsiz, {user.full_name}",
        reply_markup=employee_menu(),
    )