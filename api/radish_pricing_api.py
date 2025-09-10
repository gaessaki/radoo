from .radish_api import RadishApi


class RadishPricingApi(RadishApi):

    def get_delivery_pricing(self, order, service_code: str, pickup_date: str, packages):
        """ Get shipment rate for an order
            Route documentation:
            https://radishcoop.notion.site/Quotes-Tarifs-2024522042ba807d82cff16c1b988960?p=2024522042ba805ab186f17406bd4e46&pm=c

        :param order:           The order to get the delivery pricing for
        :param service_code:    The chosen shipment rate standard
        :param pickup_date:     The pickup date
        :param packages:        List of packages
        :return:                The price and expected dates of the delivery
        """
        path = '/delivery'

        order.ensure_one()

        package_weights = [{"weight": package.weight * 1000} for package in packages]
        body = {
            "origin": {
                "postal": order.warehouse_id.partner_id.zip
            },
            "destination": {
                "postal": order.partner_shipping_id.zip
            },
            "parcels": package_weights,
            "standards": [
                service_code
            ],
            "includeDatePredictions": True,
            **({"pickupDate": pickup_date} if pickup_date is not None else {})
        }

        return self.post(path, body)
