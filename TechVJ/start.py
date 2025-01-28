import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE, FORWARD_CHANNEL_ID  # <-- Added FORWARD_CHANNEL_ID
from database.db import db
from TechVJ.strings import HELP_TXT
import logging

# set up basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

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
        except Exception as e:
            logging.error(f"Error during editing download status message: {e}")
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
        except Exception as e:
           logging.error(f"Error during editing upload status message: {e}")
           await asyncio.sleep(5)


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
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n for bot any error content :- @SONICKUWALSSCBOT </b>", 
        reply_markup=reply_markup, 
        reply_to_message_id=message.id,
        parse_mode=enums.ParseMode.HTML
    )
    return


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(
        chat_id=message.chat.id, 
        text=f"{HELP_TXT}",
        parse_mode=enums.ParseMode.HTML
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
    

# Forwarded Message Command
@Client.on_message(filters.command(["forwarded"]))
async def send_forwarded_message(client: Client, message: Message):
    text = "This is where all of your forwarded messages will show up. This command will work only for single message forward."
    if FORWARD_CHANNEL_ID == 0:
       await client.send_message(
            chat_id=message.chat.id,
            text="**Forward Channel Is Not Set Yet.**"
       )
       return
    try:
       async for msg in client.get_chat_history(FORWARD_CHANNEL_ID, limit = 5): # change the limit to your needs. 
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
                        logging.error(f"Error during private channel handling: {e}")
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
            # bot
            elif "https://t.me/b/" in message.text:
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
                   if ERROR_MESSAGE == True:
                      logging.error(f"Error during bot handling: {e}")
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
                    try:    
                        await handle_private(client, acc, message, username, msgid)               
                    except Exception as e:
                        if ERROR_MESSAGE == True:
                            logging.error(f"Error during public handling: {e}")
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
            if msg.text:
              await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
             
              # forward custom channel ID 
              await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, msg.id)

              return
            else:
              logging.info("Message was empty")
              return
            
      except Exception as e:
            if ERROR_MESSAGE == True:
                logging.error(f"Error during sending text msg: {e}")
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            return 

    smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
    asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        if not file or os.path.getsize(file) == 0:
           logging.error(f"File downloaded with 0 size or was not created.")
           os.remove(f'{message.id}downstatus.txt')
           return await smsg.delete()
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        if ERROR_MESSAGE == True:
            logging.error(f"Error during downloading file: {e}")
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML) 
        if os.path.exists(f'{message.id}downstatus.txt'):
            os.remove(f'{message.id}downstatus.txt')
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
            if msg.document.thumbs:
               ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            else:
              ph_path = None

        # forward custom channel ID 
            # await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)
        except Exception as e:
            logging.error(f"Error downloading thumbnail for document {e}")
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            logging.error(f"Error sending document {e}")
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path and os.path.exists(ph_path): os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            if msg.video.thumbs:
               ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            else:
              ph_path = None
        # forward custom channel ID 
            # await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)
        except Exception as e:
            logging.error(f"Error downloading thumbnail for video: {e}")
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            logging.error(f"Error sending video: {e}")
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path and os.path.exists(ph_path): os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        # forward custom channel ID 
            # await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)
            
        except Exception as e:
            logging.error(f"Error sending animation {e}")
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        # forward custom channel ID 
           # await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)
            
        except Exception as e:
            logging.error(f"Error sending sticker: {e}")
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)     

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            
            # forward custom channel ID 
            # await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)
            
        
        except Exception as e:
            logging.error(f"Error sending voice: {e}")
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        try:
            if msg.audio.thumbs:
              ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            else:
              ph_path = None

        # forward custom channel ID 
           # await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)
            
        except Exception as e:
            logging.error(f"Error downloading thumbnail for audio: {e}")
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
           logging.error(f"Error sending audio: {e}")
           if ERROR_MESSAGE == True:
               await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        
        if ph_path and os.path.exists(ph_path): os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        # forward custom channel ID 
           # await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, sent_msg.id)
        
        except Exception as e:
            logging.error(f"Error sending photo: {e}")
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
    
    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')

    # forward custom channel 
    try:
      await client.forward_messages(FORWARD_CHANNEL_ID, message.chat.id, smsg.id)
    except Exception as e:
        if ERROR_MESSAGE:
            logging.error(f"Error while Forwarding: {e}")
            await client.send_message(message.chat.id, f"Error while Forwarding: {e}", reply_to_message_id=message.id)
    
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
