from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class PackageType(models.Model):
    _inherit='stock.package.type'

    package_carrier_type = fields.Selection(selection_add=[('radish', 'Radish')])

    @api.constrains('package_carrier_type', 'shipper_package_code')
    def _check_radish_name(self):
        for package in self:
            if package.package_carrier_type != 'radish':
                continue
            if not package.shipper_package_code or package.shipper_package_code.strip() == '':
                raise ValidationError(
                    _("%s doesn't have a carrier code.") % package.name)