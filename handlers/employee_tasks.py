from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from database.database import SessionLocal
from models.task import Task
from models.user import User
from states.employee import ExpenseFSM
from services.finance_service import get_employee_balance, add_expense
from services.user_service import get_user, get_leader_by_id
from services.notification_service import send_expense_notification
from keyboards.main_menu import employee_menu
from services.user_service import get_super_admin

router = Router()

@router.message(F.text == "📋 Mening vazifalarim")
async def my_tasks(message: Message):
    user = await get_user(message.from_user.id)
    if user is None:
        await message.answer("❌ Siz tizimga kirmagansiz.")
        return
    async with SessionLocal() as session:
        result = await session.execute(select(Task).where(Task.employee_id == user.id).order_by(Task.id.desc()))
        tasks = result.scalars().all()
        if not tasks:
            await message.answer("📭 Sizga vazifa biriktirilmagan.")
            return
        text="📋 Mening vazifalarim\n\n"
        for task in tasks:
            leader=await session.get(User,task.leader_id)
            leader_name=leader.full_name if leader else "Noma'lum"
            text += f"🆔 {task.id}\n🏢 Obyekt: {task.object_name}\n📝 Vazifa: {task.task_name}\n👨‍💼 Rahbar: {leader_name}\n📅 Muddat: {task.deadline}\n⚠️ Muhimlik: {task.priority}\n📌 Holati: {task.status}\n\n━━━━━━━━━━━━━━\n\n"
        await message.answer(text)

@router.message(F.text=="💳 Balansim")
async def balance_handler(message: Message):
    user=await get_user(message.from_user.id)
    balance=await get_employee_balance(user.id)
    txt=f"💰 Balansingiz:\n\n{balance:,} so'm" if balance>=0 else f"❌ Qarzingiz:\n\n{abs(balance):,} so'm"
    await message.answer(txt.replace(","," "))

@router.message(F.text=="💸 Xarajat qo'shish")
async def expense_start(message: Message,state:FSMContext):
    await state.set_state(ExpenseFSM.waiting_amount)
    await message.answer("💵 Summani kiriting:")

@router.message(ExpenseFSM.waiting_amount)
async def expense_amount(message: Message,state:FSMContext):
    try:
        amount=int(message.text.replace(" ",""))
    except:
        await message.answer("Summani raqamda kiriting.")
        return
    await state.update_data(amount=amount)
    await state.set_state(ExpenseFSM.waiting_description)
    await message.answer("📝 Izoh yozing.\n\n📎 Agar rasm yoki hujjat bo'lsa, shu xabarga biriktirib yuboring.\nRasm bo'lmasa oddiy matn yuboring.")

@router.message(ExpenseFSM.waiting_description)
async def expense_finish(message: Message,state:FSMContext):
    data=await state.get_data()
    user=await get_user(message.from_user.id)
    description=message.caption or message.text or ""
    photo=""
    if message.photo:
        photo=message.photo[-1].file_id
    elif message.document:
        photo=message.document.file_id
    await add_expense(employee_id=user.id,leader_id=user.leader_id,task_id=None,amount=data["amount"],description=description,photo=photo)
    balance=await get_employee_balance(user.id)
    leader=await get_leader_by_id(user.leader_id)
    if leader and leader.telegram_id:
        await send_expense_notification(telegram_id=leader.telegram_id,employee_name=user.full_name,amount=data["amount"],description=description,balance=balance,photo=photo if photo else None)
    admin = await get_super_admin()

    if (
        admin
        and admin.telegram_id
        and (not leader or admin.telegram_id != leader.telegram_id)
    ):
        await send_expense_notification(
            telegram_id=admin.telegram_id,
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
