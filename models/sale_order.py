# -*- coding: utf-8 -*-
from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pickup_date = fields.Text(string='Pickup date')
