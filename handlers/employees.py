from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext

from keyboards.employees import employees_menu
from keyboards.main_menu import super_admin_menu
from states.employee import AddEmployee

from services.user_service import (
    create_employee,
    get_employees,
    get_leaders,
)

router = Router()


@router.message(F.text == "👷 Xodimlar")
async def employees(message: Message):
    await message.answer(
        "👷 Xodimlar bo'limi",
        reply_markup=employees_menu(),
    )


@router.message(F.text == "➕ Xodim qo'shish")
async def add_employee(message: Message, state: FSMContext):

    leaders = await get_leaders()

    if not leaders:
        await message.answer(
            "❌ Avval kamida bitta rahbar qo'shing."
        )
        return

    keyboard = []

    for leader in leaders:
        keyboard.append(
            [KeyboardButton(text=leader.full_name)]
        )

    keyboard.append([KeyboardButton(text="⬅️ Orqaga")])

    await state.set_state(AddEmployee.waiting_name)

    await state.update_data(leaders=leaders)

    await message.answer(
        "👤 Xodimning ism familiyasini kiriting:"
    )


@router.message(AddEmployee.waiting_name)
async def employee_name(message: Message, state: FSMContext):

    await state.update_data(full_name=message.text)

    await state.set_state(AddEmployee.waiting_phone)

    await message.answer(
        "📱 Telefon raqamini kiriting:"
    )


@router.message(AddEmployee.waiting_phone)
async def employee_phone(message: Message, state: FSMContext):

    await state.update_data(phone=message.text)

    data = await state.get_data()

    leaders = data["leaders"]

    keyboard = []

    for leader in leaders:
        keyboard.append(
            [KeyboardButton(text=leader.full_name)]
        )

    keyboard.append([KeyboardButton(text="⬅️ Orqaga")])

    await state.set_state(AddEmployee.waiting_leader)

    await message.answer(
        "👨‍💼 Rahbarni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        ),
    )


@router.message(AddEmployee.waiting_leader)
async def employee_leader(message: Message, state: FSMContext):

    data = await state.get_data()

    leaders = data["leaders"]

    leader = None

    for item in leaders:
        if item.full_name == message.text:
            leader = item
            break

    if leader is None:
        await message.answer("Rahbarni tugmadan tanlang.")
        return

    await create_employee(
        full_name=data["full_name"],
        phone=data["phone"],
        leader_id=leader.id,
    )

    await state.clear()

    await message.answer(
        "✅ Xodim muvaffaqiyatli qo'shildi.",
        reply_markup=employees_menu(),
    )


@router.message(F.text == "📋 Xodimlar ro'yxati")
async def employees_list(message: Message):

    employees = await get_employees()

    if not employees:
        await message.answer("👷 Xodimlar mavjud emas.")
        return

    text = "👷 Xodimlar ro'yxati\n\n"

    for i, employee in enumerate(employees, start=1):

        text += (
            f"{i}. {employee.full_name}\n"
            f"📱 {employee.phone}\n\n"
        )

    await message.answer(text)


@router.message(F.text == "⬅️ Orqaga")
async def back(message: Message):

    await message.answer(
        "👑 Super Admin menyusi",
        reply_markup=super_admin_menu(),
    )