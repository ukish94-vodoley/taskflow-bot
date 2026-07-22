from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext

from states.leader import AddLeader
from services.user_service import create_leader, get_leaders
from config import SUPER_ADMIN_ID
from keyboards.main_menu import super_admin_menu

router = Router()

leaders_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="➕ Rahbar qo'shish")],
        [KeyboardButton(text="📋 Rahbarlar ro'yxati")],
        [KeyboardButton(text="❌ Rahbarni o'chirish")],
        [KeyboardButton(text="⬅️ Orqaga")],
    ],
    resize_keyboard=True,
)


@router.message(F.text == "👥 Rahbarlar")
async def leaders(message: Message):
    await message.answer(
        "👥 Rahbarlar bo'limi",
        reply_markup=leaders_menu,
    )


@router.message(F.text == "➕ Rahbar qo'shish")
async def add_leader(message: Message, state: FSMContext):
    await state.set_state(AddLeader.waiting_name)
    await message.answer("👤 Rahbarning ismini kiriting:")


@router.message(AddLeader.waiting_name)
async def leader_name(message: Message, state: FSMContext):

    if message.text == "⬅️ Orqaga":

        await state.clear()

        await message.answer(
            "👥 Rahbarlar bo'limi",
            reply_markup=leaders_menu,
        )

        return

    await state.update_data(
        full_name=message.text
    )

    await state.set_state(
        AddLeader.waiting_phone
    )

    await message.answer(
        "📱 Telefon raqamini kiriting:"
    )


@router.message(AddLeader.waiting_phone)
async def leader_phone(message: Message, state: FSMContext):
    if message.text == "⬅️ Orqaga":

        await state.clear()

        await message.answer(
            "👥 Rahbarlar bo'limi",
            reply_markup=leaders_menu,
        )

        return
    
    data = await state.get_data()

    await create_leader(
        full_name=data["full_name"],
        phone=message.text,
    )

    await state.clear()

    await message.answer(
        "✅ Rahbar muvaffaqiyatli qo'shildi.",
        reply_markup=leaders_menu,
    )


@router.message(F.text == "📋 Rahbarlar ro'yxati")
async def leaders_list(message: Message):
    leaders = await get_leaders()

    if not leaders:
        await message.answer("Rahbarlar topilmadi.")
        return

    text = "👨‍💼 Rahbarlar ro'yxati\n\n"

    for i, leader in enumerate(leaders, start=1):
        text += f"{i}. {leader.full_name}\n📱 {leader.phone}\n\n"

    await message.answer(text)