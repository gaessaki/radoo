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

    def get_attachment(self):
        self.ensure_one()
        if self.delivery_type != 'radish':
            return None
        
        response = self.carrier_id._radish_order_api().fetch_labels(self.name)
        if response.status_code == 200:
            # Assuming the response contains the PDF in the body
            pdf = response.content
            b64_pdf = base64.b64encode(pdf)

            attachment = self.env['ir.attachment'].create({
                'name':         f"{RADISH_LABEL_NAME}.pdf",
                'store_fname':  f"{RADISH_LABEL_NAME}",
                'type':         'binary',
                'datas':        b64_pdf,
                'res_model':    'stock.picking',
                'res_id':       self.id,
                'mimetype':     'application/x-pdf'
            })
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
        else:
            raise ValidationError(_('Failed to retrieve the label from the delivery carrier API.'))
        
    def bulk_print_attachments(self):
        pickings = self.env['stock.picking'].browse(self.env.context.get('active_ids', [])).filtered(lambda p: p.delivery_type == 'radish')

        if not pickings:
            raise ValidationError(_('No Radish pickings selected, you might have selected orders from other carriers'))
        
        response = pickings[0].carrier_id._radish_order_api().fetch_labels(pickings.mapped('name'))

        if response.status_code == 200:
            pdf = response.content
            b64_pdf = base64.b64encode(pdf)
        
            attachment = self.env['ir.attachment'].create({
                'name':         f"{RADISH_LABEL_NAME}.pdf",
                'store_fname':  f"{RADISH_LABEL_NAME}",
                'type':         'binary',
                'datas':        b64_pdf,
                'res_model':    'stock.picking',
                'res_id':       pickings[0].id,
                'mimetype':     'application/x-pdf'
            })
            return {
                'type': 'ir.actions.act_url',
                'url': f'/web/content/{attachment.id}?download=true',
                'target': 'new',
            }
        else:
            raise ValidationError(_('Failed to retrieve the label from the delivery carrier API.'))
        

    
    # Functions below are not used
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
            ('name', '=like', 'RadishLabel%')
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
        
        radish_order_api = self.carrier_id._radish_order_api()
        response = radish_order_api.get_label(self.carrier_tracking_ref)
        if response.status_code == 200:
            # Assuming the response contains the PDF in the body
            pdf = response.content
            b64_pdf = base64.b64encode(pdf)

            # Create and attach the PDF label to the stock picking
            return self.env['ir.attachment'].create({
                'name':         f"{RADISH_LABEL_NAME}_{self.carrier_tracking_ref}.pdf",
                'store_fname':  f"{RADISH_LABEL_NAME}_{self.carrier_tracking_ref}",
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