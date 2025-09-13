from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from pymongo import MongoClient
import asyncio
import re

# MongoDB connection
mongo = MongoClient(Config.MONGO_URL)
db = mongo["StatusBot"]
users_col = db["users"]  # yahan user IDs store honge

# -----------------------------
# Helper: convert time string to seconds
def parse_time(time_str: str) -> int:
    """
    Parses strings like '10s', '2m', '3h' into seconds.
    Returns 0 if invalid.
    """
    match = re.match(r"^(\d+)([smhSMH])$", time_str.strip())
    if not match:
        return 0
    value, unit = match.groups()
    value = int(value)
    unit = unit.lower()
    if unit == "s":
        return value
    elif unit == "m":
        return value * 60
    elif unit == "h":
        return value * 3600
    return 0

# -----------------------------
# Broadcast command
@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client: Client, message: Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return await message.reply_text("❌ You are not authorized.")
    if not message.reply_to_message and len(message.command) < 2:
        return await message.reply_text("⚠️ Reply to a message or /broadcast <text>")

    users = [u["user_id"] for u in users_col.find({})]
    count = 0
    for uid in users:
        try:
            if message.reply_to_message:
                await message.reply_to_message.forward(uid)
            else:
                text = " ".join(message.command[1:])
                await client.send_message(uid, text)
            count += 1
            await asyncio.sleep(0.05)  # flood control
        except:
            pass

    await message.reply_text(f"📢 Broadcast sent to {count} users.")

# -----------------------------
# Stats command
@Client.on_message(filters.command("stats") & filters.private)
async def stats(client: Client, message: Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return await message.reply_text("❌ You are not authorized.")
    total_users = users_col.count_documents({})
    total_messages = db["messages"].count_documents({})
    await message.reply_text(
        f"📊 Bot Stats:\n• Total users: {total_users}\n• Total messages in DB: {total_messages}"
    )

# -----------------------------
# Delete command
@Client.on_message(filters.command("delete") & filters.private)
async def delete_timer(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            "⚠️ Usage: /delete <time>\nExample: /delete 10s, /delete 2m, /delete 1h"
        )
    seconds = parse_time(message.command[1])
    if seconds <= 0:
        return await message.reply_text("❌ Invalid time format. Use like 10s, 2m, 3h")
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to the message you want to delete.")

    await message.reply_text(f"⏳ Message will be deleted in {seconds} seconds.")
    await asyncio.sleep(seconds)
    try:
        await message.reply_to_message.delete()
    except:
        pass
