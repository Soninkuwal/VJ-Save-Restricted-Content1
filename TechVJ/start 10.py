import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE, FORWARD_CHANNEL_ID
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

# set forward command
@Client.on_message(filters.command(["setforward"]))
async def set_forward_channel(client: Client, message: Message):
     if len(message.command) != 2:
         await message.reply_text(
             "Please provide the channel id."
         )
         return
     try:
         channel_id = int(message.command[1])
     except ValueError:
        await message.reply_text("Invalid channel ID. Please provide a valid integer.")
        return
     await db.set_forward_channel(message.from_user.id, channel_id)
     await message.reply_text(f"Forward channel set to: {channel_id}")


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
    user_forward_channel_id = await db.get_forward_channel(message.from_user.id)
    if user_forward_channel_id is None and FORWARD_CHANNEL_ID == 0:
        await client.send_message(
            chat_id=message.chat.id,
            text="**Forward Channel Is Not Set Yet. Use /setforward <channel_id>**"
        )
        return

    forward_channel_id = user_forward_channel_id if user_forward_channel_id else FORWARD_CHANNEL_ID

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


# add word replacement
@Client.on_message(filters.command(["addreplace"]))
async def add_replace(client: Client, message: Message):
    if len(message.command) != 3:
        await message.reply_text("Please provide both the old and new words.")
        return

    old_word = message.command[1]
    new_word = message.command[2]
    await db.add_replace_word(old_word, new_word)
    await message.reply_text(f"Word replacement added: '{old_word}' -> '{new_word}'")

# remove word replacement
@Client.on_message(filters.command(["removerep"]))
async def remove_replace(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Please provide the old word to remove.")
        return

    old_word = message.command[1]
    await db.remove_replace_word(old_word)
    await message.reply_text(f"Word replacement removed: '{old_word}'")


# add delete word
@Client.on_message(filters.command(["adddelete"]))
async def add_delete(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Please provide the word to delete.")
        return

    word = message.command[1]
    await db.add_delete_word(word)
    await message.reply_text(f"Delete word added: '{word}'")


# remove delete word
@Client.on_message(filters.command(["removedel"]))
async def remove_delete(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Please provide the word to remove from delete list.")
        return

    word = message.command[1]
    await db.remove_delete_word(word)
    await message.reply_text(f"Delete word removed: '{word}'")

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
    if batch_temp.IS_BATCH.get(message.from_user.id): return

    replace_words = await db.get_replace_words()
    delete_words = await db.get_delete_words()

    if "Text" == msg_type:
        if msg.text:
            text = msg.text

            for old_word, new_word in replace_words:
              text = re.sub(re.escape(old_word), new_word, text, flags=re.IGNORECASE)

            for word in delete_words:
              text = re.sub(re.escape(word), "", text, flags=re.IGNORECASE)
              
            try:
                sent_msg = await client.send_message(chat, text, entities=msg.entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            except Exception as e:
                if ERROR_MESSAGE:
                   await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                   return

            user_forward_channel_id = await db.get_forward_channel(message.from_user.id)

            forward_channel_id = user_forward_channel_id if user_forward_channel_id else FORWARD_CHANNEL_ID
            # Forward to the custom channel
            try:
              await client.forward_messages(forward_channel_id, message.chat.id, sent_msg.id)
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

    if caption:
       for old_word, new_word in replace_words:
         caption = re.sub(re.escape(old_word), new_word, caption, flags=re.IGNORECASE)

       for word in delete_words:
         caption = re.sub(re.escape(word), "", caption, flags=re.IGNORECASE)

    if batch_temp.IS_BATCH.get(message.from_user.id): return

    user_forward_channel_id = await db.get_forward_channel(message.from_user.id)

    forward_channel_id = user_forward_channel_id if user_forward_channel_id else FORWARD_CHANNEL_ID
    
    if "Document" == msg_type:
        ph_path = None
        if msg.document.thumbs:
           try:
              ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
           except Exception as e:
              if ERROR_MESSAGE:
                 await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                 ph_path = None

        try:
            sent_msg = await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message,"up"])
            # Forward to the custom channel
            try:
              await client.forward_messages(forward_channel_id, message.chat.id, sent_msg.id)
            except Exception as e:
                if ERROR_MESSAGE:
                   await client.send_message(message.chat.id, f"Error: while Forwarding Document: {e}", reply_to_message_id=message.id)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Document Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None:
           os.remove(ph_path)


    elif "Video" == msg_type:
        ph_path = None
        if msg.video.thumbs:
          try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
          except Exception as e:
              if ERROR_MESSAGE:
                 await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                 ph_path = None
        try:
            sent_msg = await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
            # Forward to the custom channel
            try:
              await client.forward_messages(forward_channel_id, message.chat.id, sent_msg.id)
            except Exception as e:
                if ERROR_MESSAGE:
                  await client.send_message(message.chat.id, f"Error: while Forwarding Video: {e}", reply_to_message_id=message.id)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Video Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
        if ph_path != None:
           os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            sent_msg = await client.send_animation(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            # Forward to the custom channel
            try:
               await client.forward_messages(forward_channel_id, message.chat.id, sent_msg.id)
            except Exception as e:
                if ERROR_MESSAGE:
                   await client.send_message(message.chat.id, f"Error: while Forwarding Animation: {e}", reply_to_message_id=message.id)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Animation Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Sticker" == msg_type:
        try:
            sent_msg = await client.send_sticker(chat, file, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            # Forward to the custom channel
            try:
                await client.forward_messages(forward_channel_id, message.chat.id, sent_msg.id)
            except Exception as e:
                if ERROR_MESSAGE:
                   await client.send_message(message.chat.id, f"Error: while Forwarding Sticker: {e}", reply_to_message_id=message.id)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Sticker Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Voice" == msg_type:
        try:
            sent_msg = await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
             # Forward to the custom channel
            try:
              await client.forward_messages(forward_channel_id, message.chat.id, sent_msg.id)
            except Exception as e:
                if ERROR_MESSAGE:
                   await client.send_message(message.chat.id, f"Error: while Forwarding Voice: {e}", reply_to_message_id=message.id)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Voice Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    elif "Audio" == msg_type:
        ph_path = None
        if msg.audio.thumbs:
           try:
              ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
           except Exception as e:
               if ERROR_MESSAGE:
                   await client.send_message(message.chat.id, f"Error: Thumbnail Download Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                   ph_path = None

        try:
            sent_msg= await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML, progress=progress, progress_args=[message, "up"])
              # Forward to the custom channel
            try:
               await client.forward_messages(forward_channel_id, message.chat.id, sent_msg.id)
            except Exception as e:
               if ERROR_MESSAGE:
                 await client.send_message(message.chat.id, f"Error: while Forwarding Audio: {e}", reply_to_message_id=message.id)
        except Exception as e:
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: Send Audio Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        if ph_path != None:
            os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            sent_msg = await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            # Forward to the custom channel
            try:
               await client.forward_messages(forward_channel_id, message.chat.id, sent_msg.id)
            except Exception as e:
                if ERROR_MESSAGE:
                    await client.send_message(message.chat.id, f"Error: while Forwarding Photo: {e}", reply_to_message_id=message.id)
        except Exception as e:
            if ERROR_MESSAGE == True:
               await client.send_message(message.chat.id, f"Error: Send Photo Error: {e}", reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

    if os.path.exists(f'{message.id}upstatus.txt'):
        os.remove(f'{message.id}upstatus.txt')

    #Auto Delete After 2min
    await asyncio.sleep(120)
    try:
        await client.delete_messages(message.chat.id, [smsg.id, sent_msg.id])
    except:
       pass

    os.remove(file)

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