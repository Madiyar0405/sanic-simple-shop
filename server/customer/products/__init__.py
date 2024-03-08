def build_products_blueprint():
    from server.customer.products.products import ProductsView
    from sanic.blueprints import Blueprint

    blueprint = Blueprint('customer-products', url_prefix='/customer/products')

    blueprint.add_route(ProductsView.as_view(), '/')

    print("blueprint", blueprint)

    return blueprint
