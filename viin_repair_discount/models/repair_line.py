from odoo import api, fields, models


class RepairLine(models.Model):
    _inherit = 'repair.line'

    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)

    @api.depends('discount')
    def _compute_price_subtotal(self):
        repair_line_no_discount = self.filtered(lambda repair_line: not repair_line.discount)
        super(RepairLine, repair_line_no_discount)._compute_price_subtotal()

        repair_line_with_discount = self - repair_line_no_discount
        for r in repair_line_with_discount:
            price_reduce = r.price_unit * (1.0 - r.discount / 100.0)
            taxes = r.tax_id.compute_all(price_reduce, r.repair_id.pricelist_id.currency_id, r.product_uom_qty, r.product_id, r.repair_id.partner_id)
            r.price_subtotal = taxes['total_excluded']
