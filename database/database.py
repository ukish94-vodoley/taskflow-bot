import os

from dotenv import load_dotenv

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

load_dotenv()

ORACLE_USER = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN")

if not ORACLE_USER or not ORACLE_PASSWORD or not ORACLE_DSN:
    raise RuntimeError(
        "Oracle database sozlamalari .env faylida topilmadi"
    )

DATABASE_URL = "oracle+oracledb://"

engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "user": ORACLE_USER,
        "password": ORACLE_PASSWORD,
        "dsn": ORACLE_DSN,
    },
    pool_pre_ping=True,
    pool_recycle=1800,
    echo=False,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)