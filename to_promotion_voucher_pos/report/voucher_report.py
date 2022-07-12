from odoo import models, fields


class VoucherReport(models.Model):
    _inherit = 'voucher.report'

    pos_order_id = fields.Many2one('pos.order', string='PoS Order', readonly=True)
    pos_config_id = fields.Many2one('pos.config', string='Point of Sales', readonly=True)
    pos_session_id = fields.Many2one('pos.session', string='PoS Session', readonly=True)
    partner_id = fields.Many2one('res.partner', string='Partner', readonly=True)
    user_id = fields.Many2one('res.users', string='Sales Person', readonly=True)

    def _select(self):
        select_str = super(VoucherReport, self)._select()
        select_str += ',v.pos_order_id, v.pos_config_id, v.pos_session_id, v.partner_id, v.user_id'
        return select_str

