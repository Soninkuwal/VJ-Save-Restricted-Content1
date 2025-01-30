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
        text=status_message
    )

# settings command
@Client.on_message(filters.command(["settings"]))
async def settings(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("⚙️ Set Custom Replace Word", callback_data="set_replace_word"),
        InlineKeyboardButton("🗑️ Delete Custom Replace Word", callback_data="delete_replace_word"),
    ],[
        InlineKeyboardButton("⚙️ Set Forward Channel", callback_data="set_forward_channel"),
    ],[
         InlineKeyboardButton("🖼️ Set Custom Thumbnail", callback_data="set_thumbnail")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(
        chat_id=message.chat.id,
        text="**⚙️ Bot Settings Menu**",
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )
    
# Callback for Settings Menu
@Client.on_callback_query(filters.regex(r"set_replace_word|delete_replace_word|set_forward_channel|set_thumbnail"))
async def settings_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    query = callback_query.data
    if query == "set_replace_word":
      await callback_query.message.reply("Send me old word and new word separated by a `=>` to be replaced, like this `old_word => new_word`")
    elif query == "delete_replace_word":
       await callback_query.message.reply("Send me the old word you want to delete.")
    elif query == "set_forward_channel":
        await callback_query.message.reply("Send me the channel ID to forward messages to.")
    elif query == "set_thumbnail":
        await callback_query.message.reply("Send me the image you want to set as custom thumbnail.")
    await callback_query.answer()

# text filter for getting settings input
@Client.on_message(filters.text & filters.private)
async def settings_text_handler(client: Client, message: Message):
    if "=>" in message.text:
        old_word, new_word = message.text.split("=>")
        old_word = old_word.strip()
        new_word = new_word.strip()
        if await db.add_replace_word(message.from_user.id, old_word, new_word):
           await message.reply("The replace word is now set!")
        else:
            await message.reply("There was an error while adding the replace word.")
    elif message.reply_to_message and message.reply_to_message.text == "Send me the old word you want to delete.":
        old_word = message.text.strip()
        if await db.remove_replace_word(message.from_user.id, old_word):
          await message.reply("The replace word is deleted!")
        else:
          await message.reply("There was an error deleting the replace word, or word was not found.")
    elif message.reply_to_message and message.reply_to_message.text == "Send me the channel ID to forward messages to.":
      try:
          channel_id = int(message.text.strip())
          if await db.add_forward_channel(message.from_user.id, channel_id):
            await message.reply("Channel ID is now set.")
          else:
            await message.reply("There was an error while setting the channel ID.")
      except ValueError:
         await message.reply("This is not a valid channel ID. Try again.")
    elif message.reply_to_message and message.reply_to_message.text == "Send me the image you want to set as custom thumbnail.":
        if message.photo:
            file_path = await message.download()
            await db.add_thumbnail(message.from_user.id, file_path)
            await message.reply("Custom thumbnail is set.")
        else:
            await message.reply("Invalid type sent, send a photo.")

# Auto delete message after 2 min
async def auto_delete_message(client: Client, message: Message):
   await asyncio.sleep(120)
   try:
        await client.delete_messages(message.chat.id, [message.id])
   except:
        pass # ignore if there is an error deleting the message.

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
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    if ERROR_MESSAGE:
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
                except:
                    try:
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        if ERROR_MESSAGE:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

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
    
    custom_replace_words = await db.get_replace_words(message.from_user.id)

    if "Text" == msg_type:
      try:
            sent_msg = await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            await forward_message(client, sent_msg, message.from_user.id)
            asyncio.create_task(auto_delete_message(client, sent_msg))
            return
      except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        await smsg.delete()
        return # added return

    if batch_temp.IS_BATCH.get(message.from_user.id): return
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))
    
    caption = sanitize_text(msg.caption, custom_replace_words)
    
    if batch_temp.IS_BATCH.get(message.from_user.id): return

    if "Document" == msg_type:
         try:
            
            thumb_path = await db.get_thumbnail(message.from_user.id)
            if not thumb_path:
                thumb = None
            else:
                 thumb = thumb_path
            input_media = InputMediaDocument(
                media=file,
                thumb=thumb, # Remove Thumbnail
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
            )
            sent_msg = await client.send_media_group(chat, [input_media], reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
            await forward_message(client, sent_msg[0], message.from_user.id)
            asyncio.create_task(auto_delete_message(client, sent_msg[0]))

         except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Video" == msg_type:
         try:
            thumb_path = await db.get_thumbnail(message.from_user.id)
            if not thumb_path:
                thumb = None
            else:
                 thumb = thumb_path

            input_media = InputMediaVideo(
                    media=file,
                    thumb=thumb, #Remove thumbnail
                    caption=caption,
                    parse_mode=enums.ParseMode.HTML,
                    duration=msg.video.duration,
                    width=msg.video.width,
                    height=msg.video.height,

                 )
             
            sent_msg = await client.send_media_group(chat, [input_media], reply_to_message_id=message.id, progress=progress, progress_args=[message, "up"])
            await forward_message(client, sent_msg[0], message.from_user.id)
            asyncio.create_task(auto_delete_message(client, sent_msg[0]))

         except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Animation" == msg_type:
      try:
            sent_msg = await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            await forward_message(client, sent_msg, message.from_user.id)
            asyncio.create_task(auto_delete_message(client, sent_msg))
      except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Sticker" == msg_type:
      try:
            sent_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            await forward_message(client, sent_msg, message.from_user.id)
            asyncio.create_task(auto_delete_message(client, sent_msg))
      except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Voice" == msg_type:
       try:
           sent_msg = await client.send_voice(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
           await forward_message(client, sent_msg, message.from_user.id)
           asyncio.create_task(auto_delete_message(client, sent_msg))
       except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
      try:
            thumb_path = await db.get_thumbnail(message.from_user.id)
            if not thumb_path:
                thumb = None
            else:
                 thumb = thumb_path
            sent_msg = await client.send_audio(chat, file, thumb=thumb, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            await forward_message(client, sent_msg, message.from_user.id)
            asyncio.create_task(auto_delete_message(client, sent_msg))
      except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Photo" == msg_type:
      try:
          sent_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
          await forward_message(client, sent_msg, message.from_user.id)
          asyncio.create_task(auto_delete_message(client, sent_msg))
      except Exception as e:
           if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')
        
    try:
       await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, smsg.id)
    except Exception as e:
       if ERROR_MESSAGE:
         await client.send_message(message.chat.id, f"Error while Forwarding: {e}", reply_to_message_id=message.id)

    os.remove(file)
    await asyncio.sleep(2)  # Wait a moment before deleting the status message
    await client.delete_messages(message.chat.id, [smsg.id])

# Function to forward the message to the channel
async def forward_message(client: Client, message: Message, user_id):
    try:
        channel_id = await db.get_forward_channel(user_id)
        if not channel_id:
            channel_id = FORWARD_CHANNEL_ID
        await client.forward_messages(channel_id, message.chat.id, message.id)
    except Exception as e:
      print(f'Error while Forwarding: {e}')

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