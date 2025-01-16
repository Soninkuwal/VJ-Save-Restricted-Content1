import motor.motor_asyncio
from config import DB_NAME, DB_URI
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users

    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            session=None,
        )

    async def add_user(self, id, name):
        if not await self.is_user_exist(id):
            user = self.new_user(id, name)
            await self.col.insert_one(user)
            logging.info(f"New user added: {id} - {name}")

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})
        logging.info(f"User deleted: {user_id}")

    async def set_session(self, id, session):
        await self.col.update_one({'id': int(id)}, {'$set': {'session': session}})
        logging.info(f"Session updated for user: {id}")

    async def get_session(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user['session'] if user else None

    async def cleanup_inactive_users(self, inactive_days=30):
        """Remove users who have been inactive for more than `inactive_days` days."""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=inactive_days)
        result = await self.col.delete_many({"last_active": {"$lt": cutoff}})
        logging.info(f"Cleaned up {result.deleted_count} inactive users.")

# Database instance
db = Database(DB_URI, DB_NAME)

# Periodic performance maintenance
async def periodic_cleanup():
    while True:
        try:
            await db.cleanup_inactive_users(inactive_days=30)
            logging.info("Periodic cleanup complete.")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
        await asyncio.sleep(3600)  # Run every hour

# Initialize periodic maintenance tasks
asyncio.create_task(periodic_cleanup())
