from odoo import models, fields, api, _
from odoo.tools import float_compare


class VoucherVoucher(models.Model):
    _inherit = 'voucher.voucher'

    pos_order_line_id = fields.Many2one('pos.order.line', string='Pos Order Line')
    pos_order_id = fields.Many2one('pos.order', related='pos_order_line_id.order_id', store=True , string='Pos Order', index=True)
    pos_config_id = fields.Many2one('pos.config', string='Pos Config', related='pos_order_id.config_id', store=True, index=True)
    pos_session_id = fields.Many2one('pos.session', string='Pos Session', related='pos_order_id.session_id', store=True, index=True)
    partner_id = fields.Many2one('res.partner', string='Partner', related='pos_order_id.partner_id', store=True, index=True)
    user_id = fields.Many2one('res.users', string='Sale Person', related='pos_order_id.user_id', store=True, index=True)
    price = fields.Float(compute='_compute_price', store=True)

    @api.depends('pos_order_line_id', 'pos_order_line_id.price_unit')
    def _compute_price(self):
        for r in self:
            r.price = r.pos_order_line_id and r.pos_order_line_id.price_unit or 0.0

    @api.model
    def check_voucher(self, voucher_ids):
        res = {}
        vouchers = self.browse(voucher_ids)
        for voucher in vouchers:
            if voucher.state == 'expired':
                res['error'] = True
                res['message'] = _('This Voucher is already expired.')
            elif voucher.state == 'used' and (voucher.voucher_type_id.payable_once or \
                    float_compare(voucher.used_amount, voucher.value, precision_rounding=self.env.company.currency_id.rounding) == 0):
                res['error'] = True
                res['message'] = _('This Voucher has been used.')
            elif voucher.state == 'inactivated':
                res['error'] = True
                res['message'] = _('This Voucher has not been activated.')
            elif voucher.current_stock_location_id.usage != 'customer':
                res['error'] = True
                res['message'] = _('This Voucher is still in your stock. Hence, it cannot be used..')
            else:
                res['error'] = False
                res['value'] = voucher.value - voucher.used_amount
                res['voucher_id'] = voucher.id
            if res['error']:
                break
        return res
