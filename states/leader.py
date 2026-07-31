from aiogram.fsm.state import State, StatesGroup


class AddLeader(StatesGroup):
    waiting_name = State()
    waiting_phone = State()


class DeleteLeader(StatesGroup):
    waiting_leader = State()


class FinanceTopup(StatesGroup):
    waiting_employee = State()
    waiting_amount = State()
    waiting_description = State()