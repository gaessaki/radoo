import base64

from odoo import models, fields, _
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def get_attachment(self):
        """
        Function from module multi_print_picking_label
        :param picking:
        :return:
        """
        self.ensure_one()
        if self.delivery_type == 'radish':
            label = self.ensure_radish_label_attachment()
            self.assert_attachment_label(label)
            return label

        return super(StockPicking, self).get_attachment()
    
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
        
        pdf = self.env.ref('cs__radish.report_radish_picking_box_label')._render_qweb_pdf(self.id)
        b64_pdf = base64.b64encode(pdf[0])
        return self.env['ir.attachment'].create({
            'name':        'RadishLabel_%s.pdf' % self.carrier_tracking_ref,
            'store_fname': 'RadishLabel_%s' % self.carrier_tracking_ref,
            'type':        'binary',
            'datas':       b64_pdf,
            'res_model':   'stock.picking',
            'res_id':      self.id,
            'mime_type':   'application/x-pdf',
        })
    
    def action_radish_set_status_sent(self):
        self.write({'radish_status': 'sent'})
        return True
