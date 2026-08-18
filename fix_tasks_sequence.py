import asyncio

from sqlalchemy import text

from database.database import engine


async def main():
    async with engine.begin() as conn:

        result = await conn.execute(
            text("SELECT MAX(id) FROM tasks")
        )

        max_id = result.scalar() or 0
        next_id = max_id + 1

        print(f"Tasks MAX ID: {max_id}")
        print(f"Sequence yangi qiymati: {next_id}")

        await conn.execute(
            text("DROP SEQUENCE tasks_id_seq")
        )

        await conn.execute(
            text(
                f"""
                CREATE SEQUENCE tasks_id_seq
                START WITH {next_id}
                INCREMENT BY 1
                NOCACHE
                """
            )
        )

        print("tasks_id_seq muvaffaqiyatli tuzatildi.")


if __name__ == "__main__":
    asyncio.run(main())