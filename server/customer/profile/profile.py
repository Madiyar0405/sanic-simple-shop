from sanic.views import HTTPMethodView
from server.admin.base import BaseView
from sanic.response import empty
from server.args import parse_list_args


class ProfileView(BaseView):

    async def get(self, request, user):
        return self.http_success('./customerProfile.html', user=user)

    async def post(self, request, user):
        return empty()



