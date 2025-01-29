import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, InputMediaPhoto, InputMediaVideo, InputMediaDocument
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
from TechVJ.strings import HELP_TXT
import re
class batch_temp(object):
    IS_BATCH = {}

async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r") as downread:
                txt = downread.read()
            await client.edit_message_text(chat, message.id, f"**Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**")
        except Exception:
            await asyncio.sleep(5)
        await asyncio.sleep(10)

# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)
    while os.path.exists(statusfile):
        try:
            with open(statusfile, "r") as upread:
                txt = upread.read()
            await client.edit_message_text(chat, message.id, f"**Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**")
        except Exception:
            await asyncio.sleep(5)
        await asyncio.sleep(10)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

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

# status command
@Client.on_message(filters.command(["status"]))
async def send_status(client: Client, message: Message):
    status_message = "**Bot Status: Idle**" if batch_temp.IS_BATCH.get(message.from_user.id) == True else "**Bot Status: Busy**"
    await client.send_message(
        chat_id=message.chat.id,
        text=status_message,
         reply_to_message_id=message.id
    )

#settings command
@Client.on_message(filters.command(["settings"]))
async def settings(client: Client, message: Message):
    buttons = [[
         InlineKeyboardButton("➕ Add Replace Words", callback_data="add_replace"),
         InlineKeyboardButton("➖ Remove Replace Words", callback_data="remove_replace"),
    ],
    [
        InlineKeyboardButton("👁️ View Replace Words", callback_data="view_replace")
    ],
     [
        InlineKeyboardButton("⚙️ Set Custom Channel", callback_data="set_channel"),
    ],
      [
        InlineKeyboardButton("🖼️ Set Custom Thumbnail", callback_data="set_thumbnail")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    sent_message = await client.send_message(
        chat_id=message.chat.id,
        text="**Settings Menu**",
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )
    await asyncio.sleep(120)
    await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)

@Client.on_callback_query(filters.regex("^add_replace"))
async def add_replace(client, callback_query):
    sent_message = await client.send_message(callback_query.message.chat.id, "**Send me the old word and the new word separated by a comma**", reply_to_message_id=callback_query.message.id)
    await asyncio.sleep(120)
    await client.delete_messages(callback_query.message.chat.id, [sent_message.id], revoke=True)
    await client.answer_callback_query(callback_query.id)
    client.add_handler(MessageHandler(add_replace_callback, filters.text & filters.private, callback_query.message.chat.id))

async def add_replace_callback(client, message):
    try:
       data = message.text.split(",")
       old_word = data[0].strip()
       new_word = data[1].strip()
       if await db.add_replace_word(message.from_user.id, old_word, new_word):
            sent_message = await client.send_message(message.chat.id, f"**Successfully Added Replace Word : \n\n Old Word - {old_word}\n New Word - {new_word}**", reply_to_message_id=message.id)
       else:
           sent_message =  await client.send_message(message.chat.id, "**Error. Try again later**", reply_to_message_id=message.id)
    except Exception as e:
        sent_message = await client.send_message(message.chat.id, f"**Error: {e}**", reply_to_message_id=message.id)
    await asyncio.sleep(120)
    await client.delete_messages(message.chat.id, [message.id, sent_message.id], revoke=True)
    client.remove_handler(MessageHandler(add_replace_callback, filters.text & filters.private, message.chat.id))

@Client.on_callback_query(filters.regex("^remove_replace"))
async def remove_replace(client, callback_query):
     sent_message = await client.send_message(callback_query.message.chat.id, "**Send me the old word you want to remove**", reply_to_message_id=callback_query.message.id)
     await asyncio.sleep(120)
     await client.delete_messages(callback_query.message.chat.id, [sent_message.id], revoke=True)
     await client.answer_callback_query(callback_query.id)
     client.add_handler(MessageHandler(remove_replace_callback, filters.text & filters.private, callback_query.message.chat.id))

async def remove_replace_callback(client, message):
    old_word = message.text.strip()
    if await db.remove_replace_word(message.from_user.id, old_word):
        sent_message = await client.send_message(message.chat.id, f"**Successfully Removed Replace Word : {old_word}**", reply_to_message_id=message.id)
    else:
        sent_message = await client.send_message(message.chat.id, "**Error. Try again later**", reply_to_message_id=message.id)
    await asyncio.sleep(120)
    await client.delete_messages(message.chat.id, [message.id, sent_message.id], revoke=True)
    client.remove_handler(MessageHandler(remove_replace_callback, filters.text & filters.private, message.chat.id))

@Client.on_callback_query(filters.regex("^view_replace"))
async def view_replace(client, callback_query):
    words = await db.get_replace_words(callback_query.message.from_user.id)
    text = "**Your Replace Words :**\n"
    if not words:
         text = "**You Have Not Added Any Replace Words Yet.**"
    else:
      for old, new in words:
        text += f"\nOld Word : **{old}**  New Word : **{new}**"
    sent_message = await client.send_message(callback_query.message.chat.id, text, reply_to_message_id=callback_query.message.id)
    await asyncio.sleep(120)
    await client.delete_messages(callback_query.message.chat.id, [sent_message.id], revoke=True)
    await client.answer_callback_query(callback_query.id)

@Client.on_callback_query(filters.regex("^set_channel"))
async def set_channel(client, callback_query):
      sent_message = await client.send_message(callback_query.message.chat.id, "**Send me the channel id**", reply_to_message_id=callback_query.message.id)
      await asyncio.sleep(120)
      await client.delete_messages(callback_query.message.chat.id, [sent_message.id], revoke=True)
      await client.answer_callback_query(callback_query.id)
      client.add_handler(MessageHandler(set_channel_callback, filters.text & filters.private, callback_query.message.chat.id))

async def set_channel_callback(client, message):
    try:
        channel_id = int(message.text.strip())
        if await db.set_user_channel(message.from_user.id, channel_id):
           sent_message = await client.send_message(message.chat.id, f"**Successfully Set Custom Channel : {channel_id}**", reply_to_message_id=message.id)
        else:
             sent_message = await client.send_message(message.chat.id, f"**Error setting the custom channel**", reply_to_message_id=message.id)
    except Exception as e:
       sent_message = await client.send_message(message.chat.id, f"**Error: {e}**", reply_to_message_id=message.id)
    await asyncio.sleep(120)
    await client.delete_messages(message.chat.id, [message.id, sent_message.id], revoke=True)
    client.remove_handler(MessageHandler(set_channel_callback, filters.text & filters.private, message.chat.id))

@Client.on_callback_query(filters.regex("^set_thumbnail"))
async def set_thumbnail(client, callback_query):
      sent_message = await client.send_message(callback_query.message.chat.id, "**Send me the Custom Thumbnail (Photo)**", reply_to_message_id=callback_query.message.id)
      await asyncio.sleep(120)
      await client.delete_messages(callback_query.message.chat.id, [sent_message.id], revoke=True)
      await client.answer_callback_query(callback_query.id)
      client.add_handler(MessageHandler(set_thumbnail_callback, filters.photo & filters.private, callback_query.message.chat.id))

async def set_thumbnail_callback(client: Client, message: Message):
        try:
            file_path = await client.download_media(message)
            if await db.set_user_thumbnail(message.from_user.id, file_path):
                sent_message = await client.send_message(message.chat.id, "**Successfully Set Custom Thumbnail.**", reply_to_message_id=message.id)
            else:
                 sent_message = await client.send_message(message.chat.id, "**Error setting the custom thumbnail.**", reply_to_message_id=message.id)
        except Exception as e:
           sent_message = await client.send_message(message.chat.id, f"**Error : {e}**", reply_to_message_id=message.id)
        await asyncio.sleep(120)
        await client.delete_messages(message.chat.id, [message.id, sent_message.id], revoke=True)
        client.remove_handler(MessageHandler(set_thumbnail_callback, filters.photo & filters.private, message.chat.id))
# Forwarded Message Command
@Client.on_message(filters.command(["forwarded"]))
async def send_forwarded_message(client: Client, message: Message):
    text = "This is where all of your forwarded messages will show up. This command will work only for single message forward."
    user_channel = await db.get_user_channel(message.from_user.id)
    if user_channel == None:
        if ERROR_MESSAGE:
            sent_message = await client.send_message(
                chat_id=message.chat.id,
                text="**Forward Channel Is Not Set Yet.**",
                reply_to_message_id=message.id
            )
        await asyncio.sleep(120)
        await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
        return
    try:
       async for msg in client.get_chat_history(user_channel, limit = 5): # change the limit to your needs.
        if msg.forward_from_chat and msg.forward_from_chat.id == message.chat.id:
          try:
             await client.copy_message(message.chat.id, msg.chat.id, msg.id)
          except Exception as e:
             if ERROR_MESSAGE:
                sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                await asyncio.sleep(120)
                await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)

       sent_message = await client.send_message(message.chat.id, text, reply_to_message_id=message.id)
       await asyncio.sleep(120)
       await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
    except Exception as e:
        if ERROR_MESSAGE:
           sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
           await asyncio.sleep(120)
           await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single", "").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
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
            except:
                batch_temp.IS_BATCH[message.from_user.id] = True
                return await message.reply("**Your Login Session Expired. So /logout First Then Login Again By - /login**")

            # private
            if "https://t.me/c/" in message.text:
                chatid = int("-100" + datas[4])
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    if ERROR_MESSAGE:
                        sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                        await asyncio.sleep(120)
                        await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)

            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE:
                        sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                        await asyncio.sleep(120)
                        await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)

            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    sent_message = await client.send_message(message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id)
                    await asyncio.sleep(120)
                    await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
                    return
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except:
                    try:
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        if ERROR_MESSAGE:
                            sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                            await asyncio.sleep(120)
                            await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
            # wait time
            await asyncio.sleep(3)
        batch_temp.IS_BATCH[message.from_user.id] = True

# Function to remove Telegram links, hashtags, and mentions
def sanitize_text(text, custom_replace_words):
    if not text: return None
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    # Remove mentions
    text = re.sub(r'@[\w_]+', '', text)
    # Remove hashtags
    text = re.sub(r'#[\w_]+', '', text)
    if custom_replace_words:
       for old, new in custom_replace_words:
           text = text.replace(old, new)
    return text

# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return
    msg_type = get_message_type(msg)
    if not msg_type: return
    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return
    if "Text" == msg_type:
        try:
            sent_msg = await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            await forward_message(client, sent_msg, message.from_user.id)
            return
        except Exception as e:
            if ERROR_MESSAGE:
                sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                await asyncio.sleep(120)
                await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
            return
    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE:
            sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            await asyncio.sleep(120)
            await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))
    custom_replace_words = await db.get_replace_words(message.from_user.id)
    caption = sanitize_text(msg.caption, custom_replace_words)

    if batch_temp.IS_BATCH.get(message.from_user.id): return
    user_thumbnail = await db.get_user_thumbnail(message.from_user.id)
    if "Document" == msg_type:
        try:
            input_media = InputMediaDocument(
                media=file,
                thumb=user_thumbnail, # Remove Thumbnail
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
            )
            sent_msg = await client.send_media_group(chat, [input_media], reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
            await forward_message(client, sent_msg, message.from_user.id)
        except Exception as e:
            if ERROR_MESSAGE:
               sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
               await asyncio.sleep(120)
               await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
    elif "Video" == msg_type:
        try:
            input_media = InputMediaVideo(
                media=file,
                thumb=user_thumbnail,  # Remove thumbnail
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                duration=msg.video.duration,
                width=msg.video.width,
                height=msg.video.height,
            )
            sent_msg = await client.send_media_group(chat, [input_media], reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
            await forward_message(client, sent_msg, message.from_user.id)
        except Exception as e:
           if ERROR_MESSAGE:
                sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                await asyncio.sleep(120)
                await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
    elif "Animation" == msg_type:
        try:
            sent_msg = await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            await forward_message(client, sent_msg, message.from_user.id)
        except Exception as e:
             if ERROR_MESSAGE:
                sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                await asyncio.sleep(120)
                await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
    elif "Sticker" == msg_type:
        try:
            sent_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            await forward_message(client, sent_msg, message.from_user.id)
        except Exception as e:
             if ERROR_MESSAGE:
                sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                await asyncio.sleep(120)
                await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
    elif "Voice" == msg_type:
        try:
            sent_msg = await client.send_voice(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            await forward_message(client, sent_msg, message.from_user.id)
        except Exception as e:
             if ERROR_MESSAGE:
               sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
               await asyncio.sleep(120)
               await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
    elif "Audio" == msg_type:
        try:
            sent_msg = await client.send_audio(chat, file, thumb=user_thumbnail, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            await forward_message(client, sent_msg, message.from_user.id)
        except Exception as e:
            if ERROR_MESSAGE:
               sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
               await asyncio.sleep(120)
               await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
    elif "Photo" == msg_type:
        try:
            sent_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            await forward_message(client, sent_msg, message.from_user.id)
        except Exception as e:
             if ERROR_MESSAGE:
                 sent_message = await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                 await asyncio.sleep(120)
                 await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)
    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
        os.remove(file)
    await asyncio.sleep(2)
    await client.delete_messages(message.chat.id, [smsg.id], revoke=True)

# Function to forward the message to the channel
async def forward_message(client: Client, message: Message, user_id):
    user_channel = await db.get_user_channel(user_id)
    if user_channel == None:
        return
    try:
      await client.forward_messages(user_channel, message.chat.id, message.id)
    except Exception as e:
        if ERROR_MESSAGE:
            sent_message = await client.send_message(message.chat.id, f"Error while Forwarding: {e}", reply_to_message_id=message.id)
            await asyncio.sleep(120)
            await client.delete_messages(message.chat.id, [sent_message.id], revoke=True)

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
from pyrogram import filters
from pyrogram.handlers import MessageHandler