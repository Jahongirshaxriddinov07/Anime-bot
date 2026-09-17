import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id_str) for id_str in os.getenv("ADMIN_IDS", "").split(",") if id_str]

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "anime_db")
DB_USER = os.getenv("DB_USER", "anime_user")
DB_PASS = os.getenv("DB_PASS", "")

STORAGE_CHANNEL_ID = int(os.getenv("STORAGE_CHANNEL_ID", 0))
