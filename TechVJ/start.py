# Don't Remove Credit Tg - @VJ_Botz
# Optimized & Batch Fixed by SONICKUWAL

import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
from TechVJ.strings import HELP_TXT

class batch_temp:
    IS_RUNNING = {}

# ================= START =================
@Client.on_message(filters.command("start"))
async def start(client, message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    btn = InlineKeyboardMarkup([
        [InlineKeyboardButton("❣️ Developer", url="https://t.me/SONICKUWALSSCBOT")],
        [
            InlineKeyboardButton("🔍 Support", url="https://t.me/SONICKUWALSSCBOT"),
            InlineKeyboardButton("🤖 Update", url="https://t.me/SONICKUWALUPDATEKANHA")
        ]
    ])
    await message.reply_text(
        f"👋 Hi {message.from_user.mention}\n\n"
        "Send link or use:\n"
        "`/batch https://t.me/c/xxxx/1-1000`\n\n"
        "/cancel – stop batch",
        reply_markup=btn
    )

# ================= HELP =================
@Client.on_message(filters.command("help"))
async def help_cmd(client, message):
    await message.reply_text(HELP_TXT)

# ================= CANCEL =================
@Client.on_message(filters.command("cancel"))
async def cancel(client, message):
    batch_temp.IS_RUNNING[message.from_user.id] = False
    await message.reply_text("❌ Batch cancelled")

# ================= BATCH COMMAND =================
@Client.on_message(filters.command("batch") & filters.private)
async def batch_cmd(client, message):
    if len(message.command) < 2:
        return await message.reply("Usage:\n/batch link")

    message.text = message.command[1]
    await process_link(client, message)

# ================= LINK HANDLER =================
@Client.on_message(filters.text & filters.private)
async def process_link(client, message):
    if "https://t.me/" not in message.text:
        return

    uid = message.from_user.id
    if batch_temp.IS_RUNNING.get(uid):
        return await message.reply("⚠️ One batch already running. Use /cancel")

    batch_temp.IS_RUNNING[uid] = True

    data = message.text.split("/")
    temp = data[-1].replace("?single", "").split("-")
    start_id = int(temp[0])
    end_id = int(temp[1]) if len(temp) > 1 else start_id

    # ===== LOGIN SESSION =====
    session = await db.get_session(uid)
    if not session:
        batch_temp.IS_RUNNING[uid] = False
        return await message.reply("/login first")

    acc = Client(
        f"batch_{uid}",
        session_string=session,
        api_id=API_ID,
        api_hash=API_HASH
    )
    await acc.connect()

    IS_BIG_BATCH = (end_id - start_id) > 20
    sent = 0

    try:
        for msgid in range(start_id, end_id + 1):
            if not batch_temp.IS_RUNNING.get(uid):
                break

            try:
                await forward_message(client, acc, message, data, msgid, IS_BIG_BATCH)
                sent += 1
                await asyncio.sleep(1.2)

            except FloodWait as e:
                await asyncio.sleep(e.value)

            except Exception as e:
                if ERROR_MESSAGE:
                    await message.reply(str(e))

    finally:
        await acc.disconnect()
        batch_temp.IS_RUNNING[uid] = False
        await message.reply(f"✅ Batch completed\nTotal sent: {sent}")

# ================= FORWARD LOGIC =================
async def forward_message(client, acc, message, data, msgid, big_batch):
    chat = message.chat.id

    # PRIVATE
    if "https://t.me/c/" in message.text:
        chatid = int("-100" + data[4])
        msg = await acc.get_messages(chatid, msgid)

    # BOT
    elif "https://t.me/b/" in message.text:
        msg = await acc.get_messages(data[4], msgid)

    # PUBLIC
    else:
        username = data[3]
        try:
            msg = await client.get_messages(username, msgid)
        except UsernameNotOccupied:
            return

    if not msg:
        return

    if msg.text:
        await client.send_message(chat, msg.text, entities=msg.entities)
        return

    if msg.media:
        await client.copy_message(chat, msg.chat.id, msg.id)

# ================= END =================
