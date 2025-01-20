import asyncio 
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message 
import time
import os
import threading
import json
from config import API_ID, API_HASH, BOT_TOKEN, CUSTOM_CHANNEL_ID
from database.db import database 
from TechVJ.strings import strings, HELP_TXT

# Function to safely access dictionary elements
def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default

# Global variable to track bot speed
bot_speed_normal = True

# Function to simulate slowdown after a period
async def simulate_slowdown():
    global bot_speed_normal
    await asyncio.sleep(7200)  # 2 hours (7200 seconds)
    bot_speed_normal = False
    print("Bot speed slowed down.")
    await asyncio.sleep(1800) #  30 minutes (1800 seconds) slow mode
    bot_speed_normal = True
    print("Bot speed back to normal.")

# Download status
async def downstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)
      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as downread:
            txt = downread.read()
        try:
            await client.edit_message_text(message.chat.id, message.id, f"Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10 if bot_speed_normal else 20) # Adjust sleep time based on bot speed
        except:
            await asyncio.sleep(5 if bot_speed_normal else 10)

# upload status
async def upstatus(client: Client, statusfile, message):
    while True:
        if os.path.exists(statusfile):
            break

        await asyncio.sleep(3)      
    while os.path.exists(statusfile):
        with open(statusfile, "r") as upread:
            txt = upread.read()
        try:
            await client.edit_message_text(message.chat.id, message.id, f"Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10 if bot_speed_normal else 20)
        except:
            await asyncio.sleep(5 if bot_speed_normal else 10)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
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
    await client.send_message(message.chat.id, f"{HELP_TXT}")

# Login command
@Client.on_message(filters.command(["login"]))
async def login_handler(client: Client, message: Message):
    user_id = message.from_user.id
    if database.find_one({'chat_id': user_id, 'logged_in': True}):
        await message.reply_text("You are already logged in.")
        return

    phone_number_prompt = await message.reply_text("Please send me your phone number in international format (e.g., +1xxxxxxxxxx).")
    
    try:
        phone_number_message = await client.listen.Message(filters.text & filters.user(user_id), timeout=60)
        phone_number = phone_number_message.text

        # Send code request
        try:
            sent_code_info = await client.send_code(phone_number)
        except FloodWait as e:
            await message.reply_text(f"FloodWait error. Please try again after {e.value} seconds.")
            return
        except Exception as e:
            await message.reply_text(f"Error sending code: {e}")
            return
            
        await phone_number_message.reply_text("Please send me the code you received.")
        
        try:
            code_message = await client.listen.Message(filters.text & filters.user(user_id), timeout=60)
            code = code_message.text
        except asyncio.TimeoutError:
            await message.reply_text("Timeout waiting for code. Please try /login again.")
            return

        # Sign in
        try:
            await client.sign_in(phone_number, sent_code_info.phone_code_hash, code)
            session_string = await client.export_session_string()
            database.update_one({'chat_id': user_id}, {'$set': {'logged_in': True, 'session': session_string}}, upsert=True)
            await code_message.reply_text("Successfully logged in!")

        except Exception as e:
            await code_message.reply_text(f"Error signing in: {e}")

    except asyncio.TimeoutError:
        await phone_number_prompt.edit("Timeout waiting for phone number. Please try /login again.")

# Logout command
@Client.on_message(filters.command(["logout"]))
async def logout_handler(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = database.find_one({'chat_id': user_id})
    
    if user_data and get(user_data, 'logged_in', False):
        database.update_one({'chat_id': user_id}, {'$set': {'logged_in': False, 'session': None}})
        await message.reply_text("Successfully logged out!")
    else:
        await message.reply_text("You are not logged in.")

# Batch processing command
@Client.on_message(filters.command(["batch"]))
async def batch_handler(client: Client, message: Message):
    user_id = message.from_user.id
    user_data = database.find_one({'chat_id': user_id})

    if not get(user_data, 'logged_in', False) or user_data['session'] is None:
        await message.reply_text(strings['need_login'])
        return

    await message.reply_text("Please send me the links, each on a new line. Send 'stop' to end.")

    links = []
    while True:
        try:
            link_message = await client.listen.Message(filters.text & filters.user(user_id), timeout=60)
            if link_message.text.lower() == 'stop':
                break
            if len(links) >= 1000:
                await link_message.reply_text("You've reached the maximum limit of 1000 links.")
                break

            if "https://t.me/" in link_message.text:
                links.append(link_message.text)
            else:
                await link_message.reply_text("Invalid link format. Please use 'https://t.me/...'")
        except asyncio.TimeoutError:
            await message.reply_text("Timeout. Send /batch again to start a new batch.")
            return

    if not links:
        await message.reply_text("No links provided.")
        return

    await message.reply_text(f"Processing {len(links)} links...")

    # Use a separate client for batch processing
    acc = Client("batch_processor", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
    await acc.connect()
    cancel_task = None # Initialize cancel task

    for link in links:
        try:
             # Cancel outgoing batch command
            @Client.on_message(filters.command(["cancel"]))
            async def cancel_batch_handler(client: Client, message: Message):
                nonlocal cancel_task
                if cancel_task:
                    cancel_task.cancel()
                    await message.reply_text("Batch processing cancelled.")
                else:
                    await message.reply_text("No batch process to cancel.")
            datas = link.split("/")
            temp = datas[-1].replace("?single","").split("-")
            fromID = int(temp[0].strip())
            try:
                toID = int(temp[1].strip())
            except:
                toID = fromID
            for msgid in range(fromID, toID + 1):

                if "https://t.me/c/" in link:
                    chatid = int("-100" + datas[4])
                    await handle_private(client, acc, message, chatid, msgid, forward_to_channel=True) 
                elif "https://t.me/b/" in link:
                    username = datas[4]
                    await handle_private(client, acc, message, username, msgid, forward_to_channel=True)
                else:
                    username = datas[3]
                    try:
                        msg = await acc.get_messages(username, msgid)
                    except UsernameNotOccupied:
                        continue 
                    try:
                        await acc.copy_message(CUSTOM_CHANNEL_ID, msg.chat.id, msg.id)
                    except Exception as e:
                        print(f"Error copying message: {e}")
                        continue

                await asyncio.sleep(3 if bot_speed_normal else 6) #Adjust sleep based on bot speed
                
        except Exception as e:
            print(f"Error processing link {link}: {e}")
            continue

    await acc.stop()
    await message.reply_text("Batch processing completed.")

# save command
@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        datas = message.text.split("/")
        temp = datas[-1].replace("?single","").split("-")
        fromID = int(temp[0].strip())
        try:
            toID = int(temp[1].strip())
        except:
            toID = fromID
        for msgid in range(fromID, toID+1):
            # private
            if "https://t.me/c/" in message.text:
                user_data = database.find_one({'chat_id': message.chat.id})
                if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                    await client.send_message(message.chat.id, strings['need_login'])
                    return
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                chatid = int("-100" + datas[4])
                await handle_private(client, acc, message, chatid, msgid)
    
            # bot
            elif "https://t.me/b/" in message.text:
                user_data = database.find_one({"chat_id": message.chat.id})
                if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                    await client.send_message(message.chat.id, strings['need_login'])
                    return
                acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid)
                except Exception as e:
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
                        user_data = database.find_one({"chat_id": message.chat.id})
                        if not get(user_data, 'logged_in', False) or user_data['session'] is None:
                            await client.send_message(message.chat.id, strings['need_login'])
                            return
                        acc = Client("saverestricted", session_string=user_data['session'], api_hash=API_HASH, api_id=API_ID)
                        await acc.connect()
                        await handle_private(client, acc, message, username, msgid)
                        
                    except Exception as e:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(3 if bot_speed_normal else 6)

# handle private
async def handle_private(client: Client, acc: Client, message: Message, chatid: int or str, msgid: int, forward_to_channel: bool = False):
    try:
        msg: Message = await acc.get_messages(chatid, msgid)
        msg_type = get_message_type(msg)
        chat = message.chat.id if not forward_to_channel else CUSTOM_CHANNEL_ID # Forward to channel if needed
        
        if "Text" == msg_type:
            try:
                if forward_to_channel:
                    await acc.send_message(chat, msg.text, entities=msg.entities)
                else:
                    await client.send_message(chat, msg.text, entities=msg.entities, reply_to_message_id=message.id)
            except MessageEmpty:
                 print("Ignoring MessageEmpty error.")

            except Exception as e:
                if not forward_to_channel:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
                return

        smsg = None if forward_to_channel else await client.send_message(message.chat.id, 'Downloading', reply_to_message_id=message.id)
        
        dosta = None if forward_to_channel else asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))
        try:
            file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
            if not forward_to_channel:
                os.remove(f'{message.id}downstatus.txt')
            
        except Exception as e:
            if not forward_to_channel:
                await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)  
            return
        
        upsta = None if forward_to_channel else asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

        if msg.caption:
            caption = msg.caption
        else:
            caption = None

        # Auto remove thumbnail if set in DB (or default to True if not set)
        user_data = database.find_one({'chat_id': message.from_user.id})
        remove_thumbnail = get(user_data, 'remove_thumbnail', True)

        if "Document" == msg_type:
            try:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except:
                ph_path = None
            
            try:
                if forward_to_channel:
                    await acc.send_document(chat, file, thumb=None if remove_thumbnail else ph_path, caption=caption) 
                else:
                    await client.send_document(chat, file, thumb=None if remove_thumbnail else ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            except MessageEmpty:
                 print("Ignoring MessageEmpty error.")
            except Exception as e:
                if not forward_to_channel:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            if ph_path != None and not remove_thumbnail: 
                os.remove(ph_path)
            

        elif "Video" == msg_type:
            try:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            except:
                ph_path = None
            
            try:
                if forward_to_channel:
                    await acc.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=None if remove_thumbnail else ph_path, caption=caption)
                else:
                    await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=None if remove_thumbnail else ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            except MessageEmpty:
                 print("Ignoring MessageEmpty error.")

            except Exception as e:
                if not forward_to_channel:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            if ph_path != None and not remove_thumbnail: 
                os.remove(ph_path)

        elif "Animation" == msg_type:
            try:
                if forward_to_channel:
                    await acc.send_animation(chat, file)
                else:
                    await client.send_animation(chat, file, reply_to_message_id=message.id)
            except MessageEmpty:
                 print("Ignoring MessageEmpty error.")

            except Exception as e:
                if not forward_to_channel:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            

        elif "Sticker" == msg_type:
            try:
                if forward_to_channel:
                    await acc.send_sticker(chat, file)
                else:
                    await client.send_sticker(chat, file, reply_to_message_id=message.id)
            except MessageEmpty:
                 print("Ignoring MessageEmpty error.")

            except Exception as e:
                if not forward_to_channel:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            

        elif "Voice" == msg_type:
            try:
                if forward_to_channel:
                    await acc.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities)
                else:
                    await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            except MessageEmpty:
                 print("Ignoring MessageEmpty error.")

            except Exception as e:
                if not forward_to_channel:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

        elif "Audio" == msg_type:
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            except:
                ph_path = None

            try:
                if forward_to_channel:
                    await acc.send_audio(chat, file, thumb=None if remove_thumbnail else ph_path, caption=caption)
                else:
                    await client.send_audio(chat, file, thumb=None if remove_thumbnail else ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])   
            except MessageEmpty:
                 print("Ignoring MessageEmpty error.")

            except Exception as e:
                if not forward_to_channel:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
            
            if ph_path != None and not remove_thumbnail: 
                os.remove(ph_path)

        elif "Photo" == msg_type:
            try:
                if forward_to_channel:
                    await acc.send_photo(chat, file, caption=caption)
                else:
                    await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id)
            except MessageEmpty:
                 print("Ignoring MessageEmpty error.")

            except Exception as e:
                if not forward_to_channel:
                    await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        
        if not forward_to_channel:
            if os.path.exists(f'{message.id}upstatus.txt'): 
                os.remove(f'{message.id}upstatus.txt')
                os.remove(file)
            await client.delete_messages(message.chat.id,[smsg.id])
    except Exception as e:
        print(f"An unexpected error occurred in handle_private: {e}")
        if not forward_to_channel:
            await client.send_message(message.chat.id, "An unexpected error occurred. Please try again later.")
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

# Start the bot and slowdown simulation
async def main():
    asyncio.create_task(simulate_slowdown())
    app = Client("my_bot",
        api_id=API_ID,
        api_hash=API_HASH,
        bot_token=BOT_TOKEN
    )

    await app.start()
    await pyrogram.idle()

if __name__ == "__main__":
    asyncio.run(main())
