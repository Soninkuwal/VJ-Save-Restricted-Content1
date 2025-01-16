import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", ""))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", ""))

# Your Mongodb Database Url
DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "")

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then False
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', False))


# If You Want group & channel Message In Your Personal Message Then Turn It True Else If You Don't Want Then False
# Check if the bot is working in a group and channel
WORKING_GROUP = bool(os.environ.get("WORKING_GROUP", True))
WORKING_CHANNEL = bool(os.environ.get("WORKING_CHANNEL", True))
