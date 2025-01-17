# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio 
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
from TechVJ.strings import HELP_TXT

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
        
        # Adding error handling for download status updates
        try:
            if txt == '0%':
                await client.edit_message_text(chat, message.id, "Error: Downloaded file is 0KB. Please try again.")
            else:
                await client.edit_message_text(chat, message.id, f"Downloaded: <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Error in downstatus: {e}")
            await asyncio.sleep(5)

async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)      
    
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        
        # Adding error handling for upload status updates
        try:
            if txt == '0%':
                await client.edit_message_text(chat, message.id, "Error: Uploaded file is 0KB. Please try again.")
            else:
                await client.edit_message_text(chat, message.id, f"Uploaded: <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10)
        except Exception as e:
            print(f"Error in upstatus: {e}")
            await asyncio.sleep(5)

# progress writer
def progress(current, total, message, type):
    if total <= 0:
        return  # Handle 0 or negative total
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")



# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
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
        text=f"<b>👋 Hi {message.from_user.mention}I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n for bot any error content :- @SONICKUWALSSCBOT </b>", 
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



@Client.on_message(filters.command(["add_replace_word"]))
async def add_replace_word(client: Client, message: Message):
    try:
        old_word, new_word = message.text.split(None, 2)[1:]
        await db.add_replace_word(message.from_user.id, old_word, new_word)
        await message.reply(f"Word replacement added: `{old_word}` -> `{new_word}`")
    except:
        await message.reply("Invalid format! Use: `/add_replace_word old_word new_word`")

    
@Client.on_message(filters.command(["delete_replace_word"]))
async def delete_replace_word(client: Client, message: Message):
    try:
        word = message.text.split(None, 1)[1]
        await db.delete_replace_word(message.from_user.id, word)
        await message.reply(f"Word `{word}` removed from replacements.")
    except:
        await message.reply("Invalid format! Use: `/delete_replace_word word`")

@Client.on_message(filters.command(["set_caption"]))
async def set_caption(client: Client, message: Message):
    caption = message.text.split(None, 1)[1]
    await db.set_caption(message.from_user.id, caption)
    await message.reply("Custom caption updated successfully!")


@Client.on_message(filters.command(["set_forward_channel"]))
async def set_forward_channel(client: Client, message: Message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL]:
        await db.set_forward_channel(message.from_user.id, message.chat.id)
        await message.reply("Forwarding channel set successfully!")
    else:
        await message.reply("Please use this command in the channel/group to set it as the forwarding channel.")






@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
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

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        return await smsg.delete()
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id): return 
            
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
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
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

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
        os.remove(file)
    await client.delete_messages(message.chat.id,[smsg.id])




# Thumbnail Handler
async def set_thumbnail(client, message: Message):
    user_id = message.from_user.id
    if not message.photo:
        await message.reply_text("Please reply to an image to set it as a thumbnail!")
        return

    thumbnail_path = f"thumbnails/{user_id}_thumb.jpg"
    os.makedirs("thumbnails", exist_ok=True)

    # Save the thumbnail
    await client.download_media(message.photo, file_name=thumbnail_path)
    await message.reply_text("Thumbnail successfully updated!")

@Client.on_message(filters.command(["set_thumbnail"]))
async def set_thumbnail_command(client: Client, message: Message):
    await set_thumbnail(client, message)

# Automatically remove existing thumbnails after use
def remove_thumbnail(user_id):
    thumbnail_path = f"thumbnails/{user_id}_thumb.jpg"
    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

def get_thumbnail(user_id):
    thumbnail_path = f"thumbnails/{user_id}_thumb.jpg"
    return thumbnail_path if os.path.exists(thumbnail_path) else None

# Auto-delete download/upload progress messages
async def auto_delete_message(client, chat_id, message_id, delay=5):
    await asyncio.sleep(delay)
    await client.delete_messages(chat_id, message_id)

# Adjust the `handle_private` function to implement changes
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty:
        return

    msg_type = get_message_type(msg)
    if not msg_type:
        return

    chat = message.chat.id
    user_id = message.from_user.id
    smsg = await client.send_message(message.chat.id, '**Downloading...**', reply_to_message_id=message.id)

    # Start download
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id)
        return await smsg.delete()

    # Handle Thumbnail
    thumbnail = get_thumbnail(user_id)

    # Start Upload
    smsg = await client.send_message(chat, '**Uploading...**', reply_to_message_id=message.id)
    try:
        if msg_type == "Document":
            await client.send_document(chat, file, thumb=thumbnail, caption=msg.caption, reply_to_message_id=message.id)
        elif msg_type == "Photo":
            await client.send_photo(chat, file, caption=msg.caption, reply_to_message_id=message.id)
        elif msg_type == "Video":
            await client.send_video(chat, file, thumb=thumbnail, caption=msg.caption, reply_to_message_id=message.id)
        elif msg_type == "text":
            await client.send_text(chat, file, caption=msg.caption, reply_to_message_id=message.id)
        elif msg_type == "animation":
            await client.send_animation(chat, file, caption=msg.caption, reply_to_message_id=message.id)
        elif msg_type == "sticker":
            await client.send_sticker(chat, file, caption=msg.caption, reply_to_message_id=message.id)
        elif msg_type == "voice":
            await client.send_voice(chat, file, caption=msg.caption, reply_to_message_id=message.id)
        
        # Add other media types if needed
    except Exception as e:
        if ERROR_MESSAGE:
            await client.send_message(chat, f"Error: {e}", reply_to_message_id=message.id)

    # Cleanup
    remove_thumbnail(user_id)
    os.remove(file)
    await auto_delete_message(client, chat, smsg.id, delay=5)
                                          
   
        

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
        
