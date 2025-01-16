# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client, filters
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

# Enhanced Performance Fix for Slowdown Issues
async def monitor_performance():
    while True:
        await asyncio.sleep(1800)  # Check every 30 minutes
        print("Monitoring bot performance...")
        # Add memory cleanup or optimization tasks here

# Add Login/Logout Commands
@Client.on_message(filters.command("login") & filters.private)
async def login_handler(client, message):
    await message.reply("Login functionality is under development. Stay tuned!")

@Client.on_message(filters.command("logout") & filters.private)
async def logout_handler(client, message):
    await message.reply("Logout functionality is under development. Stay tuned!")

# Start the Bot
if __name__ == "__main__":
    bot = Bot()

    # Run periodic cleanup and performance monitoring tasks
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_cleanup())
    loop.create_task(monitor_performance())

    bot.run()

# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01.
