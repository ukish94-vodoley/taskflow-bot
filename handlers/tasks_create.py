from aiogram import Router, F
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.fsm.context import FSMContext
from datetime import datetime


from states.task import AddTask

from services.task_service import create_task

from services.user_service import (
    get_user,
    get_employees,
    get_employee_by_name,
)

from services.notification_service import (
    send_task_notification,
)

from keyboards.main_menu import super_admin_menu
from keyboards.tasks import tasks_menu

router = Router()




@router.message(F.text == "➕ Vazifa yaratish")
async def create_task_start(
    message: Message,
    state: FSMContext,
):

    await state.clear()

    await state.set_state(
        AddTask.waiting_object
    )

    await message.answer(
        "🔧 Bajariladigan ishni kiriting:"
    )


@router.message(AddTask.waiting_object)
async def task_object(
    message: Message,
    state: FSMContext,
):

    if message.text == "⬅️ Orqaga":

        await state.clear()

        await message.answer(
            "📋 Vazifalar bo'limi",
            reply_markup=tasks_menu(),
        )

        return

    await state.update_data(
        object_name=message.text,
        task_name=message.text,
    )

    employees = await get_employees()

    keyboard = []

    for employee in employees:
        keyboard.append([KeyboardButton(text=employee.full_name)])

    keyboard.append([KeyboardButton(text="👥 Barcha xodimlarga")])
    keyboard.append([KeyboardButton(text="⬅️ Orqaga")])

    await state.set_state(AddTask.waiting_employees)

    await message.answer(
        "👷 Xodimni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        ),
    )


@router.message(AddTask.waiting_employees)
async def task_employee(
    message: Message,
    state: FSMContext,
):

    if message.text == "⬅️ Orqaga":

        await state.clear()

        await message.answer(
            "📋 Vazifalar bo'limi",
            reply_markup=tasks_menu(),
        )

        return

    await state.update_data(
        employee_name=message.text,
        deadline=datetime.now().strftime("%H:%M %d.%m.%Y"),
        priority="Oddiy",
    )

    data = await state.get_data()

    current_user = await get_user(
        message.from_user.id,
    )

    if current_user is None:

        await state.clear()

        await message.answer(
            "❌ Foydalanuvchi topilmadi.",
            reply_markup=super_admin_menu(),
        )

        return

    if data["employee_name"] == "👥 Barcha xodimlarga":

        employees = await get_employees()

        for employee in employees:

            task = await create_task(
                object_name=data["object_name"],
                task_name=data["task_name"],
                leader_id=current_user.id,
                employee_id=employee.id,
                deadline=data["deadline"],
                priority=data["priority"],
            )

            await send_task_notification(
                telegram_id=employee.telegram_id,
                task_id=task.id,
                object_name=data["object_name"],
                task_name=data["task_name"],
                deadline=data["deadline"],
                priority=data["priority"],
            )

        await state.clear()

        await message.answer(
            "✅ Vazifa barcha xodimlarga yuborildi.",
            reply_markup=super_admin_menu(),
        )

        return

    employee = await get_employee_by_name(
        data["employee_name"],
    )

    if employee is None:

        await state.clear()

        await message.answer(
            "❌ Xodim topilmadi.",
            reply_markup=super_admin_menu(),
        )

        return

    task = await create_task(
        object_name=data["object_name"],
        task_name=data["task_name"],
        leader_id=current_user.id,
        employee_id=employee.id,
        deadline=data["deadline"],
        priority=data["priority"],
    )

    await send_task_notification(
        telegram_id=employee.telegram_id,
        task_id=task.id,
        object_name=data["object_name"],
        task_name=data["task_name"],
        deadline=data["deadline"],
        priority=data["priority"],
    )

    await state.clear()

    await message.answer(
        "✅ Vazifa muvaffaqiyatli yaratildi.",
        reply_markup=super_admin_menu(),
    )


