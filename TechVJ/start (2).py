import os
import asyncio
import re
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
from TechVJ.strings import HELP_TXT
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='bot.log',
)


class batch_temp(object):
    IS_BATCH = {}


# User settings dictionary (in-memory)
user_settings = {}


# Improved Status Updates
async def update_status(client, status_file, message, chat, text_prefix):
    last_updated_percent = -1  # Track to avoid redundant edits
    while True:
        if not os.path.exists(status_file):
            break
        try:
            with open(status_file, "r") as f:
                txt = f.read().strip()

            if txt:
                percent_match = re.search(r'(\d+\.?\d*)%', txt)
                if percent_match:
                    current_percent = float(percent_match.group(1))
                    if abs(current_percent - last_updated_percent) >= 5:
                        await client.edit_message_text(
                            chat,
                            message.id,
                            f"**{text_prefix} : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**",
                        )
                        last_updated_percent = current_percent
            await asyncio.sleep(5)  # Reduced update frequency
        except Exception as e:
            logging.error(f"Error in update status: {e}")
            await asyncio.sleep(5)


async def progress(current, total, message, type):
    percent = (current / total) * 100
    with open(f"{message.id}{type}status.txt", "w") as fileup:
        fileup.write(f"{percent:.1f}%")


# Forwarding function
async def forward_to_channel(client, chat_id, message_id, user_id=None):
    try:
        forward_channel = (
            user_settings.get(user_id, {}).get("forward_channel_id")
            if user_id
            else None
        )
        if forward_channel:
            await client.forward_messages(forward_channel, chat_id, message_id)
        else:
            await client.forward_messages(FORWARD_CHANNEL_ID, chat_id, message_id)
    except Exception as e:
        logging.error(f"Error forwarding: {e}")
        try:
            message = await client.get_messages(chat_id, message_id)
            await client.copy_message(
                chat_id=chat_id, from_chat_id=message.chat.id, message_id=message.id
            )
        except Exception as ex:
             logging.error(f"Error copying message: {ex}")


# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [
        [InlineKeyboardButton("❣️ Developer", url="https://t.me/SONICKUWALSSCBOT")],
        [
            InlineKeyboardButton("🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="https://t.me/SONICKUWALSSCBOT"),
            InlineKeyboardButton(
                "🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/SONICKUWALUPDATEKANHA"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id,
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n for bot any error content :- @SONICKUWALSSCBOT </b>",
        reply_markup=reply_markup,
        reply_to_message_id=message.id,
    )
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(chat_id=message.chat.id, text=f"{HELP_TXT}")


# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(chat_id=message.chat.id, text="**Batch Successfully Cancelled.**")


# settings command
@Client.on_message(filters.command(["settings"]))
async def settings(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("Set Forward Channel", callback_data="set_forward")],
        [InlineKeyboardButton("Show Settings", callback_data="show_settings")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id,
        text="**Settings Menu**",
        reply_markup=reply_markup,
        reply_to_message_id=message.id,
    )


# callback query handler for settings
@Client.on_callback_query(filters.regex("set_forward"))
async def set_forward(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(
        chat_id=callback_query.message.chat.id,
        text="**Send me the custom channel ID you want to forward to. \n\nNote: You will need to add this bot as admin in your channel for forwarding.**",
    )
    chat_id_query = await client.listen(
        callback_query.message.chat.id, filters=filters.text
    )
    try:
        forward_channel_id = int(chat_id_query.text)
        user_settings[callback_query.from_user.id] = user_settings.get(
            callback_query.from_user.id, {}
        )
        user_settings[callback_query.from_user.id]["forward_channel_id"] = (
            forward_channel_id
        )
        await client.send_message(
            chat_id=callback_query.message.chat.id,
            text="**Custom Forward Channel Set.**",
        )
    except Exception as e:
        logging.error(f"Error set custom channel: {e}")
        await client.send_message(
            chat_id=callback_query.message.chat.id,
            text="**Invalid Channel Id.**",
        )


@Client.on_callback_query(filters.regex("show_settings"))
async def show_settings(client: Client, callback_query: pyrogram.types.CallbackQuery):
    user_id = callback_query.from_user.id
    setting = user_settings.get(user_id, {})
    forward_channel = setting.get("forward_channel_id", "Not set")
    await client.send_message(
        chat_id=callback_query.message.chat.id,
        text=f"**Your Settings:**\n\n**Custom Forward Channel**: {forward_channel}",
    )


def parse_message_link(message_text):
    pattern = re.compile(r"https://t\.me/(?:c/)?([^/]+)/(\d+)(?:-(\d+))?")
    match = pattern.match(message_text)
    if match:
        channel_id = match.group(1)
        from_msg_id = int(match.group(2))
        to_msg_id = int(match.group(3)) if match.group(3) else from_msg_id
        return channel_id, from_msg_id, to_msg_id
    return None, None, None


@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text(
                "**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**"
            )

        channel_id, from_msg_id, to_msg_id = parse_message_link(message.text)

        if not channel_id:
            await message.reply_text("**Invalid Link Format.**")
            return

        batch_temp.IS_BATCH[message.from_user.id] = False

        for msg_id in range(from_msg_id, to_msg_id + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break
            user_data = await db.get_session(message.from_user.id)
            if user_data is None:
                await message.reply(
                    "**For Downloading Restricted Content You Have To /login First.**"
                )
                batch_temp.IS_BATCH[message.from_user.id] = True
                return
            try:
                acc = Client(
                    "saverestricted",
                    session_string=user_data,
                    api_hash=API_HASH,
                    api_id=API_ID,
                )
                await acc.connect()
            except Exception as e:
                batch_temp.IS_BATCH[message.from_user.id] = True
                logging.error(f"Login error: {e}")
                return await message.reply(
                    "**Your Login Session Expired. So /logout First Then Login Again By - /login**"
                )

            try:
                if channel_id.startswith("-100"):
                    chatid = int(channel_id)
                    await handle_private(client, acc, message, chatid, msg_id)
                else:
                    await handle_private(client, acc, message, channel_id, msg_id)

            except Exception as e:
                logging.error(f"Error in message handling: {e}")
                if ERROR_MESSAGE:
                    await client.send_message(
                        message.chat.id, f"Error: {e}", reply_to_message_id=message.id
                    )

            # wait time
            await asyncio.sleep(3)
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    try:
        msg: Message = await acc.get_messages(chatid, msgid)
        if not msg or msg.empty:
            return
        msg_type = get_message_type(msg)
        if not msg_type:
            return
    except Exception as e:
        logging.error(f"Error in getting message: {e}")
        if ERROR_MESSAGE:
            await client.send_message(
                message.chat.id,
                f"Error: while Get Message: {e}",
                reply_to_message_id=message.id,
            )
        return
    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id):
        return

    if msg_type == "Text":
        if msg.text:
            try:
                sent_msg = await client.send_message(
                    chat,
                    msg.text,
                    entities=msg.entities,
                    reply_to_message_id=message.id,
                    parse_mode=enums.ParseMode.HTML,
                )
                await forward_to_channel(
                    client, message.chat.id, sent_msg.id, message.from_user.id
                )
            except Exception as e:
                logging.error(f"Error sending text message: {e}")
                if ERROR_MESSAGE:
                    await client.send_message(
                        message.chat.id,
                        f"Error Sending Text: {e}",
                        reply_to_message_id=message.id,
                        parse_mode=enums.ParseMode.HTML,
                    )
            return
        return

    smsg = await client.send_message(
        message.chat.id, "**Downloading**", reply_to_message_id=message.id
    )
    download_task = asyncio.create_task(
        update_status(client, f"{message.id}downstatus.txt", smsg, chat, "Downloaded")
    )
    file = None
    try:
        file = await acc.download_media(
            msg, progress=progress, progress_args=[message, "down"]
        )
    except Exception as e:
        logging.error(f"Error downloading media: {e}")
        if ERROR_MESSAGE:
            await client.send_message(
                message.chat.id,
                f"Error: Download Error: {e}",
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
            )
        if os.path.exists(f"{message.id}downstatus.txt"):
            os.remove(f"{message.id}downstatus.txt")
        await download_task
        return await smsg.delete()

    if batch_temp.IS_BATCH.get(message.from_user.id):
        if os.path.exists(f"{message.id}downstatus.txt"):
            os.remove(f"{message.id}downstatus.txt")
        if file and os.path.exists(file):
            os.remove(file)
        await download_task
        return await smsg.delete()

    await download_task

    upload_task = asyncio.create_task(
        update_status(client, f"{message.id}upstatus.txt", smsg, chat, "Uploaded")
    )
    try:
        if msg.caption:
            caption = msg.caption
        else:
            caption = None
        if batch_temp.IS_BATCH.get(message.from_user.id):
            return

        if msg_type == "Document":
            if msg.document.file_size == 0:
                await client.send_message(
                    chat, "**Skipping 0kb Document**", reply_to_message_id=message.id
                )
                return
            ph_path = None
            if msg.document.thumbs:
                try:
                    ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(
                            message.chat.id,
                            f"Error: Thumbnail Download Error: {e}",
                            reply_to_message_id=message.id,
                            parse_mode=enums.ParseMode.HTML,
                        )
                    ph_path = None
            sent_msg = await client.send_document(
                chat,
                file,
                thumb=ph_path,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"],
            )
            await forward_to_channel(
                client, message.chat.id, sent_msg.id, message.from_user.id
            )
            if ph_path:
                os.remove(ph_path)
        elif msg_type == "Video":
            if msg.video.file_size == 0:
                await client.send_message(
                    chat, "**Skipping 0kb Video**", reply_to_message_id=message.id
                )
                return
            ph_path = None
            if msg.video.thumbs:
                try:
                    ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(
                            message.chat.id,
                            f"Error: Thumbnail Download Error: {e}",
                            reply_to_message_id=message.id,
                            parse_mode=enums.ParseMode.HTML,
                        )
                    ph_path = None
            sent_msg = await client.send_video(
                chat,
                file,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
                thumb=ph_path,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"],
            )
            await forward_to_channel(
                client, message.chat.id, sent_msg.id, message.from_user.id
            )
            if ph_path:
                os.remove(ph_path)
        elif msg_type == "Animation":
            sent_msg = await client.send_animation(
                chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML
            )
            await forward_to_channel(
                client, message.chat.id, sent_msg.id, message.from_user.id
            )

        elif msg_type == "Sticker":
            sent_msg = await client.send_sticker(
                chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML
            )
            await forward_to_channel(
                client, message.chat.id, sent_msg.id, message.from_user.id
            )

        elif msg_type == "Voice":
            sent_msg = await client.send_voice(
                chat,
                file,
                caption=caption,
                caption_entities=msg.caption_entities,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"],
            )
            await forward_to_channel(
                client, message.chat.id, sent_msg.id, message.from_user.id
            )

        elif msg_type == "Audio":
            ph_path = None
            if msg.audio.thumbs:
                try:
                    ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(
                            message.chat.id,
                            f"Error: Thumbnail Download Error: {e}",
                            reply_to_message_id=message.id,
                            parse_mode=enums.ParseMode.HTML,
                        )
                    ph_path = None

            sent_msg = await client.send_audio(
                chat,
                file,
                thumb=ph_path,
                caption=caption,
                reply_to_message_id=message.id,
                parse_mode=enums.ParseMode.HTML,
                progress=progress,
                progress_args=[message, "up"],
            )
            await forward_to_channel(
                client, message.chat.id, sent_msg.id, message.from_user.id
            )
            if ph_path:
                os.remove(ph_path)

        elif msg_type == "Photo":
            sent_msg = await client.send_photo(
                chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML
            )
            await forward_to_channel(
                client, message.chat.id, sent_msg.id, message.from_user.id
            )

    except Exception as e:
        logging.error(f"Error during media sending/upload: {e}")
        if ERROR_MESSAGE:
            await client.send_message(
                message.chat.id, f"Error: while sending: {e}", reply_to_message_id=message.id
            )

    if os.path.exists(f"{message.id}upstatus.txt"):
        os.remove(f"{message.id}upstatus.txt")
    await upload_task
    if file and os.path.exists(file):
        os.remove(file)
    await client.delete_messages(message.chat.id, [smsg.id])


# get the type of message
def get_message_type(msg):
    if msg.document:
        return "Document"
    if msg.video:
        return "Video"
    if msg.animation:
        return "Animation"
    if msg.sticker:
        return "Sticker"
    if msg.voice:
        return "Voice"
    if msg.audio:
        return "Audio"
    if msg.photo:
        return "Photo"
    if msg.text:
        return "Text"
    return None