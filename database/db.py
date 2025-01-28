import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            session = None,
        )
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user['session']

db = Database(DB_URI, DB_NAME)



# Sample DB code (replace with your own db code)
custom_words = {}

async def add_custom_word(key, value):
    custom_words[key] = value

async def remove_custom_word(key):
    if key in custom_words:
        del custom_words[key]

async def apply_custom_words(text):
    for key, value in custom_words.items():
        text = text.replace(key, value)
    return text

@Client.on_message(filters.command("add_replace"))
async def add_replace_cmd(client, message):
    # Parse command and add to custom_words
    pass

@Client.on_message(filters.text)
async def message_handler(client, message):
  text = await apply_custom_words(message.text)
  await client.send_message(message.chat.id, text)
