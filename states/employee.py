from aiogram.fsm.state import State, StatesGroup


class AddEmployee(StatesGroup):
    waiting_name = State()
    waiting_phone = State()
    waiting_leader = State()


class DeleteEmployee(StatesGroup):
    waiting_employee = State()


class FinanceTopup(StatesGroup):
    waiting_employee = State()
    waiting_amount = State()
    waiting_description = State()


class ExpenseFSM(StatesGroup):
    waiting_amount = State()
    waiting_description = State()


class FinanceHistory(StatesGroup):
    waiting_employee = State()    


class FinanceReport(StatesGroup):
    waiting_type = State()
    waiting_employee = State()
    waiting_period = State()
    waiting_year = State()
    waiting_month = State()         


class ExpenseEditFSM(StatesGroup):
    waiting_history = State()
    waiting_reason = State()
    waiting_amount = State()
