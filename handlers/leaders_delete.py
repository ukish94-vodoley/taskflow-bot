from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states.leader import DeleteLeader

from services.user_service import (
    get_leaders,
    get_employees,
    delete_leader,
)

router = Router()


@router.message(F.text == "❌ Rahbarni o'chirish")
async def delete_leader_menu(message: Message, state: FSMContext):

    leaders = await get_leaders()

    if not leaders:
        await message.answer("Rahbarlar mavjud emas.")
        return

    keyboard = []

    for leader in leaders:
        keyboard.append(
            [
                KeyboardButton(
                    text=f"{leader.full_name} | {leader.phone}"
                )
            ]
        )

    keyboard.append([KeyboardButton(text="⬅️ Orqaga")])

    await state.set_state(DeleteLeader.waiting_leader)

    await state.update_data(leaders=leaders)

    await message.answer(
        "❌ O'chiriladigan rahbarni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        ),
    )


@router.message(DeleteLeader.waiting_leader)
async def delete_selected_leader(message: Message, state: FSMContext):

    data = await state.get_data()

    leaders = data["leaders"]

    selected = None

    for leader in leaders:
        if message.text == f"{leader.full_name} | {leader.phone}":
            selected = leader
            break

    if selected is None:
        await message.answer("Rahbarni tugmadan tanlang.")
        return

    employees = await get_employees()

    for employee in employees:
        if employee.leader_id == selected.id:
            await message.answer(
                "❌ Bu rahbarga xodimlar biriktirilgan.\n"
                "Avval xodimlarni o'chiring."
            )
            await state.clear()
            return

    await delete_leader(selected.id)

    await state.clear()

    await message.answer("✅ Rahbar muvaffaqiyatli o'chirildi.")