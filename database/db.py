import motor.motor_asyncio
from config import DB_NAME, DB_URI
import sqlite3


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

    #new
    async def set_forward_channel(self, user_id: int, forward_channel_id: int):
         self.cursor.execute(
             "UPDATE users SET forward_channel_id = ? WHERE user_id = ?",
            (forward_channel_id, user_id)
        )
         self.conn.commit()

    async def get_forward_channel(self, user_id: int):
        self.cursor.execute(
            "SELECT forward_channel_id FROM users WHERE user_id = ?",
            (user_id,)
        )
        result = self.cursor.fetchone()
        return result[0] if result else None


    async def add_replace_word(self, old_word: str, new_word: str):
        self.cursor.execute(
            "INSERT OR REPLACE INTO replace_words (old_word, new_word) VALUES (?, ?)",
            (old_word, new_word)
        )
        self.conn.commit()

    async def get_replace_words(self):
        self.cursor.execute("SELECT old_word, new_word FROM replace_words")
        return self.cursor.fetchall()

    async def remove_replace_word(self, old_word: str):
      self.cursor.execute("DELETE FROM replace_words WHERE old_word = ?", (old_word,))
      self.conn.commit()
      
    async def add_delete_word(self, word: str):
        self.cursor.execute(
            "INSERT OR IGNORE INTO delete_words (word) VALUES (?)",
            (word,)
        )
        self.conn.commit()

    async def get_delete_words(self):
         self.cursor.execute("SELECT word FROM delete_words")
         return [row[0] for row in self.cursor.fetchall()]

    async def remove_delete_word(self, word: str):
      self.cursor.execute("DELETE FROM delete_words WHERE word = ?", (word,))
      self.conn.commit()
#newend


db = Database(DB_URI, DB_NAME)


