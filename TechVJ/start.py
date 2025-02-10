# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import asyncio
import pyrogram
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied, MessageEmpty
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from config import API_ID, API_HASH, ERROR_MESSAGE
from database.db import db
from TechVJ.strings import HELP_TXT
import logging

# Configure logging (very important for debugging)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class batch_temp(object):
    IS_BATCH = {}


async def downstatus(client, statusfile, message, chat):
    try:
        while True:
            if os.path.exists(statusfile):
                break
            await asyncio.sleep(3)

        while os.path.exists(statusfile):
            with open(statusfile, "r") as downread:
                txt = downread.read()
            try:
                await client.edit_message_text(chat, message.id,
                                                f"**Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**")
                await asyncio.sleep(10)
            except FloodWait as e:
                await asyncio.sleep(e.value)  # Handle FloodWait
            except Exception as e:
                logging.error(f"Error editing download status: {e}") # Log the error
                await asyncio.sleep(5)
    except Exception as e:
         logging.error(f"Error in downstatus function: {e}")


# upload status
async def upstatus(client, statusfile, message, chat):
    try:
        while True:
            if os.path.exists(statusfile):
                break
            await asyncio.sleep(3)

        while os.path.exists(statusfile):
            with open(statusfile, "r") as upread:
                txt = upread.read()
            try:
                await client.edit_message_text(chat, message.id,
                                                f"**Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>** **{txt}**")
                await asyncio.sleep(10)
            except FloodWait as e:
                await asyncio.sleep(e.value)  # Handle FloodWait
            except Exception as e:
                logging.error(f"Error editing upload status: {e}")
                await asyncio.sleep(5)
    except Exception as e:
        logging.error(f"Error in upstatus function: {e}")



# progress writer
def progress(current, total, message, type):
    try:
        with open(f'{message.id}{type}status.txt', "w") as fileup:
            fileup.write(f"{current * 100 / total:.1f}%")
    except Exception as e:
        logging.error(f"Error writing progress: {e}")


# start command
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    try:
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
    except Exception as e:
        logging.error(f"Error in start command: {e}") # Log the error


# help command
@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    try:
        await client.send_message(
            chat_id=message.chat.id,
            text=f"{HELP_TXT}"
        )
    except Exception as e:
        logging.error(f"Error in help command: {e}")


# cancel command
@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    try:
        batch_temp.IS_BATCH[message.from_user.id] = True
        await client.send_message(
            chat_id=message.chat.id,
            text="**Batch Successfully Cancelled.**"
        )
    except Exception as e:
        logging.error(f"Error in cancel command: {e}")


@Client.on_message(filters.text & filters.private)
async def save(client: Client, message: Message):
    try:
        if "https://t.me/" in message.text:
            if batch_temp.IS_BATCH.get(message.from_user.id) == False:
                return await message.reply_text(
                    "**One Task Is Already Processing. Wait For Complete It. If You Want To Cancel This Task Then Use - /cancel**")
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
                except Exception as e:
                    logging.error(f"Error connecting to account: {e}")
                    batch_temp.IS_BATCH[message.from_user.id] = True
                    return await message.reply(
                        "**Your Login Session Expired. So /logout First Then Login Again By - /login**")

                # private
                if "https://t.me/c/" in message.text:
                    chatid = int("-100" + datas[4])
                    try:
                        await handle_private(client, acc, message, chatid, msgid)
                    except Exception as e:
                        logging.error(f"Error handling private message: {e}")
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}",
                                                      reply_to_message_id=message.id)

                # bot
                elif "https://t.me/b/" in message.text:
                    username = datas[4]
                    try:
                        await handle_private(client, acc, message, username, msgid)
                    except Exception as e:
                        logging.error(f"Error handling bot message: {e}")
                        if ERROR_MESSAGE == True:
                            await client.send_message(message.chat.id, f"Error: {e}",
                                                      reply_to_message_id=message.id)

                # public
                else:
                    username = datas[3]

                    try:
                        msg = await client.get_messages(username, msgid)
                    except UsernameNotOccupied:
                        await client.send_message(message.chat.id, "The username is not occupied by anyone",
                                                  reply_to_message_id=message.id)
                        return
                    except Exception as e:
                        logging.error(f"Error getting public message: {e}")
                        await client.send_message(message.chat.id, f"Error: {e}",
                                                      reply_to_message_id=message.id)
                        return

                    try:
                        await client.copy_message(message.chat.id, msg.chat.id, msg.id,
                                                  reply_to_message_id=message.id)
                    except Exception as e:
                        logging.error(f"Error copying public message: {e}")
                        try:
                            await handle_private(client, acc, message, username, msgid)
                        except Exception as e:
                            logging.error(f"Error handling private fallback: {e}")
                            if ERROR_MESSAGE == True:
                                await client.send_message(message.chat.id, f"Error: {e}",
                                                          reply_to_message_id=message.id)

                # wait time
                await asyncio.sleep(3)
            batch_temp.IS_BATCH[message.from_user.id] = True
    except Exception as e:
        logging.error(f"Error in save function: {e}")


# handle private
async def handle_private(client: Client, acc, message: Message, chatid: int, msgid: int):
    try:
        msg: Message = await acc.get_messages(chatid, msgid)
        if msg.empty:
            logging.warning(f"Message {msgid} in chat {chatid} is empty.")
            return
        msg_type = get_message_type(msg)
        if not msg_type:
            logging.warning(f"Message {msgid} in chat {chatid} has no detectable type.")
            return
        chat = message.chat.id
        if batch_temp.IS_BATCH.get(message.from_user.id):
            return
        if "Text" == msg_type:
            try:
                await client.send_message(chat, msg.text, entities=msg.entities,
                                          reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                return
            except Exception as e:
                logging.error(f"Error sending text message: {e}")
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}",
                                              reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
                return

        smsg = await client.send_message(message.chat.id, '**Downloading**', reply_to_message_id=message.id)
        asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg, chat))
        file = None  # Initialize file to None
        try:
            file = await acc.download_media(msg, progress=progress, progress_args=[message, "down"])

            if not file or os.path.getsize(file) == 0:
                logging.warning(f"Downloaded file is empty or invalid: {file}")
                if file:
                    try:
                        os.remove(file)
                    except:
                        pass
                await client.edit_message_text(chat, smsg.id, "**Download Failed: Empty file.**") #Notify User
                return

            try:
                os.remove(f'{message.id}downstatus.txt')
            except:
                pass

        except Exception as e:
            logging.error(f"Error downloading media: {e}")
            if ERROR_MESSAGE == True:
                await client.send_message(message.chat.id, f"Error: {e}",
                                          reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            try:
                await client.delete_messages(message.chat.id,[smsg.id])
            except:
                pass
            return


        if batch_temp.IS_BATCH.get(message.from_user.id):
            try:
                if file and os.path.exists(file): #Check if the file Exists before trying to delete it
                   os.remove(file)
                if os.path.exists(f'{message.id}downstatus.txt'):
                    os.remove(f'{message.id}downstatus.txt')
                await client.delete_messages(message.chat.id,[smsg.id])
            except:
                pass
            return

        asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg, chat))

        if msg.caption:
            caption = msg.caption
        else:
            caption = None
        if batch_temp.IS_BATCH.get(message.from_user.id):
             try:
                if file and os.path.exists(file): #Check if the file Exists before trying to delete it
                   os.remove(file)
                if os.path.exists(f'{message.id}upstatus.txt'):
                    os.remove(f'{message.id}upstatus.txt')
                await client.delete_messages(message.chat.id,[smsg.id])
             except:
                pass
             return

        if "Document" == msg_type:
            try:
                ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
            except:
                ph_path = None

            try:
                await client.send_document(chat, file, thumb=ph_path, caption=caption,
                                            reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML,
                                            progress=progress, progress_args=[message, "up"])
            except Exception as e:
                logging.error(f"Error sending document: {e}")
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}",
                                              reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if ph_path != None:
              try:
                os.remove(ph_path)
              except:
                pass


        elif "Video" == msg_type:
            try:
                ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
            except:
                ph_path = None

            try:
                await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width,
                                         height=msg.video.height, thumb=ph_path, caption=caption,
                                         reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML,
                                         progress=progress, progress_args=[message, "up"])
            except Exception as e:
                logging.error(f"Error sending video: {e}")
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}",
                                              reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)
            if ph_path != None:
                try:
                   os.remove(ph_path)
                except:
                    pass

        elif "Animation" == msg_type:
            try:
                await client.send_animation(chat, file, reply_to_message_id=message.id,
                                             parse_mode=enums.ParseMode.HTML)
            except Exception as e:
                logging.error(f"Error sending animation: {e}")
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}",
                                              reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        elif "Sticker" == msg_type:
            try:
                await client.send_sticker(chat, file, reply_to_message_id=message.id,
                                           parse_mode=enums.ParseMode.HTML)
            except Exception as e:
                logging.error(f"Error sending sticker: {e}")
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}",
                                              reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        elif "Voice" == msg_type:
            try:
                await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities,
                                         reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML,
                                         progress=progress, progress_args=[message, "up"])
            except Exception as e:
                logging.error(f"Error sending voice: {e}")
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}",
                                              reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        elif "Audio" == msg_type:
            try:
                ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
            except:
                ph_path = None

            try:
                await client.send_audio(chat, file, thumb=ph_path, caption=caption,
                                         reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML,
                                         progress=progress, progress_args=[message, "up"])
            except Exception as e:
                logging.error(f"Error sending audio: {e}")
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}",
                                              reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

            if ph_path != None:
                try:
                   os.remove(ph_path)
                except:
                    pass


        elif "Photo" == msg_type:
            try:
                await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id,
                                          parse_mode=enums.ParseMode.HTML)
            except Exception as e:
                logging.error(f"Error sending photo: {e}")
                if ERROR_MESSAGE == True:
                    await client.send_message(message.chat.id, f"Error: {e}",
                                              reply_to_message_id=message.id, parse_mode=enums.ParseMode.HTML)

        try:
            if os.path.exists(f'{message.id}upstatus.txt'):
                os.remove(f'{message.id}upstatus.txt')
            if file and os.path.exists(file):
                os.remove(file)
        except:
            pass
        try:
           await client.delete_messages(message.chat.id,[smsg.id])
        except:
            pass

    except Exception as e:
        logging.error(f"Error in handle_private function: {e}")


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