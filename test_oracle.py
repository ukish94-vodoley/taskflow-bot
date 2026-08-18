import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

user = os.getenv("ORACLE_USER")
password = os.getenv("ORACLE_PASSWORD")
dsn = os.getenv("ORACLE_DSN")

print("Oracle user:", user)
print("Connecting to Oracle...")

engine = create_engine(
    "oracle+oracledb://",
    connect_args={
        "user": user,
        "password": password,
        "dsn": dsn,
    },
)

try:
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 FROM DUAL"))
        print("ORACLE SQLALCHEMY OK:", result.scalar())

except Exception as e:
    print("ORACLE SQLALCHEMY ERROR:")
    print(e)

finally:
    engine.dispose()