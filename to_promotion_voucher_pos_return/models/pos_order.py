from odoo import models, fields, api

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    amount_return_voucher = fields.Float(string='Amount Paid by Voucher (Non-Refundable)', digits=0, compute='_onchange_amount_all')
    original_amount_total = fields.Float(string='Original Amount Total', compute='_onchange_amount_all', digits=0)
    
    @api.depends('payment_ids', 'lines.price_subtotal_incl', 'lines.discount', 'refund_original_order_id')
    def _onchange_amount_all(self):
        super(PosOrder, self)._onchange_amount_all()
        for r in self:
            r.amount_return_voucher = 0.00
            r.original_amount_total = r.amount_total
            if r.refund_original_order_id and r.refund_original_order_id.amount_paid_by_voucher > 0:
                r.update({'amount_total': r.amount_total + r.refund_original_order_id.amount_paid_by_voucher})
                r.amount_return_voucher = -r.refund_original_order_id.amount_paid_by_voucher