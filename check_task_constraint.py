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
                WHERE constraint_name = 'SYS_C0024354'
            """)
        )

        rows = result.fetchall()

        print("CONSTRAINT:")
        for row in rows:
            print(row)

        result = await conn.execute(
            text("""
                SELECT
                    constraint_name,
                    column_name,
                    position
                FROM user_cons_columns
                WHERE constraint_name = 'SYS_C0024354'
                ORDER BY position
            """)
        )

        print("\nCOLUMNS:")
        for row in result.fetchall():
            print(row)

        result = await conn.execute(
            text("""
                SELECT
                    MAX(id) AS max_id
                FROM tasks
            """)
        )

        print("\nTASK MAX ID:")
        print(result.scalar())

        result = await conn.execute(
            text("""
                SELECT
                    tasks_id_seq.NEXTVAL
                FROM dual
            """)
        )

        print("\nNEXT SEQUENCE VALUE:")
        print(result.scalar())

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())