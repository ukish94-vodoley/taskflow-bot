from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states.employee import DeleteEmployee

from services.user_service import (
    get_employees,
    delete_employee,
)

router = Router()


@router.message(F.text == "❌ Xodimni o'chirish")
async def delete_employee_menu(message: Message, state: FSMContext):

    employees = await get_employees()

    if not employees:
        await message.answer("👷 Xodimlar mavjud emas.")
        return

    keyboard = []

    for employee in employees:
        keyboard.append(
            [
                KeyboardButton(
                    text=f"{employee.full_name} | {employee.phone}"
                )
            ]
        )

    keyboard.append([KeyboardButton(text="⬅️ Orqaga")])

    await state.set_state(DeleteEmployee.waiting_employee)

    await state.update_data(employees=employees)

    await message.answer(
        "❌ O'chiriladigan xodimni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        ),
    )


@router.message(DeleteEmployee.waiting_employee)
async def delete_selected_employee(message: Message, state: FSMContext):

    data = await state.get_data()

    employees = data["employees"]

    selected = None

    for employee in employees:
        if message.text == f"{employee.full_name} | {employee.phone}":
            selected = employee
            break

    if selected is None:
        await message.answer("Xodimni tugmadan tanlang.")
        return

    await delete_employee(selected.id)

    await state.clear()

    await message.answer("✅ Xodim muvaffaqiyatli o'chirildi.")