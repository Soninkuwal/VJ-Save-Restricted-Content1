import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE, FORWARD_CHANNEL_ID
from database.db import db
from TechVJ.strings import HELP_TXT
import time
import json

class batch_temp(object):
    IS_BATCH = {}

    
class UserSettings:
    def __init__(self, file="settings.json"):
        self.file = file
        self.settings = self.load_settings()
        
    def load_settings(self):
          if not os.path.exists(self.file):
            return {}
          with open(self.file, "r") as f:
             return json.load(f)
            
    def save_settings(self):
       with open(self.file, "w") as f:
             json.dump(self.settings, f, indent=4)

    def get_setting(self, user_id, key, default=None):
        user_id= str(user_id)
        if user_id in self.settings and key in self.settings[user_id]:
            return self.settings[user_id][key]
        return default

    def set_setting(self, user_id, key, value):
        user_id= str(user_id)
        if user_id not in self.settings:
           self.settings[user_id]={}
        self.settings[user_id][key] = value
        self.save_settings()
    
    def delete_setting(self, user_id, key):
        user_id= str(user_id)
        if user_id in self.settings and key in self.settings[user_id]:
           del self.settings[user_id][key]
           self.save_settings()
    
    def get_all_setting(self, user_id):
        user_id= str(user_id)
        if user_id in self.settings:
           return self.settings[user_id]
        return {}
        
user_settings = UserSettings()

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
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

async def auto_delete_message(client, message):
    await asyncio.sleep(120)  # 2 minutes
    try:
       await client.delete_messages(message.chat.id, message.id)
    except:
       pass

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [[
        InlineKeyboardButton("â£ï¸ Developer", url="https://t.me/SONICKUWALSSCBOT")
    ], [
        InlineKeyboardButton('ðŸ” sá´œá´˜á´˜á´Ê€á´› É¢Ê€á´á´œá´˜', url='https://t.me/SONICKUWALSSCBOT'),
        InlineKeyboardButton('ðŸ¤– á´œá´˜á´…á´€á´›á´‡ á´„Êœá´€É´É´á´‡ÊŸ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    start_msg = await client.send_message(
        chat_id=message.chat.id,
        text=f"<b>ðŸ‘‹ Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n for bot any error content :- @SONICKUWALSSCBOT </b>",
        reply_markup=reply_markup,
        reply_to_message_id=message.id
    )
    asyncio.create_task(auto_delete_message(client, start_msg))
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    help_msg = await client.send_message(
        chat_id=message.chat.id,
        text=f"{HELP_TXT}"
    )
    asyncio.create_task(auto_delete_message(client, help_msg))


# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    cancel_msg = await client.send_message(
        chat_id=message.chat.id,
        text="**Batch Successfully Cancelled.**"
    )
    asyncio.create_task(auto_delete_message(client, cancel_msg))


# status command
@Client.on_message(filters.command(["status"]))
async def send_status(client: Client, message: Message):
    status_message = "**Bot Status: Idle**" if batch_temp.IS_BATCH.get(message.from_user.id) == True else "**Bot Status: Busy**"
    status_msg = await client.send_message(
        chat_id=message.chat.id,
        text=status_message
    )
    asyncio.create_task(auto_delete_message(client, status_msg))

# settings command
@Client.on_message(filters.command(["settings"]))
async def send_setting(client: Client, message: Message):
    user_id = message.from_user.id
    setting = user_settings.get_all_setting(user_id)
    text = f"**Your Current Settings:**\n\n{setting}\n\n**Use the /help command to learn about all commands**"
    setting_msg = await client.send_message(
        chat_id=message.chat.id,
        text=text
    )
    asyncio.create_task(auto_delete_message(client, setting_msg))

# set custom forward channel id
@Client.on_message(filters.command(["setforward"]))
async def set_forward_channel(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("**Please provide the channel ID after /setforward command.**")
        return
    try:
        user_id = message.from_user.id
        channel_id = int(message.command[1])
        user_settings.set_setting(user_id, "forward_channel", channel_id)
        await message.reply_text(f"**Forward channel ID set to `{channel_id}`.**")
    except ValueError:
         await message.reply_text("**Invalid Channel ID provided.**")

# set custom replace words
@Client.on_message(filters.command(["addreplace"]))
async def add_replace_word(client: Client, message: Message):
    if len(message.command) != 3:
        await message.reply_text("**Please provide the words to replace after /addreplace command.**\n\n**Ex:**`/addreplace old_word new_word`")
        return
    user_id = message.from_user.id
    old_word = message.command[1]
    new_word = message.command[2]
    replace_words = user_settings.get_setting(user_id,"replace_words",{})
    replace_words[old_word] = new_word
    user_settings.set_setting(user_id, "replace_words", replace_words)
    await message.reply_text(f"**Replace word set successfully. Whenever `{old_word}` will come it will be replaced with `{new_word}`.**")

# Delete custom replace words
@Client.on_message(filters.command(["delreplace"]))
async def del_replace_word(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("**Please provide the word to delete after /delreplace command.**\n\n**Ex:**`/delreplace old_word`")
        return
    user_id = message.from_user.id
    old_word = message.command[1]
    replace_words = user_settings.get_setting(user_id,"replace_words",{})
    if old_word in replace_words:
       del replace_words[old_word]
       user_settings.set_setting(user_id,"replace_words", replace_words)
       await message.reply_text(f"**Replace word `{old_word}` has been deleted successfully.**")
    else:
        await message.reply_text(f"**Replace word `{old_word}` not found.**")
        
# set custom delete words
@Client.on_message(filters.command(["adddelete"]))
async def add_delete_word(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("**Please provide the words to delete after /adddelete command.**\n\n**Ex:**`/adddelete delete_word`")
        return
    user_id = message.from_user.id
    delete_word = message.command[1]
    delete_words = user_settings.get_setting(user_id,"delete_words",[])
    delete_words.append(delete_word)
    user_settings.set_setting(user_id,"delete_words", delete_words)
    await message.reply_text(f"**Delete word set successfully. Whenever `{delete_word}` will come in caption it will be deleted.**")

# Delete custom delete words
@Client.on_message(filters.command(["deldelete"]))
async def del_delete_word(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("**Please provide the word to delete from delete words after /deldelete command.**\n\n**Ex:**`/deldelete delete_word`")
        return
    user_id = message.from_user.id
    delete_word = message.command[1]
    delete_words = user_settings.get_setting(user_id,"delete_words",[])
    if delete_word in delete_words:
       delete_words.remove(delete_word)
       user_settings.set_setting(user_id,"delete_words", delete_words)
       await message.reply_text(f"**Delete word `{delete_word}` has been deleted successfully.**")
    else:
        await message.reply_text(f"**Delete word `{delete_word}` not found.**")

# set custom thumbnail
@Client.on_message(filters.command(["setthumbnail"]))
async def set_thumbnail(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.photo:
        user_id = message.from_user.id
        file_id = message.reply_to_message.photo.file_id
        user_settings.set_setting(user_id, "custom_thumbnail", file_id)
        await message.reply_text("**Custom thumbnail has been set successfully.**")
    else:
        await message.reply_text("**Please reply to a photo to set it as a custom thumbnail.**")

# delete custom thumbnail
@Client.on_message(filters.command(["delthumbnail"]))
async def del_thumbnail(client: Client, message: Message):
    user_id = message.from_user.id
    user_settings.delete_setting(user_id, "custom_thumbnail")
    await message.reply_text("**Custom thumbnail has been deleted successfully.**")


# Forwarded Message Command
@Client.on_message(filters.command(["forwarded"]))
async def send_forwarded_message(client: Client, message: Message):
    text = "This is where all of your forwarded messages will show up. This command will work only for single message forward."
    user_id = message.from_user.id
    forward_channel_id = user_settings.get_setting(user_id,"forward_channel",FORWARD_CHANNEL_ID)
    if forward_channel_id == 0:
        await client.send_message(
            chat_id=message.chat.id,
            text="**Forward Channel Is Not Set Yet.**"
        )
        return
    try:
        async for msg in client.get_chat_history(forward_channel_id, limit=5):
            if msg.forward_from_chat and msg.forward_from_chat.id == message.chat.id:
                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id)
                except Exception as e:
                    if ERROR_MESSAGE:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

        await client.send_message(message.chat.id, text, reply_to_message_id=message.id)
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)


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
                    if ERROR_MESSAGE == True:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
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
                except:
                    try:
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(3)
        batch_temp.IS_BATCH[message.from_user.id] = True


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    try:
        msg: Message = await acc.get_messages(chatid, msgid)
        if msg.empty: return
        msg_type = get_message_type(msg)
        if not msg_type: return
    except Exception as e:
         if ERROR_MESSAGE:
           await client.send_message(message.chat.id, f"Error: while Get Message: {e}", reply_to_message_id=message.id)
         return
    chat = message.chat.id
    user_id = message.from_user.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return
    if "Text" == msg_type:
         if msg.text: # Check if text content exists
            text_content = msg.text
            replace_words = user_settings.get_setting(user_id,"replace_words",{})
            for old_word, new_word in replace_words.items():
               text_content = text_content.replace(old_word, new_word)
            delete_words = user_settings.get_setting(user_id,"delete_words",[])
            for delete_word in delete_words:
                text_content = text_content.replace(delete_word, "")
            try:
                sent_msg = await client.send_message(chat, text_content, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            # Forward to the custom channel
            except Exception as e:
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                return
         else:
             return

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id): return
    
    custom_thumbnail = user_settings.get_setting(user_id, "custom_thumbnail")
    
    if custom_thumbnail:
        try:
            ph_path = await acc.download_media(custom_thumbnail)
        except Exception as e:
             if ERROR_MESSAGE:
                 await client.send_message(message.chat.id, f"Error: Custom Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
             ph_path = None
    else:
       ph_path = None

    if "Document" == msg_type:
        if not file or os.stat(file).st_size == 0: # Check the file exist or not
            if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: Empty/Invalid File Downloaded", reply_to_message_id=message.id)
            return
        
        if msg.document.thumbs and not custom_thumbnail:
           try:
              ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
           except Exception as e:
              if ERROR_MESSAGE:
                 await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                 ph_path = None

        try:
            sent_msg = await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Document Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None and not custom_thumbnail:
           os.remove(ph_path)

    elif "Video" == msg_type:
        if not file or os.stat(file).st_size == 0: # Check the file exist or not
            if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: Empty/Invalid File Downloaded", reply_to_message_id=message.id)
            return
        if msg.video.thumbs and not custom_thumbnail:
          try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
          except Exception as e:
              if ERROR_MESSAGE:
                 await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                 ph_path = None
        try:
            sent_msg = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Video Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None and not custom_thumbnail:
           os.remove(ph_path)

    elif "Animation" == msg_type:
        if not file or os.stat(file).st_size == 0: # Check the file exist or not
            if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: Empty/Invalid File Downloaded", reply_to_message_id=message.id)
            return
        try:
            sent_msg = await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Animation Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Sticker" == msg_type:
        if not file or os.stat(file).st_size == 0: # Check the file exist or not
            if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: Empty/Invalid File Downloaded", reply_to_message_id=message.id)
            return
        try:
            sent_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Sticker Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Voice" == msg_type:
        if not file or os.stat(file).st_size == 0: # Check the file exist or not
            if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: Empty/Invalid File Downloaded", reply_to_message_id=message.id)
            return
        try:
            sent_msg = await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Voice Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        if not file or os.stat(file).st_size == 0: # Check the file exist or not
            if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: Empty/Invalid File Downloaded", reply_to_message_id=message.id)
            return
        if msg.audio.thumbs and not custom_thumbnail:
           try:
              ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
           except Exception as e:
               if ERROR_MESSAGE:
                   await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                   ph_path = None
        try:
            sent_msg= await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Audio Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        if ph_path != None and not custom_thumbnail:
            os.remove(ph_path)

    elif "Photo" == msg_type:
        if not file or os.stat(file).st_size == 0: # Check the file exist or not
            if ERROR_MESSAGE:
               await client.send_message(message.chat.id, f"Error: Empty/Invalid File Downloaded", reply_to_message_id=message.id)
            return
        try:
            sent_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
               await client.send_message(message.chat.id, f"Error: Send Photo Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)


    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')

    # forward custom channel
    forward_channel_id = user_settings.get_setting(user_id,"forward_channel",FORWARD_CHANNEL_ID)
    try:
      await client.forward_messages(forward_channel_id, message.chat.id, disable_notification=True)
    except Exception as e:
        if ERROR_MESSAGE:
           await client.send_message(message.chat.id, f"Error while Forwarding : {e}", reply_to_message_id=message.id)

    os.remove(file)
    await client.delete_messages(message.chat.id, [smsg.id])


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
