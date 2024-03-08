from dotenv import load_dotenv
import os
import asyncpg
from asyncpg import Connection

load_dotenv()

DATABASE_CONFIG = {
    'host': os.getenv("HOST"),
    'database': os.getenv("DATABASE"),
    'user': os.getenv("USER"),
    'password': os.getenv("PASSWORD")
}

db = None

async def   create_db_connection() -> Connection:
    global db
    if db is None:
        db = await asyncpg.connect(**DATABASE_CONFIG)
    return db

async def close_db_connection():
    if db is None:
        return False
    await db.close()
    db = None
    return True

