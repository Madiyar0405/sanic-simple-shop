from sanic.response import empty

from server.admin.base import BaseView
from server.data.repository.products import get_products, get_manufacturers, get_filtered_sorted_products


class ProductsView(BaseView):

    async def get(self, request, user):
        manufacturers = await get_manufacturers()
        component = await get_products()

        return self.http_success('./products.html', user=user, components=component, manufacturers=manufacturers)

    async def post(self, request, user):
        manufacturer = request.form.get('manufacturer')
        components = await get_filtered_sorted_products(manufacturer=manufacturer)
        manufacturers = await get_manufacturers()

        return self.http_success('./products.html', user=user, components=components, manufacturers=manufacturers)
