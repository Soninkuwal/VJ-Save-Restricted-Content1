
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import time
import os
import threading
import json
import logging
from config import API_ID, API_HASH, ADMINS
from database.db import database  # Assuming you have a db module
from TechVJ.strings import strings, HELP_TXT # Assume this is defined
import datetime # Add datetime to make logging more specific

# Set up logging
logging.basicConfig(filename='bot.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === GLOBAL SETTINGS ===
BOT_ADMINS = set() # To be filled through a command/file
CUSTOM_THUMBNAILS = {}  # User ID : path to thumbnail
CUSTOM_WORD_REPLACEMENTS = {} # User ID : { "word1" : "replace1", "word2": "replace2" }
CUSTOM_CAPTIONS = {} # User ID :  custom caption string
CUSTOM_CHANNEL = {} # User ID : Channel id for forwarding
AUTO_REACT_EMOJIS = {} # User ID : emoji
BATCH_PROCESSING_LOCKS = {} # User ID : Lock() for thread safety
USER_BATCH_CANCEL = {} # User ID : True if User want to cancel download
ENABLE_FORWARD = {} # User ID : Bool
ENABLE_ERRORS = {} # User ID : Bool
# === END GLOBAL SETTINGS ===

def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default

# ===================== HELPER FUNCTIONS ======================

async def downstatus(client: Client, statusfile, message):
     while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
        
     while os.path.exists(statusfile):
         try:
           with open(statusfile, "r") as downread:
             txt = downread.read()
         except Exception as e:
             logging.error(f"Error opening file in downstatus: {e}")
             return
         
         try:
           await client.edit_message_text(message.chat.id, message.id, f"Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
           await asyncio.sleep(10)
         except Exception as e:
             logging.error(f"Error while editing text in downstatus: {e}")
             await asyncio.sleep(5)

async def upstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
        
    while os.path.exists(statusfile):
        try:
           with open(statusfile, "r") as upread:
              txt = upread.read()
        except Exception as e:
            logging.error(f"Error opening file in upstatus: {e}")
            return
        
        try:
            await client.edit_message_text(message.chat.id, message.id, f"Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10)
        except Exception as e:
           logging.error(f"Error while editing text in upstatus: {e}")
           await asyncio.sleep(5)

def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


def log_error(error_message):
    """Logs an error message to the log file."""
    with open("bot_error.log", "a") as f:
        f.write(f"{datetime.datetime.now()}: {error_message}\n")

async def get_message_type(message: pyrogram.types.messages_and_media.message.Message):
    if message.document: return "Document"
    if message.video: return "Video"
    if message.animation: return "Animation"
    if message.sticker: return "Sticker"
    if message.voice: return "Voice"
    if message.audio: return "Audio"
    if message.photo: return "Photo"
    if message.text: return "Text"
    return None


def apply_replacements(text, user_id):
    replacements = CUSTOM_WORD_REPLACEMENTS.get(user_id, {})
    if not replacements or not text: return text
    for word, replacement in replacements.items():
        text = text.replace(word, replacement)
    return text


def apply_custom_caption(caption, user_id):
    custom_caption = CUSTOM_CAPTIONS.get(user_id)
    if not custom_caption: return caption
    return custom_caption + (f"\n{caption}" if caption else "")

# ==================== END HELPER FUNCTIONS =====================

# =================== BOT COMMANDS ============================

@Client.on_message(filters.command(["start"]))
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


@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")


@Client.on_message(filters.command(["settings"]))
async def settings_menu(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("Set Thumbnail", callback_data="set_thumb"),
        InlineKeyboardButton("Remove Thumbnail", callback_data="remove_thumb")
    ],[
        InlineKeyboardButton("Replace Words", callback_data="replace_words"),
        InlineKeyboardButton("Delete Words", callback_data="delete_words")
    ],[
        InlineKeyboardButton("Set Custom Caption", callback_data="set_caption"),
        InlineKeyboardButton("Enable Forward", callback_data="enable_forward"),
        InlineKeyboardButton("Enable Errors", callback_data="enable_errors")

    ],[
        InlineKeyboardButton("Set Custom Channel", callback_data="set_channel")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(message.chat.id, "Bot Settings Menu:", reply_markup=reply_markup, reply_to_message_id=message.id)

@Client.on_message(filters.command(["add_admin"]))
async def add_admin(client: Client, message: Message):
    if message.from_user.id not in BOT_ADMINS:
        return await message.reply_text("Only bot admin can use this command.")

    try:
       user_id = message.text.split(' ', 1)[1]
       user_id = int(user_id)
       BOT_ADMINS.add(user_id)
       await message.reply_text(f"Added {user_id} to bot admins.")
    except Exception as e:
        await message.reply_text(f"Failed to add admin, please send in the correct format `/add_admin user_id`")
        log_error(f"Failed to add user {message.from_user.id} as bot admin, due to error {e}")

@Client.on_message(filters.command(["cancel"]))
async def cancel_batch(client: Client, message: Message):
    USER_BATCH_CANCEL[message.from_user.id] = True
    await message.reply_text("Batch cancelled.")
    logging.info(f"User {message.from_user.id} cancelled batch process.")

# ===================== BOT CALLBACK QUERIES ======================

@Client.on_callback_query(filters.regex("set_thumb"))
async def set_thumb_query(client:Client, callback_query: pyrogram.types.CallbackQuery):
     await callback_query.message.reply_text("Send your custom thumbnail as a photo.")

@Client.on_callback_query(filters.regex("remove_thumb"))
async def remove_thumb_query(client:Client, callback_query: pyrogram.types.CallbackQuery):
    user_id = callback_query.from_user.id
    CUSTOM_THUMBNAILS.pop(user_id, None)
    await callback_query.message.reply_text("Custom thumbnail removed.")
    logging.info(f"User {user_id} removed custom thumbnail.")

@Client.on_callback_query(filters.regex("replace_words"))
async def replace_words_query(client:Client, callback_query: pyrogram.types.CallbackQuery):
     await callback_query.message.reply_text("Send the word replacements in JSON format (e.g., `{\"old_word\": \"new_word\", \"other_word\":\"new_word2\"}`)")

@Client.on_callback_query(filters.regex("delete_words"))
async def delete_words_query(client:Client, callback_query: pyrogram.types.CallbackQuery):
     await callback_query.message.reply_text("Send the words you want to delete from replacements in JSON array format (e.g., `[\"word1\", \"word2\"]`)")

@Client.on_callback_query(filters.regex("set_caption"))
async def set_caption_query(client:Client, callback_query: pyrogram.types.CallbackQuery):
     await callback_query.message.reply_text("Send your custom caption.")

@Client.on_callback_query(filters.regex("set_channel"))
async def set_channel_query(client:Client, callback_query: pyrogram.types.CallbackQuery):
     await callback_query.message.reply_text("Send your custom channel ID where you want to forward the messages to.")

@Client.on_callback_query(filters.regex("enable_forward"))
async def enable_forward_query(client:Client, callback_query: pyrogram.types.CallbackQuery):
    user_id = callback_query.from_user.id
    ENABLE_FORWARD[user_id] = not ENABLE_FORWARD.get(user_id, False)
    status = "enabled" if ENABLE_FORWARD[user_id] else "disabled"
    await callback_query.message.reply_text(f"Forwarding {status}.")
    logging.info(f"User {user_id} set forwarding to {status}")

@Client.on_callback_query(filters.regex("enable_errors"))
async def enable_errors_query(client:Client, callback_query: pyrogram.types.CallbackQuery):
    user_id = callback_query.from_user.id
    ENABLE_ERRORS[user_id] = not ENABLE_ERRORS.get(user_id, False)
    status = "enabled" if ENABLE_ERRORS[user_id] else "disabled"
    await callback_query.message.reply_text(f"Errors {status}.")
    logging.info(f"User {user_id} set errors to {status}")


# =================== MESSAGES HANDLER ===========================

@Client.on_message(filters.photo & filters.private)
async def handle_custom_thumb(client: Client, message: Message):
    if not message.photo: return
    if message.reply_to_message and message.reply_to_message.text == "Send your custom thumbnail as a photo.":
        CUSTOM_THUMBNAILS[message.from_user.id] = await client.download_media(message)
        await message.reply_text("Custom thumbnail set.")
        logging.info(f"User {message.from_user.id} set custom thumbnail.")

@Client.on_message(filters.text & filters.private)
async def handle_text_messages(client: Client, message: Message):
     if message.reply_to_message:
         if message.reply_to_message.text == "Send the word replacements in JSON format (e.g., `{\"old_word\": \"new_word\", \"other_word\":\"new_word2\"}`)" :
            try:
               word_replacements = json.loads(message.text)
               CUSTOM_WORD_REPLACEMENTS[message.from_user.id] = word_replacements
               await message.reply_text("Custom word replacements set.")
               logging.info(f"User {message.from_user.id} set custom word replacements: {word_replacements}")
            except Exception as e:
                await message.reply_text(f"Error parsing your JSON data, please send it in the right format. Error: {e}")
                log_error(f"User {message.from_user.id} failed to set custom word replacements: {e}")

         elif message.reply_to_message.text == "Send the words you want to delete from replacements in JSON array format (e.g., `[\"word1\", \"word2\"]`)" :
             try:
                words_to_delete = json.loads(message.text)
                if not isinstance(words_to_delete, list):
                    await message.reply_text("Please send a JSON array of strings")
                    return
                replacements = CUSTOM_WORD_REPLACEMENTS.get(message.from_user.id,{})
                for word in words_to_delete:
                   replacements.pop(word, None)
                CUSTOM_WORD_REPLACEMENTS[message.from_user.id] = replacements
                await message.reply_text("Custom word replacements deleted")
                logging.info(f"User {message.from_user.id} deleted custom word replacements: {words_to_delete}")

             except Exception as e:
                await message.reply_text(f"Error parsing your JSON data, please send it in the right format. Error: {e}")
                log_error(f"User {message.from_user.id} failed to delete custom word replacements: {e}")

         elif message.reply_to_message.text == "Send your custom caption.":
                CUSTOM_CAPTIONS[message.from_user.id] = message.text
                await message.reply_text("Custom caption set.")
                logging.info(f"User {message.from_user.id} set custom caption: {message.text}")

         elif message.reply_to_message.text == "Send your custom channel ID where you want to forward the messages to.":
            try:
              channel_id = int(message.text)
              CUSTOM_CHANNEL[message.from_user.id] = channel_id
              await message.reply_text("Custom channel ID set.")
              logging.info(f"User {message.from_user.id} set custom channel ID: {channel_id}")
            except Exception as e:
                await message.reply_text(f"Error, please send a valid channel ID. Error : {e}")
                log_error(f"User {message.from_user.id} failed to set custom channel ID: {e}")
     else:
        await handle_message(client, message)

@Client.on_message(filters.command(["login"]))
async def login_session(client: Client, message: Message):
        await message.reply("Login method is not implemented yet")

# ================== FORWARD HANDLER ======================

async def handle_message(client: Client, message: Message):
    user_id = message.from_user.id
    if AUTO_REACT_EMOJIS.get(user_id):
        try:
            await client.send_reaction(message.chat.id, message.id, AUTO_REACT_EMOJIS[user_id])
        except Exception as e:
            logging.warning(f"Error reacting to message : {e}")
    
    if "https://t.me/" not in message.text: return
    
    if message.from_user.id not in BOT_ADMINS:
      if message.text.count("https://t.me/") > 1000:
           return await message.reply("You cannot batch more than 1000 links.")

    datas = message.text.split("/")
    
    if  "https://t.me/c/" in message.text:
          if len(datas) < 5: return await message.reply("Please send a valid message link.")
          chatid = int("-100" + datas[4]) # this should always be a number
    elif "https://t.me/b/" in message.text:
      if len(datas) < 5: return await message.reply("Please send a valid message link.")
      chatid = datas[4] # this should always be a string
    elif len(datas) < 4:
        return await message.reply("Please send a valid message link.")
    else:
      chatid = datas[3] # this should always be a string

    try:
      temp = datas[-1].replace("?single","").split("-")
      fromID = int(temp[0].strip())
      try:
        toID = int(temp[1].strip())
      except:
         toID = fromID
    except Exception as e:
        log_error(f"Failed to parse link : {e}")
        return await message.reply(f"Failed to parse link : {e}")
    
    if not BATCH_PROCESSING_LOCKS.get(user_id):
        BATCH_PROCESSING_LOCKS[user_id] = threading.Lock()
    if BATCH_PROCESSING_LOCKS[user_id].locked():
        return await message.reply("One batch process is already running for you, please wait or use /cancel")
    
    with BATCH_PROCESSING_LOCKS[user_id]:
      USER_BATCH_CANCEL[user_id] = False # Reset if they try to send a new batch request
      for msgid in range(fromID, toID + 1):
            if USER_BATCH_CANCEL.get(user_id): break
            try:
                await process_message(client, message, chatid, msgid)
            except Exception as e:
               log_error(f"Failed to process message {msgid} in {chatid} due to error {e}")
               if ENABLE_ERRORS.get(user_id, False):
                 await message.reply(f"Failed to process message {msgid} in {chatid} due to error {e}")
            await asyncio.sleep(3)

async def process_message(client: Client, message: Message, chatid, msgid):
    user_id = message.from_user.id
    file = f"{message.id}.file"
    smsg = None

    try:
      if isinstance(chatid, int):
         msg = await client.get_messages(chatid, msgid)
      else:
         msg = await client.get_messages(chatid, msgid)
    except UsernameNotOccupied as e:
        await message.reply(f"Error, The username is not occupied by anyone. Error: {e}")
        return
    except Exception as e:
      log_error(f"Failed to get message {msgid} from {chatid} due to error : {e}")
      return

    if not msg:
        return

    msg_type = await get_message_type(msg)
    if not msg_type:
        if ENABLE_ERRORS.get(user_id, False):
            await message.reply("Unsupported message type.")
        return
    
    if msg_type == "Text":
      try:
          if ENABLE_FORWARD.get(user_id, False) and CUSTOM_CHANNEL.get(user_id):
              custom_caption = apply_custom_caption(msg.text, user_id)
              await client.send_message(CUSTOM_CHANNEL[user_id], custom_caption, entities = msg.entities, parse_mode=enums.ParseMode.HTML)
          else:
              custom_caption = apply_custom_caption(msg.text, user_id)
              await client.send_message(message.chat.id, custom_caption, entities = msg.entities, parse_mode=enums.ParseMode.HTML)

      except Exception as e:
        log_error(f"Failed to send text message {msgid} from {chatid} due to error : {e}")
        if ENABLE_ERRORS.get(user_id, False):
            await message.reply(f"Failed to send text message. {e}")
      return

    try:
      if ENABLE_FORWARD.get(user_id, False) and CUSTOM_CHANNEL.get(user_id):
          send_chat = CUSTOM_CHANNEL[user_id]
      else:
        send_chat = message.chat.id
      try:
            with open(f"{message.id}downstatus.txt",'w') as f:
              f.write('Downloading...')
            smsg = await client.send_message(message.chat.id, 'Downloading...')
      except Exception as e:
           log_error(f"Failed to send download status message {msgid} from {chatid} due to error : {e}")
           if ENABLE_ERRORS.get(user_id, False):
              await message.reply(f"Failed to send download status message. {e}")
           return

      if msg_type == 'Document':
         dl_file = msg.document
      elif msg_type == 'Video':
         dl_file = msg.video
      elif msg_type == 'Animation':
         dl_file = msg.animation
      elif msg_type == 'Sticker':
         dl_file = msg.sticker
      elif msg_type == 'Voice':
         dl_file = msg.voice
      elif msg_type == 'Audio':
        dl_file = msg.audio
      elif msg_type == 'Photo':
        dl_file = msg.photo
      elif msg_type == 'Text':
        dl_file = msg.text

      file = await client.download_media(dl_file, file_name = file, progress=progress, progress_args=[message,"down"])
      try:
         with open(f"{message.id}upstatus.txt", 'w') as f:
            f.write('Downloaded, Uploading...')
         await smsg.edit_text('Downloaded, Uploading...')
      except Exception as e:
          log_error(f"Failed to set upload status message {msgid} from {chatid} due to error : {e}")
          if ENABLE_ERRORS.get(user_id, False):
               await message.reply(f"Failed to set upload status message. {e}")
          if os.path.exists(file):
             os.remove(file)
          return await smsg.delete()
    except Exception as e:
        log_error(f"Failed to download media {msgid} from {chatid} due to error : {e}")
        if ENABLE_ERRORS.get(user_id, False):
             await message.reply(f"Failed to download media. {e}")
        if os.path.exists(f"{message.id}downstatus.txt"):
           os.remove(f"{message.id}downstatus.txt")
        return await smsg.delete()
      
    caption = apply_replacements(msg.caption, user_id)
    caption = apply_custom_caption(caption, user_id)
    thumbnail_path = CUSTOM_THUMBNAILS.get(user_id)

    try:
        if msg_type == "Document":
            thumb = await client.download_media(msg.document.thumbs[0].file_id) if msg.document.thumbs else thumbnail_path
            await client.send_document(send_chat, file, thumb=thumb, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        elif msg_type == "Video":
             thumb = await client.download_media(msg.video.thumbs[0].file_id) if msg.video.thumbs else thumbnail_path
             await client.send_video(send_chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        elif msg_type == "Animation":
            await client.send_animation(send_chat, file, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        elif msg_type == "Text":
            await client.send_text(send_chat, file, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        
        elif msg_type == "Sticker":
            await client.send_sticker(send_chat, file)
        elif msg_type == "Voice":
            await client.send_voice(send_chat, file, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        elif msg_type == "Audio":
            thumb = await client.download_media(msg.audio.thumbs[0].file_id) if msg.audio.thumbs else thumbnail_path
            await client.send_audio(send_chat, file, thumb=thumb, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        elif msg_type == "Photo":
            await client.send_photo(send_chat, file, caption=caption, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
    except Exception as e:
          log_error(f"Failed to send message {msgid} from {chatid} due to error : {e}")
          if ENABLE_ERRORS.get(user_id, False):
                await message.reply(f"Failed to send the message {msgid} from {chatid} due to error: {e}")
    finally:
        if os.path.exists(file):
            os.remove(file)
        if os.path.exists(f"{message.id}downstatus.txt"):
             os.remove(f"{message.id}downstatus.txt")
        if os.path.exists(f"{message.id}upstatus.txt"):
            os.remove(f"{message.id}upstatus.txt")
        if thumbnail_path and os.path.exists(thumbnail_path):
           os.remove(thumbnail_path)
        await client.delete_messages(message.chat.id,[smsg.id]) if smsg else None

