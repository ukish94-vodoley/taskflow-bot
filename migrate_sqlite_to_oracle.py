import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


load_dotenv()

SQLITE_DB = "taskflow.db"

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")


if not ORACLE_USER or not ORACLE_PASSWORD or not ORACLE_DSN:
    raise RuntimeError(
        "ORACLE_USER, ORACLE_PASSWORD yoki ORACLE_DSN .env faylida topilmadi."
    )


sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_conn.row_factory = sqlite3.Row


oracle_engine = create_engine(
    "oracle+oracledb://",
    connect_args={
        "user": ORACLE_USER,
        "password": ORACLE_PASSWORD,
        "dsn": ORACLE_DSN,
    },
)


def convert_datetime(value):
    if value is None:
        return None

    if isinstance(value, datetime):
        return value

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return None

        return datetime.fromisoformat(value)

    return value


def migrate_users(conn):
    print("\n[users]")

    rows = sqlite_conn.execute(
        "SELECT * FROM users ORDER BY id"
    ).fetchall()

    sql = text("""
        INSERT INTO users (
            id,
            telegram_id,
            full_name,
            phone,
            role,
            leader_id,
            active,
            created_at
        )
        VALUES (
            :id,
            :telegram_id,
            :full_name,
            :phone,
            :role,
            :leader_id,
            :active,
            :created_at
        )
    """)

    for row in rows:
        conn.execute(
            sql,
            {
                "id": row["id"],
                "telegram_id": row["telegram_id"],
                "full_name": row["full_name"],
                "phone": row["phone"],
                "role": row["role"],
                "leader_id": row["leader_id"],
                "active": row["active"],
                "created_at": convert_datetime(row["created_at"]),
            },
        )

    print(f"  {len(rows)} ta yozuv ko'chirildi.")
    return len(rows)


def migrate_tasks(conn):
    print("\n[tasks]")

    rows = sqlite_conn.execute(
        "SELECT * FROM tasks ORDER BY id"
    ).fetchall()

    sql = text("""
        INSERT INTO tasks (
            id,
            object_name,
            task_name,
            leader_id,
            employee_id,
            deadline,
            priority,
            status,
            "comment",
            photo,
            created_at,
            completed_at
        )
        VALUES (
            :p_id,
            :p_object_name,
            :p_task_name,
            :p_leader_id,
            :p_employee_id,
            :p_deadline,
            :p_priority,
            :p_status,
            :p_comment,
            :p_photo,
            :p_created_at,
            :p_completed_at
        )
    """)

    for row in rows:
        comment = row["comment"]

        if comment is None:
            comment = ""

        photo = row["photo"]

        if photo is None:
            photo = ""

        status = row["status"]

        if status is None:
            status = "Yangi"

        conn.execute(
            sql,
            {
                "p_id": row["id"],
                "p_object_name": row["object_name"],
                "p_task_name": row["task_name"],
                "p_leader_id": row["leader_id"],
                "p_employee_id": row["employee_id"],
                "p_deadline": row["deadline"],
                "p_priority": row["priority"],
                "p_status": status,
                "p_comment": comment,
                "p_photo": photo,
                "p_created_at": convert_datetime(
                    row["created_at"]
                ),
                "p_completed_at": convert_datetime(
                    row["completed_at"]
                ),
            },
        )

    print(f"  {len(rows)} ta yozuv ko'chirildi.")
    return len(rows)


def migrate_task_attachments(conn):
    print("\n[task_attachments]")

    rows = sqlite_conn.execute(
        "SELECT * FROM task_attachments ORDER BY id"
    ).fetchall()

    if not rows:
        print("  0 ta yozuv — o'tkazilmadi.")
        return 0

    sql = text("""
        INSERT INTO task_attachments (
            id,
            task_id,
            file_id,
            file_name,
            file_type,
            created_at
        )
        VALUES (
            :id,
            :task_id,
            :file_id,
            :file_name,
            :file_type,
            :created_at
        )
    """)

    for row in rows:
        conn.execute(
            sql,
            {
                "id": row["id"],
                "task_id": row["task_id"],
                "file_id": row["file_id"],
                "file_name": row["file_name"] or "",
                "file_type": row["file_type"],
                "created_at": convert_datetime(
                    row["created_at"]
                ),
            },
        )

    print(f"  {len(rows)} ta yozuv ko'chirildi.")
    return len(rows)


def migrate_finance(conn):
    print("\n[finance]")

    rows = sqlite_conn.execute(
        "SELECT * FROM finance ORDER BY id"
    ).fetchall()

    sql = text("""
        INSERT INTO finance (
            id,
            employee_id,
            leader_id,
            task_id,
            type,
            amount,
            description,
            photo,
            created_at,
            status,
            edited,
            old_amount,
            edit_reason,
            approved_by,
            approved_at,
            edited_at
        )
        VALUES (
            :id,
            :employee_id,
            :leader_id,
            :task_id,
            :type,
            :amount,
            :description,
            :photo,
            :created_at,
            :status,
            :edited,
            :old_amount,
            :edit_reason,
            :approved_by,
            :approved_at,
            :edited_at
        )
    """)

    for row in rows:
        conn.execute(
            sql,
            {
                "id": row["id"],
                "employee_id": row["employee_id"],
                "leader_id": row["leader_id"],
                "task_id": row["task_id"],
                "type": row["type"],
                "amount": row["amount"],
                "description": row["description"] or "",
                "photo": row["photo"] or "",
                "created_at": convert_datetime(
                    row["created_at"]
                ),
                "status": row["status"] or "approved",
                "edited": row["edited"] or 0,
                "old_amount": row["old_amount"],
                "edit_reason": row["edit_reason"] or "",
                "approved_by": row["approved_by"],
                "approved_at": convert_datetime(
                    row["approved_at"]
                ),
                "edited_at": convert_datetime(
                    row["edited_at"]
                ),
            },
        )

    print(f"  {len(rows)} ta yozuv ko'chirildi.")
    return len(rows)


def migrate_announcements(conn):
    print("\n[announcements]")

    rows = sqlite_conn.execute(
        "SELECT * FROM announcements ORDER BY id"
    ).fetchall()

    if not rows:
        print("  0 ta yozuv — o'tkazilmadi.")
        return 0

    sql = text("""
        INSERT INTO announcements (
            id,
            title,
            body,
            author_id,
            active,
            created_at
        )
        VALUES (
            :id,
            :title,
            :body,
            :author_id,
            :active,
            :created_at
        )
    """)

    for row in rows:
        conn.execute(
            sql,
            {
                "id": row["id"],
                "title": row["title"],
                "body": row["body"],
                "author_id": row["author_id"],
                "active": row["active"],
                "created_at": convert_datetime(
                    row["created_at"]
                ),
            },
        )

    print(f"  {len(rows)} ta yozuv ko'chirildi.")
    return len(rows)


def migrate_web_login_codes(conn):
    print("\n[web_login_codes]")

    rows = sqlite_conn.execute(
        "SELECT * FROM web_login_codes ORDER BY id"
    ).fetchall()

    if not rows:
        print("  0 ta yozuv — o'tkazilmadi.")
        return 0

    sql = text("""
        INSERT INTO web_login_codes (
            id,
            user_id,
            code_hash,
            expires_at,
            used_at,
            created_at
        )
        VALUES (
            :id,
            :user_id,
            :code_hash,
            :expires_at,
            :used_at,
            :created_at
        )
    """)

    for row in rows:
        conn.execute(
            sql,
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "code_hash": row["code_hash"],
                "expires_at": convert_datetime(
                    row["expires_at"]
                ),
                "used_at": convert_datetime(
                    row["used_at"]
                ),
                "created_at": convert_datetime(
                    row["created_at"]
                ),
            },
        )

    print(f"  {len(rows)} ta yozuv ko'chirildi.")
    return len(rows)


def reset_sequence(conn, table_name):
    sequence_name = f"{table_name}_id_seq"

    result = sqlite_conn.execute(
        f"SELECT MAX(id) FROM {table_name}"
    ).fetchone()

    max_id = result[0]

    next_id = 1 if max_id is None else int(max_id) + 1

    try:
        conn.execute(
            text(
                f'DROP SEQUENCE "{sequence_name}"'
            )
        )
    except Exception:
        pass

    conn.execute(
        text(
            f'''
            CREATE SEQUENCE "{sequence_name}"
            START WITH {next_id}
            INCREMENT BY 1
            NOCACHE
            '''
        )
    )

    print(
        f"  {sequence_name}: {next_id}"
    )


def main():

    print("=" * 60)
    print("SQLite -> Oracle migratsiya")
    print("=" * 60)

    total = 0

    with oracle_engine.begin() as conn:

        total += migrate_users(conn)

        total += migrate_tasks(conn)

        total += migrate_task_attachments(conn)

        total += migrate_finance(conn)

        total += migrate_announcements(conn)

        total += migrate_web_login_codes(conn)

        print("\nSequence'lar sozlanmoqda...")

        for table_name in [
            "users",
            "tasks",
            "task_attachments",
            "finance",
            "announcements",
            "web_login_codes",
        ]:
            reset_sequence(
                conn,
                table_name
            )

    print("\n" + "=" * 60)
    print(
        f"MIGRATSIYA TUGADI. JAMI: {total} TA YOZUV"
    )
    print("=" * 60)


if __name__ == "__main__":

    try:
        main()

    except Exception as e:
        print("\n!!! MIGRATSIYA XATOSI !!!")
        print(e)
        raise

    finally:
        sqlite_conn.close()
        oracle_engine.dispose()