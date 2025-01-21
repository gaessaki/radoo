from odoo import fields, models

class ResConfigSettings(models.TransientModel):
   _inherit = 'res.config.settings'

   merchant_key = fields.Char(string="Merchant Key", config_parameter='radoo.merchant_key')


