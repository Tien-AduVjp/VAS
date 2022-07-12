from odoo import fields, models, api


class AffiliateCommissionLine(models.Model):
    _inherit = 'affiliate.commission.line'

    sale_order_line_id = fields.Many2one('sale.order.line', string='Sales Order Line', readonly=True)

    @api.depends('sale_order_line_id.price_unit', 'sale_order_line_id.product_uom_qty', 'sale_order_line_id.price_subtotal')
    def _compute_total(self):
        super(AffiliateCommissionLine, self)._compute_total()
        for r in self.filtered(lambda l: l.sale_order_line_id):
            compute_aff_method = r.commission_id.company_id.compute_aff_method
            if compute_aff_method == 'before_discount':
                r.total = r.sale_order_line_id.price_unit * r.sale_order_line_id.product_uom_qty
            else:
                r.total = r.sale_order_line_id.price_subtotal

