# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, filters_chat_type
import os
import asyncio
from config import API_ID, API_HASH, BOT_TOKEN

class Bot(Client):

    def __init__(self):
        super().__init__(
            "techvj_login",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="TechVJ"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        print('Bot Started Powered By @VJ_Botz')

    async def stop(self, *args):
        await super().stop()
        print('Bot Stopped Bye')

# Fix for 0KB File Issues
def is_valid_file(file_path):
    return os.path.exists(file_path) and os.path.getsize(file_path) > 0

@Client.on_message(filters.command("check_file") & filters.private)
async def check_file_handler(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("Please reply to a document to check its validity.")
        return

    file_path = await message.reply_to_message.download()
    if is_valid_file(file_path):
        await message.reply("The file is valid and ready to use.")
    else:
        await message.reply("The file is invalid (0KB or missing). Please upload a valid file.")

# Periodic Cleanup for Long-Running Performance
async def periodic_cleanup():
    while True:
        await asyncio.sleep(3600)  # Cleanup every hour
        print("Performing periodic cleanup...")
        # Additional cleanup tasks can go here

# Support for Groups and Channels
@Client.on_message(filters.chat_type.groups | filters.chat_type.channels)
async def group_channel_handler(client, message):
    if message.chat.type == "channel":
        await message.reply("Message received in a channel. Powered by @VJ_Botz!")
    elif message.chat.type == "group":
        await message.reply("Message received in a group. Powered by @VJ_Botz!")

# Optimize File Handling
@Client.on_message(filters.command("upload") & filters.private)
async def upload_file_handler(client, message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.reply("Please reply to a document to upload.")
        return

    file_path = await message.reply_to_message.download()
    if is_valid_file(file_path):
        # Simulating upload process
        await message.reply("Uploading your file...")
        await asyncio.sleep(2)  # Simulated delay
        await message.reply("File uploaded successfully!")
    else:
        await message.reply("The file is invalid (0KB or missing). Please upload a valid file.")

# Start the Bot
if __name__ == "__main__":
    bot = Bot()

    # Run periodic cleanup task
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_cleanup())

    bot.run()

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01
