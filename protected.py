import logging
import os
from functools import wraps
import jwt
from dotenv import load_dotenv
from sanic import text



logger = logging.getLogger(__name__)

load_dotenv()


SECRET = os.getenv("SECRET")


def create_token(user):
    token = jwt.encode({
        'id': user['id'],
        'username': user['username'],
        'role': user['role'],
    }, SECRET, algorithm='HS256')
    return token

def check_token(request):
    token = request.token or request.cookies.get('token')

    logger.debug(f'check_token() -> token: {token}')

    if not token:
        return False, {'message': 'Unauthorized'}

    try:
        payload = jwt.decode(
            token, request.app.config.SECRET, algorithms=["HS256"]
        )
    except jwt.ExpiredSignatureError:
        return False, {'message': 'Expired token'}
    except jwt.InvalidTokenError:   
        return False, {'message': 'Invalid token'}

    return True, payload

def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated, payload = check_token(request)

            logger.debug(f'protected() -> is_authenticated: {is_authenticated}, payload: {payload}')

            if is_authenticated:
                kwargs['user'] = payload
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text(payload['message'], 401)

        return decorated_function

    return decorator(wrapped)









