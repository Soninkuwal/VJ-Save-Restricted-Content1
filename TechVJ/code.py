import asyncio
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import time
import os
import threading
import json
from config import API_ID, API_HASH, BOT_TOKEN, ADMINS
from database.db import database
from TechVJ.strings import strings, HELP_TXT

# --- Configuration and Setup ---
MAX_BATCH_SIZE = 1000

# --- Helper Functions ---

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
            await client.edit_message_text(message.chat.id, message.id, f"Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

async def upstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(message.chat.id, message.id, f"Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

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

# --- Bot Initialization ---
bot = Client(
    "SaveRestrictedContentBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# --- Database and User Data ---

async def get_user_data(user_id):
    user_data = await database.find_one({'chat_id': user_id})
    if not user_data:
        user_data = {
            'chat_id': user_id,
            'logged_in': False,
            'session': None,
            'custom_thumbnail': None,
            'custom_caption': None,
            'custom_words': [],
            'auto_remove_files': False, 
            'enabled_for_all': False
        }
        await database.insert_one(user_data)
    return user_data

async def update_user_data(user_id, data):
    await database.update_one({'chat_id': user_id}, {'$set': data})

# --- Start and Help Commands ---
@bot.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url="http://t.me/Sonickuwalupdatebot")
    ], [
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='http://t.me/Sonickuwalupdatebot'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(message.chat.id, f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>", reply_markup=reply_markup, reply_to_message_id=message.id)

@bot.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

# --- Admin Management ---
@bot.on_message(filters.command("add_admin") & filters.user(ADMINS))
async def add_admin_cmd(client: Client, message: Message):
    try:
        new_admin_id = int(message.text.split()[1])
        ADMINS.append(new_admin_id)
        await message.reply_text(f"Admin {new_admin_id} added successfully.")
    except (IndexError, ValueError):
        await message.reply_text("Invalid usage. Use /add_admin [user_id]")

@bot.on_message(filters.command("remove_admin") & filters.user(ADMINS))
async def remove_admin_cmd(client: Client, message: Message):
    try:
        admin_id_to_remove = int(message.text.split()[1])
        if admin_id_to_remove in ADMINS:
            ADMINS.remove(admin_id_to_remove)
            await message.reply_text(f"Admin {admin_id_to_remove} removed.")
        else:
            await message.reply_text("Admin not found.")
    except (IndexError, ValueError):
        await message.reply_text("Invalid usage. Use /remove_admin [user_id]")

# --- Settings Menu ---
@bot.on_message(filters.command("settings") & filters.private)
async def settings_menu(client: Client, message: Message):
    user_data = await get_user_data(message.from_user.id)
    buttons = [
        [InlineKeyboardButton("Set Custom Thumbnail", callback_data="set_thumbnail")],
        [InlineKeyboardButton("Remove Custom Thumbnail", callback_data="remove_thumbnail")],
        [InlineKeyboardButton("Add Custom Words", callback_data="add_words")],
        [InlineKeyboardButton("Delete Custom Words", callback_data="delete_words")],
        [InlineKeyboardButton("Set Custom Caption", callback_data="set_caption")],
        [InlineKeyboardButton("Auto Remove Files", callback_data="toggle_auto_remove")],
        [InlineKeyboardButton("Enable for all users", callback_data="toggle_enabled_all")]

    ]
    
    # Add current status indicators
    status_text = ""
    status_text += f"Auto Remove Files: {'Enabled' if user_data['auto_remove_files'] else 'Disabled'}\n"
    status_text += f"Enabled for All Users: {'Yes' if user_data['enabled_for_all'] else 'No'}\n"

    await message.reply_text(
        f"⚙️ **Settings**\n\n{status_text}",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@bot.on_callback_query()
async def settings_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    user_data = await get_user_data(user_id)
    data = query.data

    if data == "set_thumbnail":
        await query.message.reply_text("Please send me the image you want to set as the custom thumbnail.")
        await update_user_data(user_id, {"setting_thumbnail": True})

    elif data == "remove_thumbnail":
        await update_user_data(user_id, {"custom_thumbnail": None})
        await query.message.edit_text("Custom thumbnail removed.")

    elif data == "add_words":
        await query.message.reply_text("Send me the words you want to add, separated by commas (e.g., word1, word2).")
        await update_user_data(user_id, {"adding_words": True})

    elif data == "delete_words":
        if user_data['custom_words']:
            words_list = "\n".join(f"{i+1}. {word}" for i, word in enumerate(user_data['custom_words']))
            await query.message.reply_text(f"Send me the number of the word to delete:\n{words_list}")
            await update_user_data(user_id, {"deleting_words": True})
        else:
            await query.message.edit_text("No custom words set.")

    elif data == "set_caption":
        await query.message.reply_text("Send me the custom caption you want to use.")
        await update_user_data(user_id, {"setting_caption": True})

    elif data == "toggle_auto_remove":
        new_status = not user_data['auto_remove_files']
        await update_user_data(user_id, {"auto_remove_files": new_status})
        await query.message.edit_text(f"Auto Remove Files: {'Enabled' if new_status else 'Disabled'}")
    
    elif data == "toggle_enabled_all":
        if user_id in ADMINS:
            new_status = not user_data['enabled_for_all']
            await update_user_data(user_id, {"enabled_for_all": new_status})
            await query.message.edit_text(f"Enabled for all users: {'Enabled' if new_status else 'Disabled'}")
        else:
            await query.answer("Only admins can use this feature.", show_alert=True)

    await query.answer()

# --- Handle Settings Input ---
@bot.on_message(filters.private & (filters.photo | filters.text))
async def handle_settings_input(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)

    if user_data.get('setting_thumbnail'):
        if message.photo:
            photo = message.photo.file_id
            await update_user_data(user_id, {"custom_thumbnail": photo, "setting_thumbnail": False})
            await message.reply_text("Custom thumbnail set successfully.")
        else:
            await message.reply_text("Please send an image.")

    elif user_data.get('adding_words'):
        new_words = [word.strip() for word in message.text.split(",") if word.strip()]
        current_words = user_data.get('custom_words', [])
        updated_words = list(set(current_words + new_words))
        await update_user_data(user_id, {"custom_words": updated_words, "adding_words": False})
        await message.reply_text(f"Custom words added. Total words: {len(updated_words)}")
    
    elif user_data.get('deleting_words'):
        try:
            index_to_delete = int(message.text) - 1
            if 0 <= index_to_delete < len(user_data['custom_words']):
                deleted_word = user_data['custom_words'].pop(index_to_delete)
                await update_user_data(user_id, {"custom_words": user_data['custom_words'], "deleting_words": False})
                await message.reply_text(f"Word '{deleted_word}' deleted.")
            else:
                await message.reply_text("Invalid number. Please send a valid number from the list.")
        except ValueError:
            await message.reply_text("Please send a number.")

    elif user_data.get('setting_caption'):
        await update_user_data(user_id, {"custom_caption": message.text, "setting_caption": False})
        await message.reply_text("Custom caption set successfully.")

# --- Login Command ---
@bot.on_message(filters.command(["login"]))
async def login(client: Client, message: Message):
    user_data = await get_user_data(message.chat.id)
    if get(user_data, 'logged_in', False) and user_data['session'] is not None:
        await client.send_message(message.chat.id, "You are already logged in.")
        return
    
    try:
        phone_number = message.text.split()[1]
    except:
        await message.reply_text("Please enter your phone number after the /login command. (e.g., /login +1xxxxxxxxxx)")
        return
    
    try:
        session = Client(f"{message.chat.id}_session", api_id=API_ID, api_hash=API_HASH, phone_number=phone_number)
        await session.connect()
        
        sent_code = await session.send_code(phone_number)
        await client.send_message(message.chat.id, "Please send the OTP you received. (e.g., /verify 12345)")
        
        async def verify_code(client: Client, message: Message):
            try:
                code = message.text.split()[1]
                await session.sign_in(phone_number, sent_code.phone_code_hash, code)
                session_string = await session.export_session_string()
                
                # Update user data
                await update_user_data(message.chat.id, {'logged_in': True, 'session': session_string})
                
                await client.send_message(message.chat.id, "Successfully logged in!")
                await session.disconnect()

            except Exception as e:
                await client.send_message(message.chat.id, f"Error: {e}")
        
        bot.add_handler(pyrogram.handlers.MessageHandler(verify_code, filters.command(["verify"]) & filters.user(message.from_user.id)))

    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}")

# --- Batch Processing ---
@bot.on_message(filters.command("batch") & filters.private & filters.user(ADMINS))
async def batch_process(client: Client, message: Message):
    try:
        links = message.text.split()[1:]
        if len(links) > MAX_BATCH_SIZE:
            await message.reply_text(f"Maximum {MAX_BATCH_SIZE} links allowed per batch.")
            return

        processing_msg = await message.reply_text(f"Processing {len(links)} links...")
        await process_links(client, message.chat.id, links, processing_msg, message.id)

    except Exception as e:
        await message.reply_text(f"Error: {e}")

async def process_links(client, chat_id, links, processing_msg, reply_to_id, group_id=None):
    success_count = 0
    error_count = 0
    for link in links:
        try:
            await handle_message(client, chat_id, link, reply_to_id, group_id=group_id)
            success_count += 1
        except Exception as e:
            print(f"Error processing link {link}: {e}")
            error_count += 1
        
        await processing_msg.edit_text(f"Processed: {success_count + error_count}/{len(links)}\nSuccess: {success_count}\nErrors: {error_count}")
        await asyncio.sleep(2)  # Rate limiting

    await processing_msg.edit_text("Batch processing completed.")
        
# --- Handle Group/Channel Messages ---
@bot.on_message(filters.group | filters.channel)
async def handle_group_channel_message(client: Client, message: Message):
    # Check if message is from an admin or enabled for all
    if message.from_user and (message.from_user.id in ADMINS or (await get_user_data(message.from_user.id))['enabled_for_all']):
        if message.text and "https://t.me/" in message.text:
            await handle_message(client, message.chat.id, message.text, message.id, group_id=message.chat.id)
        elif message.media:
            await auto_forward_upload(client, message)

# --- Handle Private Messages ---
@bot.on_message(filters.private & filters.text & ~filters.command(["login", "start", "help", "settings", "batch", "add_admin", "remove_admin"]))
async def handle_private_message(client: Client, message: Message):
    if "https://t.me/" in message.text:
        await handle_message(client, message.chat.id, message.text, message.id)

async def handle_message(client: Client, chat_id, text, reply_to_id, group_id=None):
    if "https://t.me/" in text:
        datas = text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID

        for msgid in range(fromID, toID + 1):
            # private
            if "https://t.me/c/" in text:
                user_data = await get_user_data(chat_id)
                if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                    await client.send_message(chat_id, strings['need_login'], reply_to_message_id=reply_to_id)
                    return
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                chatid = int("-100" + datas[4])
                await handle_private(client, acc, chat_id, chatid, msgid, reply_to_id, group_id)
                await acc.disconnect()

            # bot
            elif "https://t.me/b/" in text:
                user_data = await get_user_data(chat_id)
                if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                    await client.send_message(chat_id, strings['need_login'], reply_to_message_id=reply_to_id)
                    return
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                username = datas[4]
                try:
                    await handle_private(client, acc, chat_id, username, msgid, reply_to_id, group_id)
                except Exception as e:
                    await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)
                await acc.disconnect()
            
            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    await client.send_message(chat_id, "The username is not occupied by anyone", reply_to_message_id=reply_to_id)
                    return
                try:
                    await client.copy_message(chat_id, msg.chat.id, msg.id, reply_to_message_id=reply_to_id)
                except:
                    try:
                        user_data = await get_user_data(chat_id)
                        if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                            await client.send_message(chat_id, strings['need_login'], reply_to_message_id=reply_to_id)
                            return
                        acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                        await acc.connect()
                        await handle_private(client, acc, chat_id, username, msgid, reply_to_id, group_id)
                        await acc.disconnect()
                    except Exception as e:
                        await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

            # wait time
            await asyncio.sleep(3)

# --- Auto-Forward and Upload ---
async def auto_forward_upload(client: Client, message: Message):
    user_data = await get_user_data(message.from_user.id)
    
    if message.media:
        try:
            if user_data['custom_caption']:
                caption = user_data['custom_caption'].format(
                    username=message.from_user.username or "",
                    mention=message.from_user.mention or "",
                    first_name=message.from_user.first_name or "",
                    last_name=message.from_user.last_name or "",
                    name=f"{message.from_user.first_name} {message.from_user.last_name}" if message.from_user.first_name else ""
                )
            else:
                caption = message.caption if message.caption else ""

            # Replace custom words
            for word in user_data['custom_words']:
                caption = caption.replace(word, "")

            # Use custom thumbnail if set
            thumb = user_data['custom_thumbnail'] if user_data['custom_thumbnail'] else None

            if message.photo:
                await client.send_photo(message.chat.id, message.photo.file_id, caption=caption, thumb=thumb)
            elif message.video:
                await client.send_video(message.chat.id, message.video.file_id, caption=caption, thumb=thumb, duration=message.video.duration, width=message.video.width, height=message.video.height)
            elif message.document:
                await client.send_document(message.chat.id, message.document.file_id, caption=caption, thumb=thumb)
            elif message.audio:
                await client.send_audio(message.chat.id, message.audio.file_id, caption=caption, thumb=thumb, duration=message.audio.duration)
            elif message.animation:
                await client.send_animation(message.chat.id, message.animation.file_id, caption=caption)
            elif message.voice:
                await client.send_voice(message.chat.id, message.voice.file_id, caption=caption, duration=message.voice.duration)
            elif message.sticker:
                await client.send_sticker(message.chat.id, message.sticker.file_id)
                
        except MessageEmpty:
            print("Error: Message is empty or contains invalid characters")
            if user_data['auto_remove_files']:
                    try:
                        await message.delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")

        except Exception as e:
            print(f"Error in auto_forward_upload: {e}")
            
    if user_data['auto_remove_files']:
        try:
            await message.delete()
        except Exception as e:
            print(f"Error deleting message: {e}")
        

# --- Handle Private Media Messages ---
async def handle_private(client: Client, acc, chat_id, from_chat_id, msg_id, reply_to_id, group_id=None):
    try:
        msg = await acc.get_messages(from_chat_id, msg_id)
        msg_type = get_message_type(msg)
        user_id = chat_id if group_id is None else group_id
        user_data = await get_user_data(user_id)

        if "Text" == msg_type:
            try:
                # Apply custom caption if set
                if user_data['custom_caption']:
                    caption = user_data['custom_caption'].format(
                        username=msg.from_user.username if msg.from_user else "",
                        mention=msg.from_user.mention if msg.from_user else "",
                        first_name=msg.from_user.first_name if msg.from_user else "",
                        last_name=msg.from_user.last_name if msg.from_user else "",
                        name=f"{msg.from_user.first_name} {msg.from_user.last_name}" if msg.from_user and msg.from_user.first_name else ""
                    )
                else:
                    caption = msg.text

                # Replace custom words
                for word in user_data['custom_words']:
                    caption = caption.replace(word, "")

                await client.send_message(chat_id, caption, entities=msg.entities, reply_to_message_id=reply_to_id)
            except MessageEmpty:
                print("Error: Message is empty or contains invalid characters")
                if user_data['auto_remove_files']:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")

            except Exception as e:
                await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)
                return

        smsg = await client.send_message(chat_id, 'Downloading', reply_to_message_id=reply_to_id)
        dosta = asyncio.create_task(downstatus(client, f'{msg_id}downstatus.txt', smsg))
        try:
            file = await acc.download_media(msg, progress=progress, progress_args=[smsg, "down"])
            os.remove(f'{msg_id}downstatus.txt')
        except Exception as e:
            await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)
            return

        upsta = asyncio.create_task(upstatus(client, f'{msg_id}upstatus.txt', smsg))

        # Apply custom caption if set
        if user_data['custom_caption']:
            caption = user_data['custom_caption'].format(
                username=msg.from_user.username if msg.from_user else "",
                mention=msg.from_user.mention if msg.from_user else "",
                first_name=msg.from_user.first_name if msg.from_user else "",
                last_name=msg.from_user.last_name if msg.from_user else "",
                name=f"{msg.from_user.first_name} {msg.from_user.last_name}" if msg.from_user and msg.from_user.first_name else ""
            )
        else:
            caption = msg.caption if msg.caption else ""

        # Replace custom words
        for word in user_data['custom_words']:
            caption = caption.replace(word, "")

        # Use custom thumbnail if set
        ph_path = user_data['custom_thumbnail'] if user_data['custom_thumbnail'] else None

        if "Document" == msg_type:
            try:
                await client.send_document(chat_id, file, thumb=ph_path, caption=caption, reply_to_message_id=reply_to_id, progress=progress, progress_args=[smsg, "up"])
            except MessageEmpty:
                print("Error: Message is empty or contains invalid characters")
                if user_data['auto_remove_files']:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")

            except Exception as e:
                await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

        elif "Video" == msg_type:
            try:
                await client.send_video(chat_id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=reply_to_id, progress=progress, progress_args=[smsg, "up"])
            except MessageEmpty:
                print("Error: Message is empty or contains invalid characters")
                if user_data['auto_remove_files']:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")

            except Exception as e:
                await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

        elif "Animation" == msg_type:
            try:
                await client.send_animation(chat_id, file, reply_to_message_id=reply_to_id, caption=caption)
            except MessageEmpty:
                print("Error: Message is empty or contains invalid characters")
                if user_data['auto_remove_files']:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")

            except Exception as e:
                await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

        elif "Sticker" == msg_type:
            try:
                await client.send_sticker(chat_id, file, reply_to_message_id=reply_to_id)
            except Exception as e:
                await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

        elif "Voice" == msg_type:
            try:
                await client.send_voice(chat_id, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=reply_to_id, progress=progress, progress_args=[smsg, "up"])
            except MessageEmpty:
                print("Error: Message is empty or contains invalid characters")
                if user_data['auto_remove_files']:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")

            except Exception as e:
                await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

        elif "Audio" == msg_type:
            try:
                await client.send_audio(chat_id, file, thumb=ph_path, caption=caption, reply_to_message_id=reply_to_id, progress=progress, progress_args=[smsg, "up"])
            except MessageEmpty:
                print("Error: Message is empty or contains invalid characters")
                if user_data['auto_remove_files']:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")

            except Exception as e:
                await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

        elif "Photo" == msg_type:
            try:
                await client.send_photo(chat_id, file, caption=caption, reply_to_message_id=reply_to_id)
            except MessageEmpty:
                print("Error: Message is empty or contains invalid characters")
                if user_data['auto_remove_files']:
                    try:
                        await msg.delete()
                    except Exception as e:
                        print(f"Error deleting message: {e}")

            except Exception as e:
                await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

        if os.path.exists(f'{msg_id}upstatus.txt'):
            os.remove(f'{msg_id}upstatus.txt')
            if user_data['auto_remove_files']:
                os.remove(file)
        await client.delete_messages(chat_id, [smsg.id])

    except Exception as e:
        print(f"Error in handle_private: {e}")
        await client.send_message(chat_id, f"Error: {e}", reply_to_message_id=reply_to_id)

# --- Auto Reaction ---
@bot.on_message(group= -1)
async def auto_react(client: Client, message: Message):
    if message.from_user and message.from_user.id in ADMINS:
        try:
            await message.react("👍")
        except Exception as e:
            print(f"Error reacting to message: {e}")

# --- Bot Start ---
print("Bot started")
bot.run()