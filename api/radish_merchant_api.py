from .radish_api import RadishApi

class RadishMerchantApi(RadishApi):

    def validate_merchant_key(self, key):
        path = '/keys/validation'
        data = {
            'merchantKey': key
        }
        response = self.post(path, data)
        
        if response == None:
            return { 'success' : True }