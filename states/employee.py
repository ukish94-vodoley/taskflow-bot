from aiogram.fsm.state import State, StatesGroup


class AddEmployee(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_leader = State()


class DeleteEmployee(StatesGroup):
    waiting_employee = State()