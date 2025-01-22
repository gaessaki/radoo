from .radish_api import RadishApi

class RadishOrderApi(RadishApi):
    # TODO: all of these should be fixed to use the new stuff
    def fetch_orders(self, order_ids, merchant_key):
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        query_string = ''
        for order_id in order_ids:
            if query_string != '':
                query_string += '&'
            query_string += f'order_refs={order_id}'
        url = f'{self.BASE_URL}merchant/orders?{query_string}'

        headers = {
            'Content-Type': 'application/json',
            'x-functions-key': self.AF_KEY,
            'merchant-key': merchant_key,
            'timeout': str(self.TIMEOUT)
        }

        try:
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.TIMEOUT
                )

            if response.status_code == 400:
                raise HttpException(400, 'Bad Request')
            if response.status_code == 401:
                raise HttpException(401, 'The provided merchant key is invalid.')
            if response.status_code == 404:
                raise HttpException(404, 'Could not find orders!')
            
            return response.json()      
        except requests.exceptions.RequestException as e:
            raise HttpException(500, str(e))

    def create_order(self, order, merchant_key):
        url = f'{self.BASE_URL}merchants/orders'
        headers = {
            'Content-Type': 'application/json',
            'x-functions-key': self.AF_KEY,
            'merchant-key': merchant_key,
            'timeout': str(self.TIMEOUT)
        }

        try:
            response = requests.post(
                url, 
                headers=headers, 
                data=json.dumps(order.toJSON()), 
                timeout=self.TIMEOUT
                )

            if response.status_code == 401:
                raise HttpException(401, 'The provided merchant key is invalid.')
            if response.status_code != 200:
                raise HttpException(response.status_code, response.text)

            return response.json()
        except requests.exceptions.RequestException as e:
            raise HttpException(500, str(e))
        
    def confirm_orders(self, order_ids, merchant_key):
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        orders = list(map(lambda order_id: { 
            'ref': order_id , 
            'status': 'ready' 
            }, order_ids))
        
        url = f'{self.BASE_URL}merchant/orders'
        headers = {
            'Content-Type': 'application/json',
            'x-functions-key': self.AF_KEY,
            'merchant-key': merchant_key,
            'timeout': str(self.TIMEOUT)
        }
        data = {
            'orders': orders
        }

        try:
            response = requests.patch(
                url, 
                headers=headers, 
                data=json.dumps(data)
                )

            if response.status_code == 401:
                raise HttpException(401, 'The provided merchant key is invalid.')
            if response.status_code == 404:
                raise HttpException(404, 'Could not find orders!')
            if response.status_code != 200:
                raise HttpException(response.status_code, response.text)
            
            return response.json()
        except requests.exceptions.RequestException as e:
            raise HttpException(500, str(e))
        
    def fetch_labels(self, order_ids, merchant_key):
        if not isinstance(order_ids, list):
            order_ids = [order_ids]

        query_string = ''
        for order_id in order_ids:
            if query_string != '':
                query_string += '&'
            query_string += f'order_refs={order_id}'
        url = f'{self.BASE_URL}merchant/orders/labels?{query_string}'

        headers = {
            'Content-Type': 'application/json',
            'x-functions-key': self.AF_KEY,
            'merchant-key': merchant_key,
            'timeout': str(self.TIMEOUT)
        }

        try:
            response = requests.get(
                url, 
                headers=headers, 
                timeout=self.TIMEOUT
                )

            if response.status_code == 401:
                raise HttpException(401, 'The provided merchant key is invalid.')
            if response.status_code == 404:
                raise HttpException(404, 'Could not find labels!')
            if response.status_code != 200:
                raise HttpException(response.status_code, response.text)
            
            response = response.json()
            if not response:
                raise HttpException(404, 'Could not find labels!')
            content_type = response.headers['content-type']
            if content_type != 'application/pdf':
                raise HttpException(500, 'Invalid content type')
            
            response = Response(response.content)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'inline; filename="document.pdf"'
            response.headers['Content-Length'] = str(len(response.content))

            return response
        except requests.exceptions.RequestException as e:
            raise HttpException(500, str(e))