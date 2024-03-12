from db import db


async def create_products_table():
    await db.execute('''
        CREATE TABLE IF NOT EXISTS components (
            id SERIAL PRIMARY KEY,
            component_name VARCHAR(100),
            model VARCHAR(100),
            manufacturer VARCHAR(100),
            price DECIMAL(10, 2),
            availability BOOLEAN
        )   
    ''')



async def get_products():
    components = await db.fetch('SELECT * FROM components')
    return components


async def get_users():
    users = await db.fetch('SELECT * FROM users')
    return users


async def get_component_name():
    component_name_records = await db.fetch('SELECT DISTINCT component_name FROM components')
    component_name = [record['component_name'] for record in component_name_records]
    return component_name


async def get_manufacturers():
    manufacturers_records = await db.fetch('SELECT DISTINCT manufacturer FROM components')
    manufacturers = [record['manufacturer'] for record in manufacturers_records]
    return manufacturers

async def get_filtered_sorted_products(manufacturer=None, component_name=None, sort_by=None, order=None, page=1, per_page=10):

    sql_query = "SELECT * FROM components WHERE 1=1"

    if manufacturer:
        sql_query += f" AND manufacturer = '{manufacturer}'"

    if component_name:
        sql_query += f" AND component_name ILIKE '%{component_name}%'"

    if sort_by and order:
        sql_query += f" ORDER BY {sort_by} {order}"

    offset = (page - 1) * per_page
    sql_query += f" LIMIT {per_page} OFFSET {offset}"

    components = await db.fetch(sql_query)

    return components

