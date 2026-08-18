from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext

from sqlalchemy import select

from database.database import SessionLocal
from models.task import Task
from models.user import User

from states.employee import ExpenseFSM
from states.task import CompleteTask
from services.finance_service import get_employee_balance, add_expense
from services.user_service import get_user, get_leader_by_id
from services.notification_service import send_expense_notification
from keyboards.main_menu import employee_menu
from services.user_service import get_super_admin


router = Router()


# ============================================================
# XODIMNING VAZIFALARI
# ============================================================

@router.message(F.text == "📋 Mening vazifalarim")
async def my_tasks(message: Message):

    user = await get_user(message.from_user.id)

    if user is None:
        await message.answer("❌ Siz tizimga kirmagansiz.")
        return

    async with SessionLocal() as session:

        result = await session.execute(
            select(Task)
            .where(Task.employee_id == user.id)
        )

        tasks = result.scalars().all()

    if not tasks:
        await message.answer(
            "📋 Sizga hozircha vazifa biriktirilmagan."
        )
        return

    new_count = sum(
        1 for task in tasks
        if task.status == "Yangi"
    )

    checking_count = sum(
        1 for task in tasks
        if task.status == "Tekshirilmoqda"
    )

    rework_count = sum(
        1 for task in tasks
        if task.status == "Qayta ishlashda"
    )

    completed_count = sum(
        1 for task in tasks
        if task.status == "Bajarildi"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🔵 Yangi ({new_count})",
                    callback_data="mytasks_status_Yangi",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🟡 Tekshirilayotgan ({checking_count})",
                    callback_data="mytasks_status_Tekshirilmoqda",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🔄 Qayta ko‘rish ({rework_count})",
                    callback_data="mytasks_status_Qayta ishlashda",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🟢 Bajarilgan ({completed_count})",
                    callback_data="mytasks_status_Bajarildi",
                )
            ],
        ]
    )

    await message.answer(
        "📋 <b>MENING VAZIFALARIM</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )


# ============================================================
# STATUS BO‘YICHA VAZIFALAR
# ============================================================

@router.callback_query(
    F.data.startswith("mytasks_status_")
)
async def my_tasks_by_status(callback: CallbackQuery):

    user = await get_user(callback.from_user.id)

    if user is None:
        await callback.answer(
            "❌ Siz tizimga kirmagansiz.",
            show_alert=True,
        )
        return

    status = callback.data.replace(
        "mytasks_status_",
        "",
        1,
    )

    async with SessionLocal() as session:

        result = await session.execute(
            select(Task)
            .where(
                Task.employee_id == user.id,
                Task.status == status,
            )
            .order_by(Task.id.desc())
        )

        tasks = result.scalars().all()

    status_titles = {
        "Yangi": "🔵 YANGI VAZIFALAR",
        "Tekshirilmoqda": "🟡 TEKSHIRILAYOTGAN VAZIFALAR",
        "Qayta ishlashda": "🔄 QAYTA KO‘RISH KERAK",
        "Bajarildi": "🟢 BAJARILGAN VAZIFALAR",
    }

    title = status_titles.get(
        status,
        "📋 VAZIFALAR",
    )

    if not tasks:

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Vazifalar bo‘limiga",
                        callback_data="mytasks_menu",
                    )
                ]
            ]
        )

        await callback.message.edit_text(
            f"{title}\n\n"
            "Bu bo‘limda hozircha vazifalar yo‘q.",
            reply_markup=keyboard,
        )

        await callback.answer()
        return

    keyboard = []

    for task in tasks:

        task_name = task.task_name or "Nomsiz vazifa"

        if len(task_name) > 35:
            task_name = task_name[:35] + "..."

        keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"#{task.id} • {task_name}",
                    callback_data=f"mytask_open_{task.id}",
                )
            ]
        )

    keyboard.append(
        [
            InlineKeyboardButton(
                text="🔙 Vazifalar bo‘limiga",
                callback_data="mytasks_menu",
            )
        ]
    )

    await callback.message.edit_text(
        f"{title}\n\n"
        f"Jami: <b>{len(tasks)} ta</b>\n\n"
        "Vazifani tanlang:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard
        ),
        parse_mode="HTML",
    )

    await callback.answer()


# ============================================================
# VAZIFALAR MENYUSIGA QAYTISH
# ============================================================

@router.callback_query(
    F.data == "mytasks_menu"
)
async def my_tasks_menu(callback: CallbackQuery):

    user = await get_user(callback.from_user.id)

    if user is None:
        await callback.answer(
            "❌ Siz tizimga kirmagansiz.",
            show_alert=True,
        )
        return

    async with SessionLocal() as session:

        result = await session.execute(
            select(Task)
            .where(Task.employee_id == user.id)
        )

        tasks = result.scalars().all()

    new_count = sum(
        1 for task in tasks
        if task.status == "Yangi"
    )

    checking_count = sum(
        1 for task in tasks
        if task.status == "Tekshirilmoqda"
    )

    rework_count = sum(
        1 for task in tasks
        if task.status == "Qayta ishlashda"
    )

    completed_count = sum(
        1 for task in tasks
        if task.status == "Bajarildi"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"🔵 Yangi ({new_count})",
                    callback_data="mytasks_status_Yangi",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🟡 Tekshirilayotgan ({checking_count})",
                    callback_data="mytasks_status_Tekshirilmoqda",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🔄 Qayta ko‘rish ({rework_count})",
                    callback_data="mytasks_status_Qayta ishlashda",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"🟢 Bajarilgan ({completed_count})",
                    callback_data="mytasks_status_Bajarildi",
                )
            ],
        ]
    )

    await callback.message.edit_text(
        "📋 <b>MENING VAZIFALARIM</b>\n\n"
        "Kerakli bo‘limni tanlang:",
        reply_markup=keyboard,
        parse_mode="HTML",
    )

    await callback.answer()


# ============================================================
# VAZIFA KARTASI
# ============================================================

@router.callback_query(
    F.data.startswith("mytask_open_")
)
async def open_employee_task(callback: CallbackQuery):

    try:
        task_id = int(
            callback.data.replace(
                "mytask_open_",
                "",
                1,
            )
        )
    except ValueError:

        await callback.answer(
            "❌ Vazifa ID noto‘g‘ri.",
            show_alert=True,
        )
        return

    user = await get_user(callback.from_user.id)

    if user is None:
        await callback.answer(
            "❌ Siz tizimga kirmagansiz.",
            show_alert=True,
        )
        return

    async with SessionLocal() as session:

        task = await session.get(
            Task,
            task_id,
        )

        if task is None or task.employee_id != user.id:

            await callback.answer(
                "❌ Vazifa topilmadi.",
                show_alert=True,
            )
            return

        leader = await session.get(
            User,
            task.leader_id,
        )

    status_icons = {
        "Yangi": "🔵",
        "Tekshirilmoqda": "🟡",
        "Qayta ishlashda": "🔄",
        "Bajarildi": "🟢",
    }

    status_icon = status_icons.get(
        task.status,
        "📌",
    )

    text = (
        f"📋 <b>VAZIFA #{task.id}</b>\n\n"
        f"🏢 <b>Obyekt:</b> {task.object_name}\n"
        f"📌 <b>Vazifa:</b> {task.task_name}\n\n"
        f"👨‍💼 <b>Rahbar:</b> "
        f"{leader.full_name if leader else 'Nomaʼlum'}\n"
        f"📅 <b>Muddat:</b> {task.deadline}\n"
        f"⚠️ <b>Muhimlik:</b> {task.priority}\n"
        f"{status_icon} <b>Holati:</b> {task.status}\n\n"
        f"💬 <b>Izoh:</b>\n"
        f"{task.comment or '-'}"
    )

    keyboard_rows = []

    # Yangi yoki qayta ishlashdagi vazifani
    # xodim bajarishi mumkin
    if task.status in (
        "Yangi",
        "Qayta ishlashda",
    ):

        keyboard_rows.append(
            [
                InlineKeyboardButton(
                    text="✅ Vazifani yakunlash",
                    callback_data=f"mytask_complete_{task.id}",
                )
            ]
        )

    keyboard_rows.append(
        [
            InlineKeyboardButton(
                text="🔙 Orqaga",
                callback_data=f"mytasks_status_{task.status}",
            )
        ]
    )

    await callback.message.edit_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=keyboard_rows
        ),
        parse_mode="HTML",
    )

    await callback.answer()

# ============================================================
# VAZIFANI YAKUNLASHNI BOSHLASH
# ============================================================

@router.callback_query(
    F.data.startswith("mytask_complete_")
)
async def start_task_completion(
    callback: CallbackQuery,
    state: FSMContext,
):

    try:
        task_id = int(
            callback.data.replace(
                "mytask_complete_",
                "",
                1,
            )
        )
    except ValueError:

        await callback.answer(
            "❌ Vazifa ID noto‘g‘ri.",
            show_alert=True,
        )
        return

    user = await get_user(
        callback.from_user.id
    )

    if user is None:
        await callback.answer(
            "❌ Siz tizimga kirmagansiz.",
            show_alert=True,
        )
        return

    async with SessionLocal() as session:

        task = await session.get(
            Task,
            task_id,
        )

        if task is None:
            await callback.answer(
                "❌ Vazifa topilmadi.",
                show_alert=True,
            )
            return

        if task.employee_id != user.id:
            await callback.answer(
                "❌ Bu vazifa sizga tegishli emas.",
                show_alert=True,
            )
            return

        if task.status not in (
            "Yangi",
            "Qayta ishlashda",
        ):
            await callback.answer(
                "❌ Bu vazifani hozir yakunlab bo‘lmaydi.",
                show_alert=True,
            )
            return

    await state.update_data(
        task_id=task_id
    )

    await state.set_state(
        CompleteTask.waiting_photo
    )

    await callback.message.answer(
        "📎 <b>Hisobot faylini yuboring.</b>\n\n"
        "🖼 Rasm\n"
        "🎥 Video\n"
        "🎤 Ovoz\n"
        "🎬 Video message\n"
        "📄 PDF yoki boshqa hujjat\n\n"
        "(Hozircha bir dona fayl yuboring.)",
        parse_mode="HTML",
    )

    await callback.answer()    


# ============================================================
# BALANS
# ============================================================

@router.message(F.text == "💰 Balansim")
async def balance_handler(message: Message):

    user = await get_user(message.from_user.id)

    if user is None:
        await message.answer(
            "❌ Siz tizimga kirmagansiz."
        )
        return

    balance = await get_employee_balance(user.id)

    if balance >= 0:
        txt = (
            f"💰 <b>Balansingiz:</b>\n\n"
            f"{balance:,} so'm"
        )
    else:
        txt = (
            f"❌ <b>Qarzingiz:</b>\n\n"
            f"{abs(balance):,} so'm"
        )

    await message.answer(
        txt.replace(",", " "),
        parse_mode="HTML",
    )


# ============================================================
# XARAJAT QO‘SHISH
# ============================================================

@router.message(F.text == "💸 Xarajat qo'shish")
async def expense_start(
    message: Message,
    state: FSMContext,
):

    await state.set_state(
        ExpenseFSM.waiting_amount
    )

    await message.answer(
        "💵 Summani kiriting:"
    )


@router.message(
    ExpenseFSM.waiting_amount
)
async def expense_amount(
    message: Message,
    state: FSMContext,
):

    try:
        amount = int(
            message.text.replace(" ", "")
        )
    except Exception:

        await message.answer(
            "Summani raqamda kiriting."
        )
        return

    await state.update_data(
        amount=amount
    )

    await state.set_state(
        ExpenseFSM.waiting_description
    )

    await message.answer(
        "📋 Izoh yozing.\n\n"
        "📎 Agar rasm yoki hujjat bo'lsa, "
        "shu xabarga biriktirib yuboring.\n"
        "Rasm bo'lmasa oddiy matn yuboring."
    )


@router.message(
    ExpenseFSM.waiting_description
)
async def expense_finish(
    message: Message,
    state: FSMContext,
):

    data = await state.get_data()

    user = await get_user(
        message.from_user.id
    )

    description = (
        message.caption
        or message.text
        or ""
    )

    photo = ""

    if message.photo:
        photo = message.photo[-1].file_id

    elif message.document:
        photo = message.document.file_id

    await add_expense(
        employee_id=user.id,
        leader_id=user.leader_id,
        task_id=None,
        amount=data["amount"],
        description=description,
        photo=photo,
    )

    balance = await get_employee_balance(
        user.id
    )

    leader = await get_leader_by_id(
        user.leader_id
    )

    if leader and leader.telegram_id:

        await send_expense_notification(
            telegram_id=leader.telegram_id,
            employee_id=user.id,
            employee_name=user.full_name,
            amount=data["amount"],
            description=description,
            balance=balance,
            photo=photo if photo else None,
        )

    admin = await get_super_admin()

    if (
        admin
        and admin.telegram_id
        and (
            not leader
            or admin.telegram_id != leader.telegram_id
        )
    ):

        await send_expense_notification(
            telegram_id=admin.telegram_id,
            employee_id=user.id,
            employee_name=user.full_name,
            amount=data["amount"],
            description=description,
            balance=balance,
            photo=photo if photo else None,
        )

    await state.clear()

    await message.answer(
        "✅ Xarajat muvaffaqiyatli saqlandi.",
        reply_markup=employee_menu(),
    )