from sanic import Blueprint, Sanic, response, text
from jinja2 import Environment, FileSystemLoader
import asyncpg
import re
from functools import wraps
import jwt
from quart import redirect
from dotenv import load_dotenv
import os
from sanic.cookies import Cookie
import bcrypt
from sanic import Sanic
from sanic.response import json
from sanic import Sanic, response
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio


from db import db
from protected import create_token, protected
import logging

load_dotenv()

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

logging.basicConfig(level=logging.DEBUG)

USERNAME_REGEX = r'^[a-zA-Z0-9]+$'

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


@app.before_server_start
async def before_server_start(*args, **kwargs):
    await db.connect()


@app.before_server_stop
async def before_server_stop(*args, **kwargs):
    await db.close()


from server.admin.profile import build_profile_blueprint

app.blueprint(build_profile_blueprint())

from server.admin.products import build_products_blueprint

app.blueprint(build_products_blueprint())

from server.customer.products import build_products_blueprint

app.blueprint(build_products_blueprint())

from server.customer.profile import build_profile_blueprint

app.blueprint(build_profile_blueprint())


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

    user = await db.fetchrow('SELECT * FROM users WHERE username = $1', username)

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        token = create_token(user)
        if token:
            if user['role'] == 'admin':
                response_obj = response.redirect('/admin/profile')
            else:
                response_obj = response.redirect('/customer/profile')
            response_obj.cookies['token'] = token
            response_obj.cookies['token']['httponly'] = True
            response_obj.cookies['token']['max-age'] = 3600
            return response_obj
    else:
        return response.json({'message': 'Invalid username or password'}, status=401)


@app.route('/logout', methods=['GET'])
async def logout(request):
    response_obj = response.redirect('/login')
    response_obj.cookies['token'] = ''
    response_obj.cookies['token']['max-age'] = 0
    return response_obj




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
        return response.text('Invalid username', status=400)

    if not password or len(password) < 8:
        return response.text('Password is short', status=400)

    try:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_password_str = hashed_password.decode('utf-8')
    except Exception as e:
        return response.text('Error hashing password', status=500)

    conn = await create_db_connection()

    user_exist = await conn.fetchval('SELECT COUNT(*) FROM users WHERE username = $1', username)
    if user_exist:
        return response.text('username already exist', status=400)

    try:
        await conn.execute('INSERT INTO users (username, password,role) VALUES ($1, $2, $3)', username,
                           hashed_password_str, role)
        await conn.close()
    except Exception as e:
        print(f'Error inserting user into database: {e}')
        return response.text('Error registering user', status=500)

    return response.redirect('./login')

@app.route('/add_product', methods=['POST'])
async def add_product(request):
    data = request.form
    component_name = data.get('component_name')
    model = data.get('model')
    manufacturer = data.get('manufacturer')
    price = data.get('price')
    quantity_int = data.get('quantity')
    quantity = int(quantity_int)


    if not (component_name and model and manufacturer and price ):
        return response.text('Please provide all product details', status=400)

    conn = await create_db_connection()
    await conn.execute('''
        INSERT INTO components (component_name, model, manufacturer, price, quantity)
        VALUES ($1, $2, $3, $4, $5)
    ''', component_name, model, manufacturer, price, quantity)
    await conn.close()

    return response.redirect('/admin/profile')

@app.route('/add_to_cart/<component_id:int>', methods=['POST'])
@protected
async def add_to_cart(request, user, component_id: int):
    data = request.form
    quantity = int(data.get('quantity'))

    if not (component_id and quantity):
        return response.text('Please provide all required details', status=400)

    conn = await create_db_connection()
    await conn.execute('''
        INSERT INTO cart (user_id, component_id, quantity)
        VALUES ($1, $2, $3)
    ''', user['id'], component_id, quantity)
    await conn.close()

    if user['role'] == 'admin':
        return response.redirect('/admin/products')
    else:
        return response.redirect('/customer/products')

async def delete_user(request, user_id):
    user_id = int(user_id)
    await db.execute('DELETE FROM users WHERE id = $1', user_id)
    return response.redirect('/admin/profile')


@app.route('/delete_component/<component_id>', methods=['POST'])
async def delete_product(request, component_id):
    component_id = int(component_id)
    await db.execute('DELETE FROM components WHERE id = $1', component_id)
    return response.redirect('/admin/products')


@app.route('/delete_from_cart/<component_id>', methods=['POST'])
@protected
async def delete_from_cart(request, component_id, user):
    component_id = int(component_id)
    await db.execute('DELETE FROM cart WHERE component_id = $1', component_id)
    if user['role'] == 'admin':
        return response.redirect('/admin/cart')
    else:
        return response.redirect('/customer/cart')

async def remove_expired_items():
    await db.execute('DELETE FROM cart WHERE added_at < NOW() - INTERVAL \'4 hours\'')

scheduler.add_job(remove_expired_items, 'interval', hours=4)

@app.listener('before_server_start')
async def start_scheduler(app, loop):
    scheduler.start()

@app.listener('after_server_stop')
async def stop_scheduler(app, loop):
    scheduler.shutdown()




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, access_log=True, debug=True)
