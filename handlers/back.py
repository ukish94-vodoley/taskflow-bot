from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from keyboards.main_menu import (
    super_admin_menu,
    employee_menu,
)

from services.user_service import get_user

router = Router()


@router.message(F.text == "⬅️ Orqaga")
async def back(message: Message, state: FSMContext):

    await state.clear()

    user = await get_user(message.from_user.id)

    if message.from_user.id == 0:
        return

    if user is None:

        await message.answer(
            "👑 Super Admin menyusi",
            reply_markup=super_admin_menu(),
        )

        return

    if user.role in ("super_admin", "leader"):

        await message.answer(
            "👑 Asosiy menyu",
            reply_markup=super_admin_menu(),
        )

        return

    if user.role == "employee":

        await message.answer(
            "👷 Asosiy menyu",
            reply_markup=employee_menu(),
        )

        return