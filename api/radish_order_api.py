import json
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
    
    def create_order(self, picking):
        sale_order = picking.sale_id
        if not sale_order:
            raise ValueError("No sale order linked to the picking.")
        partner = sale_order.partner_id
        
        order ={
            'order_ref': picking.name,
            'recipient': {
                'first': partner.name if partner.name else '',
                'last': '',
                'company': partner.company_name if partner.company_name else '',
                'phone': partner.phone if partner.phone else '',
            },
            'address': {
                'line1': partner.street if partner.street else '',
                'line2': partner.street2 if partner.street2 else '',
                'city': partner.city if partner.city else '',
                'province': partner.state_id.name if partner.state_id else '',
                'postal': partner.zip if partner.zip else '',
                'country': partner.country_code if partner.country_code else '',
                'notes': partner.comment if partner.comment else ''
            },
            'platform': 'radoo'
        }
        return self.post('', order)
 
    def confirm_orders(self, order_ids):
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        orders = list(map(lambda order_id: { 
            'ref': order_id , 
            'status': 'ready' 
            }, order_ids))
        
        return self.request('patch', '', {'orders': orders})
    
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

