def build_products_blueprint():
    from server.admin.products.products import ProductsView
    from sanic.blueprints import Blueprint

    blueprint = Blueprint('admin-products', url_prefix='/admin/products')

    blueprint.add_route(ProductsView.as_view(), '/')

    print("blueprint", blueprint)

    return blueprint
