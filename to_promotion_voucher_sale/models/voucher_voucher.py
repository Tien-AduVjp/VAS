from odoo import models, fields, api, _


class VoucherVoucher(models.Model):
    _inherit = 'voucher.voucher'

    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line')
    sale_order_id = fields.Many2one('sale.order', related='sale_order_line_id.order_id', store=True , string='Sale Order', index=True)
    partner_id = fields.Many2one('res.partner', string='Partner', related='sale_order_id.partner_id', store=True, index=True)
    price = fields.Float(string='Sold Price', compute='_compute_price', store=True,
                         help="The actual price when selling this promotion voucher")

    @api.depends('sale_order_line_id', 'sale_order_line_id.price_unit')
    def _compute_price(self):
        for r in self:
            r.price = r.sale_order_line_id and r.sale_order_line_id.price_unit or 0.0

