from server.admin.base import BaseView
from server.data.repository.products import get_products, get_manufacturers, get_filtered_sorted_products, get_component_name


class ProductsView(BaseView):
    async def get(self, request, user):
        manufacturers = await get_manufacturers()
        component_name = await get_component_name()
        component = await get_products()
        price = await get_filtered_sorted_products()
        return self.http_success('./customerProducts.html', user=user, components=component, manufacturers=manufacturers, component_name=component_name, price=price)

    async def post(self, request, user):
        manufacturer = request.form.get('manufacturer')
        component_name = request.form.get('component_name')
        sort_by = request.form.get('sort_by')
        order = request.form.get('order')
        components = await get_filtered_sorted_products(manufacturer=manufacturer, component_name=component_name, sort_by=sort_by, order=order)
        manufacturers = await get_manufacturers()
        component_name = await get_component_name()
        return self.http_success('./customerProducts.html', user=user, components=components, manufacturers=manufacturers, component_name=component_name)









