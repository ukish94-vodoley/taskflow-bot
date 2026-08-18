import asyncio

from sqlalchemy import text

from database.database import engine


async def main():
    async with engine.connect() as conn:

        result = await conn.execute(
            text("SELECT MAX(id) FROM users")
        )

        max_id = result.scalar() or 0

        print(f"Users MAX ID: {max_id}")

        result = await conn.execute(
            text("SELECT users_id_seq.NEXTVAL FROM dual")
        )

        next_value = result.scalar()

        print(f"Users sequence NEXTVAL: {next_value}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())