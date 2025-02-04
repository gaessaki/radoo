import json

from odoo.addons.radoo.api.models.radish_address import RadishAddress
from odoo.addons.radoo.api.models.radish_order import RadishOrder
from odoo.addons.radoo.api.models.radish_recipient import RadishRecipient
from .radish_api import RadishApi

class RadishOrderApi(RadishApi):
    def fetch_orders(self, order_ids): 
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        query_string = ''
        for order_id in order_ids:
            if query_string != '':
                query_string += '&'
            query_string += f'order_refs={order_id}'

        return self.get(query_string)
    
    def initialize_order(self, picking):
        partner = picking.partner_id
        
        recipient = RadishRecipient(picking_partner=partner)
        address = RadishAddress(picking_partner=partner)
        order = RadishOrder(order_ref=picking.name, recipient=recipient, address=address)
    
        body = { 'order': order.toJSON(), 'platform': 'radoo' }
        return self.post('', body)
 
    def confirm_order(self, picking, packages):
        partner = picking.partner_id

        recipient = RadishRecipient(picking_partner=partner)
        address = RadishAddress(picking_partner=partner)
        order = RadishOrder(order_ref=picking.name, recipient=recipient, address=address)

        body = { 'order': order.toJSON(), 'parcels': packages, 'platform': 'radoo', 'confirm': True }
        return self.post('', body)
    
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
        
        content_type = response.headers['content-type']
        if content_type != 'application/pdf':
            raise Exception(500, 'Invalid content type')

        return response

