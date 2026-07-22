import asyncio

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN

from handlers.start import router
from handlers.auth import router as auth_router

from handlers.leaders import router as leaders_router
from handlers.leaders_delete import router as leaders_delete_router

from handlers.employees import router as employees_router
from handlers.employees_delete import router as employees_delete_router

from handlers.tasks import router as tasks_router
from handlers.tasks_create import router as tasks_create_router
from handlers.tasks_list import router as tasks_list_router
from handlers.tasks_delete import router as tasks_delete_router
from handlers.task_complete import router as task_complete_router
from handlers.employee_tasks import router as employee_tasks_router
from handlers.leader_review import router as leader_review_router
from handlers.task_callbacks import router as task_callbacks_router
from handlers.task_card import router as task_card_router

from handlers.report import router as report_router
from handlers.search import router as search_router

from handlers.back import router as back_router

from database.init_db import init_db

from scheduler import start_scheduler

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

dp.include_router(router)
dp.include_router(auth_router)
dp.include_router(leaders_router)
dp.include_router(leaders_delete_router)
dp.include_router(employees_router)
dp.include_router(employees_delete_router)
dp.include_router(tasks_router)
dp.include_router(tasks_create_router)
dp.include_router(tasks_list_router)
dp.include_router(tasks_delete_router)
dp.include_router(employee_tasks_router)
dp.include_router(task_complete_router)
dp.include_router(leader_review_router)
dp.include_router(task_callbacks_router)
dp.include_router(task_card_router)
dp.include_router(report_router)
dp.include_router(search_router)
dp.include_router(back_router)


async def main():
    await init_db()

    start_scheduler()

    print("===================================")
    print("TaskFlow Bot ishga tushdi")
    print("===================================")
    print("✅ Scheduler ishga tushdi")
    print("===================================")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())