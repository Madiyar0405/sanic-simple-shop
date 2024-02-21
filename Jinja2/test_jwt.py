import jwt
from typing import Tuple, Optional

SECRET = 'salt'

def generate_token(payload: dict) -> str:
    token = jwt.encode(payload, SECRET)
    return token


def check_token(token) -> Tuple[bool, Optional[dict]]:
    if not (token and isinstance(token, str)):
    
        return False, None

    try:
        return True, jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        return False, None
    
    return False, None


def get_products(token: str):
    is_valid, payload = check_token(token)
    if is_valid:
        return False
    
    user_id = payload.get('id')

    user = db.fetchrow('SELECT * FROM users WHERE id = $1', user_id)

    if user:
        await db.fetch()
        return ['A', 'B']
    else:
        return False
    
async def create_product(token: str):
    is_valid, payload = check_token(token)
    if is_valid:
        return False
    
    user_id = payload.get('id')

    user = db.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
    
    if user['role'] == 'admin':
        pass
    else:
        return False


def login(username, password):
    user = db.fetchrow('SELECT * FROM users WHERE username = $1 AND password = $2', username, password)

    if user:
        token = generate_token({'id': user['id']})
        print('token:', token)

        return token
    
    return False


token = generate_token({'id': 10})
print('token:', token)

is_valid, payload = check_token(token)
print('is_valid:', is_valid, 'payload:', payload)

