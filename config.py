import os

#Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

#Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

#Database 
DB_URI = os.environ.get("DB_URI", "")

# Admin and Log
ADMIN = [int(id) for id in os.environ.get("ADMIN", "").split(",")]
ADMINS = [int(id) for id in os.environ.get("ADMINS", "").split(",")]
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))
CUSTOM_CHANNEL_ID = -1002260543763
# Features
ERROR_MESSAGE = True
#CUSTOM_CHANNEL_ID = os.environ.get("CUSTOM_CHANNEL_ID", "")
DEFAULT_REACTIONS = ["👍", "❤️", "🔥"] #Default reactions for the bot on messages
