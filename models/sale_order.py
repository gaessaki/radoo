from odoo import models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()

        for picking in self.picking_ids:
            if picking.delivery_type == 'radish':
                picking.carrier_id._radish_order_api().create_order(picking)

        return res