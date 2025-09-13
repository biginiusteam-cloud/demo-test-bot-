import os
import re

class Config:
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    API_ID = int(os.environ.get("API_ID", ""))
    API_HASH = os.environ.get("API_HASH", "")
    MONGO_URL = os.environ.get("MONGO_URL", "")
    DATABASE_CHANNEL = int(os.environ.get("DATABASE_CHANNEL", "-1002275599146"))
    WELCOME_PIC = os.environ.get("WELCOME_PIC", "https://envs.sh/F-V.jpg")
    UNIQUE_ID_REGEX = re.compile(r"(?i)unique\s*id\s*[:\-]\s*([A-Za-z0-9_\-\.]+)")

    # ✅ Multiple admins
    ADMIN_IDS = [int(x.strip()) for x in os.environ.get("ADMIN_IDS", "7547946252,7881272094").split(",") if x.strip()]
