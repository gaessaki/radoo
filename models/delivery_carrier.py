from odoo import models,fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.radoo.api.radish_merchant_api import RadishMerchantApi
from odoo.addons.radoo.api.radish_order_api import RadishOrderApi
from odoo import models,fields, _
from odoo.exceptions import UserError, ValidationError

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
                title = _("Successfully!")
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
        return RadishMerchantApi('merchants', self.radish_merchant_key)
    
    def _radish_order_api(self):
        return RadishOrderApi('merchants/orders', self.radish_merchant_key)
    
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