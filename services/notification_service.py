from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import BOT_TOKEN

bot = Bot(BOT_TOKEN)


async def send_task_notification(
    telegram_id: int,
    task_id: int,
    object_name: str,
    task_name: str,
    deadline: str,
    priority: str,
):

    if not telegram_id:
        return

    doc_no = f"DOC-{task_id:06d}"

    text = (
        "🔔 Sizga yangi vazifa biriktirildi.\n\n"
        f"🆔 {doc_no}\n\n"
        f"🏢 Obyekt: {object_name}\n"
        f"📝 Vazifa: {task_name}\n"
        f"📅 Muddat: {deadline}\n"
        f"⚠️ Muhimlik: {priority}"
    )

    try:
        await bot.send_message(
            telegram_id,
            text,
        )
    except Exception:
        pass


async def send_completed_notification(
    telegram_id: int,
    task_id: int,
    employee_name: str,
    object_name: str,
    task_name: str,
):

    if not telegram_id:
        return

    doc_no = f"DOC-{task_id:06d}"

    text = (
        "✅ Vazifa bajarildi.\n\n"
        f"🆔 {doc_no}\n\n"
        f"👷 Xodim: {employee_name}\n"
        f"🏢 Obyekt: {object_name}\n"
        f"📝 Vazifa: {task_name}"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash",
                    callback_data=f"approve_{task_id}",
                ),
                InlineKeyboardButton(
                    text="🔄 Qayta ishlash",
                    callback_data=f"return_{task_id}",
                ),
            ]
        ]
    )

    try:
        await bot.send_message(
            telegram_id,
            text,
            reply_markup=keyboard,
        )
    except Exception:
        pass


async def send_reminder_notification(
    telegram_id: int,
    employee_name: str,
    tasks: list,
):

    if not telegram_id:
        return

    text = (
        f"🔔 Assalomu alaykum, {employee_name}!\n\n"
        "Sizda bajarilmagan vazifalar mavjud:\n\n"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[]
    )

    for task in tasks:

        doc_no = f"DOC-{task['id']:06d}"

        text += (
            f"🆔 {doc_no}\n"
            f"🏢 {task['object']}\n"
            f"📝 {task['task']}\n"
            f"📅 {task['deadline']}\n"
            f"⚠️ {task['priority']}\n\n"
        )

        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text=f"📂 DOC-{task['id']:06d} ni ochish",
                    callback_data=f"task_{task['id']}",
                )
            ]
        )

    text += "✅ Vazifani bajarganingizdan so'ng bot orqali tasdiqlang."

    try:
        await bot.send_message(
            telegram_id,
            text,
            reply_markup=keyboard,
        )
    except Exception:
        pass