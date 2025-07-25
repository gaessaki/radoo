import base64
import logging

from odoo import models, _
from odoo.addons.radoo.api.models.radish_address import RadishAddress
from odoo.addons.radoo.api.models.radish_order import RadishOrder
from odoo.addons.radoo.api.models.radish_recipient import RadishRecipient
from odoo.exceptions import ValidationError
from ..api.radish_utils import radish_html2text

_logger = logging.getLogger(__name__)

RADISH_LABEL_NAME = 'RadishLabel'


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_confirm(self):
        res = super(StockPicking, self).action_confirm()

        for pick in self:
            if pick.delivery_type == 'radish' and pick.carrier_id and pick.carrier_id.integration_level == 'rate_and_ship' and pick.picking_type_code != 'incoming' and not pick.carrier_tracking_ref and pick.picking_type_id.print_label:
                try:
                    pick.carrier_id._radish_order_api().initialize_order(pick)
                except BaseException as e:
                    _logger.exception(e)

        return res

    def to_radish_address(self):
        self.ensure_one()
        address = RadishAddress(
            self.partner_id.street,
            self.partner_id.street2,
            self.partner_id.city,
            self.partner_id.state_id.name,
            self.partner_id.zip,
            self.partner_id.country_id.name,
            radish_html2text(self.note),
        )
        return address

    def to_radish_recipient(self):
        self.ensure_one()
        partner = self.partner_id
        first = partner.name or partner.commercial_company_name or ''
        last = ''
        company = partner.commercial_company_name

        current_partner = partner
        phone = current_partner.phone
        email = current_partner.email
        lang = current_partner.lang
        while current_partner and (not phone or not email or not lang):
            if not lang:
                lang = current_partner.lang
            if not phone:
                phone = current_partner.phone
                # In priority, take the same language as the partner's phone
                lang = current_partner.lang or lang
            if not email:
                email = current_partner.email
                # In priority, take the same language as the partner's email
                lang = current_partner.lang or lang

            current_partner = current_partner.parent_id
        lang = RadishRecipient.sanitize_lang(lang)
        recipient = RadishRecipient(
            first,
            last,
            company,
            phone,
            email,
            lang
        )
        return recipient

    def to_radish_order(self):
        self.ensure_one()
        recipient = self.to_radish_recipient()
        address = self.to_radish_address()
        return RadishOrder(order_ref=self.name, recipient=recipient, address=address)

    def get_radish_attachment(self):
        self.ensure_one()
        if self.delivery_type == 'radish':
            attachment = self.ensure_radish_label_attachment()
            return {
                'type':   'ir.actions.act_url',
                'url':    f'/web/content/{attachment.id}?download=true',
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

    def _create_radish_label_attachment(self):
        self.ensure_one()

        response = self.carrier_id._radish_order_api().fetch_labels(self.name)
        if response.status_code == 200:
            # Assuming the response contains the PDF in the body
            pdf = response.content
            b64_pdf = base64.b64encode(pdf)

            return self.env['ir.attachment'].create({
                'name':        f"{RADISH_LABEL_NAME}.pdf",
                'store_fname': f"{RADISH_LABEL_NAME}",
                'type':        'binary',
                'datas':       b64_pdf,
                'res_model':   'stock.picking',
                'res_id':      self.id,
                'mimetype':    'application/x-pdf'
            })
        else:
            raise ValidationError(_('Failed to retrieve the label from the delivery carrier API.'))

    # Bulk print all selected labels
    # def bulk_print_attachments(self):
    #     pickings = self.env['stock.picking'].browse(self.env.context.get('active_ids', [])).filtered(lambda p: p.delivery_type == 'radish')

    #     if not pickings:
    #         raise ValidationError(_('No Radish pickings selected, you might have selected orders from other carriers'))

    #     response = pickings[0].carrier_id._radish_order_api().fetch_labels(pickings.mapped('name'))

    #     if response.status_code == 200:
    #         pdf = response.content
    #         b64_pdf = base64.b64encode(pdf)

    #         attachment = self.env['ir.attachment'].create({
    #             'name':         f"{RADISH_LABEL_NAME}.pdf",
    #             'store_fname':  f"{RADISH_LABEL_NAME}",
    #             'type':         'binary',
    #             'datas':        b64_pdf,
    #             'res_model':    'stock.picking',
    #             'res_id':       pickings[0].id,
    #             'mimetype':     'application/x-pdf'
    #         })
    #         return {
    #             'type': 'ir.actions.act_url',
    #             'url': f'/web/content/{attachment.id}?download=true',
    #             'target': 'new',
    #         }
    #     else:
    #         raise ValidationError(_('Failed to retrieve the label from the delivery carrier API.'))
