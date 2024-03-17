from sanic.response import empty

from server.admin.base import BaseView
from server.data.repository.products import get_product_from_cart


class CartView(BaseView):

    async def get(self, request, user):
        cart = await get_product_from_cart(request)

        return self.http_success('./customerCart.html', user=user, cart=cart)

    async def post(self, request, user):
       return empty()
