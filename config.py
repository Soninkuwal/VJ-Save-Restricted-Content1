import os

#Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

#Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "20945078"))

#Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "93f6b8ce4bb0ab61b4c7e42187f2aa64")

#Database 
DB_URI = os.environ.get("DB_URI", "mongodb+srv://meenakanhaiyalal638:files@files.8ko8k.mongodb.net/?retryWrites=true&w=majority&appName=files")
