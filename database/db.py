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
            forward_channel_id=None,
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
        return user.get('session')

    async def set_forward_channel(self, user_id: int, forward_channel_id: int):
        await self.col.update_one({'id': int(user_id)}, {'$set': {'forward_channel_id': forward_channel_id}})

    async def get_forward_channel(self, user_id: int):
        user = await self.col.find_one({'id': int(user_id)})
        return user.get('forward_channel_id')

    async def add_replace_word(self, old_word: str, new_word: str):
         replace_col = self.db.replace_words
         await replace_col.insert_one({"old_word": old_word, "new_word": new_word})
      
    async def get_replace_words(self):
         replace_col = self.db.replace_words
         cursor = replace_col.find({})
         return await cursor.to_list(length=None)

    async def remove_replace_word(self, old_word: str):
      replace_col = self.db.replace_words
      await replace_col.delete_one({"old_word":old_word})

    async def add_delete_word(self, word: str):
        delete_col = self.db.delete_words
        await delete_col.insert_one({"word": word})

    async def get_delete_words(self):
         delete_col = self.db.delete_words
         cursor = delete_col.find({})
         result = await cursor.to_list(length=None)
         return [row.get("word") for row in result ]

    async def remove_delete_word(self, word: str):
        delete_col = self.db.delete_words
        await delete_col.delete_one({"word": word})


db = Database(DB_URI, DB_NAME)
