from pyrogram import Client, filters
from pyrogram.types import Message
from config import Config
from pymongo import MongoClient
import asyncio
import re

mongo = MongoClient(Config.MONGO_URL)
db = mongo["StatusBot"]
users_col = db["users"]

# Default delete timer (seconds)
DELETE_TIMER = 60

def parse_time(time_str: str) -> int:
    match = re.match(r"^(\d+)([smhSMH])$", time_str.strip())
    if not match: return 0
    value, unit = match.groups()
    value = int(value)
    unit = unit.lower()
    if unit == "s": return value
    elif unit == "m": return value*60
    elif unit == "h": return value*3600
    return 0

# -----------------------------
# Set auto-delete timer
@Client.on_message(filters.command("setdelete") & filters.private)
async def set_delete(client: Client, message: Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return await message.reply_text("❌ You are not authorized.")
    if len(message.command)<2:
        return await message.reply_text("⚠️ Usage: /setdelete <time>\nExample: /setdelete 10s")
    seconds = parse_time(message.command[1])
    if seconds <= 0:
        return await message.reply_text("❌ Invalid time format.")
    global DELETE_TIMER
    DELETE_TIMER = seconds
    await message.reply_text(f"⏳ Auto-delete timer set to {message.command[1]}")

# -----------------------------
# Broadcast
@Client.on_message(filters.command("broadcast") & filters.private)
async def broadcast(client: Client, message: Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return await message.reply_text("❌ You are not authorized.")
    if not message.reply_to_message and len(message.command)<2:
        return await message.reply_text("⚠️ Reply to a message or /broadcast <text>")

    users = [u["user_id"] for u in users_col.find({})]
    count = 0

    # Get text to send (normal message, not forward)
    if message.reply_to_message:
        text_to_send = message.reply_to_message.text or message.reply_to_message.caption
    else:
        text_to_send = " ".join(message.command[1:])

    for uid in users:
        try:
            await client.send_message(uid, text_to_send)  # broadcast message, NO delete
            count += 1
            await asyncio.sleep(0.05)
        except:
            pass

    await message.reply_text(f"📢 Broadcast sent to {count} users.")

# -----------------------------
# Stats
@Client.on_message(filters.command("stats") & filters.private)
async def stats(client: Client, message: Message):
    if message.from_user.id not in Config.ADMIN_IDS:
        return await message.reply_text("❌ You are not authorized.")
    total_users = users_col.count_documents({})
    total_messages = db["messages"].count_documents({})
    reply = await message.reply_text(
        f"📊 Bot Stats:\n• Total users: {total_users}\n• Total messages in DB: {total_messages}"
    )
    # Auto-delete stats message
    await asyncio.sleep(DELETE_TIMER)
    try:
        await reply.delete()
    except:
        pass
