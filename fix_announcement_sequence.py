import asyncio

from sqlalchemy import text

from database.database import engine


async def main():
    async with engine.begin() as conn:
        result = await conn.execute(
            text("""
                SELECT COUNT(*)
                FROM user_sequences
                WHERE sequence_name = 'ANNOUNCEMENTS_ID_SEQ'
            """)
        )

        exists = result.scalar()

        if exists:
            print("ANNOUNCEMENTS_ID_SEQ allaqachon mavjud.")
        else:
            await conn.execute(
                text("""
                    CREATE SEQUENCE announcements_id_seq
                    START WITH 7
                    INCREMENT BY 1
                    NOCACHE
                """)
            )
            print("ANNOUNCEMENTS_ID_SEQ yaratildi.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())