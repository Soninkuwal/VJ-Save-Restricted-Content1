import asyncio
import os
import re
import time
import json

import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated,
    UserAlreadyParticipant,
    InviteHashExpired,
    UsernameNotOccupied,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from config import API_ID, API_HASH
from database.db import database
from TechVJ.strings import strings, HELP_TXT

# Global Variables for Settings
DEFAULT_THUMBNAIL = None  # Placeholder for a default thumbnail
CUSTOM_CAPTIONS = {}  # Dictionary to store custom captions {word: replacement}
BATCH_RUNNING = {}  # Dictionary to track running batch processes {chat_id: asyncio.Task}
USER_REACTIONS = {}  # Dictionary to store user reactions {user_id: emoji}
CUSTOM_CHANNEL_ID = None

# Helper Functions

def get(obj, key, default=None):
    try:
        return obj[key]
    except:
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
        except:
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
        except:
            await asyncio.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f"{message.id}{type}status.txt", "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# Function to apply custom captions
def apply_custom_caption(caption):
    if not caption:
        return None
    for word, replacement in CUSTOM_CAPTIONS.items():
        caption = caption.replace(word, replacement)
    return caption

def extract_chat_and_message_ids(text):
    """
    Extracts chat and message IDs from a Telegram link.
    Supports both private (t.me/c/...) and public (t.me/...) links.

    Args:
        text: The Telegram link.

    Returns:
        A tuple containing the chat ID (int or str) and a list of message IDs (int).
        Returns None, None if the link is invalid.
    """
    match = re.match(r"https://t\.me/(?:c/)?(\w+)/(\d+(?:-\d+)?)", text)
    if not match:
        return None, None

    chat_part = match.group(1)
    message_part = match.group(2)

    if message_part.isdigit():
        message_ids = [int(message_part)]
    else:
        start, end = map(int, message_part.split("-"))
        message_ids = list(range(start, end + 1))

    if chat_part.isdigit():
        # It's a private chat ID
        chat_id = -1000000000000 - int(chat_part)  # Adjust for private chat IDs
    else:
        # It's a public chat username
        chat_id = chat_part

    return chat_id, message_ids

# --- Bot Commands and Handlers ---

# Start Command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("❣️ Developer", url="http://t.me/Sonickuwalupdatebot")],
        [
            InlineKeyboardButton("🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ", url="http://t.me/Sonickuwalupdatebot"),
            InlineKeyboardButton("🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ", url="https://t.me/SONICKUWALUPDATEKANHA"),
        ],
        [InlineKeyboardButton("⚙️ Settings", callback_data="settings")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        message.chat.id,
        f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>",
        reply_markup=reply_markup,
        reply_to_message_id=message.id,
    )
    return

# Help Command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

# Settings Command
@Client.on_message(filters.command(["settings"]))
async def settings_command(client: Client, message: Message):
    await send_settings_menu(client, message)

# --- Settings Menu and Callbacks ---

async def send_settings_menu(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("Set Custom Thumbnail", callback_data="set_thumbnail")],
        [InlineKeyboardButton("Replace Custom Words", callback_data="replace_words")],
        [InlineKeyboardButton("Delete Custom Words", callback_data="delete_words")],
        [InlineKeyboardButton("Set Custom Channel ID", callback_data="set_channel_id")],
        [InlineKeyboardButton("Set Reaction Emoji", callback_data="set_reaction")],
        [InlineKeyboardButton("❌ Close", callback_data="close_settings")],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        message.chat.id, "⚙️ **Settings**\n\nChoose an option:", reply_markup=reply_markup, reply_to_message_id=message.id
    )

@Client.on_callback_query(filters.regex(r"^settings$"))
async def settings_callback(client: Client, query: CallbackQuery):
    await query.answer()
    await send_settings_menu(client, query.message)

@Client.on_callback_query(filters.regex(r"^set_thumbnail$"))
async def set_thumbnail_callback(client: Client, query: CallbackQuery):
    global DEFAULT_THUMBNAIL
    await query.answer()
    await query.message.edit("Send me a photo to set as the default thumbnail.")
    # Set a state for the user so we know they are setting a thumbnail
    database.update_one({"chat_id": query.message.chat.id}, {"$set": {"state": "set_thumbnail"}}, upsert=True)

@Client.on_callback_query(filters.regex(r"^replace_words$"))
async def replace_words_callback(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.edit(
        "Send me words to replace in the format: `word1:replacement1, word2:replacement2`\n"
        "Example: `hello:hi, bye:goodbye`"
    )
    database.update_one({"chat_id": query.message.chat.id}, {"$set": {"state": "replace_words"}}, upsert=True)

@Client.on_callback_query(filters.regex(r"^delete_words$"))
async def delete_words_callback(client: Client, query: CallbackQuery):
    await query.answer()
    if not CUSTOM_CAPTIONS:
        await query.message.edit("No custom words are set.")
        return
    await query.message.edit(
        "Send me words to delete from custom captions, separated by commas.\n"
        "Example: `hello, bye`"
    )
    database.update_one({"chat_id": query.message.chat.id}, {"$set": {"state": "delete_words"}}, upsert=True)

@Client.on_callback_query(filters.regex(r"^set_channel_id$"))
async def set_channel_id_callback(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.edit("Send me the custom channel ID (e.g., -100xxxxxxxxxx or @username).")
    database.update_one({"chat_id": query.message.chat.id}, {"$set": {"state": "set_channel_id"}}, upsert=True)

@Client.on_callback_query(filters.regex(r"^set_reaction$"))
async def set_reaction_callback(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.edit("Send me the emoji you want to use for auto-reactions.")
    database.update_one({"chat_id": query.message.chat.id}, {"$set": {"state": "set_reaction"}}, upsert=True)

@Client.on_callback_query(filters.regex(r"^close_settings$"))
async def close_settings_callback(client: Client, query: CallbackQuery):
    await query.answer()
    await query.message.delete()

# --- State Handlers for Settings ---

@Client.on_message(filters.private & ~filters.command(["start", "help", "settings", "login", "logout"]))
async def handle_states(client: Client, message: Message):
    user_data = database.find_one({"chat_id": message.chat.id})
    state = get(user_data, "state")

    if state == "set_thumbnail":
        if message.photo:
            global DEFAULT_THUMBNAIL
            DEFAULT_THUMBNAIL = message.photo.file_id
            await message.reply_text("Custom thumbnail set successfully!")
        else:
            await message.reply_text("Please send a photo.")
        database.update_one({"chat_id": message.chat.id}, {"$unset": {"state": ""}})

    elif state == "replace_words":
        global CUSTOM_CAPTIONS
        try:
            words_to_replace = message.text.split(",")
            for pair in words_to_replace:
                word, replacement = pair.split(":")
                CUSTOM_CAPTIONS[word.strip()] = replacement.strip()
            await message.reply_text("Custom words updated successfully!")
        except:
            await message.reply_text("Invalid format. Please use `word1:replacement1, word2:replacement2`")
        database.update_one({"chat_id": message.chat.id}, {"$unset": {"state": ""}})

    elif state == "delete_words":
        words_to_delete = message.text.split(",")
        deleted = False
        for word in words_to_delete:
            word = word.strip()
            if word in CUSTOM_CAPTIONS:
                del CUSTOM_CAPTIONS[word]
                deleted = True
        if deleted:
            await message.reply_text("Custom words deleted successfully!")
        else:
            await message.reply_text("No words were deleted. Check if the words exist.")
        database.update_one({"chat_id": message.chat.id}, {"$unset": {"state": ""}})

    elif state == "set_channel_id":
        global CUSTOM_CHANNEL_ID
        try:
            channel_id = int(message.text) if message.text.startswith("-100") else message.text
            CUSTOM_CHANNEL_ID = channel_id
            await message.reply_text(f"Custom channel ID set to {CUSTOM_CHANNEL_ID}")
        except ValueError:
            await message.reply_text("Invalid channel ID format.")
        database.update_one({"chat_id": message.chat.id}, {"$unset": {"state": ""}})

    elif state == "set_reaction":
        global USER_REACTIONS
        if message.text and len(message.text) == 1:
            USER_REACTIONS[message.from_user.id] = message.text
            await message.reply_text(f"Auto-reaction emoji set to {message.text}")
        else:
            await message.reply_text("Please send a single emoji.")
        database.update_one({"chat_id": message.chat.id}, {"$unset": {"state": ""}})

    else:
        # Normal message handling if no state is set
        await save(client, message)

# --- Main Logic for Saving Content ---

@Client.on_message(filters.text & filters.private & ~filters.command(["start", "help", "settings", "login", "logout"]))
async def save(client: Client, message: Message):
    global BATCH_RUNNING
    if "https://t.me/" in message.text:
        chat_id, message_ids = extract_chat_and_message_ids(message.text)

        if chat_id is None or message_ids is None:
          await client.send_message(message.chat.id, "Invalid Telegram link format.", reply_to_message_id=message.id)
          return
        
        # Check if a batch process is already running for this user
        if message.chat.id in BATCH_RUNNING:
            await client.send_message(
                message.chat.id,
                "A batch process is already running. Please wait or use /cancel_batch to stop it.",
                reply_to_message_id=message.id,
            )
            return
        if len(message_ids) > 1000:
            await client.send_message(message.chat.id, "You can only process up to 1000 links at a time in a batch.", reply_to_message_id=message.id)
            return
        
        user_data = database.find_one({"chat_id": message.chat.id})
        if not get(user_data, 'logged_in', False) or user_data['session'] is None:
            await client.send_message(message.chat.id, strings['need_login'])
            return

        async def process_batch():
            try:
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                await client.send_message(message.chat.id, f"Starting batch process for {len(message_ids)} messages...", reply_to_message_id=message.id)

                for msg_id in message_ids:
                  try:
                      if isinstance(chat_id, int):
                        msg = await acc.get_messages(chat_id, msg_id)
                      else:
                        msg = await acc.get_messages(chat_id, msg_id)

                      await handle_message(client, acc, message, msg, user_data)
                      await asyncio.sleep(2)  # Reduced delay to speed up batch processing
                  except FloodWait as e:
                    print(f"FloodWait: Sleeping for {e.value} seconds due to flood wait")
                    await asyncio.sleep(e.value)  # Wait for the specified time
                    # Retry logic
                    try:
                      if isinstance(chat_id, int):
                        msg = await acc.get_messages(chat_id, msg_id)
                      else:
                        msg = await acc.get_messages(chat_id, msg_id)
                      await handle_message(client, acc, message, msg, user_data)
                    except Exception as e:
                        await client.send_message(message.chat.id, f"Error on retry after FloodWait: {e}", reply_to_message_id=message.id)
                  except Exception as e:
                      await client.send_message(message.chat.id, f"Error processing message {msg_id}: {e}", reply_to_message_id=message.id)
            except Exception as e:
                await client.send_message(message.chat.id, f"Error during batch process: {e}", reply_to_message_id=message.id)
            finally:
                await acc.disconnect()
                if message.chat.id in BATCH_RUNNING:
                    del BATCH_RUNNING[message.chat.id]

        # Start the batch process in the background
        task = asyncio.create_task(process_batch())
        BATCH_RUNNING[message.chat.id] = task
        

# handle_message function
async def handle_message(client: Client, acc: Client, message: Message, msg: Message, user_data: dict):
    msg_type = get_message_type(msg)
    chat = message.chat.id

    # Auto-reaction
    if message.from_user.id in USER_REACTIONS:
        try:
            await message.react(USER_REACTIONS[message.from_user.id])
        except Exception as e:
            print(f"Failed to react to message: {e}")

    # Forward to custom channel
    if CUSTOM_CHANNEL_ID:
        try:
            if msg_type == "Text":
                await acc.send_message(CUSTOM_CHANNEL_ID, msg.text, entities=msg.entities)
            else:
                await acc.copy_message(CUSTOM_CHANNEL_ID, msg.chat.id, msg.id)
        except Exception as e:
            print(f"Failed to forward message to custom channel: {e}")

    if "Text" == msg_type:
        try:
            caption = apply_custom_caption(msg.text)
            await client.send_message(chat, caption, entities=msg.entities, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            return

    smsg = await client.send_message(message.chat.id, "Downloading", reply_to_message_id=message.id)
    dosta = asyncio.create_task(downstatus(client, f"{message.id}downstatus.txt", smsg))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f"{message.id}downstatus.txt")

    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        return

    upsta = asyncio.create_task(upstatus(client, f"{message.id}upstatus.txt", smsg))

    caption = apply_custom_caption(msg.caption)

    thumb = DEFAULT_THUMBNAIL
    if "Document" == msg_type:
        try:
            if not thumb:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
                thumb = ph_path
            else:
                ph_path = None
        except:
            ph_path = None

        try:
            await client.send_document(
                chat,
                file,
                thumb=thumb,
                caption=caption,
                reply_to_message_id=message.id,
                progress=progress,
                progress_args=[message, "up"],
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        if ph_path:
            os.remove(ph_path)

    elif "Video" == msg_type:
        try:
            if not thumb:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
                thumb = ph_path
            else:
                ph_path = None
        except:
            ph_path = None
        try:
            await client.send_video(
                chat,
                file,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
                thumb=thumb,
                caption=caption,
                reply_to_message_id=message.id,
                progress=progress,
                progress_args=[message, "up"],
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        if ph_path:
            os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

    elif "Voice" == msg_type:
        try:
            await client.send_voice(
                chat,
                file,
                caption=caption,
                caption_entities=msg.caption_entities,
                reply_to_message_id=message.id,
                progress=progress,
                progress_args=[message, "up"],
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
   elif "Audio" == msg_type:
        try:
            if not thumb:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
                thumb = ph_path
            else:
                ph_path = None
        except:
            ph_path = None

        try:
            await client.send_audio(
                chat,
                file,
                thumb=thumb,
                caption=caption,
                reply_to_message_id=message.id,
                progress=progress,
                progress_args=[message, "up"],
            )
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

        if ph_path:
            os.remove(ph_path)
    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

    if os.path.exists(f"{message.id}upstatus.txt"):
        os.remove(f"{message.id}upstatus.txt")
    if os.path.exists(file):
        os.remove(file)
    await client.delete_messages(message.chat.id, [smsg.id])

@Client.on_message(filters.command(["cancel_batch"]))
async def cancel_batch_command(client: Client, message: Message):
    global BATCH_RUNNING
    if message.chat.id in BATCH_RUNNING:
        BATCH_RUNNING[message.chat.id].cancel()
        del BATCH_RUNNING[message.chat.id]
        await client.send_message(message.chat.id, "Current batch process cancelled.", reply_to_message_id=message.id)
    else:
        await client.send_message(message.chat.id, "No batch process is running.", reply_to_message_id=message.id)

# --- Login and Logout ---


@Client.on_message(filters.command(["login"]))
async def login(client, message):
    try:
        user_data = database.find_one({"chat_id": message.chat.id})
        if user_data and user_data['logged_in'] is True:
            await message.reply_text(strings['already_logged_in'])
            return
        data = message.text.split(" ", 1)[1]
        session_string = data.strip()
        logged_acc = Client("saverestricted", session_string=session_string, api_hash=API_HASH, api_id=API_ID)
        await logged_acc.connect()
        me = await logged_acc.get_me()
        database.update_one(
            {"chat_id": message.chat.id},
            {
                "$set": {
                    "session": session_string,
                    "name": me.first_name,
                    "username": me.username,
                    "logged_in": True,
                }
            },
            upsert=True,
        )
        await message.reply_text(strings['logged_in'].format(me.first_name))
    except Exception as e:
        print(e)
        await message.reply_text("Invalid session")

@Client.on_message(filters.command(["logout"]))
async def logout(client, message):
    try:
        user_data = database.find_one({"chat_id": message.chat.id})
        if user_data and user_data['logged_in'] is True:
            database.update_one({"chat_id": message.chat.id}, {"$set": {"logged_in": False}})
            await message.reply_text(strings['logged_out'])
        else:
            await message.reply_text(strings['already_logged_out'])
    except Exception as e:
        print(e)

# --- Helper Functions ---

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    try:
        msg.document.file_id
        return "Document"
    except:
        pass

    try:
        msg.video.file_id
        return "Video"
    except:
        pass

    try:
        msg.animation.file_id
        return "Animation"
    except:
        pass

    try:
        msg.sticker.file_id
        return "Sticker"
    except:
        pass

    try:
        msg.voice.file_id
        return "Voice"
    except:
        pass

    try:
        msg.audio.file_id
        return "Audio"
    except:
        pass

    try:
        msg.photo.file_id
        return "Photo"
    except:
        pass

    try:
        msg.text
        return "Text"
    except:
        pass 
