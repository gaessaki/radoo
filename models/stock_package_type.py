# -*- coding: utf-8 -*-
from odoo import fields, models


class PackageType(models.Model):
    _inherit = 'stock.package.type'

    package_carrier_type = fields.Selection(
        selection_add=[('radish', 'Radish')]
    )
