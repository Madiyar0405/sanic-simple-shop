def build_products_blueprint():
    from server.customer.products.products import ProductsView
    from server.customer.products.cart import CartView
    from sanic.blueprints import Blueprint

    blueprint = Blueprint('customer-products', url_prefix='/customer')

    blueprint.add_route(ProductsView.as_view(), '/products')
    blueprint.add_route(CartView.as_view(), '/cart')

    print("blueprint", blueprint)

    return blueprint
