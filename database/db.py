
import sqlite3
import motor.motor_asyncio
from config import DB_NAME, DB_URI

class Database:
    
    def __init__(self, db_path="user.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_table()
        
    
    def _create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            first_name TEXT,
            session_string TEXT,
            custom_forward_channel INTEGER
        )
        """)
        self.conn.commit()
        

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

    

    async def add_user(self, user_id, first_name):
        self.cursor.execute("INSERT INTO users (user_id, first_name) VALUES (?,?)", (user_id, first_name))
        self.conn.commit()

    async def add_session(self, user_id, session_string):
        self.cursor.execute("UPDATE users SET session_string = ? WHERE user_id = ?", (session_string, user_id))
        self.conn.commit()
    
    async def get_session(self, user_id):
        self.cursor.execute("SELECT session_string FROM users WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return None

    async def remove_session(self, user_id):
         self.cursor.execute("UPDATE users SET session_string = NULL WHERE user_id = ?", (user_id,))
         self.conn.commit()
    
    async def add_channel(self, user_id, channel_id):
         self.cursor.execute("UPDATE users SET custom_forward_channel = ? WHERE user_id = ?", (channel_id, user_id))
         self.conn.commit()
    
    async def get_channel(self, user_id):
         self.cursor.execute("SELECT custom_forward_channel FROM users WHERE user_id = ?", (user_id,))
         result = self.cursor.fetchone()
         if result:
            return result[0]
         return None
    
db = Database(DB_URI, DB_NAME)

