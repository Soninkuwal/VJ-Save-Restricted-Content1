import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, FilePartMissing, MediaInvalid, PeerIdInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE, FORWARD_CHANNEL_ID
from database.db import db
from TechVJ.strings import HELP_TXT
import logging
import concurrent.futures
from enum import Enum

logging.basicConfig(level=logging.ERROR)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

# Message Type Constants
class MessageType(Enum):
    DOCUMENT = "Document"
    VIDEO = "Video"
    ANIMATION = "Animation"
    STICKER = "Sticker"
    VOICE = "Voice"
    AUDIO = "Audio"
    PHOTO = "Photo"
    TEXT = "Text"
    
async def download_media(client, message):
    loop = asyncio.get_event_loop()
    file = await loop.run_in_executor(executor, client.download_media, message,block=False)
    return file

async def fast_download_media(client, message):
    loop = asyncio.get_event_loop()
    file = await loop.run_in_executor(executor, client.download_media, message)
    return file


class batch_temp(object):
    IS_BATCH = {}


async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# progress writer
async def progress(current, total, message, type):
    percent = (current / total) * 100
    if percent % 10 == 0:  # हर 10% पर अपडेट करें
        with open(f'{message.id}{type}status.txt', "w") as fileup:
            fileup.write(f"{percent:.1f}%")


# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url="https://t.me/SONICKUWALSSCBOT")
    ], [
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/SONICKUWALSSCBOT'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id,
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n for bot any error content :- @SONICKUWALSSCBOT </b>",
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}"
    )


# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id,
        text="**Batch Successfully Cancelled.**"
    )

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" not in message.text:
        return
    if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
    
    datas = message.text.split("/")
    temp = datas[-1].replace("?single", "").split("-")
    try:
        fromID = int(temp[0].strip())
    except ValueError:
        return await message.reply_text("**Invalid link format provided.**")
    try:
        toID = int(temp[1].strip())
    except (IndexError, ValueError):
        toID = fromID
    
    batch_temp.IS_BATCH[message.from_user.id] = False
    for msgid in range(fromID, toID + 1):
        if batch_temp.IS_BATCH.get(message.from_user.id):
            break
        user_data = await db.get_session(message.from_user.id)
        if user_data is None:
            await message.reply("**For Downloading Restricted Content You Have To /login First.**")
            batch_temp.IS_BATCH[message.from_user.id] = True
            return
        try:
             acc = Client("saverestricted", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
             await acc.connect()
        except Exception as e:
            logging.error(f"Error while connecting to client: {e}")
            batch_temp.IS_BATCH[message.from_user.id] = True
            return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")


            # private
        if "https://t.me/c/" in message.text:
            chatid = int("-100" + datas[4])
            try:
               await handle_private(client, acc, message, chatid, msgid)
            except Exception as e:
                 logging.error(f"Error processing private channel message: {e}")
                 if ERROR_MESSAGE == True:
                   await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # bot
        elif "https://t.me/b/" in message.text:
             username = datas[4]
             try:
               await handle_private(client, acc, message, username, msgid)
             except Exception as e:
                 logging.error(f"Error processing bot message: {e}")
                 if ERROR_MESSAGE == True:
                   await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)


        # public
        else:
            username = datas[3]
            try:
                msg = await client.get_messages(username, msgid)
            except UsernameNotOccupied:
                await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                return
            try:
                await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
            except Exception as e:
                    logging.error(f"Error while coping public message: {e}")
                    try:
                      await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                         logging.error(f"Error while processing  message: {e}")
                         if ERROR_MESSAGE == True:
                             await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
        await asyncio.sleep(3)
    batch_temp.IS_BATCH[message.from_user.id] = True

async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    try:
        msg: Message = await acc.get_messages(chatid, msgid)
        if msg.empty:
            return
        msg_type = get_message_type(msg)
        if not msg_type:
           return
    except (PeerIdInvalid, FloodWait) as e:
        await asyncio.sleep(e.value)
    except Exception as e:
         logging.error(f"Error while Get Message: {e}")
         if ERROR_MESSAGE:
           await client.send_message(message.chat.id, f"Error: while Get Message: {e}", reply_to_message_id=message.id)
         return

    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id):
        return
    if MessageType.TEXT == msg_type:
        if msg.text: # Check if text content exists
           try:
                sent_msg = await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
           except Exception as e:
              logging.error(f"Error while Sending text message: {e}")
              if ERROR_MESSAGE:
                  await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                  ph_path = None
            # Forward to the custom channel
           try:
             await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)   
           except Exception as e:
               logging.error(f"Error while Forwarding Message: {e}")
               if ERROR_MESSAGE == True:
                  await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
               return
        else:
             return

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    file = None
    try:
         file = await download_media(acc, msg)
         os.remove(f'{message.id}downstatus.txt')
    except (FloodWait) as e:
         await asyncio.sleep(e.value)
    except Exception as e:
        logging.error(f"Error during Download: {e}")
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        return await smsg.delete()
    if not file:
        return await smsg.delete()
    if os.path.getsize(file) == 0:
        os.remove(file)
        return await client.edit_message_text(chat, smsg.id, "❌ **Skipping, File size is 0 KB.**")
    if batch_temp.IS_BATCH.get(message.from_user.id):
        os.remove(file)
        return
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id):
        os.remove(file)
        return

    ph_path = None
    if (msg_type in [MessageType.DOCUMENT, MessageType.VIDEO, MessageType.AUDIO]):
        thumb = None
        if msg_type == MessageType.DOCUMENT and msg.document.thumbs:
           thumb = msg.document.thumbs[0]
        elif msg_type == MessageType.VIDEO and msg.video.thumbs:
            thumb = msg.video.thumbs[0]
        elif msg_type == MessageType.AUDIO and msg.audio.thumbs:
            thumb = msg.audio.thumbs[0]

        if thumb:
            try:
                ph_path = await acc.download_media(thumb.file_id)
            except Exception as e:
              logging.error(f"Error: Thumbnail Download Error: {e}")
              if ERROR_MESSAGE:
                 await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                 ph_path = None
    try:
       sent_msg = await send_media(client, chat, file, msg, msg_type, ph_path, caption, message.id)
       # Forward to the custom channel
       try:
          await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)
       except Exception as e:
           logging.error(f"Error: while Forwarding: {e}")
           if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: while Forwarding {msg_type}: {e}", reply_to_message_id=message.id)
    except Exception as e:
            logging.error(f"Error: Send Media Error: {e}")
            if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: Send Media Error {msg_type}: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    if ph_path and os.path.exists(ph_path):
           os.remove(ph_path)
    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')


    os.remove(file)
    await client.delete_messages(message.chat.id, [smsg.id])

async def send_media(client, chat, file, msg, msg_type, ph_path, caption, reply_to_message_id):
    try:
        if msg_type == MessageType.DOCUMENT:
          return await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=reply_to_message_id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        elif msg_type == MessageType.VIDEO:
           return  await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=reply_to_message_id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        elif msg_type == MessageType.ANIMATION:
           return await client.send_animation(chat, file, reply_to_message_id=reply_to_message_id, parse_mode=enums.ParseMode.HTML)
        elif msg_type == MessageType.STICKER:
            return await client.send_sticker(chat, file, reply_to_message_id=reply_to_message_id, parse_mode=enums.ParseMode.HTML)
        elif msg_type == MessageType.VOICE:
            return await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=reply_to_message_id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        elif msg_type == MessageType.AUDIO:
           return await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=reply_to_message_id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        elif msg_type == MessageType.PHOTO:
            return await client.send_photo(chat, file, caption=caption, reply_to_message_id=reply_to_message_id, parse_mode=enums.ParseMode.HTML)

    except Exception as e:
            logging.error(f"Error sending media type {msg_type}: {e}")
            raise e

# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    if msg.document:
        return MessageType.DOCUMENT
    if msg.video:
        return MessageType.VIDEO
    if msg.animation:
        return MessageType.ANIMATION
    if msg.sticker:
       return MessageType.STICKER
    if msg.voice:
        return MessageType.VOICE
    if msg.audio:
       return MessageType.AUDIO
    if msg.photo:
       return MessageType.PHOTO
    if msg.text:
        return MessageType.TEXT
    return None