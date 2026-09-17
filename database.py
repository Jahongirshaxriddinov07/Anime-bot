import asyncpg
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS

class Database:
    def __init__(self):
        self.pool = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        await self.create_tables()

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    full_name VARCHAR(255),
                    phone VARCHAR(50),
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS channels (
                    id SERIAL PRIMARY KEY,
                    channel_id BIGINT UNIQUE,
                    invite_link TEXT
                );

                CREATE TABLE IF NOT EXISTS anime (
                    code VARCHAR(50) PRIMARY KEY,
                    file_id TEXT,
                    title TEXT
                );
            """)

    async def add_user(self, user_id: int, full_name: str, phone: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO users (user_id, full_name, phone)
                VALUES ($1, $2, $3)
                ON CONFLICT (user_id) DO NOTHING
            """, user_id, full_name, phone)

    async def is_registered(self, user_id: int) -> bool:
        async with self.pool.acquire() as conn:
            val = await conn.fetchval("SELECT user_id FROM users WHERE user_id = $1", user_id)
            return val is not None

    async def get_all_users(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT user_id FROM users")

    async def add_channel(self, channel_id: int, invite_link: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO channels (channel_id, invite_link)
                VALUES ($1, $2)
                ON CONFLICT (channel_id) DO UPDATE SET invite_link = $2
            """, channel_id, invite_link)

    async def get_channels(self):
        async with self.pool.acquire() as conn:
            return await conn.fetch("SELECT channel_id, invite_link FROM channels")

    async def delete_channel(self, channel_id: int):
        async with self.pool.acquire() as conn:
            await conn.execute("DELETE FROM channels WHERE channel_id = $1", channel_id)

    async def add_anime(self, code: str, file_id: str, title: str):
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO anime (code, file_id, title)
                VALUES ($1, $2, $3)
                ON CONFLICT (code) DO UPDATE SET file_id = $2, title = $3
            """, code, file_id, title)

    async def get_anime(self, code: str):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("SELECT file_id, title FROM anime WHERE code = $1", code)

db = Database()
