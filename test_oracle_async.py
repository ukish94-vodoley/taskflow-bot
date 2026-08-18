import asyncio

from sqlalchemy import text

from database.database import engine


async def main():
    async with engine.connect() as conn:

        result = await conn.execute(
            text("SELECT COUNT(*) FROM users")
        )

        users_count = result.scalar()

        result = await conn.execute(
            text("SELECT COUNT(*) FROM tasks")
        )

        tasks_count = result.scalar()

        result = await conn.execute(
            text("SELECT COUNT(*) FROM finance")
        )

        finance_count = result.scalar()

        print("=" * 50)
        print("ORACLE TEST")
        print("=" * 50)

        print("Users:", users_count)
        print("Tasks:", tasks_count)
        print("Finance:", finance_count)

        print("=" * 50)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())