from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.addons.radoo.api.radish_merchant_api import RadishMerchantApi


class ResConfigSettings(models.TransientModel):
   _inherit = 'res.config.settings'

   merchant_key = fields.Char(string="Merchant Key", config_parameter='radoo.merchant_key')

   def action_validate_merchant_key(self):
      merchant_key = self.merchant_key
      merchant_api = self._radish_merchant_api()

      if not merchant_key:
         raise UserError("Merchant Key is required.")
      try: 
         if merchant_api.validate_merchant_key(merchant_key):
            return {}
      except Exception as e:
            raise UserError(f"Error during validation: {str(e)}")

   def _radish_merchant_api(self):
      return RadishMerchantApi('merchants')
