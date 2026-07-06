import asyncio

from aiogram import Bot
from aiogram import Dispatcher

from config import BOT_TOKEN

from handlers.start import router
from handlers.leaders import router as leaders_router
from handlers.employees import router as employees_router
from handlers.leaders_delete import router as leaders_delete_router
from handlers.employees_delete import router as employees_delete_router

from database.init_db import init_db


bot = Bot(BOT_TOKEN)

dp = Dispatcher()

dp.include_router(router)
dp.include_router(leaders_router)
dp.include_router(employees_router)
dp.include_router(leaders_delete_router)
dp.include_router(employees_delete_router)


async def main():

    await init_db()

    print("===================================")
    print("TaskFlow Bot ishga tushdi")
    print("===================================")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())