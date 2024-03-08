def build_profile_blueprint():
    from server.customer.profile.profile import ProfileView
    from sanic.blueprints import Blueprint

    blueprint = Blueprint('customer-profile', url_prefix='/customer/profile')

    blueprint.add_route(ProfileView.as_view(), '/')

    print("blueprint", blueprint)

    return blueprint
