from odoo import fields, models, api
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
   _inherit = 'res.config.settings'

   merchant_key = fields.Char(string="Merchant Key", config_parameter='radoo.merchant_key')

   def action_validate_merchant_key(self):
      merchant_key = self.merchant_key

      if not merchant_key:
         raise UserError("Merchant Key is required.")
      
      from odoo.addons.radoo.api.radoo_api import validate_merchant_key

      try: 
         if validate_merchant_key(merchant_key):
            return {}
         else: 
            raise UserError("Merchant Key validation failed.")
         
      except Exception as e:
            raise UserError(f"Error during validation: {str(e)}")


