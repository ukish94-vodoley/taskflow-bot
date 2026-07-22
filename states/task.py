from aiogram.fsm.state import State, StatesGroup


class AddTask(StatesGroup):

    waiting_object = State()
    waiting_task = State()
    waiting_employees = State()
    waiting_files = State()
    waiting_deadline = State()
    waiting_priority = State()
    waiting_confirm = State()


class DeleteTask(StatesGroup):

    waiting_task = State()


class CompleteTask(StatesGroup):

    waiting_task = State()
    waiting_photo = State()
    waiting_comment = State()


class ReviewTask(StatesGroup):

    waiting_task = State()
    waiting_action = State()
    waiting_reason = State()