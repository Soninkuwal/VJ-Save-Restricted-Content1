import asyncio
import os
import json
import time
import re
from datetime import datetime

import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from config import API_ID, API_HASH
from database.db import database
from TechVJ.strings import strings, HELP_TXT

# --- Constants ---
MAX_BATCH_SIZE = 1000
ADMIN_LIST = []  # Initialize with your admin user IDs later

# --- Helper Functions ---

def get(obj, key, default=None):
    try:
        return obj[key]
    except (KeyError, TypeError):
        return default

def is_admin(user_id):
    return user_id in ADMIN_LIST

def parse_link(text):
    """Parses a Telegram link and returns chat ID/username and message ID(s)."""
    match = re.match(r"https://t\.me/(?:c/(\d+)|(\w+)|b/(\w+))/(\d+)(?:-(\d+))?(?:\?single)?", text)
    if not match:
        return None

    chat_id, username, bot_username, start_msg_id, end_msg_id = match.groups()

    if chat_id:
        chat_id = -1000000000000 - int(chat_id)  # Convert to internal format
    elif bot_username:
      username = bot_username
    start_msg_id = int(start_msg_id)
    end_msg_id = int(end_msg_id) if end_msg_id else start_msg_id

    return chat_id, username, start_msg_id, end_msg_id

# --- Progress & Status ---

async def downstatus(client: Client, statusfile, message):
    start_time = time.time()
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            elapsed_time = time.time() - start_time
            
            await client.edit_message_text(
                message.chat.id,
                message.id,
                f"Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}\nTime taken: {elapsed_time:.2f}s",
            )
            await asyncio.sleep(5)  # Reduced sleep time
        except Exception as e:
            print(f"Error in downstatus: {e}")
            await asyncio.sleep(5)

async def upstatus(client: Client, statusfile, message):
    start_time = time.time()
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            elapsed_time = time.time() - start_time
            await client.edit_message_text(
                message.chat.id,
                message.id,
                f"Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}\nTime taken: {elapsed_time:.2f}s",
            )
            await asyncio.sleep(5) # Reduced sleep time
        except Exception as e:
            print(f"Error in upstatus: {e}")
            await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# --- Settings Management ---

class Settings:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.data = database.get_settings(chat_id) or {
            "custom_thumbnail": None,
            "custom_caption": "",
            "replace_words": {},
            "auto_delete_files" : False,
            "auto_react": False,
            "forward_mode":False,
            "target_channel_id":None
        }

    def set(self, key, value):
        self.data[key] = value
        database.update_settings(self.chat_id, self.data)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def add_replace_word(self, original, replacement):
        self.data["replace_words"][original] = replacement
        database.update_settings(self.chat_id, self.data)

    def remove_replace_word(self, original):
        if original in self.data["replace_words"]:
            del self.data["replace_words"][original]
            database.update_settings(self.chat_id, self.data)

# --- Command Handlers ---

@Client.on_message(filters.command(["start"]) & filters.private)
async def send_start(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url="http://t.me/Sonickuwalupdatebot")
    ], [
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='http://t.me/Sonickuwalupdatebot'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        message.chat.id,
        f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>",
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )

@Client.on_message(filters.command(["help"]) & filters.private)
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

@Client.on_message(filters.command("settings") & filters.private)
async def settings_command(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    settings = Settings(message.chat.id)
    buttons = [
        [
            InlineKeyboardButton("Set Custom Thumbnail", callback_data="set_thumbnail"),
            InlineKeyboardButton("Remove Custom Thumbnail", callback_data="remove_thumbnail"),
        ],
        [
            InlineKeyboardButton("Add Replace Word", callback_data="add_replace_word"),
            InlineKeyboardButton("Remove Replace Word", callback_data="remove_replace_word"),
        ],
        [
            InlineKeyboardButton("Set Custom Caption", callback_data="set_caption"),
            InlineKeyboardButton("Remove Custom Caption", callback_data="remove_caption"),
        ],
        [
            InlineKeyboardButton("Set Target Channel", callback_data="set_target_channel"),
        ],
        [
            InlineKeyboardButton(f"Auto Delete Files: {'✅' if settings.get('auto_delete_files') else '❌'}", callback_data="toggle_auto_delete"),
        ],
        [
            InlineKeyboardButton(f"Auto React: {'✅' if settings.get('auto_react') else '❌'}", callback_data="toggle_auto_react"),
        ],
        [
            InlineKeyboardButton(f"forward Mode : {'✅' if settings.get('forward_mode') else '❌'}", callback_data="toggle_forward_mode"),
        ],
        
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text("Bot Settings:", reply_markup=reply_markup)

@Client.on_message(filters.command("add_admin") & filters.private)
async def add_admin_command(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if len(message.command) != 2:
        await message.reply_text("Usage: /add_admin <user_id>")
        return

    try:
        new_admin_id = int(message.command[1])
        ADMIN_LIST.append(new_admin_id)
        await message.reply_text(f"User {new_admin_id} added to the admin list.")
    except ValueError:
        await message.reply_text("Invalid user ID.")

@Client.on_message(filters.command("cancel_batch") & filters.private)
async def cancel_batch_command(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    # In a real implementation, you would need a way to track and manage
    # ongoing batch operations, possibly using a dictionary or database
    # to store batch IDs and their corresponding tasks.
    # For this example, we'll just send a message.

    await message.reply_text("Canceling the ongoing batch operation... (Not fully implemented)")

@Client.on_callback_query(filters.regex(r"^(set_thumbnail|remove_thumbnail|add_replace_word|remove_replace_word|set_caption|remove_caption|toggle_auto_delete|toggle_auto_react|toggle_forward_mode|set_target_channel)$"))
async def settings_callback(client: Client, query: CallbackQuery):
    settings = Settings(query.message.chat.id)

    if query.data == "set_thumbnail":
        await query.message.reply_text("Please send me the image you want to use as the custom thumbnail.")
        # Set a flag in user's settings to indicate that we're waiting for a thumbnail
        settings.set("expecting_thumbnail", True)

    elif query.data == "remove_thumbnail":
        settings.set("custom_thumbnail", None)
        await query.message.edit_text("Custom thumbnail removed.")

    elif query.data == "add_replace_word":
        await query.message.reply_text("Please send the word you want to replace in the format: `original:replacement`")
        settings.set("expecting_replace_word", True)

    elif query.data == "remove_replace_word":
        await query.message.reply_text("Please send the word you want to stop replacing.")
        settings.set("expecting_remove_replace_word", True)

    elif query.data == "set_caption":
        await query.message.reply_text("Please send the custom caption you want to use.")
        settings.set("expecting_caption", True)

    elif query.data == "remove_caption":
      settings.set("custom_caption", None)
      await query.message.edit_text("Custom caption removed.")

    elif query.data == "set_target_channel":
        await query.message.reply_text("Please send the target channel ID .")
        settings.set("expecting_target_channel", True)

    elif query.data == "toggle_auto_delete":
      settings.set("auto_delete_files", not settings.get("auto_delete_files"))
      await query.message.edit_reply_markup(
          InlineKeyboardMarkup(
              [
                  [
                      InlineKeyboardButton(
                          f"Auto Delete Files: {'✅' if settings.get('auto_delete_files') else '❌'}",
                          callback_data="toggle_auto_delete",
                      )
                  ]
              ]
          )
      )
    
    elif query.data == "toggle_auto_react":
      settings.set("auto_react", not settings.get("auto_react"))
      await query.message.edit_reply_markup(
          InlineKeyboardMarkup(
              [
                  [
                      InlineKeyboardButton(
                          f"Auto React: {'✅' if settings.get('auto_react') else '❌'}",
                          callback_data="toggle_auto_react",
                      )
                  ]
              ]
          )
      )

    elif query.data == "toggle_forward_mode":
      settings.set("forward_mode", not settings.get("forward_mode"))
      await query.message.edit_reply_markup(
          InlineKeyboardMarkup(
              [
                  [
                      InlineKeyboardButton(
                          f"forward Mode: {'✅' if settings.get('forward_mode') else '❌'}",
                          callback_data="toggle_forward_mode",
                      )
                  ]
              ]
          )
      )

@Client.on_message(filters.photo & filters.private)
async def handle_thumbnail_photo(client: Client, message: Message):
    settings = Settings(message.chat.id)
    if settings.get("expecting_thumbnail"):
        settings.set("custom_thumbnail", message.photo.file_id)
        settings.set("expecting_thumbnail", False)
        await message.reply_text("Custom thumbnail set successfully.")

@Client.on_message(filters.text & filters.private)
async def handle_settings_input(client: Client, message: Message):
    settings = Settings(message.chat.id)

    if settings.get("expecting_replace_word"):
        try:
            original, replacement = message.text.split(":", 1)
            settings.add_replace_word(original.strip(), replacement.strip())
            settings.set("expecting_replace_word", False)
            await message.reply_text(f"Word replacement added: `{original}` -> `{replacement}`")
        except ValueError:
            await message.reply_text("Invalid format. Please use `original:replacement`")

    elif settings.get("expecting_remove_replace_word"):
        original = message.text.strip()
        settings.remove_replace_word(original)
        settings.set("expecting_remove_replace_word", False)
        await message.reply_text(f"Word replacement for `{original}` removed.")

    elif settings.get("expecting_caption"):
        settings.set("custom_caption", message.text)
        settings.set("expecting_caption", False)
        await message.reply_text("Custom caption set successfully.")

    elif settings.get("expecting_target_channel"):
        try:
            target_channel_id = int(message.text)
            settings.set("target_channel_id", target_channel_id)
            settings.set("expecting_target_channel", False)
            await message.reply_text(f"Target channel ID set to : {target_channel_id}")
        except ValueError:
            await message.reply_text("Invalid target channel ID. Please provide a valid integer.")

@Client.on_message(filters.private & ~filters.command(["start", "help", "settings", "add_admin", "cancel_batch"]))
async def save(client: Client, message: Message):
    # --- Input Validation & Parsing ---

    if not message.text:
      return

    if "https://t.me/" not in message.text:
      if settings.get('auto_react'):
          await message.react("👍")
      return

    links = message.text.split()
    total_links = len(links)

    if total_links > MAX_BATCH_SIZE:
        await message.reply_text(f"You can send a maximum of {MAX_BATCH_SIZE} links at once.")
        return

    settings = Settings(message.chat.id)
    logged_in = False
    user_data = database.find_one({'chat_id': message.chat.id})

    if user_data and get(user_data, 'logged_in', False) and user_data['session']:
        acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
        try:
            await acc.connect()
            logged_in = True
        except Exception as e:
            print(f"Error connecting to user account: {e}")
            await client.send_message(message.chat.id, "Error connecting to your account. Please /login again.")
            logged_in = False

    # --- Main Processing Loop ---
    s_time = time.time()

    for link in links:
        parsed_data = parse_link(link)
        if not parsed_data:
            await client.send_message(message.chat.id, f"Invalid Telegram link: {link}", reply_to_message_id=message.id)
            continue

        chat_id, username, start_msg_id, end_msg_id = parsed_data
        
        # --- Batch Handling (if applicable) ---
        for msg_id in range(start_msg_id, end_msg_id + 1):
            try:
                # --- Fetching the Message ---
                if chat_id:  # Private chat/channel
                    if not logged_in:
                        await client.send_message(message.chat.id, strings['need_login'])
                        return
                    msg = await acc.get_messages(chat_id, msg_id)
                else:  # Public channel
                    try:
                        msg = await client.get_messages(username, msg_id)
                    except UsernameNotOccupied:
                        await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                        return

                # --- Handling Different Message Types ---
                msg_type = get_message_type(msg)

                if msg_type == "Text":
                  try:
                      text = msg.text
                      if settings.get('replace_words'):
                        for o, r in settings.get('replace_words').items():
                          text = re.sub(o, r, text, flags=re.IGNORECASE)
                      if settings.get('forward_mode') and settings.get('target_channel_id'):
                        await client.send_message(settings.get('target_channel_id'), text, entities=msg.entities)
                      else:
                        await client.send_message(message.chat.id, text, entities=msg.entities, reply_to_message_id=message.id)
                  except MessageEmpty:
                      await client.send_message(message.chat.id, "**Error:** The message is empty.", reply_to_message_id=message.id)
                  except Exception as e:
                      await client.send_message(message.chat.id, f"**Error:** {e}", reply_to_message_id=message.id)

                else:
                    # --- Downloading and Uploading ---
                    smsg = await client.send_message(message.chat.id, 'Downloading', reply_to_message_id=message.id)
                    dosta = asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))
                    try:
                        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
                        os.remove(f'{message.id}downstatus.txt')
                        
                    except Exception as e:
                        await client.send_message(message.chat.id, f"**Error**: {e}", reply_to_message_id=message.id)
                        continue
                    upsta = asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

                    caption = settings.get("custom_caption") or msg.caption or ""

                    if settings.get('replace_words'):
                      for o, r in settings.get('replace_words').items():
                        caption = re.sub(o, r, caption, flags=re.IGNORECASE)

                    # --- Sending the File ---
                    thumb = settings.get("custom_thumbnail")

                    try:
                        if msg_type == "Document":
                            if not thumb:
                                try:
                                    ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
                                    thumb = ph_path
                                except:
                                  thumb = None
                            if settings.get('forward_mode') and settings.get('target_channel_id'):
                              await client.send_document(settings.get('target_channel_id'), file, thumb=thumb, caption=caption, progress=progress, progress_args=[message, "up"])
                            else:
                              await client.send_document(message.chat.id, file, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

                        elif msg_type == "Video":
                            if not thumb:
                                try:
                                    ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
                                    thumb = ph_path
                                except:
                                  thumb = None
                            if settings.get('forward_mode') and settings.get('target_channel_id'):
                              await client.send_video(settings.get('target_channel_id'), file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=caption, progress=progress, progress_args=[message, "up"])
                            else:
                              await client.send_video(message.chat.id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

                        elif msg_type == "Animation":
                            if settings.get('forward_mode') and settings.get('target_channel_id'):
                              await client.send_animation(settings.get('target_channel_id'), file, reply_to_message_id=message.id)
                            else:
                              await client.send_animation(message.chat.id, file, reply_to_message_id=message.id)

                        elif msg_type == "Sticker":
                            if settings.get('forward_mode') and settings.get('target_channel_id'):
                              await client.send_sticker(settings.get('target_channel_id'), file, reply_to_message_id=message.id)
                            else:
                              await client.send_sticker(message.chat.id, file, reply_to_message_id=message.id)

                        elif msg_type == "Voice":
                            if settings.get('forward_mode') and settings.get('target_channel_id'):
                              await client.send_voice(settings.get('target_channel_id'), file, caption=caption, caption_entities=msg.caption_entities, progress=progress, progress_args=[message, "up"])
                            else:
                              await client.send_voice(message.chat.id, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

                        elif msg_type == "Audio":
                            if not thumb:
                                try:
                                    ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
                                    thumb = ph_path
                                except:
                                  thumb = None

                            if settings.get('forward_mode') and settings.get('target_channel_id'):
                              await client.send_audio(settings.get('target_channel_id'), file, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
                            else:
                              await client.send_audio(message.chat.id, file, thumb=thumb, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

                        elif msg_type == "Photo":
                            if settings.get('forward_mode') and settings.get('target_channel_id'):
                              await client.send_photo(settings.get('target_channel_id'), file, caption=caption, reply_to_message_id=message.id)
                            else:
                              await client.send_photo(message.chat.id, file, caption=caption, reply_to_message_id=message.id)

                    except Exception as e:
                        await client.send_message(message.chat.id, f"**Error**: {e}", reply_to_message_id=message.id)
                    finally:
                        if settings.get('auto_delete_files') and os.path.exists(file):
                            os.remove(file)
                        if thumb and os.path.exists(thumb):
                            os.remove(thumb)
                        if os.path.exists(f'{message.id}upstatus.txt'):
                            os.remove(f'{message.id}upstatus.txt')
                        await client.delete_messages(message.chat.id,[smsg.id])

            except FloodWait as e:
                await asyncio.sleep(e.value)  # Wait for the specified time
                continue # Retry the same message
            except (UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired) as e:
                print(f"Skipping message due to error: {e}")
                continue
            except Exception as e:
                await client.send_message(message.chat.id, f"**Error**: {e}", reply_to_message_id=message.id)
                continue

            # --- Wait & Auto-Reactions ---
            await asyncio.sleep(3)  # Increased to 3 seconds for potential rate limiting
            if settings.get('auto_react'):
                await message.react("👍")

    # --- Cleanup & Final Message ---
    e_time = time.time()
    time_taken = round(e_time - s_time, 2)
    if total_links > 1:
        await client.send_message(message.chat.id, f"Batch completed!\nProcessed {total_links} links in {time_taken} seconds.")

    try:
        await acc.disconnect()
    except:
        pass

# --- Login/Logout ---

@Client.on_message(filters.command(["login"]) & filters.private)
async def login(client: Client, message: Message):
    user_data = database.find_one({'chat_id': message.chat.id})
    if user_data and get(user_data, 'logged_in', False) and get(user_data, 'session', None):
        await client.send_message(message.chat.id, 'Already Logged In', reply_to_message_id=message.id)
        return

    try:
        user_data = {
            'chat_id': message.chat.id,
            'logged_in': False,
            'session': None
        }
        database.add_user(user_data)
    except Exception as e:
        print(e)

    try:
        # --- 1. Send code ---
        try:
            sent_code = await client.send_code(message.chat.id)
        except (ApiIdInvalid, ApiIdPublishedFlood):
            await message.reply_text("Invalid API ID/Hash. Please set them in config.py")
            return
        except PhoneNumberInvalid:
            await message.reply_text("Invalid Phone Number. Please set it in config.py")
            return
        
        await message.reply_text("Please send your phone number in international format (e.g., +11234567890)")
        
        @Client.on_message(filters.private & ~filters.command(["login", "logout", "start", "help", "settings"]) & filters.regex(r"^\+\d+$"), group=1)
        async def receive_phone_number(client: Client, phone_message: Message):
            phone_number = phone_message.text

            try:
                sent_code = await client.send_code(phone_number)
            except FloodWait as e:
                await phone_message.reply_text(f"Flood error. Please wait {e.value} seconds and try again.")
                return

            await phone_message.reply_text(f"Please send the code you received from Telegram (check other devices if logged in).")

            @Client.on_message(filters.private & ~filters.command(["login", "logout", "start", "help", "settings"]) & ~filters.regex(r"^\+\d+$"), group=2)
            async def receive_code(client: Client, code_message: Message):
                code = code_message.text

                try:
                    # --- 2. Sign in ---
                    me = await client.sign_in(phone_number, sent_code.phone_code_hash, code)
                    
                    session_string = await client.export_session_string()
                    user_data['session'] = session_string
                    user_data['logged_in'] = True
                    database.update_user(user_data)
                    await code_message.reply_text(f"Logged in as {me.first_name} {me.last_name or ''} ({me.id})")

                    # --- Disconnect to avoid session conflicts ---
                    await client.disconnect()

                except Exception as e:
                    await code_message.reply_text(f"Error: {e}")

    except Exception as e:
        await message.reply_text(f"Error: {e}")

@Client.on_message(filters.command(["logout"]) & filters.private)
async def logout(client: Client, message: Message):
    user_data = database.find_one({'chat_id': message.chat.id})
    if not get(user_data, 'logged_in', False) or user_data['session'] is None:
        await client.send_message(message.chat.id, "Not Logged In", reply_to_message_id=message.id)
        return

    try:
        acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
        await acc.connect()
        await acc.stop()
    except:
        pass

    user_data['session'] = None
    user_data['logged_in'] = False
    database.update_user(user_data)
    await client.send_message(message.chat.id, "Logged out successfully", reply_to_message_id=message.id)

# --- Message Type Helper ---

def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    if msg.text:
        return "Text"
    elif msg.document:
        return "Document"
    elif msg.video:
        return "Video"
    elif msg.animation:
        return "Animation"
    elif msg.sticker:
        return "Sticker"
    elif msg.voice:
        return "Voice"
    elif msg.audio:
        return "Audio"
    elif msg.photo:
        return "Photo"
    else:
        return "Unknown"

# --- Initialize Admins ---

if __name__ == "__main__":
    try:
        with open("admins.json", "r") as f:
            data = json.load(f)
            ADMIN_LIST = data.get("admin_ids", [])
    except FileNotFoundError:
        print("admins.json file not found. Creating a new one.")
        with open("admins.json", "w") as f:
            json.dump({"admin_ids": []}, f)

    print("Bot started")
    Client("SaveRestricted").run()