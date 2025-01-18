# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, BOT_TOKEN, ERROR_MESSAGE, ADMINS, LOG_CHANNEL
from database.db import db
from TechVJ.strings import HELP_TXT

class batch_temp(object):
    IS_BATCH = {}

# Error handling decorator
def error_handler(func):
    async def wrapper(client: Client, message: Message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            if ERROR_MESSAGE:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            if LOG_CHANNEL:
                error_info = f"Error: {e}\nCommand: {message.text}\nUser: {message.from_user.id} {message.from_user.username} {message.from_user.first_name}"
                await client.send_message(LOG_CHANNEL, error_info)
    return wrapper

# download status
async def downstatus(client, statusfile, message, chat, file_type):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Downloading {file_type}: <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# upload status
async def upstatus(client, statusfile, message, chat, file_type):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(chat, message.id, f"**Uploading {file_type}: <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# start command
@Client.on_message(filters.command(["start"]) & filters.private)
@error_handler
async def send_start(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "👋")
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "https://t.me/SONICKUWALSSCBOT")
    ],[
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
@Client.on_message(filters.command(["help"]) & filters.private)
@error_handler
async def send_help(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "ℹ️")
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}"
    )


# cancel command
@Client.on_message(filters.command(["cancel"]) & filters.private)
@error_handler
async def send_cancel(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "❌")
    batch_temp.IS_BATCH[message.from_user.id] = True
    await client.send_message(
        chat_id=message.chat.id, 
        text="**Batch Successfully Cancelled.**"
    )
    return


# custom word replace command
@Client.on_message(filters.command("replace") & filters.private)
@error_handler
async def set_replace_words(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "✍️")
    if len(message.command) < 3:
        return await message.reply_text("Use: /replace <word> <replacement>")
    
    replace_data = await db.get_replace(message.from_user.id)
    if replace_data is None:
        await db.add_replace(message.from_user.id, {message.command[1]: message.command[2]})
    else:
        replace_data.update({message.command[1]: message.command[2]})
        await db.update_replace(message.from_user.id, replace_data)
    
    await message.reply_text(f"**{message.command[1]}** will be replaced with **{message.command[2]}**")
    return

# delete word replace command
@Client.on_message(filters.command("delreplace") & filters.private)
@error_handler
async def del_replace_words(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "🗑️")
    if len(message.command) < 2:
       return await message.reply_text("Use: /delreplace <word>")
   
    replace_data = await db.get_replace(message.from_user.id)
    if replace_data is None:
        return await message.reply_text("You haven't set any word to replace yet.")
    
    if message.command[1] in replace_data:
        del replace_data[message.command[1]]
        await db.update_replace(message.from_user.id, replace_data)
        await message.reply_text(f"**{message.command[1]}** will not be replaced")
    else:
        await message.reply_text(f"Word **{message.command[1]}** not found in replace list.")
    return


# show replace words
@Client.on_message(filters.command("showreplace") & filters.private)
@error_handler
async def show_replace_words(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "📑")
    replace_data = await db.get_replace(message.from_user.id)
    if replace_data is None:
        return await message.reply_text("You haven't set any word to replace yet.")
    text = ""
    for i,j in replace_data.items():
        text += f"{i} => {j} \n"
    
    await message.reply_text(f"**Replaced Word List:** \n\n {text}")
    return


# custom thumbnail set
@Client.on_message(filters.command("thumbnail") & filters.private)
@error_handler
async def set_thumbnail(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "🖼️")
    if message.reply_to_message:
        if message.reply_to_message.photo or message.reply_to_message.document:
            file_id = message.reply_to_message.photo.file_id if message.reply_to_message.photo else message.reply_to_message.document.file_id
            await db.set_thumb(message.from_user.id, file_id)
            await message.reply_text("Thumbnail updated!")
            return
        
        else:
            return await message.reply_text("Reply to Photo/Document to set as thumbnail.")

    await message.reply_text("Reply to Photo/Document to set as thumbnail.")
    return

# custom thumbnail delete
@Client.on_message(filters.command("delthumb") & filters.private)
@error_handler
async def delete_thumbnail(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "🗑️")
    await db.del_thumb(message.from_user.id)
    await message.reply_text("Thumbnail removed!")
    return

# automatic forward message to custom channel
@Client.on_message(filters.command("setchannel") & filters.private)
@error_handler
async def set_forward_channel(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "📢")
    if len(message.command) < 2:
        return await message.reply_text("Use: /setchannel <channel_id>")
    try:
        channel_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("Invalid channel ID. Please provide an integer.")
    
    await db.set_forward_channel(message.from_user.id, channel_id)
    await message.reply_text(f"Forward channel set to `{channel_id}`")
    return

# remove forward channel
@Client.on_message(filters.command("delchannel") & filters.private)
@error_handler
async def del_forward_channel(client: Client, message: Message):
    await client.react(message.chat.id, message.id, "🗑️")
    await db.del_forward_channel(message.from_user.id)
    await message.reply_text("Forward channel removed!")
    return


@Client.on_message(filters.text & filters.private)
@error_handler
async def save(client: Client, message: Message):
    
    user_replace_data = await db.get_replace(message.from_user.id)
    if user_replace_data is not None:
        text = message.text
        for i,j in user_replace_data.items():
           text = text.replace(i,j) 
        
        message.text = text
        
    if "https://t.me/" in message.text:
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
        for msgid in range(fromID, toID+1):
            if batch_temp.IS_BATCH.get(message.from_user.id): break
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
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty: return 
    msg_type = get_message_type(msg)
    if not msg_type: return 
    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    if "Text" == msg_type:
        try:
            await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, f'**Downloading {msg_type}**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat, msg_type))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    if not os.path.exists(file):
        return await smsg.delete()
    os.remove(f'{message.id}downstatus.txt')
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat, msg_type))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    thumb = await db.get_thumb(message.from_user.id)
    ph_path = None
    if thumb is not None:
        try:
           ph_path = await acc.download_media(thumb)
        except:
            pass
            
    if "Document" == msg_type:
        try:
           await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
      
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
      
        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        except:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if os.path.exists(f'{message.id}upstatus.txt'): 
        os.remove(f'{message.id}upstatus.txt')
    
    forward_channel = await db.get_forward_channel(message.from_user.id)
    if forward_channel:
        try:
           await client.copy_message(forward_channel,chat, message.id)
        except:
            pass
    os.remove(file)

    await client.delete_messages(message.chat.id,[smsg.id])


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


if __name__ == "__main__":
    bot = Client(
        "Save_Restricted",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )
    bot.run()
