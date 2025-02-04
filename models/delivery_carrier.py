import base64
import json
import logging
from odoo import models,fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.radoo.api.radish_merchant_api import RadishMerchantApi
from odoo.addons.radoo.api.radish_order_api import RadishOrderApi
from odoo import models,fields, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[('radish', 'Radish')],
        ondelete={'radish': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})}
        )
    
    radish_merchant_key = fields.Char(
        string='Merchant Key',
        help='The merchant key for the Radish API. You can request a merchant key from your Radish relationship manager.',
    )

    radish_expected_business_days = fields.Integer(
        string='Anticipated Number of Delivery Days',
        help='The anticipated number of business days after a pickup is confirmed with which to compute the delivery date.',
        default=1,
    )

    radish_shipping_deadline_time = fields.Datetime(
        string='Shipping Cutoff', 
        help="The cutoff time after which the delivery will be pushed to the next business day.", 
        default="2025-01-10 15:00:00"
    )

    @api.constrains('radish_merchant_key')
    def action_validate_merchant_key(self):
        merchant_key = self.radish_merchant_key
        merchant_api = self._radish_merchant_api()

        if not merchant_key:
            raise ValidationError("Merchant Key is required.")
        try: 
            if merchant_api.validate_merchant_key(merchant_key):
                title = _("Success!")
                message = _("Merchant Key Validated Successfully!")
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': title,
                        'message': message,
                        'sticky': False,
                    }
                }
        except Exception as e:
                raise ValidationError(f"Error during validation: {str(e)}")

    def _radish_merchant_api(self):
        return RadishMerchantApi('merchants', merchant_key=self.radish_merchant_key)
    
    def _radish_order_api(self):
        return RadishOrderApi('merchants/orders', merchant_key=self.radish_merchant_key)
    
    def radish_rate_shipment(self, order):
        """Compute the price of the order shipment

        :param order: recordset of sale.order
        :return: dict: {'success': boolean,
                       'price': a float,
                       'error_message': a string containing an error message,
                       'warning_message': a string containing a warning message}
        """
        self.ensure_one()
        
        price = self.fixed_price
        return {
            'success':         True,
            'price':           price,
            'warning_message': None,
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
                    packages.append({
                        'ref': package.name,
                        'dimensions': {
                            'length': package_type.packaging_length,
                            'width': package_type.width,
                            'height': package_type.height,
                            'unit': package_type.length_uom_name,
                        },
                        'weight': {
                            'value': package.weight,
                            'unit': package_type.weight_uom_name,
                        }
                    })

            response = api.confirm_order(picking, packages)

            if response.status_code != 200:
                raise ValidationError(_('Failed to send the order to the delivery carrier.'))
            response_data = response.json()
            results.append({
                'exact_price': self.fixed_price,
                'tracking_number': response_data.get('trackingRef')
            })
            try:
                # Pre generate the label
                picking.with_delay().ensure_radish_label_attachment()
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
        raise ValidationError(_('Please contact Radish customer support to cancel the shipment.'))
    
    def _radish_get_default_custom_package_code(self):
        """ Some delivery carriers require a prefix to be sent in order to use custom
        packages (ie not official ones). This optional method will return it as a string.
        """
        self.ensure_one()
        return False
