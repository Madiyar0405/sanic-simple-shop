def build_products_blueprint():
    from server.admin.products.products import ProductsView
    from server.admin.products.cart import CartView
    from sanic.blueprints import Blueprint

    blueprint = Blueprint('admin-products', url_prefix='/admin')

    blueprint.add_route(ProductsView.as_view(), '/products')
    blueprint.add_route(CartView.as_view(), '/cart')

    print("blueprint", blueprint)

    return blueprint
