# Don't Remove Credit Tg - @VJ_Botz
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

import tempfile

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


# Unified progress bar
def progress(current, total, message, operation):
    percent = f"{current * 100 / total:.1f}%"
    with open(f"{message.id}_{operation}_status.txt", "w") as file:
        file.write(f"{operation.capitalize()} Progress: {percent}")

# Cleanup after progress tracking
async def clean_progress_files(message_id, operation):
    status_file = f"{message_id}_{operation}_status.txt"
    if os.path.exists(status_file):
        os.remove(status_file)




# Permanent thumbnail management
async def set_thumbnail(client: Client, message: Message):
    if not message.document:
        return await message.reply_text("Please reply to a valid image to set as thumbnail.")
    thumb_path = await safe_file_operation(client.download_media, message.document)
    global THUMBNAIL_PATH
    THUMBNAIL_PATH = thumb_path
    await message.reply_text("Thumbnail updated successfully!")


# Optimized slow speed handling with semaphore
semaphore = asyncio.Semaphore(3)

# Command to remove global thumbnail
@Client.on_message(filters.command(["remove_thumbnail"]))
async def remove_thumbnail(client, message):
    global THUMBNAIL_PATH
    if os.path.exists(THUMBNAIL_PATH):
        os.remove(THUMBNAIL_PATH)
        THUMBNAIL_PATH = None
        await message.reply_text("Thumbnail removed successfully!")
    else:
        await message.reply_text("No thumbnail set.")
        


# Progress callback with retry mechanism
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as status_file:
        status_file.write(f"{current * 100 / total:.1f}%")

# Enhanced download status tracking
async def track_status(client, statusfile, message, text_prefix, chat):
    while not os.path.exists(statusfile):
        await asyncio.sleep(2)

    while os.path.exists(statusfile):
        with open(statusfile, "r") as file:
            status = file.read()
        try:
            await client.edit_message_text(
                chat_id=chat,
                message_id=message.id,
                text=f"{text_prefix} **{status}**",
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(5)
        except FloodWait as e:
            await asyncio.sleep(e.value)

# Optimized file handling with retry logic
async def safe_file_operation(operation, *args, retries=3):
    for attempt in range(retries):
        try:
            return await operation(*args)
        except Exception as e:
            if attempt == retries - 1:
                raise e
            await asyncio.sleep(2)

# Handle private chats and file operations
async def handle_private(client, acc, message, chatid, msgid):
    try:
        msg = await acc.get_messages(chatid, msgid)
        if msg.empty:
            return

        file_path = await safe_file_operation(acc.download_media, msg, progress, [message, "down"])
        if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            raise ValueError("File is 0 KB or failed to download.")
        
        await safe_file_operation(client.send_document, message.chat.id, file_path, reply_to_message_id=message.id)
        os.remove(file_path)

    except Exception as e:
        if ERROR_MESSAGE:
            await message.reply_text(f"Error: {str(e)}", parse_mode=enums.ParseMode.HTML)





# Define the channel where messages should be forwarded
FORWARD_CHANNEL_ID = -1002260543763  # Replace with your target channel ID

@Client.on_message(filters.private & filters.text)
async def auto_forward(client: Client, message: Message):
    """
    Automatically forward messages received in private chats to a predefined channel.
    """
    try:
        # Forward the incoming message to the target channel
        forwarded_message = await client.forward_messages(
            chat_id=FORWARD_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_ids=message.id
        )

        # Optionally, notify the user about the successful forwarding
        await message.reply_text("Your message has been forwarded successfully!")
    
    except Exception as e:
        # Log the error or notify the user
        await message.reply_text(f"Error forwarding your message: {str(e)}")

# Hook for other message types (e.g., media, documents, etc.)
@Client.on_message(filters.private & ~filters.text)
async def auto_forward_media(client: Client, message: Message):
    """
    Automatically forward media messages to the predefined channel.
    """
    try:
        # Forward media or non-text messages
        forwarded_message = await client.forward_messages(
            chat_id=FORWARD_CHANNEL_ID,
            from_chat_id=message.chat.id,
            message_ids=message.id
        )

        # Notify user of successful forwarding
        await message.reply_text("Your media has been forwarded successfully!")

    except Exception as e:
        # Handle errors gracefully
        await message.reply_text(f"Error forwarding your media: {str(e)}")



def apply_customizations(user_data, text):
    replace_words = user_data.get("replace_words", [])
    delete_words = user_data.get("delete_words", [])
    
    # Replace words
    for old_word, new_word in replace_words:
        text = text.replace(old_word, new_word)
    
    # Delete words
    for word in delete_words:
        text = text.replace(word, "")
    
    return text

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    user_data = await db.get_user(message.from_user.id)
    if user_data:
        custom_caption = user_data.get("custom_caption", "")
        if custom_caption:
            message.text += f"\n\n{custom_caption}"
        message.text = apply_customizations(user_data, message.text)
    
    # Continue processing...



@Client.on_message(filters.command(["set_caption"]))
async def set_caption(client, message):
    if len(message.command) < 2:
        await message.reply("Please provide a caption. Usage: /set_caption Your caption here")
        return
    new_caption = " ".join(message.command[1:])
    await db.update_user(message.from_user.id, {"custom_caption": new_caption})
    await message.reply(f"Custom caption set to: {new_caption}")
@Client.on_message(filters.command(["add_replace_word"]))
async def add_replace_word(client, message):
    if len(message.command) < 3:
        await message.reply("Usage: /add_replace_word word_to_replace new_word")
        return
    word_to_replace, new_word = message.command[1], message.command[2]
    user_data = await db.get_user(message.from_user.id)
    replace_words = user_data.get("replace_words", [])
    replace_words.append((word_to_replace, new_word))
    await db.update_user(message.from_user.id, {"replace_words": replace_words})
    await message.reply(f"Word '{word_to_replace}' will now be replaced with '{new_word}'.")

@Client.on_message(filters.command(["remove_replace_word"]))
async def remove_replace_word(client, message):
    if len(message.command) < 2:
        await message.reply("Usage: /remove_replace_word word_to_replace")
        return
    word_to_replace = message.command[1]
    user_data = await db.get_user(message.from_user.id)
    replace_words = [w for w in user_data.get("replace_words", []) if w[0] != word_to_replace]
    await db.update_user(message.from_user.id, {"replace_words": replace_words})
    await message.reply(f"Word '{word_to_replace}' has been removed from replace list.")
    


                   


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
        
