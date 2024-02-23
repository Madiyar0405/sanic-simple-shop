from sanic import Blueprint, Sanic, response
from jinja2 import Environment, FileSystemLoader
import asyncpg
from sanic_jwt import initialize, exceptions
from sanic_jwt.decorators import protected
from sanic import Blueprint, text
import re
from functools import wraps
import jwt
from quart import redirect
from dotenv import load_dotenv
import os
from sanic.cookies import Cookie


load_dotenv()



app = Sanic(__name__)





app.config.SECRET = os.getenv("SECRET")




env = Environment(loader=FileSystemLoader('templates'))

DATABASE_CONFIG = {
    'host': os.getenv("HOST"),
    'database': os.getenv("DATABASE"),
    'user': os.getenv("USER"),
    'password': os.getenv("PASSWORD")
}

async def create_db_connection():
    return await asyncpg.connect(**DATABASE_CONFIG)

def get_token_from_cookie(request):
    token = request.cookies.get('token')
    return token

def check_token(request):
    if not request.token:
        return False

    try:
        jwt.decode(
            request.token, request.app.config.SECRET, algorithms=["HS256"]
        )
    except jwt.exceptions.InvalidTokenError:
        return False
    else:
        return True

def protected(wrapped):
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            is_authenticated = check_token(request)

            if is_authenticated:
                response = await f(request, *args, **kwargs)
                return response
            else:
                return text("You are unauthorized.", 401)

        return decorated_function

    return decorator(wrapped)



@app.route('/login', methods=['POST', 'GET'])
async def login(request):
    if request.method == 'GET':
        template = env.get_template('./login.html')
        return response.html(template.render())

    data = request.form
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return response.json({'message': 'Username or password is missing'}, status=400)

    conn = await create_db_connection()
    user = await conn.fetchrow('SELECT * FROM users WHERE username = $1 AND password = $2', username, password)
    await conn.close()

    if user:
        token = jwt.encode({'username': username}, app.config.SECRET, algorithm='HS256')
        if token:
            response_obj = response.redirect(f'/products?token={token}')
            response_obj.cookies['token'] = token
            response_obj.cookies['token']['httponly'] = True
            response_obj.cookies['token']['max-age'] = 3600
            return response_obj
    else:
        return response.json({'message': 'Invalid username or password'}, status=401)



async def create_products_table():
    conn = await create_db_connection()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255),
            description TEXT,
            price NUMERIC(10, 2)
        )   
    ''')
    await conn.close()

async def get_products():
    conn = await create_db_connection()
    products = await conn.fetch('SELECT * FROM products')
    await conn.close()
    return products

@app.route('/profile')  
async def profile(request):
    template = env.get_template('./profile.html')
    return response.html(template.render())


@app.route('/products')
async def products(request):
    template = env.get_template('./products.html')
    token = request.args.get('token')
    # products = await get_products()


    token = get_token_from_cookie(request)
    if token:
        try:
            payload = jwt.decode(token, app.config.SECRET, algorithms=['HS256'])
            username = payload.get('username')
            products = await get_products()
            return response.html(template.render(username=username, products=products))
        except jwt.ExpiredSignatureError:
            return response.json({'message': 'Expired token'}, status=401)
        except jwt.InvalidTokenError:   
            return response.json({'message': 'Invalid token'}, status=401)
    else:
        return response.json({'message': 'Token is missing'}, status=401)


    # if token:
    #     try:
    #         payload = jwt.decode(token, app.config.SECRET, algorithms=['HS256'])
    #         username = payload.get('username')
    #         products = await get_products()
    #         return response.html(template.render(username=username, products=products))
    #     except jwt.ExpiredSignatureError:
    #         return response.json({'message': 'Expired token'}, status=401)
    #     except jwt.InvalidTokenError:   
    #         return response.json({'message': 'Invalid token'}, status=401)
    # else:
    #     return response.json({'message': 'Token is missing'}, status=401)
   


USERNAME_REGEX = r'^[a-zA-Z0-9]+$'
@app.route('/register', methods=['GET', 'POST'])
async def register_user(request):
    if request.method == 'GET':
        template = env.get_template('./register.html')

        return response.html(template.render())

    data = request.form



    username = data.get('username')
    password = data.get('password')
    role = 'customer'

    if not username or not re.match(USERNAME_REGEX, username):
        return response.text('Invalid username' , status = 400)
    
    if not password or len(password) < 8:
        return response.text('Password is short' , status = 400)
    
    conn = await create_db_connection()
    await conn.execute('INSERT INTO users (username, password,role) VALUES ($1, $2, $3)', username, password, role)
    await conn.close()

    return response.redirect('./login')







# def protected():
#     def decorator(f):
#         @wraps(f)
#         async def decorated_function(request, *args, **kwargs):
#             token = request.headers.get('Authorization')

#             if not token:
#                 return response.json({'message': 'Token is missing'}, status=401)
        
#             try:
#                 payload = jwt.decode(token, app.config.SECRET, algorithms='HS256')
#             except jwt.ExpiredSignatureError:
#                 return response.json({'message' : 'Token is expired'} , status=401)
#             except jwt.InvalidTokenError:
#                 return response.json({'message' : 'Invalid token' }, status=401)
        
#             request['user'] = payload['username']
#             return await f (request, *args, **kwargs)
#         return decorated_function
#     return decorator
        

@app.route('/success')
@protected
async def success(request):
    return response.text('Login successful')

@app.route('/failure')
async def failure(request):
    return response.text('Invalid username or password', status=401)

@app.route('/add_product', methods=['POST'])
async def add_product(request):
    data = request.form
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')

    if not (name and description and price):
        return response.text('Please provide all product details', status=400)

    conn = await create_db_connection()
    await conn.execute('''
        INSERT INTO products (name, description, price)
        VALUES ($1, $2, $3)
    ''', name, description, price)
    await conn.close()

    return response.redirect('/profile')


@app.route('/delete_product/<product_id>', methods=['POST'])
async def delete_product(request, product_id):
    # Convert product_id to integer
    product_id = int(product_id)
    conn = await create_db_connection()
    await conn.execute('DELETE FROM products WHERE id = $1', product_id)
    await conn.close()
    return response.redirect('/profile')



# @app.get('/protected')
# @protected()
# async def protected_route(request):
#     user = request['user']
#     return response.json({'message' : f'hello {user}'}, status=200)

if __name__ == '__main__':
    app.add_task(create_products_table())
    app.run(host='0.0.0.0', port=8000)
