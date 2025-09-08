from datetime import date

from odoo.addons.delivery.models.sale_order import SaleOrder
from .radish_api import RadishApi

class RadishPricingApi(RadishApi):

    def get_delivery_pricing(self, order, service_code: str):
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
            "pickupDate": order.pickup_date
        }

        return self.post(path, body)
