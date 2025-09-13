from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import Config
from pymongo import MongoClient

# MongoDB connection
mongo = MongoClient(Config.MONGO_URL)
db = mongo["StatusBot"]
users_col = db["users"]

@Client.on_message(filters.command(["start"]) & filters.private)
async def start_message(client, message):
    # Save user ID to DB if not already
    users_col.update_one(
        {"user_id": message.from_user.id},
        {"$setOnInsert": {"user_id": message.from_user.id}},
        upsert=True
    )

    buttons = [
        [InlineKeyboardButton("🔎 Check Status", callback_data="check_status")]
    ]
    await message.reply_photo(
        photo=Config.WELCOME_PIC,
        caption=(
            "👋 <b>Welcome!</b>\n\n"
            "Tap the button below to check your status."
        ),
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@Client.on_message(filters.command(["help"]) & filters.private)
async def help_message(client, message):
    await message.reply_text(
        "ℹ️ <b>How it works</b>\n\n"
        "1) Tap <b>Check Status</b>\n"
        "2) Send your <b>Unique ID</b>\n"
        "3) I’ll send back the exact status message saved for your ID.\n\n"
        "Admins Commands:\n"
        "/broadcast <text> - Send message to all users\n"
        "/stats - Total users and messages\n"
        "/setdelete <time> - Set auto-delete timer for status messages (10s, 2m, 1h)"
    )
