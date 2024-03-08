import logging
import os
import re

import asyncpg
import bcrypt
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from sanic import Sanic, response

from db import DB
from protected import create_token
from server.data.repository.products import get_manufacturers

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

USERNAME_REGEX = r'^[a-zA-Z0-9]+$'

app = Sanic(__name__)
db = DB()


app.config.SECRET = os.getenv("SECRET")

env = Environment(loader=FileSystemLoader('templates'))

DATABASE_CONFIG = {
    'host': os.getenv("HOST"),
    'database': os.getenv("DATABASE"),
    'user': os.getenv("USER"),
    'password': os.getenv("PASSWORD")
}



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

    conn = await db.connect()
    user = await conn.fetchrow('SELECT * FROM users WHERE username = $1', username)


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
    conn = await DB.connect()

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


@app.route('/get_filtered_components')
async def get_filtered_components(request):
    manufacturer = request.args.get('manufacturer')
    sort_by = request.args.get('sort_by')
    order = request.args.get('order')
    page = int(request.args.get('page', 1))
    per_page = 10

    manufacturers = await get_manufacturers()
    components = await get_components(manufacturer)

    template = env.get_template('index.html')
    return response.html(
        template.render(components=components, manufacturers=manufacturers, component_name=manufacturer,
                        sort_by=sort_by, order=order, page=page))


@app.route('/add_product', methods=['POST'])
async def add_product(request):
    data = request.form
    component_name = data.get('component_name')
    model = data.get('model')
    manufacturer = data.get('manufacturer')
    price = data.get('price')
    availability = data.get('availability')

    if availability == True:
        availability = True
    else:
        availability = False

    if not (component_name and model and manufacturer and price):
        return response.text('Please provide all product details', status=400)

    conn = await db.connect()
    await conn.execute('''
        INSERT INTO components (component_name, model, manufacturer, price, availability)
        VALUES ($1, $2, $3, $4, $5)
    ''', component_name, model, manufacturer, price, availability)
    await conn.close()

    return response.redirect('/admin/profile')


app.route('/delete_users/<user_id>', methods=['POST'])


async def delete_user(request, user_id):
    user_id = int(user_id)
    conn = await db.connect()
    await conn.execute('DELETE FROM users WHERE id = $1', user_id)
    await conn.close()
    return response.redirect('/admin/profile')


@app.route('/delete_component/<component_id>', methods=['POST'])
async def delete_product(request, component_id):
    component_id = int(component_id)
    conn = await db.connect()
    await conn.execute('DELETE FROM components WHERE id = $1', component_id)
    await conn.close()
    return response.redirect('/admin/products')


if __name__ == '__main__':
    # app.add_task(create_products_table())

    app.run(host='0.0.0.0', port=8000, access_log=True, debug=True)
