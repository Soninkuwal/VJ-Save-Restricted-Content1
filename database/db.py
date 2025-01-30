import os
import sqlite3

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


    def __init__(self, uri=None, db_name=None):
        if uri and db_name: # Check if URI and DB_NAME exists, if not then create a sqlite database, if they do exists then create a mongodb connection
            self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
            self._db = self._client.get_database(db_name)
            self._replace_words_collection = self._db.get_collection("replace_words")
            self._forward_channel_collection = self._db.get_collection("forward_channels")
            self._thumbnail_collection = self._db.get_collection("thumbnails")
        else:
           self.conn = sqlite3.connect('replace.db')
           self.cursor = self.conn.cursor()
           self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS replace_words (
                user_id INTEGER,
                old_word TEXT,
                new_word TEXT,
                UNIQUE(user_id, old_word)
                )
            """)
           self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS forward_channels (
                user_id INTEGER UNIQUE,
                channel_id INTEGER
                )
            """)
           self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS thumbnails (
                user_id INTEGER UNIQUE,
                file_path TEXT
            )
            """)
           self.conn.commit()

    async def add_replace_word(self, user_id, old_word, new_word):
        if hasattr(self, '_client'):
          try:
            await self._replace_words_collection.insert_one({
              "user_id": user_id,
              "old_word": old_word,
               "new_word": new_word
               })
            return True
          except Exception:
              return False
        else:
           try:
             self.cursor.execute(
            "INSERT INTO replace_words (user_id, old_word, new_word) VALUES (?, ?, ?)",
            (user_id, old_word, new_word)
           )
             self.conn.commit()
             return True
           except sqlite3.IntegrityError:
             return False

    async def get_replace_words(self, user_id):
      if hasattr(self, '_client'):
        cursor = self._replace_words_collection.find({"user_id": user_id})
        result = []
        async for document in cursor:
             result.append((document["old_word"], document["new_word"]))
        return result
      else:
        self.cursor.execute("SELECT old_word, new_word FROM replace_words WHERE user_id = ?", (user_id,))
        return self.cursor.fetchall()
      

    async def remove_replace_word(self, user_id, old_word):
         if hasattr(self, '_client'):
            result = await self._replace_words_collection.delete_one({"user_id": user_id, "old_word": old_word})
            return result.deleted_count > 0
         else:
           self.cursor.execute("DELETE FROM replace_words WHERE user_id = ? AND old_word = ?", (user_id, old_word))
           self.conn.commit()
           return self.cursor.rowcount > 0

    async def add_forward_channel(self, user_id, channel_id):
      if hasattr(self, '_client'):
        try:
            await self._forward_channel_collection.insert_one({"user_id": user_id, "channel_id": channel_id})
            return True
        except Exception:
           return False
      else:
        try:
          self.cursor.execute("INSERT INTO forward_channels (user_id, channel_id) VALUES (?, ?)", (user_id, channel_id))
          self.conn.commit()
          return True
        except sqlite3.IntegrityError:
          return False
    
    async def get_forward_channel(self, user_id):
        if hasattr(self, '_client'):
            document = await self._forward_channel_collection.find_one({"user_id": user_id})
            if document:
                return document["channel_id"]
            else:
                return None
        else:
           self.cursor.execute("SELECT channel_id FROM forward_channels WHERE user_id = ?", (user_id,))
           result = self.cursor.fetchone()
           return result[0] if result else None

    async def add_thumbnail(self, user_id, file_path):
        if hasattr(self, '_client'):
           try:
               await self._thumbnail_collection.insert_one({"user_id":user_id, "file_path":file_path})
               return True
           except:
                return False
        else:
           try:
               self.cursor.execute("INSERT INTO thumbnails (user_id, file_path) VALUES (?, ?)", (user_id, file_path))
               self.conn.commit()
               return True
           except sqlite3.IntegrityError:
               return False
    
    async def get_thumbnail(self, user_id):
         if hasattr(self, '_client'):
            document = await self._thumbnail_collection.find_one({"user_id": user_id})
            if document:
                return document["file_path"]
            else:
                return None
         else:
             self.cursor.execute("SELECT file_path FROM thumbnails WHERE user_id = ?", (user_id,))
             result = self.cursor.fetchone()
             return result[0] if result else None

    async def close(self):
        if hasattr(self, '_client'):
          self._client.close()
        else:
            self.conn.close()
if os.getenv("DB_URI"):
    DB_URI = os.getenv("DB_URI")
else:
    from config import DB_URI
if os.getenv("DB_NAME"):
    DB_NAME = os.getenv("DB_NAME")
else:
    from config import DB_NAME

db = Database(DB_URI, DB_NAME)

