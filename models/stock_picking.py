import base64
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.radoo.api.radish_order_api import RadishOrderApi

RADISH_LABEL_NAME = 'RadishLabel'

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    radish_order_status = fields.Selection([
        ('placed', 'Pending Pickup'),
        ('ready', 'Ready'),
        ('done', 'Delivered'),
        ('cancelled', 'Cancelled')
    ], string='Radish Status')

    def action_confirm(self):
        res = super(StockPicking, self).action_confirm()

        if self.delivery_type == 'radish':
            self.carrier_id._radish_order_api().initialize_order(self)

        return res

    def get_radish_attachment(self):
        self.ensure_one()
        if self.delivery_type == 'radish':
            attachment = self.ensure_radish_label_attachment()
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }

    def ensure_radish_label_attachment(self):
        self.ensure_one()
        if self.delivery_type != 'radish':
            return None
        attachment = self._find_radish_label_attachment()
        if not len(attachment):
            attachment = self._create_radish_label_attachment()
        return attachment
    
    def _find_radish_label_attachment(self):
        self.ensure_one()
        return self.env['ir.attachment'].search([
            ('res_model', '=', 'stock.picking'),
            ('res_id', '=', self.id),
            ('name', '=like', f'{RADISH_LABEL_NAME}%')
        ],
            order='create_date desc',
            limit=1,
        )
    
    def _assert_must_and_can_create_radish_label_attachment(self):
        self.ensure_one()
        if not self.carrier_tracking_ref:
            if self.picking_type_id.code == 'outgoing':
                raise ValidationError(_("A tracking reference is required to print %s's label.") % self.name)
            return None
        
    def _create_radish_label_attachment(self):
        self.ensure_one()
        self._assert_must_and_can_create_radish_label_attachment()
        
        response = self.carrier_id._radish_order_api().fetch_labels(self.name)
        if response.status_code == 200:
            # Assuming the response contains the PDF in the body
            pdf = response.content
            b64_pdf = base64.b64encode(pdf)

            return self.env['ir.attachment'].create({
                'name':         f"{RADISH_LABEL_NAME}.pdf",
                'store_fname':  f"{RADISH_LABEL_NAME}",
                'type':         'binary',
                'datas':        b64_pdf,
                'res_model':    'stock.picking',
                'res_id':       self.id,
                'mimetype':     'application/x-pdf'
            })
        else:
            raise ValidationError(_('Failed to retrieve the label from the delivery carrier API.'))
    
    def radish_set_status_sent(self):
        raise NotImplementedError("This method should be implemented by the Radish module.")
    
    def _check_carrier_details_compliance(self):
        for picking in self:
            if picking.delivery_type == 'radish':
                picking._assert_must_and_can_create_radish_label_attachment()

        super()._check_carrier_details_compliance()