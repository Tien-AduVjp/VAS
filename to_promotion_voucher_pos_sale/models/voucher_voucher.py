from odoo import models, api, _
from odoo.exceptions import ValidationError


class VoucherVoucher(models.Model):
    _inherit = 'voucher.voucher'
    
    @api.constrains('pos_order_line_id', 'sale_order_line_id')
    def _check_constrains_pos_sale_order_line(self):
        for r in self:
            if r.pos_order_line_id and r.sale_order_line_id:
                raise ValidationError(_("Voucher '%s' can not be linked to both of pos order line and sale order line at the same time.") % r.name)
    
    @api.depends('pos_order_line_id', 'pos_order_line_id.price_unit', 'sale_order_line_id', 'sale_order_line_id.price_unit')
    def _compute_price(self):
        for r in self:
            if r.pos_order_line_id:
                r.price = r.pos_order_line_id.price_unit
            elif r.sale_order_line_id:
                r.price = r.sale_order_line_id.price_unit
            else:
                r.price = 0.0

            