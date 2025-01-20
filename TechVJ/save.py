# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import asyncio
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, CallbackQuery
import time
import os
import threading
import json
from config import API_ID, API_HASH
from database.db import database
from TechVJ.strings import strings, HELP_TXT

# --- Helper Functions ---

def get(obj, key, default=None):
    try:
        return obj[key]
    except:
        return default

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
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

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
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)

# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")

# --- Database and Settings Management ---

async def get_user_settings(user_id):
    user_data = database.find_one({'chat_id': user_id})
    if not user_data:
        user_data = {
            'chat_id': user_id,
            'logged_in': False,
            'session': None,
            'default_thumb': None,
            'custom_caption': None,
            'delete_words': [],
            'replace_words': {},
            'forward_as_copy': True,
            'empty_msg_error': False  # Option to handle empty message errors
        }
        database.insert_one(user_data)
    return user_data

async def update_user_settings(user_id, settings_dict):
    database.update_one({'chat_id': user_id}, {'$set': settings_dict})

# --- Bot Commands ---

# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url = "http://t.me/Sonickuwalupdatebot")
    ],[
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='http://t.me/Sonickuwalupdatebot'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ],
    [
        InlineKeyboardButton('⚙️ Settings', callback_data='settings')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(message.chat.id, f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>", reply_markup=reply_markup, reply_to_message_id=message.id)
    return

# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

# --- Settings Command and Callbacks ---

@Client.on_message(filters.command("settings"))
async def settings_command(client: Client, message: Message):
    await settings_markup(client, message.chat.id, message.id)

async def settings_markup(client: Client, chat_id: int, message_id: int):
    user_settings = await get_user_settings(chat_id)
    buttons = [
        [InlineKeyboardButton("Remove Default Thumbnail", callback_data="remove_thumb")],
        [InlineKeyboardButton("Set Custom Thumbnail", callback_data="set_thumb")],
        [InlineKeyboardButton("Set Custom Caption", callback_data="set_caption")],
        [InlineKeyboardButton("Remove Custom Caption", callback_data="remove_caption")],
        [InlineKeyboardButton("Add Delete Words", callback_data="add_delete_words")],
        [InlineKeyboardButton("Remove Delete Words", callback_data="remove_delete_words")],
        [InlineKeyboardButton("Add Replace Words", callback_data="add_replace_words")],
        [InlineKeyboardButton("Remove Replace Words", callback_data="remove_replace_words")],
        [InlineKeyboardButton(f"Forward as Copy: {'On' if user_settings['forward_as_copy'] else 'Off'}", callback_data="toggle_forward_copy")],
        [InlineKeyboardButton(f"Empty Message Error Handling: {'On' if user_settings['empty_msg_error'] else 'Off'}", callback_data="toggle_empty_msg_error")],
        [InlineKeyboardButton("Close", callback_data="close_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    try:
        await client.edit_message_text(chat_id, message_id, "⚙️ **Settings:**", reply_markup=reply_markup)
    except:
        await client.send_message(chat_id, "⚙️ **Settings:**", reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("settings"))
async def settings_callback(client: Client, query: CallbackQuery):
    await settings_markup(client, query.message.chat.id, query.message.id)
    await query.answer()

@Client.on_callback_query(filters.regex("remove_thumb"))
async def remove_thumb_callback(client: Client, query: CallbackQuery):
    await update_user_settings(query.message.chat.id, {'default_thumb': None})
    await query.answer("Default thumbnail removed!")
    await settings_markup(client, query.message.chat.id, query.message.id)

@Client.on_callback_query(filters.regex("set_thumb"))
async def set_thumb_callback(client: Client, query: CallbackQuery):
    await query.answer()
    msg = await client.ask(query.message.chat.id, "Send me the new thumbnail")
    if msg.media:
        # To do : save the thumb
        await update_user_settings(query.message.chat.id, {'default_thumb': "To implement"})
        await query.message.reply("Custom thumbnail set!")
        await settings_markup(client, query.message.chat.id, query.message.id)
    else:
        await query.message.reply("Invalid media")
        await settings_markup(client, query.message.chat.id, query.message.id)

# To do : Implement the others callbacks (set_caption, remove_caption, add_delete_words, etc.)
# ...

@Client.on_callback_query(filters.regex("toggle_forward_copy"))
async def toggle_forward_copy_callback(client: Client, query: CallbackQuery):
    user_settings = await get_user_settings(query.message.chat.id)
    new_setting = not user_settings['forward_as_copy']
    await update_user_settings(query.message.chat.id, {'forward_as_copy': new_setting})
    await query.answer(f"Forward as copy set to {'On' if new_setting else 'Off'}")
    await settings_markup(client, query.message.chat.id, query.message.id)

@Client.on_callback_query(filters.regex("toggle_empty_msg_error"))
async def toggle_empty_msg_error_callback(client: Client, query: CallbackQuery):
    user_settings = await get_user_settings(query.message.chat.id)
    new_setting = not user_settings['empty_msg_error']
    await update_user_settings(query.message.chat.id, {'empty_msg_error': new_setting})
    await query.answer(f"Empty Message Error Handling set to {'On' if new_setting else 'Off'}")
    await settings_markup(client, query.message.chat.id, query.message.id)

@Client.on_callback_query(filters.regex("close_settings"))
async def close_settings_callback(client: Client, query: CallbackQuery):
    await query.message.delete()
    await query.answer()

# --- Main Logic for Saving Content ---

@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    if "https://t.me/" in message.text:
        user_settings = await get_user_settings(message.chat.id)
        
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
                if not get(user_settings, 'logged_in', False) or user_settings['session'] is None:
                    await client.send_message(message.chat.id, strings['need_login'])
                    return
                acc = Client("saverestricted", session_string=user_settings['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                chatid = int("-100" + datas[4])
                await handle_private(client, acc, message, chatid, msgid, user_settings)
    
            # bot
            elif "https://t.me/b/" in message.text:
                if not get(user_settings, 'logged_in', False) or user_settings['session'] is None:
                    await client.send_message(message.chat.id, strings['need_login'])
                    return
                acc = Client("saverestricted", session_string=user_settings['session'], api_hash=API_HASH, api_id=API_ID)
                await acc.connect()
                username = datas[4]
                try:
                    await handle_private(client, acc, message, username, msgid, user_settings)
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
                    if user_settings['forward_as_copy']:
                        await client.copy_message(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                    else:
                        await client.forward_messages(message.chat.id, msg.chat.id, msg.id, reply_to_message_id=message.id)
                except MessageEmpty:
                    if user_settings['empty_msg_error']:
                        await client.send_message(message.chat.id, "Error: The message is empty.", reply_to_message_id=message.id)
                except Exception as e:
                    try:    
                        if not get(user_settings, 'logged_in', False) or user_settings['session'] is None:
                            await client.send_message(message.chat.id, strings['need_login'])
                            return
                        acc = Client("saverestricted", session_string=user_settings['session'], api_hash=API_HASH, api_id=API_ID)
                        await acc.connect()
                        await handle_private(client, acc, message, username, msgid, user_settings)
                        
                    except Exception as e:
                        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

            # wait time
            await asyncio.sleep(3)

# --- Handle Private Function with Customization ---

async def handle_private(client: Client, acc: Client, message: Message, chatid: int, msgid: int, user_settings):
    try:
        msg: Message = await acc.get_messages(chatid, msgid)
    except MessageEmpty:
        if user_settings['empty_msg_error']:
            await client.send_message(message.chat.id, "Error: The message is empty.", reply_to_message_id=message.id)
        return

    msg_type = get_message_type(msg)
    chat = message.chat.id

    # --- Text Handling ---
    if "Text" == msg_type:
        try:
            text_content = apply_caption_settings(msg.text, user_settings)
            if user_settings['forward_as_copy']:
                await client.send_message(chat, text_content, entities=msg.entities, reply_to_message_id=message.id)
            else:
                await client.forward_messages(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)
        except MessageEmpty:
            if user_settings['empty_msg_error']:
                await client.send_message(message.chat.id, "Error: The message is empty.", reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        return

    # --- Media Handling ---
    smsg = await client.send_message(message.chat.id, 'Downloading', reply_to_message_id=message.id)
    dosta = asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        return

    upsta = asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

    caption = apply_caption_settings(msg.caption, user_settings) if msg.caption else None

    # --- Send Media with Customizations ---
    try:
        if "Document" == msg_type:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id) if msg.document.thumbs else None
            if user_settings['forward_as_copy']:
                await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            else:
                await client.forward_messages(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)
            if ph_path:
                os.remove(ph_path)

        elif "Video" == msg_type:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id) if msg.video.thumbs else None
            if user_settings['forward_as_copy']:
                await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            else:
                await client.forward_messages(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)
            if ph_path:
                os.remove(ph_path)

        elif "Animation" == msg_type:
            if user_settings['forward_as_copy']:
                await client.send_animation(chat, file, reply_to_message_id=message.id)
            else:
                await client.forward_messages(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)

        elif "Sticker" == msg_type:
            if user_settings['forward_as_copy']:
                await client.send_sticker(chat, file, reply_to_message_id=message.id)
            else:
                await client.forward_messages(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)

        elif "Voice" == msg_type:
            if user_settings['forward_as_copy']:
                await client.send_voice(chat, file, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            else:
                await client.forward_messages(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)
            
        elif "Audio" == msg_type:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id) if msg.audio.thumbs else None
            if user_settings['forward_as_copy']:
                await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
            else:
                await client.forward_messages(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)
            if ph_path:
                os.remove(ph_path)

        elif "Photo" == msg_type:
            if user_settings['forward_as_copy']:
                await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id)
            else:
                await client.forward_messages(chat, msg.chat.id, msg.id, reply_to_message_id=message.id)

    except MessageEmpty:
        if user_settings['empty_msg_error']:
            await client.send_message(message.chat.id, "Error: The message is empty.", reply_to_message_id=message.id)
    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    finally:
        if os.path.exists(f'{message.id}upstatus.txt'):
            os.remove(f'{message.id}upstatus.txt')
        if os.path.exists(file):
            os.remove(file)
        await client.delete_messages(message.chat.id, [smsg.id])

# --- Helper Function for Caption Settings ---

def apply_caption_settings(text, user_settings):
    if user_settings['custom_caption']:
        text = user_settings['custom_caption']
    
    if user_settings['delete_words']:
        for word in user_settings['delete_words']:
            text = text.replace(word, "")

    if user_settings['replace_words']:
        for original, replacement in user_settings['replace_words'].items():
            text = text.replace(original, replacement)

    return text

# --- Helper Function to Get Message Type ---
# (This function remains unchanged)
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
