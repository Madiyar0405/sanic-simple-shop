execute = None
fetch = [{}, {}, {}, ...]
fetchrow = {}


import asyncpg
asyncpg.Record


user = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
print(dict(user))
user['id']
