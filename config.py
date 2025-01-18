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
ADMINS = [int(id) for id in os.environ.get("ADMINS", "").split(",")]
LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", ""))

# Features
ERROR_MESSAGE = True
AUTO_FORWARD_CHANNEL = os.environ.get("AUTO_FORWARD_CHANNEL")
DEFAULT_REACTIONS = ["👍", "❤️", "🔥"] #Default reactions for the bot on messages
