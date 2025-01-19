import asyncio
import os
import json
import time
import threading
import re

import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery

from config import API_ID, API_HASH, BOT_TOKEN
from database.db import database
from TechVJ.strings import strings, HELP_TXT

# --- Constants ---
MAX_BATCH_SIZE = 1000
DEFAULT_THUMBNAIL = None  # You can set a default thumbnail URL here
REACTION_EMOJIS = ["👍", "👎", "❤️", "🔥", "🎉", "🤩", "😱", "😁", "😢", "🤔"]

# --- Global Variables ---
CUSTOM_THUMBNAILS = {}  # {user_id: thumbnail_url}
CUSTOM_CAPTIONS = {}  # {user_id: caption}
CUSTOM_WORDS = {}  # {user_id: [word1, word2, ...]}
BATCH_LINKS = {}  # {user_id: [link1, link2, ...]}
BATCH_TASKS = {}  # {user_id: asyncio.Task}

# --- Helper Functions ---
def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in ["administrator", "creator"]
    except:
        return False

async def download_and_store_thumbnail(client: Client, user_id, message: Message):
    global CUSTOM_THUMBNAILS
    
    if message.photo:
        photo = message.photo
    elif message.document and "image" in message.document.mime_type:
        photo = message.document
    else:
      await message.reply_text("Please send a photo or an image file as a document.")
      return False

    try:
        file_path = await client.download_media(photo)
        CUSTOM_THUMBNAILS[user_id] = file_path
        return True
    except Exception as e:
        await message.reply_text(f"Error downloading thumbnail: {e}")
        return False
    
async def remove_stored_thumbnail(user_id):
    global CUSTOM_THUMBNAILS
    if user_id in CUSTOM_THUMBNAILS:
        try:
            os.remove(CUSTOM_THUMBNAILS[user_id])
        except:
            pass
        del CUSTOM_THUMBNAILS[user_id]

async def get_stored_thumbnail(user_id):
    global CUSTOM_THUMBNAILS
    return CUSTOM_THUMBNAILS.get(user_id)

# --- Progress Monitoring ---
async def downstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(message.chat.id, message.id,
                                           f"Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
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
            await client.edit_message_text(message.chat.id, message.id,
                                           f"Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# --- Start Command ---
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url="http://t.me/Sonickuwalupdatebot")
    ], [
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='http://t.me/Sonickuwalupdatebot'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(message.chat.id,
                              f"<b>👋 Hi {message.from_user.mention}, I am a Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>",
                              reply_markup=reply_markup, reply_to_message_id=message.id)
    return

@Client.on_message(filters.command(["settings"]))
async def settings_menu(client: Client, message: Message):
  user_id = message.from_user.id
  buttons = [
      [
          InlineKeyboardButton("Set Custom Thumbnail", callback_data=f"set_thumb_{user_id}"),
          InlineKeyboardButton("Remove Custom Thumbnail", callback_data=f"remove_thumb_{user_id}")
      ],
      [
          InlineKeyboardButton("Add Custom Caption", callback_data=f"add_caption_{user_id}"),
          InlineKeyboardButton("Remove Custom Caption", callback_data=f"remove_caption_{user_id}")
      ],
      [
          InlineKeyboardButton("Add Custom Words", callback_data=f"add_words_{user_id}"),
          InlineKeyboardButton("Remove Custom Words", callback_data=f"remove_words_{user_id}")
      ],
      [
          InlineKeyboardButton("❌ Close", callback_data="close_settings")
      ]
  ]
  await message.reply_text("⚙️ **Settings:**", reply_markup=InlineKeyboardMarkup(buttons))

@Client.on_callback_query(filters.regex(r"^set_thumb_(\d+)"))
async def set_thumbnail_callback(client: Client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    await callback_query.message.edit_text("Please send me the image you want to set as your custom thumbnail.")
    
    # Await the next message from the user (expecting an image)
    try:
      response = await client.listen.Message(filters.user(user_id) & (filters.photo | (filters.document & filters.regex("image"))), timeout=60)

      if await download_and_store_thumbnail(client, user_id, response):
        await callback_query.message.edit_text("✅ Custom thumbnail set successfully!")
      else:
        await callback_query.message.edit_text("❌ Failed to set custom thumbnail.")
    except asyncio.TimeoutError:
      await callback_query.message.edit_text("❌ Time out! Please try again.")
    except Exception as e:
      await callback_query.message.edit_text(f"❌ Error: {e}")
    

@Client.on_callback_query(filters.regex(r"^remove_thumb_(\d+)"))
async def remove_thumbnail_callback(client: Client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    await remove_stored_thumbnail(user_id)
    await callback_query.message.edit_text("✅ Custom thumbnail removed successfully!")
    
@Client.on_callback_query(filters.regex(r"^add_caption_(\d+)"))
async def add_caption_callback(client: Client, callback_query: CallbackQuery):
  user_id = int(callback_query.data.split("_")[-1])
  if callback_query.from_user.id != user_id:
      await callback_query.answer("This is not for you!", show_alert=True)
      return

  await callback_query.message.edit_text("Please send me the custom caption you want to add.")
  
  try:
    response = await client.listen.Message(filters.user(user_id) & filters.text, timeout=60)
    CUSTOM_CAPTIONS[user_id] = response.text
    await callback_query.message.edit_text("✅ Custom caption added successfully!")
  except asyncio.TimeoutError:
    await callback_query.message.edit_text("❌ Time out! Please try again.")
  except Exception as e:
      await callback_query.message.edit_text(f"❌ Error: {e}")

@Client.on_callback_query(filters.regex(r"^remove_caption_(\d+)"))
async def remove_caption_callback(client: Client, callback_query: CallbackQuery):
  user_id = int(callback_query.data.split("_")[-1])
  if callback_query.from_user.id != user_id:
      await callback_query.answer("This is not for you!", show_alert=True)
      return
  
  if user_id in CUSTOM_CAPTIONS:
      del CUSTOM_CAPTIONS[user_id]
      await callback_query.message.edit_text("✅ Custom caption removed successfully!")
  else:
      await callback_query.message.edit_text("❌ No custom caption set for you.")
      
@Client.on_callback_query(filters.regex(r"^add_words_(\d+)"))
async def add_words_callback(client: Client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    await callback_query.message.edit_text("Please send me the custom words you want to add, separated by commas (e.g., word1, word2, word3).")

    try:
        response = await client.listen.Message(filters.user(user_id) & filters.text, timeout=60)
        words = [word.strip() for word in response.text.split(",")]
        CUSTOM_WORDS[user_id] = words
        await callback_query.message.edit_text("✅ Custom words added successfully!")
    except asyncio.TimeoutError:
        await callback_query.message.edit_text("❌ Time out! Please try again.")
    except Exception as e:
        await callback_query.message.edit_text(f"❌ Error: {e}")

@Client.on_callback_query(filters.regex(r"^remove_words_(\d+)"))
async def remove_words_callback(client: Client, callback_query: CallbackQuery):
    user_id = int(callback_query.data.split("_")[-1])
    if callback_query.from_user.id != user_id:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    if user_id in CUSTOM_WORDS:
        del CUSTOM_WORDS[user_id]
        await callback_query.message.edit_text("✅ Custom words removed successfully!")
    else:
        await callback_query.message.edit_text("❌ No custom words set for you.")

@Client.on_callback_query(filters.regex(r"^close_settings$"))
async def close_settings_callback(client: Client, callback_query: CallbackQuery):
    await callback_query.message.delete()

# --- Help Command ---
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

# --- Batch Handling ---
@Client.on_message(filters.command(["batch"]))
async def start_batch(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id in BATCH_LINKS:
        await message.reply_text("You already have an active batch. Please send /cancel_batch to cancel it.")
        return

    BATCH_LINKS[user_id] = []
    await message.reply_text("Please send me the links you want to include in the batch, one by one. Send /done_batch when you're finished.")

@Client.on_message(filters.command(["done_batch"]))
async def end_batch(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in BATCH_LINKS:
        await message.reply_text("You don't have an active batch. Start one with /batch.")
        return
    
    links = BATCH_LINKS[user_id]
    if not links:
      await message.reply_text("Your batch list is empty.")
      del BATCH_LINKS[user_id]
      return
    
    if len(links) > MAX_BATCH_SIZE:
        await message.reply_text(f"Too many links! The maximum batch size is {MAX_BATCH_SIZE}.")
        del BATCH_LINKS[user_id]
        return

    await message.reply_text(f"Starting batch processing for {len(links)} links...")
    
    async def process_batch():
        for link in links:
            await save(client, message, link, user_initiated=False)
            await asyncio.sleep(5)  # Adjust sleep time as needed to manage speed

        del BATCH_LINKS[user_id]
        if user_id in BATCH_TASKS:
            del BATCH_TASKS[user_id]
        await message.reply_text("Batch processing completed!")

    batch_task = asyncio.create_task(process_batch())
    BATCH_TASKS[user_id] = batch_task

@Client.on_message(filters.command(["cancel_batch"]))
async def cancel_batch(client: Client, message: Message):
    user_id = message.from_user.id
    if user_id not in BATCH_LINKS:
        await message.reply_text("You don't have an active batch to cancel.")
        return

    if user_id in BATCH_TASKS:
        BATCH_TASKS[user_id].cancel()
        del BATCH_TASKS[user_id]

    del BATCH_LINKS[user_id]
    await message.reply_text("Batch processing cancelled.")
    

# --- Main Save Function ---
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message, link_from_batch=None, user_initiated=True):
    user_id = message.from_user.id
    text = link_from_batch if link_from_batch else message.text

    # Add link to batch list if active
    if user_initiated and user_id in BATCH_LINKS and "https://t.me/" in text:
      BATCH_LINKS[user_id].append(text)
      await message.reply_text(f"Link added to batch. Current batch size: {len(BATCH_LINKS[user_id])}. Send /done_batch when finished.")
      return

    if "https://t.me/" in text:
        datas = text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
            
        if fromID == toID:
          await handle_message(client, message, fromID, text, datas)
          
        elif (toID - fromID) > MAX_BATCH_SIZE and not await is_admin(client, message.chat.id, user_id):
          await message.reply_text(f"⚠️ Warning: You are not an admin and are trying to process a batch larger than the allowed limit of {MAX_BATCH_SIZE} messages. This operation is restricted to bot admins only for performance reasons. \n\n**If you are an admin of this bot, please ensure you are sending this command from a chat where the bot is also an admin, and that your user ID has been properly configured as an admin.**\n\nFor regular users, please limit your batch requests to {MAX_BATCH_SIZE} messages or use the `/batch` command for controlled batch processing.")
          return
        
        else:
            for msgid in range(fromID, toID + 1):
                await handle_message(client, message, msgid, text, datas)
                await asyncio.sleep(5)  # Adjust sleep time as needed

async def handle_message(client: Client, message: Message, msgid: int, text: str, datas: list):
        user_id = message.from_user.id
        # private
        if "https://t.me/c/" in text:
            user_data = database.find_one({'chat_id': user_id})
            if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                await client.send_message(user_id, strings['need_login'])
                return
            acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
            await acc.connect()
            chatid = int("-100" + datas[4])
            await handle_private(client, acc, message, chatid, msgid)

        # bot
        elif "https://t.me/b/" in text:
            user_data = database.find_one({"chat_id": user_id})
            if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                await client.send_message(user_id, strings['need_login'])
                return
            acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
            await acc.connect()
            username = datas[4]
            try:
                await handle_private(client, acc, message, username, msgid)
            except Exception as e:
                await client.send_message(user_id, f"Error: {e}", reply_to_message_id=message.id)

        # public
        else:
            username = datas[3]

            try:
                msg = await client.get_messages(username, msgid)
            except UsernameNotOccupied:
                await client.send_message(user_id, "The username is not occupied by anyone",
                                          reply_to_message_id=message.id)
                return
            try:
                await client.copy_message(user_id, msg.chat.id, msg.id, reply_to_message_id=message.id)
            except:
                try:
                    user_data = database.find_one({"chat_id": user_id})
                    if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                        await client.send_message(user_id, strings['need_login'])
                        return
                    acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH,
                                 api_id=API_ID)
                    await acc.connect()
                    await handle_private(client, acc, message, username, msgid)

                except Exception as e:
                    await client.send_message(user_id, f"Error: {e}", reply_to_message_id=message.id)

# --- Auto-Reaction ---
@Client.on_message(filters.group | filters.channel)
async def auto_react(client: Client, message: Message):
    if message.chat and (message.chat.type in ["group", "supergroup", "channel"]):
      await message.react(random.choice(REACTION_EMOJIS))

# --- Auto-Forward/Upload ---
@Client.on_message(filters.group | filters.channel)
async def auto_forward_upload(client: Client, message: Message):
    user_id = message.from_user.id

    # Check for custom channel ID
    user_data = database.find_one({"chat_id": user_id})
    custom_channel_id = get(user_data, "custom_channel_id")

    if custom_channel_id:
        target_chat_id = custom_channel_id
    else:
        target_chat_id = user_id  # Default to user's private chat if no custom channel

    if message.media:
        caption = CUSTOM_CAPTIONS.get(user_id, message.caption)
        thumbnail = await get_stored_thumbnail(user_id)
        
        if CUSTOM_WORDS.get(user_id) and caption:
            for word in CUSTOM_WORDS[user_id]:
              caption = caption.replace(word, "")
              
        smsg = await client.send_message(target_chat_id, 'Auto-Downloading...')
        dosta = asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))

        try:
            file = await client.download_media(message, progress=progress, progress_args=[message, "down"])
            os.remove(f'{message.id}downstatus.txt')
        except Exception as e:
            await client.edit_message_text(target_chat_id, smsg.id, f"Download Error: {e}")
            return

        upsta = asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

        try:
            if message.photo:
                await client.send_photo(target_chat_id, file, caption=caption)
            elif message.video:
                await client.send_video(target_chat_id, file, caption=caption, thumb=thumbnail,
                                        duration=message.video.duration, width=message.video.width,
                                        height=message.video.height,
                                        progress=progress, progress_args=[message, "up"])
            elif message.document:
              if not thumbnail and "image" in message.document.mime_type:
                thumbnail = await client.download_media(message.document)

              await client.send_document(target_chat_id, file, caption=caption, thumb=thumbnail,
                                        progress=progress, progress_args=[message, "up"])
            elif message.audio:
                await client.send_audio(target_chat_id, file, caption=caption, thumb=thumbnail,
                                        progress=progress, progress_args=[message, "up"])
            elif message.animation:
                await client.send_animation(target_chat_id, file, caption=caption)
            elif message.voice:
                await client.send_voice(target_chat_id, file, caption=caption,
                                        progress=progress, progress_args=[message, "up"])
            elif message.sticker:
                await client.send_sticker(target_chat_id, file)

            await client.delete_messages(target_chat_id, [smsg.id])
            if os.path.exists(f'{message.id}upstatus.txt'):
                os.remove(f'{message.id}upstatus.txt')
                os.remove(file)

        except Exception as e:
            await client.edit_message_text(target_chat_id, smsg.id, f"Upload Error: {e}")

    elif message.text:
        text = message.text
        if CUSTOM_WORDS.get(user_id):
            for word in CUSTOM_WORDS[user_id]:
                text = text.replace(word, "")
        await client.send_message(target_chat_id, text)
        
    
# --- Handle Private Messages ---
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    user_id = message.from_user.id
    msg = await acc.get_messages(chatid, msgid)
    msg_type = get_message_type(msg)
    
    caption = CUSTOM_CAPTIONS.get(user_id, msg.caption)
    thumbnail = await get_stored_thumbnail(user_id)
    
    if CUSTOM_WORDS.get(user_id) and caption:
        for word in CUSTOM_WORDS[user_id]:
            caption = caption.replace(word, "")
    
    chat = user_id

    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id)
        except MessageEmpty:
          await client.send_message(user_id, "❌ The message is empty or contains invalid characters.", reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(user_id, f"Error: {e}", reply_to_message_id=message.id)
            return

    smsg = await client.send_message(user_id, 'Downloading', reply_to_message_id=message.id)
    dosta = asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))

    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')

    except Exception as e:
        await client.edit_message_text(user_id, smsg.id, f"Error: {e}")
        return

    upsta = asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

    try:
        if "Document" == msg_type:
            if not thumbnail and msg.document.thumbs:
              try:
                  thumbnail = await acc.download_media(msg.document.thumbs[0].file_id)
              except:
                  pass
            elif not thumbnail and "image" in msg.document.mime_type:
              thumbnail = await acc.download_media(msg.document)

            await client.send_document(chat, file, thumb=thumbnail, caption=caption, reply_to_message_id=message.id,
                                       progress=progress, progress_args=[message, "up"])

        elif "Video" == msg_type:
            if not thumbnail and msg.video.thumbs:
              try:
                thumbnail = await acc.download_media(msg.video.thumbs[0].file_id)
              except:
                pass
            
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width,
                                    height=msg.video.height, thumb=thumbnail, caption=caption,
                                    reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        elif "Animation" == msg_type:
            await client.send_animation(chat, file, reply_to_message_id=message.id, caption=caption)

        elif "Sticker" == msg_type:
            await client.send_sticker(chat, file, reply_to_message_id=message.id)

        elif "Voice" == msg_type:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities,
                                    reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])

        elif "Audio" == msg_type:
            if not thumbnail and msg.audio.thumbs:
              try:
                thumbnail = await acc.download_media(msg.audio.thumbs[0].file_id)
              except:
                pass
            
            await client.send_audio(chat, file, thumb=thumbnail, caption=caption, reply_to_message_id=message.id,
                                    progress=progress, progress_args=[message, "up"])

        elif "Photo" == msg_type:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id)

        await client.delete_messages(user_id, [smsg.id])
        if os.path.exists(f'{message.id}upstatus.txt'):
            os.remove(f'{message.id}upstatus.txt')
            os.remove(file)
            if thumbnail and type(thumbnail) is str:
              os.remove(thumbnail)

    except MessageEmpty:
      await client.edit_message_text(user_id, smsg.id, "❌ The message is empty or contains invalid characters.")
    except Exception as e:
      await client.edit_message_text(user_id, smsg.id, f"Error: {e}")

# --- Message Type ---
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
      
# --- Bot Initialization and Error Handling ---
import random

# (The rest of your existing code, including login, etc. goes here)
# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

print('\nBot Started! Now You can use this...\n')
print('Dont Forget to Follow on https://youtube.com/@Tech_VJ\n')
print('If you facing any problem Contact Owner @KingVJ01')
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

app.run()
