import asyncio

from sqlalchemy import text
from database.database import engine


async def main():
    async with engine.begin() as conn:

        print("1/3 tasks...")

        await conn.execute(text("""
            ALTER TABLE tasks MODIFY (
                "comment" VARCHAR2(1000) NULL,
                photo VARCHAR2(500) NULL
            )
        """))

        print("2/3 task_attachments...")

        await conn.execute(text("""
            ALTER TABLE task_attachments MODIFY (
                file_name VARCHAR2(300) NULL
            )
        """))

        print("3/3 finance...")

        await conn.execute(text("""
            ALTER TABLE finance MODIFY (
                description VARCHAR2(1000) NULL,
                photo VARCHAR2(500) NULL,
                edit_reason VARCHAR2(1000) NULL
            )
        """))

    print()
    print("Oracle ustunlari muvaffaqiyatli o'zgartirildi.")


asyncio.run(main())