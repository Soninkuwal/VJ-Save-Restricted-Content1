# requirements.txt
# pyrogram
# python-dotenv
# asyncio
# pymongo
# tqdm
# pillow
import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from dotenv import load_dotenv
load_dotenv()
import logging
from tqdm.asyncio import tqdm
import re
from PIL import Image
# logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
from config import API_ID, API_HASH, ERROR_MESSAGE, LOG_CHANNEL
from database.db import database
from TechVJ.strings import strings, HELP_TXT

ADMINS = [int(admin_id) for admin_id in os.environ.get("ADMIN_IDS", "7841292070").split(",")]
class batch_temp(object):
    IS_BATCH = {}
    BATCH_LIMIT = 1000  # Maximum links in a batch

class bot_config(object):
    CUSTOM_THUMBNAIL = None
    REPLACE_WORDS = {}
    DELETE_WORDS = []
    CUSTOM_CAPTION = None
    FORWARD_CHANNEL = None
    SHOW_ERROR_MESSAGE = False


def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default


async def downstatus(client, statusfile, message):
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


# upload status
async def upstatus(client, statusfile, message):
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


# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")
        
async def log_message(client, message):
    try:
        await client.send_message(LOG_CHANNEL, message, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        logging.error(f"Error Sending Log Message: {e}")
        
async def react_to_command(client, message):
    try:
         await client.send_reaction(message.chat.id, message.id, "😍")
    except:
        pass

async def retry_with_backoff(func, *args, retries=3, delay=2):
    for i in range(retries):
        try:
            return await func(*args)
        except Exception as e:
            logging.error(f"Retry Attempt {i + 1}/{retries} - Error: {e} -  Function: {func.__name__}")
            if i < retries - 1:
                await asyncio.sleep(delay * (2 ** i))  # Exponential backoff
    return None

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    await react_to_command(client, message)
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "http://t.me/Sonickuwalupdatebot")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='http://t.me/Sonickuwalupdatebot'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(message.chat.id, f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>", reply_markup=reply_markup, reply_to_message_id=message.id)
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await react_to_command(client, message)
    await client.send_message(message.chat.id, f"{HELP_TXT}")

@Client.on_message(filters.command(["setting"]))
async def setting_menu(client: Client, message: Message):
     await react_to_command(client, message)
     if not message.from_user.id in ADMINS:
        return await message.reply("Only admin can access the setting menu.")
     buttons = [[
         InlineKeyboardButton("Set Custom Thumbnail", callback_data="set_thumbnail"),
         InlineKeyboardButton("Remove Custom Thumbnail", callback_data="remove_thumbnail"),
     ],[
        InlineKeyboardButton("Set Forward Channel", callback_data="set_forward_channel"),
        InlineKeyboardButton("Replace Words", callback_data="set_replace_word"),
     ],[
         InlineKeyboardButton("Delete Words", callback_data="set_delete_word"),
         InlineKeyboardButton("Set Custom Caption", callback_data="set_custom_caption")
     ],[
         InlineKeyboardButton("Show Setting", callback_data="show_setting")
     ],[
         InlineKeyboardButton("Error Message True/False", callback_data="set_error_message")
     ]]
     reply_markup = InlineKeyboardMarkup(buttons)
     await message.reply("Setting Menu", reply_markup=reply_markup)
    
@Client.on_callback_query(filters.regex(r"^set_(thumbnail|forward_channel|replace_word|delete_word|custom_caption|error_message|show_setting)|remove_thumbnail"))
async def handle_setting_callback(client: Client, callback_query):
    await callback_query.answer()
    
    if callback_query.data == "set_thumbnail":
       await client.send_message(callback_query.message.chat.id, "Send me your Custom Thumbnail Image.", reply_to_message_id=callback_query.message.id)
       
       set_thumbnail_filter = filters.create(lambda _, message: message.from_user.id == callback_query.from_user.id and message.photo)
       thumb_message = await client.listen.Message(callback_query.message.chat.id, filters=set_thumbnail_filter, timeout=60)
       if not thumb_message: return await callback_query.message.reply("Time Out! You Took To Much Time.")
       
       try:
           path = await client.download_media(thumb_message.photo.file_id)
           bot_config.CUSTOM_THUMBNAIL = path
           await callback_query.message.reply("Custom Thumbnail Setting Done Successfully")
       except Exception as e:
             await callback_query.message.reply(f"Error: {e}")
    elif callback_query.data == "remove_thumbnail":
        bot_config.CUSTOM_THUMBNAIL = None
        await callback_query.message.reply("Custom Thumbnail Removed Successfully!")
    elif callback_query.data == "set_forward_channel":
        await client.send_message(callback_query.message.chat.id, "Send me your target forward channel username / id.", reply_to_message_id=callback_query.message.id)
        set_forward_filter = filters.create(lambda _, message: message.from_user.id == callback_query.from_user.id and message.text)
        forward_message = await client.listen.Message(callback_query.message.chat.id, filters=set_forward_filter, timeout=60)
        if not forward_message: return await callback_query.message.reply("Time Out! You Took To Much Time.")
        try:
             bot_config.FORWARD_CHANNEL = forward_message.text.strip()
             await callback_query.message.reply("Forward Channel Setting Done Successfully")
        except Exception as e:
            await callback_query.message.reply(f"Error: {e}")
    
    elif callback_query.data == "set_replace_word":
         await client.send_message(callback_query.message.chat.id, "Send me a old and new word format like (old,new)  for replace. Example - (old1,new1) (old2,new2)", reply_to_message_id=callback_query.message.id)
         set_replace_filter = filters.create(lambda _, message: message.from_user.id == callback_query.from_user.id and message.text)
         replace_message = await client.listen.Message(callback_query.message.chat.id, filters=set_replace_filter, timeout=60)
         if not replace_message: return await callback_query.message.reply("Time Out! You Took To Much Time.")
         try:
             text_list = replace_message.text.split()
             for text in text_list:
                if "," in text:
                  old_word, new_word = text.replace("(", "").replace(")", "").split(",")
                  bot_config.REPLACE_WORDS[old_word] = new_word
             await callback_query.message.reply("Replace Word Setting Done Successfully")
         except Exception as e:
            await callback_query.message.reply(f"Error: {e}")

    elif callback_query.data == "set_delete_word":
         await client.send_message(callback_query.message.chat.id, "Send me a word list for delete. Example - word1 word2 word3", reply_to_message_id=callback_query.message.id)
         set_delete_filter = filters.create(lambda _, message: message.from_user.id == callback_query.from_user.id and message.text)
         delete_message = await client.listen.Message(callback_query.message.chat.id, filters=set_delete_filter, timeout=60)
         if not delete_message: return await callback_query.message.reply("Time Out! You Took To Much Time.")
         try:
            bot_config.DELETE_WORDS = delete_message.text.split()
            await callback_query.message.reply("Delete Word Setting Done Successfully")
         except Exception as e:
            await callback_query.message.reply(f"Error: {e}")
    
    elif callback_query.data == "set_custom_caption":
        await client.send_message(callback_query.message.chat.id, "Send me your custom caption. Use {text} for adding original caption.", reply_to_message_id=callback_query.message.id)
        set_caption_filter = filters.create(lambda _, message: message.from_user.id == callback_query.from_user.id and message.text)
        caption_message = await client.listen.Message(callback_query.message.chat.id, filters=set_caption_filter, timeout=60)
        if not caption_message: return await callback_query.message.reply("Time Out! You Took To Much Time.")
        try:
           bot_config.CUSTOM_CAPTION = caption_message.text
           await callback_query.message.reply("Custom Caption Setting Done Successfully!")
        except Exception as e:
            await callback_query.message.reply(f"Error {e}")

    elif callback_query.data == "set_error_message":
        bot_config.SHOW_ERROR_MESSAGE = not bot_config.SHOW_ERROR_MESSAGE
        await callback_query.message.reply(f"Error Message {'Enabled' if bot_config.SHOW_ERROR_MESSAGE else 'Disabled'} Sucessfully.")
    elif callback_query.data == "show_setting":
        text = "**--Setting--**\n"
        text += f"**Custom Thumbnail :** {bot_config.CUSTOM_THUMBNAIL}\n"
        text += f"**Forward Channel :** {bot_config.FORWARD_CHANNEL}\n"
        text += f"**Replace Words :** {bot_config.REPLACE_WORDS}\n"
        text += f"**Delete Words :** {bot_config.DELETE_WORDS}\n"
        text += f"**Custom Caption :** {bot_config.CUSTOM_CAPTION}\n"
        text += f"**Show Error Message:** {bot_config.SHOW_ERROR_MESSAGE}\n"
        await callback_query.message.reply(text)
# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    await react_to_command(client, message)
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )

def replace_text(text):
    for old,new in bot_config.REPLACE_WORDS.items():
        text = text.replace(old,new)
    for word in bot_config.DELETE_WORDS:
       text = text.replace(word,"")
    return text

def create_custom_caption(original_caption):
    if bot_config.CUSTOM_CAPTION:
        if "{text}" in bot_config.CUSTOM_CAPTION:
           custom_caption = bot_config.CUSTOM_CAPTION.replace("{text}",original_caption if original_caption else "")
        else:
            custom_caption = bot_config.CUSTOM_CAPTION + " " + (original_caption if original_caption else "")
        return custom_caption
    else:
        return original_caption

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        await react_to_command(client, message)
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            return await message.reply_text("**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        batch_temp.IS_BATCH[message.from_user.id] = False
        if not message.from_user.id in ADMINS:
             if (toID - fromID) > batch_temp.BATCH_LIMIT:
                 await message.reply_text(f"You exceeded the batch limit of {batch_temp.BATCH_LIMIT}")
                 batch_temp.IS_BATCH[message.from_user.id] = True
                 return
        
        total_messages = toID - fromID + 1
        pbar = tqdm(total=total_messages, desc="Processing Batch", disable=False)
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
            user_data = database.find_one({'chat_id': message.chat.id})
            if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                await message.reply("**For Downloading Restricted Content You Have To /login First.**")
                batch_temp.IS_BATCH[message.from_user.id] = True
                return
            try:
                 acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
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
                    logging.error(f"Error in private message {e}")
                    if bot_config.SHOW_ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    logging.error(f"Error in bot message {e}")
                    if bot_config.SHOW_ERROR_MESSAGE == True:
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
                        logging.error(f"Error in public message {e}")
                        if bot_config.SHOW_ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            pbar.update(1)
            # wait time
            await asyncio.sleep(1)
        batch_temp.IS_BATCH[message.from_user.id] = True
        pbar.close()


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if not msg: return
    if msg.empty: return
    msg_type = get_message_type(msg)
    if not msg_type: return 
    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            text = msg.text
            text = replace_text(text)
            await client.send_message(chat, text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            logging.error(f"Error sending text message {e}")
            if bot_config.SHOW_ERROR_MESSAGE == True:
                 await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))
    file = None
    try:
         file = await retry_with_backoff(acc.download_media, msg, progress=progress, progress_args=[message, "down"])
         if file:
            os.remove(f'{message.id}downstatus.txt')
            file_size = os.path.getsize(file)
            if file_size == 0 :
                if os.path.exists(file): os.remove(file)
                return await smsg.delete()
    except Exception as e:
        logging.error(f"Error downloading media {e}")
        if bot_config.SHOW_ERROR_MESSAGE == True:
             await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if file and os.path.exists(file): os.remove(file)
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id):
        if file and os.path.exists(file): os.remove(file)
        return
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    
    if caption: caption = replace_text(caption)
    
    caption = create_custom_caption(caption)

    if batch_temp.IS_BATCH.get(message.from_user.id):
        if file and os.path.exists(file): os.remove(file)
        return
    
    thumb_path = bot_config.CUSTOM_THUMBNAIL
    if "Document" == msg_type:
        try:
            if msg.document.thumbs:
                 thumb_path = await retry_with_backoff(acc.download_media, msg.document.thumbs[0].file_id)
        except:
           pass
        
        try:
            await client.send_document(chat, file, thumb=thumb_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            logging.error(f"Error Sending Document {e}")
            if bot_config.SHOW_ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Video" == msg_type:
        try:
            if msg.video.thumbs:
                thumb_path = await retry_with_backoff(acc.download_media, msg.video.thumbs[0].file_id)
        except:
             pass
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=thumb_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
             logging.error(f"Error Sending Video {e}")
             if bot_config.SHOW_ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
             logging.error(f"Error Sending Animation {e}")
             if bot_config.SHOW_ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            logging.error(f"Error Sending Sticker {e}")
            if bot_config.SHOW_ERROR_MESSAGE == True:
                 await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
             logging.error(f"Error Sending Voice {e}")
             if bot_config.SHOW_ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
             if msg.audio.thumbs:
                 thumb_path = await retry_with_backoff(acc.download_media, msg.audio.thumbs[0].file_id)
        except:
             pass

        try:
            await client.send_audio(chat, file, thumb=thumb_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
             logging.error(f"Error Sending Audio {e}")
             if bot_config.SHOW_ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except:
             logging.error(f"Error Sending Photo {e}")
             if bot_config.SHOW_ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
    if file and os.path.exists(file):
        os.remove(file)
    if thumb_path != None and thumb_path != bot_config.CUSTOM_THUMBNAIL and os.path.exists(thumb_path):
        os.remove(thumb_path)
    await client.delete_messages(message.chat.id,[smsg.id])
    
    if bot_config.FORWARD_CHANNEL:
        try:
            await client.copy_message(bot_config.FORWARD_CHANNEL, chat, msgid)
            
        except Exception as e:
            logging.error(f"Error Forwading Message {e}")
        
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
