# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import os
import time
import re
from datetime import datetime

import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageNotModified, MessageEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
from pyrogram.errors import FloodWait, MessageEmpty
from config import API_ID, API_HASH
from database.db import database
from TechVJ.strings import strings, HELP_TXT

# --- Constants ---
ADMINS = [1234567890]  # Replace with your admin IDs, you can add multiple
THUMBNAIL_COLLECTION = "thumbnails"
BATCHES = {}  # Store active batch processes {chat_id: {msg_id, from_id, to_id}}
CUSTOM_CAPTIONS = {}  # {user_id: "Custom Caption"}
REPLACE_WORDS = {} # {user_id: [(word_to_replace, replacement_word)]}

# --- Helper Functions ---

def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default

def is_admin(user_id):
    return user_id in ADMINS

def get_readable_time(seconds: int) -> str:
    """Get Time From Seconds"""
    count = 0
    up_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    hmm = len(time_list)
    for x in range(hmm):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    if len(time_list) == 4:
        up_time += time_list.pop() + ", "
    time_list.reverse()
    up_time += ":".join(time_list)
    return up_time

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
            
            try:
                await client.edit_message_text(message.chat.id, message.id, f"Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}\n\n**Time Taken :** `{get_readable_time(time.time() - start_time)}`")
            except MessageNotModified:
                pass    
            await asyncio.sleep(10)
            
        except:
            await asyncio.sleep(5)

# upload status
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
            try:
                await client.edit_message_text(message.chat.id, message.id, f"Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}\n\n**Time Taken :** `{get_readable_time(time.time() - start_time)}`")
            except MessageNotModified:
                pass
            await asyncio.sleep(10)
            
        except:
            await asyncio.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# --- Bot setup ---
# (No changes needed here if you've configured correctly)

# --- Start command ---
@Client.on_message(filters.command(["start"]) & filters.private)
async def send_start(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "http://t.me/Sonickuwalupdatebot")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='http://t.me/Sonickuwalupdatebot'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
	]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(message.chat.id, f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>", reply_markup=reply_markup, reply_to_message_id=message.id)
    return

# --- Help command ---
@Client.on_message(filters.command(["help"]) & filters.private)
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

# --- Admin Commands ---

# --- Add Admin ---
@Client.on_message(filters.command("addadmin") & filters.private)
async def add_admin(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if len(message.command) < 2:
        await message.reply_text("Please provide the user ID to add as an admin.")
        return

    try:
        new_admin_id = int(message.command[1])
        ADMINS.append(new_admin_id)
        await message.reply_text(f"User {new_admin_id} added as an admin.")
    except ValueError:
        await message.reply_text("Invalid user ID format.")

# --- Set Thumbnail ---
@Client.on_message(filters.command("set_thumbnail") & filters.private)
async def set_thumbnail(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if not message.reply_to_message or not message.reply_to_message.photo:
        await message.reply_text("Please reply to a photo to set it as a thumbnail.")
        return

    file_id = message.reply_to_message.photo.file_id
    await database.update_one({"user_id": message.from_user.id}, {"$set": {"thumbnail": file_id}}, upsert=True)
    await message.reply_text("Thumbnail set successfully!")

# --- Remove Thumbnail ---
@Client.on_message(filters.command("remove_thumbnail") & filters.private)
async def remove_thumbnail(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    await database.update_one({"user_id": message.from_user.id}, {"$unset": {"thumbnail": ""}})
    await message.reply_text("Thumbnail removed successfully!")

# --- Add Custom Caption ---
@Client.on_message(filters.command("add_caption") & filters.private)
async def add_caption(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if len(message.command) < 2:
        await message.reply_text("Please provide a custom caption.")
        return

    CUSTOM_CAPTIONS[message.from_user.id] = " ".join(message.command[1:])
    await message.reply_text("Custom caption added successfully!")

# --- Remove Custom Caption ---
@Client.on_message(filters.command("remove_caption") & filters.private)
async def remove_caption(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if message.from_user.id in CUSTOM_CAPTIONS:
        del CUSTOM_CAPTIONS[message.from_user.id]
        await message.reply_text("Custom caption removed!")
    else:
        await message.reply_text("No custom caption set for you.")

# --- Add Replace Words ---
@Client.on_message(filters.command("add_replace_words") & filters.private)
async def add_replace_words(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if len(message.command) < 3:
        await message.reply_text("Please provide words to replace in the format: /add_replace_words word1 replacement1 word2 replacement2 ...")
        return
    
    words_to_replace = message.command[1::2]
    replacements = message.command[2::2]

    if len(words_to_replace) != len(replacements):
        await message.reply_text("Number of words to replace and replacements should be equal.")
        return
    
    replace_list = []
    for word, replacement in zip(words_to_replace, replacements):
        replace_list.append((word, replacement))

    REPLACE_WORDS[message.from_user.id] = replace_list
    await message.reply_text("Words to replace added successfully!")

# --- Remove Replace Words ---
@Client.on_message(filters.command("remove_replace_words") & filters.private)
async def remove_replace_words(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return
    
    if message.from_user.id in REPLACE_WORDS:
        del REPLACE_WORDS[message.from_user.id]
        await message.reply_text("Replacement words removed successfully!")
    else:
        await message.reply_text("No replacement words set for you.")
    

# --- Start Batch ---
@Client.on_message(filters.command("batch") & filters.private)
async def start_batch(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return
    
    if len(message.command) < 2:
        await message.reply_text("Please provide at least one link to start the batch process.")
        return

    links = message.command[1:]
    if len(links) > 1000:
        await message.reply_text("You can only process up to 1000 links in a single batch.")
        return

    msg = await message.reply_text("Batch process started!")
    batch_id = msg.id
    BATCHES[message.chat.id] = {"msg_id": batch_id, "links": links, "success": 0, "failed": 0, "user_id":message.from_user.id}
    await process_batch(client, message.chat.id)
    

# --- Cancel Batch ---
@Client.on_message(filters.command("cancel_batch") & filters.private)
async def cancel_batch(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if message.chat.id in BATCHES:
        user_id = BATCHES[message.chat.id]['user_id']
        if user_id != message.from_user.id :
            await message.reply_text("You are not authorized to cancel batch.")
            return

        del BATCHES[message.chat.id]
        await message.reply_text("Batch process cancelled.")
    else:
        await message.reply_text("No active batch process found.")

# --- Set Custom Channel ID ---
@Client.on_message(filters.command("set_channel") & filters.private)
async def set_channel(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if len(message.command) < 2:
        await message.reply_text("Please provide the channel ID.")
        return

    try:
        channel_id = int(message.command[1])
        await database.update_one({"user_id": message.from_user.id}, {"$set": {"channel_id": channel_id}}, upsert=True)
        await message.reply_text(f"Custom channel ID set to {channel_id}")
    except ValueError:
        await message.reply_text("Invalid channel ID format.")

# --- Message Empty Handling ---
@Client.on_message(filters.command("message_empty_handling") & filters.private)
async def message_empty_handling(client: Client, message: Message):
    if not is_admin(message.from_user.id):
        await message.reply_text("You are not authorized to use this command.")
        return

    if len(message.command) < 2:
        await message.reply_text("Please specify 'on' or 'off' to enable or disable message empty handling.")
        return

    value = message.command[1].lower()
    if value not in ["on", "off"]:
        await message.reply_text("Invalid value. Please use 'on' or 'off'.")
        return

    enabled = value == "on"
    await database.update_one({"user_id": message.from_user.id}, {"$set": {"message_empty_handling": enabled}}, upsert=True)
    await message.reply_text(f"Message empty handling {'enabled' if enabled else 'disabled'}.")

# --- Process Batch Function ---
async def process_batch(client: Client, chat_id: int):
    batch_info = BATCHES.get(chat_id)
    if not batch_info:
        return

    total_links = len(batch_info["links"])
    for index, link in enumerate(batch_info["links"]):
        if chat_id not in BATCHES:  # Check if batch was cancelled
            break
        try:
            await save_content_from_link(client, batch_info["user_id"], link)
            BATCHES[chat_id]["success"] += 1
        except Exception as e:
            print(f"Error processing link {link}: {e}")
            BATCHES[chat_id]["failed"] += 1
            

        success_count = BATCHES[chat_id]["success"]
        failed_count = BATCHES[chat_id]["failed"]

        try:
            await client.edit_message_text(
                chat_id,
                batch_info["msg_id"],
                f"Batch Process\n\nTotal Links: {total_links}\nProcessed: {index + 1}\nSuccess: {success_count}\nFailed: {failed_count}"
            )
        except MessageNotModified:
            pass

    if chat_id in BATCHES:
        await client.send_message(chat_id, f"Batch process completed!\n\nTotal Links: {total_links}\nSuccess: {success_count}\nFailed: {failed_count}")
        del BATCHES[chat_id]

# --- Save Content from Link ---
async def save_content_from_link(client: Client, user_id: int, link: str):
    # Extract chat ID and message ID from the link
    try:
        datas = link.split("/")
        if "https://t.me/c/" in link:
            chat_id = int("-100" + datas[4])
            msg_id = int(datas[5].replace("?single",""))
        elif "https://t.me/b/" in link:
            return
            # chat_id = datas[4] # this is a bot username, need to resolve to id via API in future
            # msg_id = int(datas[5].replace("?single",""))
        else:  # Assuming public channel
            chat_id = datas[3]
            msg_id = int(datas[4].replace("?single",""))
    except (IndexError, ValueError):
        raise ValueError("Invalid link format.")

    user_data = database.find_one({'user_id': user_id}) # Using user_id now
    if not get(user_data, 'logged_in', False) or user_data['session'] is None:
        raise Exception(strings['need_login'])

    acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
    await acc.connect()

    try:
        msg = await acc.get_messages(chat_id, msg_id)

        # Forward if enabled
        if get(user_data, 'forward_enabled', False):  
            await msg.forward(user_data.get('forward_chat_id'))
            return

        # --- Handle Custom Channel ID ---
        custom_channel_id = get(user_data, 'channel_id')
        destination_chat_id = custom_channel_id if custom_channel_id else user_id

        # --- Add Reaction ---
        if destination_chat_id != user_id:
            try:
                await acc.send_reaction(chat_id, msg_id, "👍")  # Default reaction, can be customizable
            except Exception as e:
                print(f"Failed to add reaction: {e}")

        # --- Copy/Send Message ---
        await copy_or_send_message(client, acc, msg, destination_chat_id, user_id)

    except UsernameNotOccupied:
        raise ValueError("The username is not occupied by anyone")
    except (InviteHashExpired, UserIsBlocked, InputUserDeactivated):
        raise ValueError("Invalid link or chat is inaccessible.")
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await save_content_from_link(client, user_id, link)
    except Exception as e:
        if get(user_data, 'message_empty_handling', False) and isinstance(e, MessageEmpty):
            print("Encountered MessageEmpty error, skipping...")
            return
        raise e
    finally:
        await acc.disconnect()

# --- Copy or Send Message ---
async def copy_or_send_message(client: Client, acc: Client, msg: Message, destination_chat_id: int, user_id: int):
    
    smsg = await client.send_message(destination_chat_id, 'Downloading')
    dosta = asyncio.create_task(downstatus(client, f'{msg.id}downstatus.txt', smsg))
    
    file = None
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[smsg,"down"])
        os.remove(f'{msg.id}downstatus.txt')
        
    except Exception as e:
        await client.send_message(destination_chat_id, f"Error: {e}")
    
    upsta = asyncio.create_task(upstatus(client, f'{msg.id}upstatus.txt', smsg))

    user_data = database.find_one({"user_id": user_id})
    
    # --- Apply Custom Caption ---
    caption = get(CUSTOM_CAPTIONS, user_id, msg.caption)

    # --- Apply Replace Words ---
    replace_words_list = get(REPLACE_WORDS, user_id, [])
    if caption and replace_words_list:
        for word, replacement in replace_words_list:
            caption = caption.replace(word, replacement)

    # --- Get Thumbnail ---
    ph_path = None
    if user_data and user_data.get('thumbnail'):
        ph_path = await acc.download_media(user_data['thumbnail'])

    msg_type = get_message_type(msg)
    
    if "Text" == msg_type:
        try:
            await client.send_message(destination_chat_id, msg.text, entities=msg.entities)
        except Exception as e:
            await client.send_message(destination_chat_id, f"Error: {e}")
            return
    
    elif "Document" == msg_type:
        try:
            await client.send_document(destination_chat_id, file, thumb=ph_path, caption=caption, progress=progress, progress_args=[smsg,"up"])
        except Exception as e:
            await client.send_message(destination_chat_id, f"Error: {e}")

    elif "Video" == msg_type:
        try:
            await client.send_video(destination_chat_id, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, progress=progress, progress_args=[smsg,"up"])
        except Exception as e:
            await client.send_message(destination_chat_id, f"Error: {e}")

    elif "Animation" == msg_type:
        try:
            await client.send_animation(destination_chat_id, file, caption=caption)
        except Exception as e:
            await client.send_message(destination_chat_id, f"Error: {e}")

    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(destination_chat_id, file)
        except Exception as e:
            await client.send_message(destination_chat_id, f"Error: {e}")

    elif "Voice" == msg_type:
        try:
            await client.send_voice(destination_chat_id, file, caption=caption, progress=progress, progress_args=[smsg,"up"])
        except Exception as e:
            await client.send_message(destination_chat_id, f"Error: {e}")

    elif "Audio" == msg_type:
        try:
            await client.send_audio(destination_chat_id, file, thumb=ph_path, caption=caption, progress=progress, progress_args=[smsg,"up"])
        except Exception as e:
            await client.send_message(destination_chat_id, f"Error: {e}")

    elif "Photo" == msg_type:
        try:
            await client.send_photo(destination_chat_id, file, caption=caption)
        except Exception as e:
            await client.send_message(destination_chat_id, f"Error: {e}")

    if ph_path:
        os.remove(ph_path)
    
    if os.path.exists(f'{msg.id}upstatus.txt'): 
        os.remove(f'{msg.id}upstatus.txt')
        os.remove(file)
    await client.delete_messages(destination_chat_id,[smsg.id])

# --- Main Save Logic ---
@Client.on_message(filters.text & filters.private, group=2)
async def save(client: Client, message: Message):
    
    # --- Auto Reaction ---
    try:
        await message.react("👍") # You can customize the emoji
    except Exception as e:
        print(f"Failed to react to message: {e}")

    if "https://t.me/" in message.text:
        try:
            await save_content_from_link(client, message.from_user.id, message.text)
        except ValueError as e:
            await message.reply_text(str(e))
        except Exception as e:
            await message.reply_text(f"Error: {e}")

# --- get the type of message ---
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