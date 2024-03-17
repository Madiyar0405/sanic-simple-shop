def build_profile_blueprint():
    from server.admin.profile.profile import ProfileView
    from sanic.blueprints import Blueprint

    blueprint = Blueprint('admin-profile', url_prefix='/admin')

    blueprint.add_route(ProfileView.as_view(), '/profile')

    print("blueprint", blueprint)

    return blueprint