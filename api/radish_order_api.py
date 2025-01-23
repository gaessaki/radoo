# import json

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
    
    def create_order(self, order):
        # order_json = json.dumps({
        #     'order_ref': order.order_ref,
        #     'recipient': {
        #         'first': order.recipient_first,
        #         'last': order.recipient_last,
        #         'company': order.recipient_company,
        #         'phone': order.recipient_phone,
        #     },
        #     'address': {
        #         'line1': order.address_line1,
        #         'line2': order.address_line2,
        #         'city': order.address_city,
        #         'province': order.address_state,
        #         'postal': order.address_zip,
        #         'country': order.address_country,
        #         'notes': order.address_notes
        #     }
        # })
        return self.post('', order.toJson())
 
    def confirm_orders(self, order_ids):
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        orders = list(map(lambda order_id: { 
            'ref': order_id , 
            'status': 'ready' 
            }, order_ids))
        
        return self.request('patch', '', orders)
    
    def fetch_labels(self, order_ids):
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        query_string = ''
        for order_id in order_ids:
            if query_string != '':
                query_string += '&'
            query_string += f'order_refs={order_id}'

        response = self.get('labels?' + query_string)
    
        if not response:
                raise Exception(404, 'Could not find labels!')
        content_type = response.headers['content-type']
        if content_type != 'application/pdf':
            raise Exception(500, 'Invalid content type')
        
        return response.headers
    