from odoo.addons.radoo.api.models.radish_address import RadishAddress
from odoo.addons.radoo.api.models.radish_order import RadishOrder
from odoo.addons.radoo.api.models.radish_recipient import RadishRecipient
from .radish_api import RadishApi
from odoo.exceptions import UserError


class RadishOrderApi(RadishApi):
    # def fetch_orders(self, order_ids): 
    #     if not isinstance(order_ids, list):
    #         order_ids = [order_ids]

    #     query_string = ''
    #     for order_id in order_ids:
    #         if query_string != '':
    #             query_string += '&'
    #         query_string += f'order_refs={order_id}'

    #     return self.get(query_string)

    def initialize_order(self, picking):
        order = picking.to_radish_order()

        body = {'order': order.toJSON(), 'platform': 'radoo'}
        if picking.carrier_id.radish_service_code:
            body['service_code'] = picking.carrier_id.radish_service_code
        return self.post('', body)

    def confirm_order(self, picking, packages):
        order = picking.to_radish_order()

        body = {'order': order.toJSON(), 'parcels': packages, 'platform': 'radoo', 'confirm': True}
        if picking.carrier_id.radish_service_code:
            body['service_code'] = picking.carrier_id.radish_service_code
        return self.post('', body)

    def cancel_order(self, picking):
        order = [{
            'ref':    picking.name,
            'status': 'cancelled',
        }]

        return self.request('patch', '', {'orders': order})

    def fetch_labels(self, order_ids):
        if not isinstance(order_ids, list):
            order_ids = [order_ids]
        query_string = ''
        for order_id in order_ids:
            if query_string != '':
                query_string += '&'
            query_string += f'order_refs={order_id}'

        response = self.get('/labels?' + query_string)

        if not response:
            raise Exception(404, 'Could not find labels!')

        content_type = response.headers.get('content-type', None)
        if content_type != 'application/pdf':
            raise Exception(500, 'Invalid content type')

        return response
