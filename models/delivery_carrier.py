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
        help='Merchant Key for Radish API. You can request a merchant key from your Radish relationship manager.',
    )

    radish_expected_business_days = fields.Integer(
        string='Expected delivery date business days',
        help='Number of business days to add to the validation date to compute the expected delivery date.',
        default=1,
    )

    radish_shipping_deadline_time = fields.Datetime(
        string='Shipping deadline time', 
        help="If the picking is validated after this time, we will add another extra day to the expected scheduled date.", 
        default="2025-01-10 19:00:00"
    )

    radish_minimum_order = fields.Boolean(
        string='Minimum Order Amount Required',
        help='Check if the carrier has a minimum order amount.',
        default=False,
    )

    radish_minimum_order_amount = fields.Float(
        string='Minimum Order Amount',
        help='Minimum order amount to use this carrier.',
        default=0.0,
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
            raise ValidationError(_('No Radish pickings selected, you might have selected orders from other carriers'))
        
        results = []
        for picking in pickings:
            response = self._radish_order_api().confirm_orders(picking.name)
            if response.status_code != 200:
                raise ValidationError(_('Failed to send the order to the delivery carrier API.'))
            response_data = response.json()
            results.append({
                'exact_price': self.fixed_price,
                'tracking_number': response_data[0].get('trackingRef')
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
        raise ValidationError(_('Please contact Radish support to cancel the shipment.'))
    
    def _radish_get_default_custom_package_code(self):
        """ Some delivery carriers require a prefix to be sent in order to use custom
        packages (ie not official ones). This optional method will return it as a string.
        """
        self.ensure_one()
        return False
