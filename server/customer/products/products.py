from sanic.response import empty

from server.admin.base import BaseView
from server.data.repository.products import get_products


class ProductsView(BaseView):

    async def get(self, request, user):
        component = await get_products()

        return self.http_success('./customerProducts.html', user=user, components=component)

    async def post(self, request, user):
        return empty()
