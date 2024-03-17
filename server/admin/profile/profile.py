from sanic.views import HTTPMethodView
from server.admin.base import BaseView
from sanic.response import empty
from server.args import parse_list_args
from server.data.repository.products import get_users


class ProfileView(BaseView):

    async def get(self, request, user):
        employee = await get_users()
        return self.http_success('./profile.html', user=user, employee=employee)

    async def post(self, request, user):
        return empty()