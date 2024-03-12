import asyncio
import os
import traceback

import asyncpg
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    'host': os.getenv("HOST"),
    'database': os.getenv("DATABASE"),
    'user': os.getenv("USER"),
    'password': os.getenv("PASSWORD")
}

class DB:
    pool = None

    async def connect(self):
        print('BEFORE connect')
        self.pool = await asyncpg.create_pool(**DATABASE_CONFIG)
        print('AFTER connect')

    async def close(self):
        print('BEFORE close')
        try:
            await asyncio.wait_for(self.pool.close(), 5)
        except (Exception,):
            traceback.print_exc()
        finally:
            self.pool = None
        print('AFTER close')

    async def fetch(self, *args, **kwargs):
        async with self.pool.acquire() as conn:
            print('fetch() ->', conn, args, kwargs)
            return await conn.fetch(*args, **kwargs)

    async def fetchrow(self, *args, **kwargs):
        async with self.pool.acquire() as conn:
            print('fetchrow() ->', conn, args, kwargs)
            return await conn.fetchrow(*args, **kwargs)

    async def fetchval(self, *args, **kwargs):
        async with self.pool.acquire() as conn:
            print('fetchval() ->', conn, args, kwargs)
            return await conn.fetchval(*args, **kwargs)

    async def execute(self, *args, **kwargs):
        async with self.pool.acquire() as conn:
            print('execute() ->', conn, args, kwargs)
            return await conn.execute(*args, **kwargs)


db = DB()
