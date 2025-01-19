import asyncio
import os
import time
import json
from typing import Union

import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated,
    UserAlreadyParticipant,
    InviteHashExpired,
    UsernameNotOccupied,
    BadRequest,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from config import API_ID, API_HASH
from database.db import database
from TechVJ.strings import strings, HELP_TXT

def get(obj, key, default=None):
    try:
        return obj[key]
    except Exception:
        return default

async def downstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(
                message.chat.id,
                message.id,
                f"Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}",
            )
            await asyncio.sleep(10)
        except Exception:
            await asyncio.sleep(5)

# upload status
async def upstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(
                message.chat.id,
                message.id,
                f"Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}",
            )
            await asyncio.sleep(10)
        except Exception:
            await asyncio.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f"{message.id}{type}status.txt", "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("❣️ Developer", url="http://t.me/Sonickuwalupdatebot")],
        [
            InlineKeyboardButton(
                "🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="http://t.me/Sonickuwalupdatebot"
            ),
            InlineKeyboardButton(
                "🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/SONICKUWALUPDATEKANHA"
            ),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        message.chat.id,
        f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>",
        reply_markup=reply_markup,
        reply_to_message_id=message.id,
    )
    return

# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

# Custom Channel ID
CUSTOM_CHANNEL_ID = os.environ.get("CUSTOM_CHANNEL_ID", None)  # Get from environment variable
if CUSTOM_CHANNEL_ID:
    try:
        CUSTOM_CHANNEL_ID = int(CUSTOM_CHANNEL_ID)
    except ValueError:
        print("Error: CUSTOM_CHANNEL_ID must be an integer.")
        CUSTOM_CHANNEL_ID = None

# --- Custom Words ---
custom_words_dict = {}  # Dictionary to store custom words and their replacements

@Client.on_message(filters.command(["addword"]))
async def add_custom_word(client: Client, message: Message):
    try:
        _, word, replacement = message.text.split(" ", 2)
        custom_words_dict[word] = replacement
        await message.reply_text(f"Word '{word}' added with replacement '{replacement}'.")
    except ValueError:
        await message.reply_text("Invalid format. Use `/addword <word> <replacement>`.")

@Client.on_message(filters.command(["delword"]))
async def delete_custom_word(client: Client, message: Message):
    try:
        _, word = message.text.split(" ", 1)
        if word in custom_words_dict:
            del custom_words_dict[word]
            await message.reply_text(f"Word '{word}' deleted.")
        else:
            await message.reply_text(f"Word '{word}' not found.")
    except ValueError:
        await message.reply_text("Invalid format. Use `/delword <word>`.")

@Client.on_message(filters.command(["replace"]))
async def replace_words_in_message(client: Client, message: Message):
    if message.reply_to_message:
        original_message = message.reply_to_message
        new_text = original_message.text
        for word, replacement in custom_words_dict.items():
            new_text = new_text.replace(word, replacement)
        if new_text != original_message.text:
            await original_message.edit_text(new_text)
            await message.reply_text("Message edited with replaced words.")
        else:
            await message.reply_text("No words replaced.")
    else:
        await message.reply_text("Reply to a message to replace words.")

# --- Custom Captions ---
custom_captions = {}

@Client.on_message(filters.command(["addcaption"]))
async def add_custom_caption(client: Client, message: Message):
    try:
        _, file_type, caption = message.text.split(" ", 2)
        custom_captions[file_type.lower()] = caption
        await message.reply_text(
            f"Custom caption added for file type '{file_type}'."
        )
    except ValueError:
        await message.reply_text(
            "Invalid format. Use `/addcaption <file_type> <caption>`."
        )

@Client.on_message(filters.command(["delcaption"]))
async def delete_custom_caption(client: Client, message: Message):
    try:
        _, file_type = message.text.split(" ", 1)
        if file_type.lower() in custom_captions:
            del custom_captions[file_type.lower()]
            await message.reply_text(f"Custom caption for '{file_type}' deleted.")
        else:
            await message.reply_text(f"Custom caption for '{file_type}' not found.")
    except ValueError:
        await message.reply_text("Invalid format. Use `/delcaption <file_type>`.")

#--- Toggle Features ---
toggle_message_empty_check = True

@Client.on_message(filters.command(["toggle_message_empty"]))
async def toggle_message_empty(client: Client, message: Message):
    global toggle_message_empty_check
    toggle_message_empty_check = not toggle_message_empty_check
    status = "Enabled" if toggle_message_empty_check else "Disabled"
    await message.reply_text(f"Message empty check: {status}")

@Client.on_message(filters.private)
async def save(client: Client, message: Message):
    # --- High Speed Optimization (Simplified for brevity) ---
    # In a real implementation, you might use asynchronous file I/O,
    # connection pooling, and other techniques to optimize performance.
    # This is a placeholder for those optimizations.
    # You would also monitor the bot's performance to determine when to switch
    # between high-speed and low-speed modes.
    
    # Placeholder for throttling after 1-2 hours of high-speed operation
    if hasattr(save, "start_time") and (time.time() - save.start_time > 7200):
       # Example of slowing down: Increase sleep time
        await asyncio.sleep(5)  # Increased sleep time as a simple throttling mechanism
        
    if not hasattr(save, "start_time"):
        save.start_time = time.time()

    if "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except Exception:
            toID = fromID
        for msgid in range(fromID, toID + 1):
            # private
            if "https://t.me/c/" in message.text:
                user_data = database.find_one({"chat_id": message.chat.id})
                if (
                    not get(user_data, "logged_in", False)
                    or user_data["session"] is None
                ):
                    await client.send_message(message.chat.id, strings["need_login"])
                    return
                acc = Client(
                    "saverestricted",
                    session_string=user_data["session"],
                    api_hash=API_HASH,
                    api_id=API_ID,
                )
                await acc.connect()
                chatid = int("-100" + datas[4])
                await handle_private(client, acc, message, chatid, msgid)

            # bot
            elif "https://t.me/b/" in message.text:
                user_data = database.find_one({"chat_id": message.chat.id})
                if (
                    not get(user_data, "logged_in", False)
                    or user_data["session"] is None
                ):
                    await client.send_message(message.chat.id, strings["need_login"])
                    return
                acc = Client(
                    "saverestricted",
                    session_string=user_data["session"],
                    api_hash=API_HASH,
                    api_id=API_ID,
                )
                await acc.connect()
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    await client.send_message(
                        message.chat.id, f"Error: {e}", reply_to_message_id=message.id
                    )

            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    await client.send_message(
                        message.chat.id,
                        "The username is not occupied by anyone",
                        reply_to_message_id=message.id,
                    )
                    return
                try:
                    await client.copy_message(
                        message.chat.id,
                        msg.chat.id,
                        msg.id,
                        reply_to_message_id=message.id,
                    )
                except Exception:
                    try:
                        user_data = database.find_one({"chat_id": message.chat.id})
                        if (
                            not get(user_data, "logged_in", False)
                            or user_data["session"] is None
                        ):
                            await client.send_message(
                                message.chat.id, strings["need_login"]
                            )
                            return
                        acc = Client(
                            "saverestricted",
                            session_string=user_data["session"],
                            api_hash=API_HASH,
                            api_id=API_ID,
                        )
                        await acc.connect()
                        await handle_private(client, acc, message, username, msgid)

                    except Exception as e:
                        await client.send_message(
                            message.chat.id,
                            f"Error: {e}",
                            reply_to_message_id=message.id,
                        )

            # wait time
            await asyncio.sleep(3)

# handle private
async def handle_private(
    client: Client, acc: Client, message: Message, chatid: Union[int, str], msgid: int
):
    msg: Message = await acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)
    chat = message.chat.id

    # --- Replace Custom Words ---
    if msg_type == "Text" and custom_words_dict:
        for word, replacement in custom_words_dict.items():
            msg.text = msg.text.replace(word, replacement)

    if msg_type == "Text":
        try:
             # Send message and handle potential error
            sent_message = await client.send_message(
                chat,
                msg.text,
                entities=msg.entities,
                reply_to_message_id=message.id,
                disable_web_page_preview=True
            )

            # Check for MESSAGE_EMPTY error if toggle is enabled
            if toggle_message_empty_check and sent_message.empty:
                await message.reply_text("Warning: The message sent is empty or contains invalid characters.")
        
        except BadRequest as e:
            if toggle_message_empty_check and "MESSAGE_EMPTY" in str(e):
                await message.reply_text(
                    "Error: The message sent is empty or contains invalid characters."
                )
        except Exception as e:
            await client.send_message(
                message.chat.id, f"Error: {e}", reply_to_message_id=message.id
            )
            return

    smsg = await client.send_message(
        message.chat.id, "Downloading", reply_to_message_id=message.id
    )
    dosta = asyncio.create_task(
        downstatus(client, f"{message.id}downstatus.txt", smsg)
    )
    try:
        file = await acc.download_media(
            msg, progress=progress, progress_args=[message, "down"]
        )
        os.remove(f"{message.id}downstatus.txt")

    except Exception as e:
        await client.send_message(
            message.chat.id, f"Error: {e}", reply_to_message_id=message.id
        )
        return
    
    upsta = asyncio.create_task(upstatus(client, f"{message.id}upstatus.txt", smsg))

    # --- Custom Caption ---
    caption = custom_captions.get(msg_type.lower(), msg.caption)

    # --- Auto Remove Default Thumbnail ---
    ph_path = None
    if msg_type in ["Document", "Video", "Audio"]:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id if msg_type == "Video" else msg.document.thumbs[0].file_id if msg_type == "Document" else msg.audio.thumbs[0].file_id)
        except Exception:
            ph_path = None

    # --- Forward to Custom Channel ---
    forward_to_channel = CUSTOM_CHANNEL_ID is not None

    try:
        if msg_type == "Document":
            await client.send_document(
                CUSTOM_CHANNEL_ID if forward_to_channel else chat,
                file,
                thumb=None,  # Auto Remove Thumbnail
                caption=caption,
                force_document=True,
                reply_to_message_id=None
                if forward_to_channel
                else message.id,  # Forward to custom channel or send to user
                progress=progress,
                progress_args=[message, "up"],
            )

        elif msg_type == "Video":
            await client.send_video(
                CUSTOM_CHANNEL_ID if forward_to_channel else chat,
                file,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
                thumb=None,  # Auto Remove Thumbnail
                caption=caption,
                supports_streaming=True,
                reply_to_message_id=None if forward_to_channel else message.id,
                progress=progress,
                progress_args=[message, "up"],
            )

        elif msg_type == "Animation":
            await client.send_animation(
                CUSTOM_CHANNEL_ID if forward_to_channel else chat,
                file,
                reply_to_message_id=None if forward_to_channel else message.id,
            )

        elif msg_type == "Sticker":
            await client.send_sticker(
                CUSTOM_CHANNEL_ID if forward_to_channel else chat,
                file,
                reply_to_message_id=None if forward_to_channel else message.id,
            )

        elif msg_type == "Voice":
            await client.send_voice(
                CUSTOM_CHANNEL_ID if forward_to_channel else chat,
                file,
                caption=caption,
                reply_to_message_id=None if forward_to_channel else message.id,
                progress=progress,
                progress_args=[message, "up"],
            )

        elif msg_type == "Audio":
            await client.send_audio(
                CUSTOM_CHANNEL_ID if forward_to_channel else chat,
                file,
                thumb=None,  # Auto Remove Thumbnail
                caption=caption,
                reply_to_message_id=None if forward_to_channel else message.id,
                progress=progress,
                progress_args=[message, "up"],
            )

        elif msg_type == "Photo":
            await client.send_photo(
                CUSTOM_CHANNEL_ID if forward_to_channel else chat,
                file,
                caption=caption,
                reply_to_message_id=None if forward_to_channel else message.id,
            )

    except Exception as e:
        await client.send_message(
            message.chat.id, f"Error: {e}", reply_to_message_id=message.id
        )

    # --- Auto Remove File and Thumbnail ---
    if os.path.exists(f"{message.id}upstatus.txt"):
        os.remove(f"{message.id}upstatus.txt")
        os.remove(file)
        if ph_path:
            os.remove(ph_path)

    await client.delete_messages(message.chat.id, [smsg.id])

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except Exception:
        pass

    try:
        msg.video.file_id
        return "Video"
    except Exception:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except Exception:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except Exception:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except Exception:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except Exception:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except Exception:
        pass

    try:
        msg.text
        return "Text"
    except Exception:
        pass