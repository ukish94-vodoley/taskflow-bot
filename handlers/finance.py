from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    FSInputFile,
)
from aiogram.fsm.context import FSMContext

from models import finance
from states.employee import FinanceTopup

from services.user_service import (
    get_user,
    get_employees,
    get_employee_by_name,
)

from services.finance_service import (
    get_all_balances,
    add_topup,
    get_finance_history,
    get_employee_history_for_period,
    get_finance_report_data,
)

from states.employee import FinanceHistory

from services.user_service import get_employees

from services.finance_service import get_employee_balance

# from states.employee import FinanceReport


from models.user import User
from services.user_service import get_user_by_id
from services.excel_service import create_finance_report


# MONTHS = {
#     "Yanvar": 1,
#     "Fevral": 2,
#     "Mart": 3,
#     "Aprel": 4,
#     "May": 5,
#     "Iyun": 6,
#     "Iyul": 7,
#     "Avgust": 8,
#     "Sentabr": 9,
#     "Oktabr": 10,
#     "Noyabr": 11,
#     "Dekabr": 12,
# }

router = Router()


finance_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Balans to'ldirish"),
        ],
        [
            KeyboardButton(text="👥 Balanslar"),
            KeyboardButton(text="📜 Tarix"),
        ],
        [
            KeyboardButton(text="📊 Moliya hisoboti"),
        ],
        [
            KeyboardButton(text="⬅️ Orqaga"),
        ],
    ],
    resize_keyboard=True,
)


@router.message(F.text == "📜 Tarix")
async def history_start(
    message: Message,
    state: FSMContext,
):
    employees = await get_employees()

    keyboard = []

    for employee in employees:
        keyboard.append(
            [KeyboardButton(text=employee.full_name)]
        )

    keyboard.append(
        [KeyboardButton(text="❌ Bekor qilish")]
    )

    await state.set_state(
        FinanceHistory.waiting_employee
    )

    await message.answer(
        "👤 Xodimni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        ),
    )

@router.message(F.text == "💰 Moliya")
async def finance_menu_handler(message: Message):
    await message.answer(
        "💰 Moliya bo'limi",
        reply_markup=finance_menu,
    )


@router.message(F.text == "⬅️ Orqaga")
async def back_menu(message: Message):
    from keyboards.main_menu import super_admin_menu

    await message.answer(
        "Asosiy menyu",
        reply_markup=super_admin_menu(),
    )


@router.message(F.text == "👥 Balanslar")
async def balances_handler(message: Message):

    balances = await get_all_balances()

    if not balances:
        await message.answer("Xodimlar topilmadi.")
        return

    text = "💰 Xodimlar balansi\n\n"

    for item in balances:

        employee = item["employee"]
        balance = item["balance"]

        if balance >= 0:
            status = f"✅ Qoldiq: {balance:,} so'm"
        else:
            status = f"❌ Qarzdor: {abs(balance):,} so'm"

        text += (
            f"👤 {employee.full_name}\n"
            f"{status}\n\n"
        )

    await message.answer(
        text.replace(",", " ")
    )


@router.message(F.text == "➕ Balans to'ldirish")
async def topup_start(
    message: Message,
    state: FSMContext,
):
    employees = await get_employees()

    if not employees:
        await message.answer("Xodim topilmadi.")
        return

    keyboard = []

    for employee in employees:
        keyboard.append(
            [
                KeyboardButton(
                    text=employee.full_name
                )
            ]
        )

    keyboard.append(
        [
            KeyboardButton(text="❌ Bekor qilish")
        ]
    )

    await state.set_state(
        FinanceTopup.waiting_employee
    )

    await message.answer(
        "Xodimni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
        ),
    )


@router.message(
    FinanceTopup.waiting_employee
)
async def topup_employee(
    message: Message,
    state: FSMContext,
):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await finance_menu_handler(message)
        return

    employee = await get_employee_by_name(
        message.text
    )

    if employee is None:
        await message.answer(
            "Xodim topilmadi."
        )
        return

    await state.update_data(
        employee_id=employee.id,
        employee_name=employee.full_name,
    )

    await state.set_state(
        FinanceTopup.waiting_amount
    )

    await message.answer(
        "Summani kiriting:"
    )


@router.message(
    FinanceTopup.waiting_amount
)
async def topup_amount(
    message: Message,
    state: FSMContext,
):
    try:
        amount = int(
            message.text.replace(" ", "")
        )
    except:
        await message.answer(
            "Summani raqamda kiriting."
        )
        return

    await state.update_data(
        amount=amount
    )

    await state.set_state(
        FinanceTopup.waiting_description
    )

    await message.answer(
        "Izoh kiriting (yoki '-' yuboring):"
    )


@router.message(
    FinanceTopup.waiting_description
)
async def topup_description(
    message: Message,
    state: FSMContext,
):
    data = await state.get_data()

    user = await get_user(
        message.from_user.id
    )

    description = ""

    if message.text != "-":
        description = message.text

    await add_topup(
        employee_id=data["employee_id"],
        leader_id=user.id,
        amount=data["amount"],
        description=description,
    )

    await state.clear()

    await message.answer(
        (
            "✅ Balans muvaffaqiyatli to'ldirildi.\n\n"
            f"👤 {data['employee_name']}\n"
            f"💵 {data['amount']:,} so'm"
        ).replace(",", " "),
        reply_markup=finance_menu,
    )


@router.message(FinanceHistory.waiting_employee)
async def history_employee(
    message: Message,
    state: FSMContext,
):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await finance_menu_handler(message)
        return

    employee = await get_employee_by_name(message.text)

    if employee is None:
        await message.answer("Xodim topilmadi.")
        return

    balance = await get_employee_balance(employee.id)

    await message.answer(
        f"👤 {employee.full_name}\n"
        f"💰 Joriy balans: {balance:,} so'm\n\n"
        "Qaysi davr tarixini ko‘rmoqchisiz?".replace(",", " "),
        reply_markup=history_period_keyboard(employee.id),
    )

    await state.clear()

    await message.answer(
        "Moliyaviy bo'lim",
        reply_markup=finance_menu,
    )




def history_period_keyboard(employee_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Oxirgi 3 kun", callback_data=f"finance_history_{employee_id}_3"),
                InlineKeyboardButton(text="Oxirgi 10 kun", callback_data=f"finance_history_{employee_id}_10"),
            ],
            [InlineKeyboardButton(text="📜 Barcha tarix", callback_data=f"finance_history_{employee_id}_all")],
        ]
    )


async def send_history_for_period(message: Message, employee: User, days: int | None):
    history = await get_employee_history_for_period(employee.id, days)
    balance = await get_employee_balance(employee.id)
    period = "Barcha tarix" if days is None else f"Oxirgi {days} kun"
    header = (
        f"👤 {employee.full_name}\n"
        f"📅 {period}\n"
        f"💰 Joriy balans: {balance:,} so'm\n\n"
    ).replace(",", " ")

    if not history:
        await message.answer(header + "📭 Bu davr uchun tarix mavjud emas.")
        return

    chunks = [header]
    for finance in history:
        icon = "🟢" if finance.type == "topup" else "🔴"
        date = (finance.created_at + timedelta(hours=5)).strftime("%d.%m.%Y %H:%M")
        row = (
            f"{icon} {finance.amount:,} so'm\n"
            f"📝 {finance.description or '-'}\n"
            f"📅 {date}\n\n"
        ).replace(",", " ")
        if len(chunks[-1]) + len(row) > 3600:
            chunks.append("")
        chunks[-1] += row

    for chunk in chunks:
        await message.answer(chunk)


@router.callback_query(F.data.startswith("finance_history_"))
async def finance_history_callback(callback: CallbackQuery):
    payload = callback.data.replace("finance_history_", "", 1)
    try:
        employee_id, period = payload.rsplit("_", 1)
        employee_id = int(employee_id)
        days = None if period == "all" else int(period)
        if days not in (None, 3, 10):
            raise ValueError
        employee = await get_user_by_id(employee_id)
    except (ValueError, IndexError):
        # Eski bildirishnomalardagi tugma xodim ismini saqlagan edi.
        # Ular ham ishlashi uchun barcha tarixni ko'rsatamiz.
        employee = await get_employee_by_name(payload)
        days = None
    if employee is None or employee.role != "employee":
        await callback.answer("Xodim topilmadi.", show_alert=True)
        return

    await send_history_for_period(callback.message, employee, days)
    await callback.answer()


@router.message(F.text == "📊 Moliya hisoboti")
async def finance_report_start(message: Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📅 Oxirgi 1 oylik", callback_data="finance_report_30")],
            [InlineKeyboardButton(text="📊 Barcha davrlar", callback_data="finance_report_all")],
        ]
    )
    await message.answer("Excel hisobot uchun davrni tanlang:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("finance_report_"))
async def finance_report_callback(callback: CallbackQuery):
    user = await get_user(callback.from_user.id)
    if user is None or user.role not in ("super_admin", "leader"):
        await callback.answer("Bu hisobot uchun ruxsat yo‘q.", show_alert=True)
        return
    period = callback.data.replace("finance_report_", "")
    if period == "30":
        days, label = 30, "Oxirgi 1 oy"
    elif period == "all":
        days, label = None, "Barcha davrlar"
    else:
        await callback.answer("Davr noto‘g‘ri.", show_alert=True)
        return

    await callback.answer("Hisobot tayyorlanmoqda…")
    rows = await get_finance_report_data(days)
    output = create_finance_report(rows, label)
    await callback.message.answer_document(
        FSInputFile(output),
        caption=f"📊 {label} uchun moliyaviy hisobot",
    )
