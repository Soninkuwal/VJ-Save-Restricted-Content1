# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import pyrogram
import logging  # Import logging module
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE, FORWARD_CHANNEL_ID  # <-- Added FORWARD_CHANNEL_ID
from database.db import db
from TechVJ.strings import HELP_TXT

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s') # Changed level to ERROR to capture errors by default

class batch_temp(object):
    IS_BATCH = {}

async def auto_delete_message(client: Client, chat_id: int, message_id: int, delay: int = 5): # Auto delete function
    await asyncio.sleep(delay)
    try:
        await client.delete_messages(chat_id, message_id)
    except Exception as e:
        logging.error(f"Error deleting message {message_id} in chat {chat_id}: {e}") # Log deletion errors

async def send_message_auto_delete(client: Client, chat_id: int, text: str, reply_markup=None, reply_to_message_id=None, parse_mode=enums.ParseMode.HTML, delay: int = 5): # Send with auto delete
    msg = await client.send_message(chat_id, text, reply_markup=reply_markup, reply_to_message_id=reply_to_message_id, parse_mode=parse_mode)
    asyncio.create_task(auto_delete_message(client, chat_id, msg.id, delay))
    return msg # Return message object if needed for further operations


async def downstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)

    status_message = None # Initialize status_message outside the loop
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            text = f"**Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**"
            if status_message:
                status_message = await client.edit_message_text(chat, status_message.id, text) # Edit existing message
            else:
                status_message = await client.send_message(chat, text) # Send new message initially

            if FORWARD_CHANNEL_ID != 0 and status_message: # Forward status message if channel is set
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, status_message.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding download status message: {forward_e}") # Log forwarding errors
            await asyncio.sleep(10)
        except Exception as e:
            logging.error(f"Error in downstatus loop: {e}") # Log errors in downstatus loop
            await asyncio.sleep(5)
    if status_message: # Delete status message when download finishes or errors
        await auto_delete_message(client, chat, status_message.id)


# upload status
async def upstatus(client, statusfile, message, chat):
    while True:
        if os.path.exists(statusfile):
            break
        await asyncio.sleep(3)

    status_message = None # Initialize status_message outside the loop
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            text = f"**Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**"
            if status_message:
                status_message = await client.edit_message_text(chat, status_message.id, text) # Edit existing message
            else:
                status_message = await client.send_message(chat, text) # Send new message initially

            if FORWARD_CHANNEL_ID != 0 and status_message: # Forward status message if channel is set
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, status_message.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding upload status message: {forward_e}") # Log forwarding errors

            await asyncio.sleep(10)
        except Exception as e:
            logging.error(f"Error in upstatus loop: {e}") # Log errors in upstatus loop
            await asyncio.sleep(5)

    if status_message: # Delete status message when upload finishes or errors
        await auto_delete_message(client, chat, status_message.id)


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
        InlineKeyboardButton("❣️ Developer", url = "https://t.me/SONICKUWALSSCBOT")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='https://t.me/SONICKUWALSSCBOT'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    start_text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n for bot any error content :- @SONICKUWALSSCBOT </b>"
    await send_message_auto_delete( # Using auto_delete for start message
        client=client,
        chat_id=message.chat.id,
        text=start_text,
        reply_markup=reply_markup,
        reply_to_message_id=message.id,
    )
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await send_message_auto_delete( # Using auto_delete for help message
        client=client,
        chat_id=message.chat.id,
        text=f"{HELP_TXT}",
        reply_to_message_id=message.id,
    )


# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await send_message_auto_delete( # Using auto_delete for cancel message
        client=client,
        chat_id=message.chat.id,
        text="**Batch Successfully Cancelled.**",
        reply_to_message_id=message.id,
    )


# status command
@Client.on_message(filters.command(["status"]))
async def send_status(client: Client, message: Message):
    status_message_text = "**Bot Status: Idle**" if batch_temp.IS_BATCH.get(message.from_user.id) == True else "**Bot Status: Busy**"
    await send_message_auto_delete( # Using auto_delete for status message
        client=client,
        chat_id=message.chat.id,
        text=status_message_text,
        reply_to_message_id=message.id,
    )


# Forwarded Message Command
@Client.on_message(filters.command(["forwarded"]))
async def send_forwarded_message(client: Client, message: Message):
    text = "This is where all of your forwarded messages will show up. This command will work only for single message forward."
    if FORWARD_CHANNEL_ID == 0:
       await send_message_auto_delete( # Using auto_delete if forward channel not set
            client=client,
            chat_id=message.chat.id,
            text="**Forward Channel Is Not Set Yet.**",
            reply_to_message_id=message.id,
       )
       return
    try:
       forwarded_messages_text = ""
       async for msg in client.get_chat_history(FORWARD_CHANNEL_ID, limit = 5): # change the limit to your needs.
        if msg.forward_from_chat and msg.forward_from_chat.id == message.chat.id:
          try:
             copied_msg = await client.copy_message(message.chat.id, msg.chat.id, msg.id)
             asyncio.create_task(auto_delete_message(client, message.chat.id, copied_msg.id)) # Auto delete forwarded history messages
          except Exception as e:
             if ERROR_MESSAGE:
                error_msg = await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id) # Auto delete error message
                logging.error(f"Error while copying forwarded message: {e}") # Log copy errors

       await send_message_auto_delete(client, message.chat.id, text, reply_to_message_id=message.id) # Auto delete info message
    except Exception as e:
        if ERROR_MESSAGE:
           error_msg = await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id) # Auto delete error message
           logging.error(f"Error in forwarded command: {e}") # Log forwarded command errors


@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        if batch_temp.IS_BATCH.get(message.from_user.id) == False:
            await send_message_auto_delete(client, message.chat.id, "**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**", reply_to_message_id=message.id) # Auto delete busy message
            return
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
                await send_message_auto_delete(client, message.chat.id, "**For Downloading Restricted Content You Have To /login First.**", reply_to_message_id=message.id) # Auto delete login required message
                batch_temp.IS_BATCH[message.from_user.id] = True
                return
            try:
                acc = Client("saverestricted", session_string=user_data, api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
            except Exception as acc_e:
                logging.error(f"Account connection error: {acc_e}") # Log account connection errors
                batch_temp.IS_BATCH[message.from_user.id] = True
                await send_message_auto_delete(client, message.chat.id, "**Your Login Session Expired. So /logout First Then Login Again By - /login**", reply_to_message_id=message.id) # Auto delete session expired message
                return

            # private
            if "https://t.me/c/" in message.text:
                try:
                    chatid = int("-100" + datas[4])
                except IndexError:
                    await send_message_auto_delete(client, message.chat.id, "**Invalid private channel link.**", reply_to_message_id=message.id) # Auto delete invalid link message
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return
                try:
                    await handle_private(client, acc, message, chatid, msgid)
                except Exception as e:
                    logging.error(f"Error in handle_private (private): {e}") # Log handle_private errors for private channels
                    if ERROR_MESSAGE == True:
                        await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id) # Auto delete general error message

            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                    logging.error(f"Error in handle_private (bot): {e}") # Log handle_private errors for bot links
                    if ERROR_MESSAGE == True:
                        await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id) # Auto delete general error message

            # public
            else:
                username = datas[3]

                try:
                    msg = await client.get_messages(username, msgid)
                except UsernameNotOccupied:
                    await send_message_auto_delete(client, message.chat.id, "The username is not occupied by anyone", reply_to_message_id=message.id) # Auto delete username not occupied message
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return
                except Exception as e_username: # Catch other potential errors during get_messages for public channels
                    logging.error(f"Error getting messages for public channel: {e_username}")
                    await send_message_auto_delete(client, message.chat.id, f"Error accessing public channel: {e_username}", reply_to_message_id=message.id) # Auto delete access error message
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return

                try:
                    await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except Exception as copy_e: # Catch errors during copy_message for public channels
                    logging.error(f"Error copying message for public channel: {copy_e}")
                    try:
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        logging.error(f"Error in handle_private (fallback for public): {e}") # Log handle_private fallback errors
                        if ERROR_MESSAGE == True:
                            await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id) # Auto delete general error message

            # wait time
            await asyncio.sleep(3)
        batch_temp.IS_BATCH[message.from_user.id] = True

# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    msg: Message = await acc.get_messages(chatid, msgid)
    if msg.empty:
        await send_message_auto_delete(client, message.chat.id, "**Message is empty or not available.**", reply_to_message_id=message.id) # Auto delete empty message info
        return
    msg_type = get_message_type(msg)
    if not msg_type:
        await send_message_auto_delete(client, message.chat.id, "**Unsupported message type.**", reply_to_message_id=message.id) # Auto delete unsupported type info
        return
    chat = message.chat.id
    if batch_temp.IS_BATCH.get(message.from_user.id): return
    if "Text" == msg_type:
        try:
            if msg.text: # Check if msg.text is not None or empty
                sent_msg = await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                asyncio.create_task(auto_delete_message(client, chat, sent_msg.id)) # Auto delete text message
                if FORWARD_CHANNEL_ID != 0:
                    try:
                        await client.forward_messages(FORWARD_CHANNEL_ID, chat, sent_msg.id)
                    except Exception as forward_e:
                        logging.error(f"Error forwarding text message: {forward_e}") # Log text message forwarding errors
            else:
                await send_message_auto_delete(client, message.chat.id, "**Empty text message encountered.**", reply_to_message_id=message.id) # Auto delete empty text message error
        except Exception as e:
            logging.error(f"Error sending text message: {e}") # Log text sending errors
            if ERROR_MESSAGE == True:
                await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete general error message
        return

    smsg = await send_message_auto_delete(client, message.chat.id, '**Downloading**', reply_to_message_id=message.id) # Auto delete downloading status
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', message, chat))
    file = None # Initialize file to None
    ph_path = None # Initialize ph_path to None
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e_download:
        logging.error(f"Error during download: {e_download}") # Log download errors
        if ERROR_MESSAGE == True:
            await send_message_auto_delete(client, message.chat.id, f"Error during download: {e_download}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete download error message
        if smsg:
            await client.delete_messages(message.chat.id, [smsg.id]) # Delete status message if download fails
        return

    if not file or os.stat(file).st_size == 0: # Check if file is valid and not 0KB
        logging.error(f"Downloaded file is empty or invalid: {file}") # Log empty file error
        if file and os.path.exists(file): # Clean up potentially created empty file
            os.remove(file)
        if smsg:
            await client.delete_messages(message.chat.id, [smsg.id]) # Delete status message if file is empty
        await send_message_auto_delete(client, message.chat.id, "**Downloaded file is empty or invalid. Skipping upload.**", reply_to_message_id=message.id) # Auto delete empty file message
        return


    if batch_temp.IS_BATCH.get(message.from_user.id):
        if file and os.path.exists(file): # Clean up downloaded file if batch is cancelled
            os.remove(file)
        if smsg:
            await client.delete_messages(message.chat.id, [smsg.id]) # Delete status message if batch is cancelled
        return
    asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', message, chat))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    if batch_temp.IS_BATCH.get(message.from_user.id):
        if file and os.path.exists(file): # Clean up downloaded file if batch is cancelled
            os.remove(file)
        if smsg:
            await client.delete_messages(message.chat.id, [smsg.id]) # Delete status message if batch is cancelled
        return

    try: # Try to download thumbnail, handle potential errors gracefully
        if msg_type in ["Document", "Video", "Audio"]:
            try:
                if msg_type == "Document" and msg.document.thumbs:
                    thumb_id = msg.document.thumbs[0].file_id
                elif msg_type == "Video" and msg.video.thumbs:
                    thumb_id = msg.video.thumbs[0].file_id
                elif msg_type == "Audio" and msg.audio.thumbs:
                    thumb_id = msg.audio.thumbs[0].file_id
                else:
                    thumb_id = None

                if thumb_id:
                    ph_path = await acc.download_media(thumb_id)

            except Exception as thumb_e:
                logging.error(f"Error downloading thumbnail: {thumb_e}") # Log thumbnail download errors
                ph_path = None # Set ph_path to None if thumbnail download fails
    except:
        ph_path = None # Ensure ph_path is None if any error during thumbnail processing

    if "Document" == msg_type:
        try:
            sent_msg = await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            asyncio.create_task(auto_delete_message(client, chat, sent_msg.id)) # Auto delete document message

            if FORWARD_CHANNEL_ID != 0:
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, sent_msg.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding document message: {forward_e}") # Log document forwarding errors
        except Exception as e:
            logging.error(f"Error sending document: {e}") # Log document sending errors
            if ERROR_MESSAGE == True:
                await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete general error message
        if ph_path != None and os.path.exists(ph_path): os.remove(ph_path)


    elif "Video" == msg_type:
        try:
            sent_msg = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            asyncio.create_task(auto_delete_message(client, chat, sent_msg.id)) # Auto delete video message
            if FORWARD_CHANNEL_ID != 0:
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, sent_msg.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding video message: {forward_e}") # Log video forwarding errors
        except Exception as e:
            logging.error(f"Error sending video: {e}") # Log video sending errors
            if ERROR_MESSAGE == True:
                await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete general error message
        if ph_path != None and os.path.exists(ph_path): os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            sent_msg = await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            asyncio.create_task(auto_delete_message(client, chat, sent_msg.id)) # Auto delete animation message
            if FORWARD_CHANNEL_ID != 0:
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, sent_msg.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding animation message: {forward_e}") # Log animation forwarding errors
        except Exception as e:
            logging.error(f"Error sending animation: {e}") # Log animation sending errors
            if ERROR_MESSAGE == True:
                await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete general error message

    elif "Sticker" == msg_type:
        try:
            sent_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            asyncio.create_task(auto_delete_message(client, chat, sent_msg.id)) # Auto delete sticker message
            if FORWARD_CHANNEL_ID != 0:
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, sent_msg.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding sticker message: {forward_e}") # Log sticker forwarding errors
        except Exception as e:
            logging.error(f"Error sending sticker: {e}") # Log sticker sending errors
            if ERROR_MESSAGE == True:
                await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete general error message

    elif "Voice" == msg_type:
        try:
            sent_msg = await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            asyncio.create_task(auto_delete_message(client, chat, sent_msg.id)) # Auto delete voice message
            if FORWARD_CHANNEL_ID != 0:
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, sent_msg.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding voice message: {forward_e}") # Log voice forwarding errors

        except Exception as e:
            logging.error(f"Error sending voice: {e}") # Log voice sending errors
            if ERROR_MESSAGE == True:
                await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete general error message

    elif "Audio" == msg_type:
        try:
            sent_msg = await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            asyncio.create_task(auto_delete_message(client, chat, sent_msg.id)) # Auto delete audio message
            if FORWARD_CHANNEL_ID != 0:
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, sent_msg.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding audio message: {forward_e}") # Log audio forwarding errors
        except Exception as e:
            logging.error(f"Error sending audio: {e}") # Log audio sending errors
            if ERROR_MESSAGE == True:
                await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete general error message

        if ph_path != None and os.path.exists(ph_path): os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            sent_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            asyncio.create_task(auto_delete_message(client, chat, sent_msg.id)) # Auto delete photo message
            if FORWARD_CHANNEL_ID != 0:
                try:
                    await client.forward_messages(FORWARD_CHANNEL_ID, chat, sent_msg.id)
                except Exception as forward_e:
                    logging.error(f"Error forwarding photo message: {forward_e}") # Log photo forwarding errors

        except Exception as e:
            logging.error(f"Error sending photo: {e}") # Log photo sending errors
            if ERROR_MESSAGE == True:
                await send_message_auto_delete(client, message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) # Auto delete general error message

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')

    if smsg: # Forward the initial 'Downloading' status message ID to the custom channel
        try:
            if FORWARD_CHANNEL_ID != 0:
                await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, smsg.id)
        except Exception as forward_e:
            logging.error(f"Error forwarding initial status message: {forward_e}") # Log initial status forwarding errors
            if ERROR_MESSAGE:
               await send_message_auto_delete(client, message.chat.id, f"Error while Forwarding Status Message: {forward_e}", reply_to_message_id=message.id) # Auto delete forward error message

    if file and os.path.exists(file): # Remove file only if it exists and is not None
        os.remove(file)
    if smsg:
        await client.delete_messages(message.chat.id, [smsg.id]) # Delete initial status message


# get the type of message
def get_message_type(msg: pyrogram.types.messages_and_media.message.Message):
    if msg.document:
        return "Document"
    elif msg.video:
        return "Video"
    elif msg.animation:
        return "Animation"
    elif msg.sticker:
        return "Sticker"
    elif msg.voice:
        return "Voice"
    elif msg.audio:
        return "Audio"
    elif msg.photo:
        return "Photo"
    elif msg.text:
        return "Text"
    else:
        return None
