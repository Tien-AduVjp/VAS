from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    mobile_token_ids = fields.One2many('mobile.device.token', 'partner_id', string='Mobile Tokens', readonly=True)

    def _prepare_mobile_notification_detail_vals(self):
        self.ensure_one()
        return {
            'partner_id': self.id,
            'state': 'new',
            'retried_count': 0,
            'message_id': '',
            'error_message': '',
            }
