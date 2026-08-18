import asyncio

from sqlalchemy import text

from database.database import engine


async def main():
    async with engine.connect() as conn:
        result = await conn.execute(
            text("""
                SELECT id, full_name, phone, active
                FROM users
                WHERE phone = :phone
            """),
            {"phone": "+998776851194"},
        )

        rows = result.fetchall()

        print("TOPILGAN USERLAR:")

        for row in rows:
            print(row)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())