from odoo import models, fields, api

class Radoo(models.Model):
    _name = 'radoo'
    _description = 'Radish Integration'

    name = fields.Char(string='Carrier Name')
    api_key = fields.Char(string='API Key')
    base_url = fields.Char(string='API Base URL')
    active = fields.Boolean(string='Active', default=True)

    