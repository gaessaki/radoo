import logging
from types import SimpleNamespace

from odoo import api
from odoo import models, fields, _
from odoo.addons.radoo.api.radish_merchant_api import RadishMerchantApi
from odoo.addons.radoo.api.radish_order_api import RadishOrderApi
from odoo.addons.radoo.api.radish_pricing_api import RadishPricingApi
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[('radish', 'Radish')],
        ondelete={'radish': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})}
    )

    radish_prod_merchant_key = fields.Char(
        string='Merchant Key (Production)',
        help='The merchant key for the Radish API. You can request a merchant key from your Radish relationship manager.',
    )

    radish_test_merchant_key = fields.Char(
        string='Merchant Key (Test)',
        help='The merchant key for the Radish API. You can request a merchant key from your Radish relationship manager.',
    )

    radish_service_code = fields.Char(
        string='Radish Service Code',
    )

    radish_fixed_price = fields.Float(string='Fixed Price', default=10.00)

    radish_use_fixed_price = fields.Boolean(string='Use the fixed price in shipment rates', default=True)

    radish_include_expected_delivery = fields.Boolean(string='Use API for expected shipment delivery dates', default=False)

    # show_radish_bulk_print = fields.Boolean(string='Enable Bulk Printing of Radish Orders', default=False)

    @api.constrains('radish_prod_merchant_key')
    def action_validate_prod_merchant_key(self):
        for record in self:
            self._validate_merchant_key(record.radish_prod_merchant_key)

    @api.constrains('radish_test_merchant_key')
    def action_validate_test_merchant_key(self):
        for record in self:
            self._validate_merchant_key(record.radish_test_merchant_key)

    def _validate_merchant_key(self, merchant_key):
        merchant_api = self._radish_merchant_api()
        if not merchant_key:
            return
        try:
            if merchant_api.validate_merchant_key(merchant_key):
                title = _("Success!")
                message = _("Merchant Key Validated Successfully!")
                return {
                    'type':   'ir.actions.client',
                    'tag':    'display_notification',
                    'params': {
                        'title':   title,
                        'message': message,
                        'sticky':  False,
                    }
                }
        except Exception as e:
            raise ValidationError(_("Error during validation: %s") % e)

    def _radish_merchant_api(self):
        return RadishMerchantApi('merchants', debug_logging=self.log_xml)

    def _radish_order_api(self):
        merchant_key = self.radish_prod_merchant_key if self.prod_environment else self.radish_test_merchant_key
        if not merchant_key:
            raise UserError("No merchant key found for the selected environment.")
        return RadishOrderApi('merchants/orders', merchant_key=merchant_key, debug_logging=self.log_xml)

    def _radish_pricing_api(self):
        merchant_key = self.radish_prod_merchant_key if self.prod_environment else self.radish_test_merchant_key
        if not merchant_key:
            raise UserError("No merchant key found for the selected environment.")
        return RadishPricingApi('merchants/pricing', merchant_key=merchant_key, debug_logging=self.log_xml)

    def radish_rate_shipment(self, order):
        """Compute the price of the order shipment

        :param order: recordset of sale.order
        :return: dict: {'success': boolean,
                       'price': a float,
                       'error_message': a string containing an error message,
                       'warning_message': a string containing a warning message}
        """
        self.ensure_one()

        if not self.radish_include_expected_delivery and self.radish_use_fixed_price:
            return {
                'success':                  True,
                'price':                    self.radish_fixed_price,
                'warning_message':          None,
            }

        api = self._radish_pricing_api()

        packages = self.radish_get_package_weights(order)
        pickup_date = self.radish_order_picking_date(order)

        response = api.get_delivery_pricing(order, self.radish_service_code, pickup_date, packages)
        response_data = response.json()

        rates = response_data.get("rates", [])
        if not rates:
            raise ValidationError(f"No shipment rate found for order {order.id}.")

        first_rate = rates[0]

        price: float = self.radish_fixed_price
        if not self.radish_use_fixed_price:
            cost_info = first_rate.get("cost", {})
            amount = cost_info.get("amount")

            try:
                price = amount / 100
            except TypeError:
                raise ValidationError("No amount found in rate response.")

        dates = None
        expected_delivery_date = None
        if self.radish_include_expected_delivery:
            dates = first_rate.get("datePredictions", [])
            if not dates:
                raise ValidationError(f"No shipment dates found.")

            # The most probable date is returned. In case of a tie, the earliest is returned.
            expected_delivery_date = min(dates, key=lambda d: (-d['value'], d['date']))['date']

        return {
            'success':                          True,
            'price':                            price,
            'expected_delivery_date':           expected_delivery_date,
            'radish_expected_delivery_dates':   dates,
            'warning_message':                  None,
        }

    def radish_send_shipping(self, pickings):
        """ Send the package to the service provider

        :param pickings: A recordset of pickings
        :return list: A list of dictionaries (one per picking) containing of the form:
                         { 'exact_price': price,
                           'tracking_number': number }
        """
        self.ensure_one()
        if not pickings:
            raise UserError(_('No Radish stock pickings are selected. You might have selected orders from other carriers.'))

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        api = self._radish_order_api()
        results = []
        for picking in pickings:
            packages = []
            if len(picking.partner_id):
                if not len(picking.package_ids):
                    raise UserError(_('No packages found for picking %s.') % picking.name)
                for package in picking.package_ids:
                    if not len(package.package_type_id):
                        raise ValidationError(_('No package type found for package %s.') % package.name)
                    package_type = package.package_type_id
                    products = []
                    for quant in package.quant_ids:
                        product = quant.product_id
                        products.append({
                            'name':     product.name,
                            'quantity': quant.quantity,
                            'image':    f'{base_url}/web/image?model=product.product&id={product.id}&field=image_512',
                        })
                    packages.append({
                        'ref':        package.name,
                        'dimensions': {
                            'length': package_type.packaging_length,
                            'width':  package_type.width,
                            'height': package_type.height,
                            'unit':   package_type.length_uom_name,
                        },
                        'weight':     {
                            'value': package.weight,
                            'unit':  package_type.weight_uom_name,
                        },
                        'products':   products
                    })

            response = api.confirm_order(picking, packages)
            response_data = response.json()
            results.append({
                'exact_price':     self.fixed_price,
                'tracking_number': response_data.get('trackingRef')
            })
            try:
                # Pre generate the label
                picking._create_radish_label_attachment()
            except Exception as e:
                _logger.exception(e)

        return results

    def radish_get_tracking_link(self, picking):
        """ Get the tracking link

        :param picking: recordset of stock.picking
        :return: string: tracking link
        """
        self.ensure_one()
        return f"https://radish.coop/tracking/{picking.carrier_tracking_ref}"

    def radish_cancel_shipment(self, picking):
        """ Cancel the shipment

        :param picking: recordset of stock.picking
        :return: bool: True if the shipment was successfully canceled
        """
        self.ensure_one()
        self._radish_order_api().cancel_order(picking)
        return True

    def radish_get_package_weights(self, order):
        packages = [SimpleNamespace(weight=order._get_estimated_weight())]
        return packages

    def radish_order_picking_date(self, order):
        return None
