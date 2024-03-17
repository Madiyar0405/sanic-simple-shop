from sanic.views import HTTPMethodView
from protected import protected
from app import env
from sanic.response import html

class BaseView(HTTPMethodView):
    decorators = [protected]

    def http_success(self, template_path: str, **kwargs):
        template = env.get_template(template_path)
        return html(template.render(**kwargs))