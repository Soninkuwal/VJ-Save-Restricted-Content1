
import asyncio
import pyrogram
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant, InviteHashExpired, UsernameNotOccupied
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import time
import os
import threading
import json
import ffmpeg
import yt_dlp
from config import API_ID, API_HASH
from database.db import database
from TechVJ.strings import strings, HELP_TXT

# --- CONFIGURATION FILE ---
CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "channel_id": None,
    "remove_thumbnail": True,
    "allow_empty_message": False,
    "custom_text_replace": {},
    "custom_text_delete": [],
    "custom_caption": ""
}


def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_CONFIG


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)


config = load_config()

# --- HELPER FUNCTIONS ---
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
            await client.edit_message_text(message.chat.id, message.id,
                                           f"Downloaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
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
            await client.edit_message_text(message.chat.id, message.id,
                                           f"Uploaded : <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a> {txt}")
            await asyncio.sleep(10)
        except:
            await asyncio.sleep(5)


# progress writer
def progress(current, total, message, type):
    with open(f'{message.id}{type}status.txt', "w") as fileup:
        fileup.write(f"{current * 100 / total:.1f}%")


async def auto_speed_control(client: Client, message):
    """Simulates speed management."""
    await asyncio.sleep(1)  # Fast speed
    await asyncio.sleep(60 * 2)  # Slow speed after 1-2 hours
    

async def remove_thumbnail(message):
    """Removes thumbnail from message if present."""
    if message.photo or message.video or message.document:
        if message.photo:
            if message.photo.file_id:
               return None 
        if message.video:
           if message.video.file_id:
              return None 
        if message.document:
            if message.document.file_id:
                return None
    return None


def replace_custom_text(text, config):
    """Replaces configured text in message."""
    if not isinstance(text, str):
        return text
    for old, new in config.get("custom_text_replace", {}).items():
        text = text.replace(old, new)
    return text


def delete_custom_text(text, config):
    """Deletes configured text in message."""
    if not isinstance(text, str):
        return text
    for word in config.get("custom_text_delete", []):
        text = text.replace(word, "")
    return text


def handle_caption(text, config):
    """Adds custom caption to the message."""
    if not isinstance(text, str):
        text = ""
    return  config.get("custom_caption", "") + text


async def forward_to_channel(client: Client, message: Message, config):
    """Forwards various media types with download and upload progress."""
    channel_id = config.get("channel_id")
    if not channel_id:
        await message.reply("Error: Channel ID not configured. Use /settings.")
        return

    if message.text:
        if not config["allow_empty_message"] and not message.text.strip():
            await message.reply("Error: Message is empty and empty messages are not allowed.")
            return
        text = message.text
        text = replace_custom_text(text, config)
        text = delete_custom_text(text, config)
        text = handle_caption(text,config)
        
        try:
             await client.send_message(channel_id, text)
        except Exception as e:
            await message.reply(f"Error: {e}")
        return
    
    msg = message
    chat = channel_id
    acc = client
    msg_type = get_message_type(msg)

    smsg = await client.send_message(msg.chat.id, "Processing...", reply_to_message_id=message.id)
    dosta = asyncio.create_task(downstatus(client, f'{message.id}downstatus.txt', smsg))
    try:
        file = await acc.download_media(msg, progress=progress, progress_args=[message,"down"])
        os.remove(f'{message.id}downstatus.txt')
        
    except Exception as e:
        await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)  
        return
    
    upsta = asyncio.create_task(upstatus(client, f'{message.id}upstatus.txt', smsg))

    if msg.caption:
        caption = msg.caption
    else:
        caption = None
    
    caption = replace_custom_text(caption, config)
    caption = delete_custom_text(caption, config)
    caption = handle_caption(caption,config)
    
    
    if "Document" == msg_type:
        try:
            ph_path = await acc.download_media(msg.document.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_document(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        if ph_path != None: os.remove(ph_path)
        

    elif "Video" == msg_type:
        try:
            ph_path = await acc.download_media(msg.video.thumbs[0].file_id)
        except:
            ph_path = None
        
        try:
            await client.send_video(chat, file, duration=msg.video.duration, width=msg.video.width, height=msg.video.height, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        if ph_path != None: os.remove(ph_path)

    elif "Animation" == msg_type:
        try:
            await client.send_animation(chat, file, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        

    elif "Sticker" == msg_type:
        try:
            await client.send_sticker(chat, file, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        

    elif "Voice" == msg_type:
        try:
            await client.send_voice(chat, file, caption=caption, caption_entities=msg.caption_entities, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)

    elif "Audio" == msg_type:
        try:
            ph_path = await acc.download_media(msg.audio.thumbs[0].file_id)
        except:
            ph_path = None

        try:
            await client.send_audio(chat, file, thumb=ph_path, caption=caption, reply_to_message_id=message.id, progress=progress, progress_args=[message,"up"])   
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
        
        if ph_path != None: os.remove(ph_path)

    elif "Photo" == msg_type:
        try:
            await client.send_photo(chat, file, caption=caption, reply_to_message_id=message.id)
        except Exception as e:
            await client.send_message(message.chat.id, f"Error: {e}", reply_to_message_id=message.id)
    
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


async def download_media(client, message):
    """Downloads media from a Telegram message and returns the file path."""
    file_path = None
    if message.video:
      file_path = await client.download_media(message.video)
    elif message.document:
      file_path = await client.download_media(message.document)
    elif message.audio:
      file_path = await client.download_media(message.audio)
    elif message.voice:
      file_path = await client.download_media(message.voice)
    elif message.photo:
        file_path = await client.download_media(message.photo)
    elif message.animation:
      file_path = await client.download_media(message.animation)
    return file_path

async def convert_video_to_mp4(input_path):
    """Converts video to MP4 format using FFmpeg."""
    output_path = os.path.splitext(input_path)[0] + ".mp4"
    try:
        ffmpeg.input(input_path).output(output_path, vcodec="libx264", acodec="aac").overwrite_output().run(quiet=True)
        return output_path
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
        return None

async def add_multiple_audio_tracks(input_path, audio_paths):
    """Adds multiple audio tracks to a video using FFmpeg."""
    input_streams = [ffmpeg.input(input_path)]
    for i, audio_path in enumerate(audio_paths):
        input_streams.append(ffmpeg.input(audio_path))
    
    output_path = os.path.splitext(input_path)[0] + "_audio.mp4"
    
    try:
        
        (
            ffmpeg
            .concat(*input_streams, v=1, a=1)
            .output(output_path, vcodec="copy", acodec="aac", map="0:v", map_audio="1:a", strict="-2")
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
        return None

async def add_subtitles_to_video(input_path, subtitle_path):
    """Adds subtitles to a video using FFmpeg."""
    output_path = os.path.splitext(input_path)[0] + "_subtitled.mp4"
    try:
        ffmpeg.input(input_path).output(output_path, vf=f"subtitles={subtitle_path}").overwrite_output().run(quiet=True)
        return output_path
    except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
        return None

async def add_watermark_to_video(input_path, watermark_path, position="se", margin="10:10"):
    """Adds a watermark to a video using FFmpeg."""
    output_path = os.path.splitext(input_path)[0] + "_watermarked.mp4"
    try:
        ffmpeg.input(input_path).input(watermark_path).output(output_path,
             filter_complex=f"[1:v]scale=60:60[wm];[0:v][wm]overlay={position}:{margin}"
             ).overwrite_output().run(quiet=True)
        return output_path
    except ffmpeg.Error as e:
      print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
      return None

async def merge_videos(video_paths):
  """Merges multiple videos using FFmpeg."""
  if not video_paths:
        return None
  output_path = "merged_video.mp4"
  input_streams = [ffmpeg.input(video) for video in video_paths]
  try:
     (
            ffmpeg
            .concat(*input_streams, v=1, a=0)
            .output(output_path, vcodec="copy")
            .overwrite_output()
            .run(quiet=True)
        )
     return output_path
  except ffmpeg.Error as e:
        print(f"FFmpeg Error: {e.stderr.decode('utf8')}")
        return None

async def upload_media_to_telegram(client, message, file_path, caption_text=""):
    """Uploads media to Telegram."""
    try:
        if file_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.m3u8')):
           await client.send_video(message.chat.id, file_path, caption=caption_text)
        elif file_path.lower().endswith(('.mp3', '.aac', '.wav', '.ogg')):
           await client.send_audio(message.chat.id, file_path, caption=caption_text)
        elif file_path.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
            await client.send_photo(message.chat.id, file_path, caption=caption_text)
        else:
           await client.send_document(message.chat.id, file_path, caption=caption_text)
    except Exception as e:
        await message.reply(f"Error uploading file: {e}")

async def download_social_media_video(url):
    """Downloads a video from social media using yt-dlp."""
    try:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info_dict)
            return file_path
    except Exception as e:
        print(f"yt-dlp Error: {e}")
        return None

# --- COMMAND HANDLERS ---
@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    buttons = [[
        InlineKeyboardButton("❣️ Developer", url="http://t.me/Sonickuwalupdatebot")
    ], [
        InlineKeyboardButton('🔍 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ', url='http://t.me/Sonickuwalupdatebot'),
        InlineKeyboardButton('🤖 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ', url='https://t.me/SONICKUWALUPDATEKANHA')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await client.send_message(message.chat.id, f"<b>👋 Hi {message.from_user.mention}, I am Save Restricted Content Bot, I can send you restricted content by its post link.\n\nFor downloading restricted content /login first.\n\nKnow how to use bot by - /help \n\n🤩 join telegram channel <a href=https://t.me/SONICKUWALUPDATEKANHA>JOIN UPDATED CHANNEL</a>\n\n BOT ANY ERROR CONTET :- Here it is: @Sonickuwalupdatebot. What do you want to do with the bot?</b>",
                            reply_markup=reply_markup, reply_to_message_id=message.id)
    return


@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await client.send_message(message.chat.id, f"{HELP_TXT}")

@Client.on_message(filters.command(["settings"]))
async def settings_command(client: Client, message: Message):
    """Handles bot settings."""
    global config
    buttons = [
        [InlineKeyboardButton("Set Channel ID", callback_data="set_channel_id")],
        [InlineKeyboardButton("Toggle Auto Thumbnail Removal", callback_data="toggle_thumbnail")],
         [InlineKeyboardButton("Toggle Allow Empty Message", callback_data="toggle_empty_message")],
        [InlineKeyboardButton("Set Custom Text Replace", callback_data="set_text_replace")],
        [InlineKeyboardButton("Set Custom Text Delete", callback_data="set_text_delete")],
        [InlineKeyboardButton("Set Custom Caption", callback_data="set_custom_caption")],
          [InlineKeyboardButton("Video to MP4", callback_data="convertmp4")],
        [InlineKeyboardButton("Add Multiple Audio", callback_data="add_audio")],
        [InlineKeyboardButton("Add Subtitles", callback_data="add_subtitles")],
        [InlineKeyboardButton("Add Watermark", callback_data="add_watermark")],
        [InlineKeyboardButton("Merge Videos", callback_data="merge_videos")],
        [InlineKeyboardButton("Download from URL", callback_data="download_url")],
        [InlineKeyboardButton("Show Current Settings", callback_data="show_settings")],
        [InlineKeyboardButton("Cancel", callback_data="cancel_settings")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply("Bot Settings:", reply_markup=reply_markup)

@Client.on_callback_query(filters.regex("^set_channel_id$"))
async def set_channel_id_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(callback_query.message.chat.id, "Please enter the channel ID:",
        reply_to_message_id = callback_query.message.id)
    await client.register_next_step_handler(callback_query.message, set_channel_id_step)

async def set_channel_id_step(client: Client, message: Message):
    global config
    try:
        channel_id = int(message.text)
        config["channel_id"] = channel_id
        save_config(config)
        await message.reply(f"Channel ID set to: {channel_id}")
    except ValueError:
        await message.reply("Invalid channel ID format, please enter numbers only")

@Client.on_callback_query(filters.regex("^toggle_thumbnail$"))
async def toggle_thumbnail_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    global config
    config["remove_thumbnail"] = not config.get("remove_thumbnail", False)
    save_config(config)
    await callback_query.answer(f"Auto Thumbnail Removal: {'Enabled' if config['remove_thumbnail'] else 'Disabled'}")

@Client.on_callback_query(filters.regex("^toggle_empty_message$"))
async def toggle_empty_message_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    global config
    config["allow_empty_message"] = not config.get("allow_empty_message", False)
    save_config(config)
    await callback_query.answer(f"Allow Empty Message: {'Enabled' if config['allow_empty_message'] else 'Disabled'}")

@Client.on_callback_query(filters.regex("^set_text_replace$"))
async def set_text_replace_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(callback_query.message.chat.id, "Please enter custom text replace in json format, example: `{'old_text1':'new_text1','old_text2':'new_text2'}`:",
        reply_to_message_id = callback_query.message.id)
    await client.register_next_step_handler(callback_query.message, set_text_replace_step)

async def set_text_replace_step(client: Client, message: Message):
    global config
    try:
        custom_text = json.loads(message.text)
        config["custom_text_replace"] = custom_text
        save_config(config)
        await message.reply(f"Custom text replace set to: {custom_text}")
    except json.JSONDecodeError:
        await message.reply("Invalid JSON format for custom replace.")

@Client.on_callback_query(filters.regex("^set_text_delete$"))
async def set_text_delete_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(callback_query.message.chat.id, "Please enter custom text delete, example: `['word1','word2']`:",
        reply_to_message_id = callback_query.message.id)
    await client.register_next_step_handler(callback_query.message, set_text_delete_step)

async def set_text_delete_step(client: Client, message: Message):
    global config
    try:
        custom_text = json.loads(message.text)
        config["custom_text_delete"] = custom_text
        save_config(config)
        await message.reply(f"Custom text delete set to: {custom_text}")
    except json.JSONDecodeError:
       await message.reply("Invalid JSON format for custom delete.")


@Client.on_callback_query(filters.regex("^set_custom_caption$"))
async def set_custom_caption_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(callback_query.message.chat.id, "Please enter the custom caption text:",
        reply_to_message_id = callback_query.message.id)
    await client.register_next_step_handler(callback_query.message, set_custom_caption_step)

async def set_custom_caption_step(client: Client, message: Message):
    global config
    config["custom_caption"] = message.text
    save_config(config)
    await message.reply(f"Custom caption set to: {config['custom_caption']}")


@Client.on_callback_query(filters.regex("^show_settings$"))
async def show_settings_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    global config
    settings_text = f"Current Settings:\n"
    for key, value in config.items():
        settings_text += f"  {key}: {value}\n"
    await callback_query.message.reply(settings_text)


@Client.on_callback_query(filters.regex("^cancel_settings$"))
async def cancel_settings_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await callback_query.message.delete()


@Client.on_callback_query(filters.regex("^convertmp4$"))
async def convert_mp4_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(callback_query.message.chat.id, "Reply to the video you want to convert to MP4.")
    await client.register_next_step_handler(callback_query.message, convert_mp4_handler)


@Client.on_callback_query(filters.regex("^add_audio$"))
async def add_audio_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(callback_query.message.chat.id, "Reply to the video and provide audio message IDs separated by spaces.")
    await client.register_next_step_handler(callback_query.message, add_audio_handler)

@Client.on_callback_query(filters.regex("^add_subtitles$"))
async def add_subtitles_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
  await client.send_message(callback_query.message.chat.id, "Reply to the video and provide subtitle message ID.")
  await client.register_next_step_handler(callback_query.message, add_subtitles_handler)

@Client.on_callback_query(filters.regex("^add_watermark$"))
async def add_watermark_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(callback_query.message.chat.id, "Reply to the video and provide watermark message ID (photo/video).")
    await client.register_next_step_handler(callback_query.message, add_watermark_handler)

@Client.on_callback_query(filters.regex("^merge_videos$"))
async def merge_videos_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
  await client.send_message(callback_query.message.chat.id, "Provide the message IDs of the videos to merge, separated by spaces.")
  await client.register_next_step_handler(callback_query.message, merge_videos_handler)


@Client.on_callback_query(filters.regex("^download_url$"))
async def download_url_callback(client: Client, callback_query: pyrogram.types.CallbackQuery):
    await client.send_message(callback_query.message.chat.id, "Please send the URL to download:")
    await client.register_next_step_handler(callback_query.message, download_from_url_handler)


@Client.on_message(filters.command(["convertmp4"]))
async def convert_mp4_handler(client: Client, message: Message):
    """Handles video to MP4 conversion."""
    if not message.reply_to_message:
        await message.reply("Please reply to a video message to convert it to MP4.")
        return
    
    replied_message = message.reply_to_message
    if not replied_message.video:
          await message.reply("Please reply to a video message to convert it to MP4.")
          return

    await message.reply("Downloading the video...")
    input_path = await download_media(client, replied_message)
    if not input_path:
        await message.reply("Error: Could not download the video.")
        return

    await message.reply("Converting video to MP4...")
    output_path = await convert_video_to_mp4(input_path)
    if not output_path:
        await message.reply("Error: Could not convert the video.")
    else:
        await message.reply("Uploading converted video...")
        await upload_media_to_telegram(client, message, output_path, "Converted to MP4")

    os.remove(input_path)
    if output_path:
        os.remove(output_path)

@Client.on_message(filters.command(["add_audio"]))
async def add_audio_handler(client: Client, message: Message):
    """Handles adding multiple audio tracks to video."""
    if not message.reply_to_message:
         await message.reply("Please reply to a video message with audio files to add to it.")
         return
    
    replied_message = message.reply_to_message
    if not replied_message.video:
          await message.reply("Please reply to a video message with audio files to add to it.")
          return

    audio_messages = []
    for msg in message.text.split()[1:]:
        try:
            audio_messages.append(int(msg))
        except ValueError:
            await message.reply(f"Invalid message ID: {msg}")
            return

    if not audio_messages:
      await message.reply("Please provide some audios message IDs as parameter.")
      return

    await message.reply("Downloading the video...")
    input_path = await download_media(client, replied_message)
    if not input_path:
        await message.reply("Error: Could not download the video.")
        return

    await message.reply("Downloading audio files...")
    audio_paths = []
    for audio_id in audio_messages:
         try:
             audio_msg = await client.get_messages(message.chat.id, audio_id)
         except Exception as e:
             await message.reply(f"Error downloading audio with message ID {audio_id}, Error: {e}")
             continue
         
         if not audio_msg.audio:
             await message.reply(f"Message with ID {audio_id} is not a audio")
             continue
         audio_path = await download_media(client, audio_msg)
         if not audio_path:
             await message.reply(f"Error downloading audio with message ID {audio_id}")
             continue
         audio_paths.append(audio_path)
    if not audio_paths:
        await message.reply("Error: No valid audio tracks downloaded.")
        return

    await message.reply("Adding audio tracks to the video...")
    output_path = await add_multiple_audio_tracks(input_path, audio_paths)
    if not output_path:
        await message.reply("Error: Could not add audio tracks to the video.")
    else:
       await message.reply("Uploading the video with audio...")
       await upload_media_to_telegram(client, message, output_path, "Video with added audio tracks.")
    
    os.remove(input_path)
    if output_path:
        os.remove(output_path)
    for audio_path in audio_paths:
         os.remove(audio_path)
    
@Client.on_message(filters.command(["add_subtitles"]))
async def add_subtitles_handler(client: Client, message: Message):
   if not message.reply_to_message:
      await message.reply("Please reply to a video message with subtitle file.")
      return

   replied_message = message.reply_to_message
   if not replied_message.video:
      await message.reply("Please reply to a video message with subtitle file.")
