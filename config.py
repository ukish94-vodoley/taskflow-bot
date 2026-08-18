import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("SUPER_ADMIN_ID", "0"))
WEB_SECRET_KEY = os.getenv("WEB_SECRET_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN .env faylida topilmadi!")

if not WEB_SECRET_KEY:
    raise ValueError("WEB_SECRET_KEY .env faylida topilmadi!")
