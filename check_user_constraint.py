import asyncio

from sqlalchemy import text

from database.database import engine


async def main():
    async with engine.connect() as conn:

        result = await conn.execute(
            text("""
                SELECT
                    constraint_name,
                    constraint_type,
                    table_name
                FROM user_constraints
                WHERE constraint_name = 'SYS_C0024339'
            """)
        )

        print("CONSTRAINT:")
        for row in result.fetchall():
            print(row)

        result = await conn.execute(
            text("""
                SELECT
                    constraint_name,
                    column_name,
                    position
                FROM user_cons_columns
                WHERE constraint_name = 'SYS_C0024339'
                ORDER BY position
            """)
        )

        print("\nCOLUMNS:")
        for row in result.fetchall():
            print(row)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())