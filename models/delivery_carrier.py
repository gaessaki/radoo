from odoo import models,fields, _
from odoo.exceptions import UserError, ValidationError

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(
        selection_add=[('radish', 'Radish')],
        ondelete={'radish': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})}
        )
    
    radish_merchant_key = fields.Char(string='Merchant Key')

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