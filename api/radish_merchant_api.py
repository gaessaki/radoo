from .radish_api import RadishApi

class RadishMerchantApi(RadishApi):

    def validate_merchant_key(self, key):
        path = '/keys/validation'
        data = {
            'merchantKey': key
        }
        response = self.post(path, data)
        return { 'success' : True }


    def get_delivery_pricing(self, order):
        path = '/pricing/delivery'

        order.ensure_one()

        try:
            packages = order.get_packages_by_volume()
        except Exception as exc:
            raise exc

        package_weights = [{"weight": package.weight * 1000} for package in packages]
        body = {
            "origin": {
                "postal": order.partner_from_id.zip
            },
            "destination": {
                "postal": order.partner_shipping_id.zip
            },
            "parcels": package_weights,
            "standards": [
                "standard" # TODO add customization here if needed
            ],
            "includeDatePredictions": True,
            "pickupDate": "2025-08-22" # TODO which date should I use here
        }

        return self.post(path, body)
