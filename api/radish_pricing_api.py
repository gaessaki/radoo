from .radish_api import RadishApi

class RadishPricingApi(RadishApi):

    def get_delivery_pricing(self, order, service_code):
        path = '/delivery'

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
                service_code
            ],
            "includeDatePredictions": True,
            "pickupDate": "2025-08-22" # FIXME which date should I use here
        }

        return self.post(path, body)
