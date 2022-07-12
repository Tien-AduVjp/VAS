from odoo import api, fields, models


class RepairFee(models.Model):
    _inherit = 'repair.fee'

    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)

    @api.depends('discount')
    def _compute_price_subtotal(self):
        repair_fee_no_discount = self.filtered(lambda repair_fee: not repair_fee.discount)
        super(RepairFee, repair_fee_no_discount)._compute_price_subtotal()

        repair_fee_with_discount = self - repair_fee_no_discount
        for r in repair_fee_with_discount:
            price_reduce = r.price_unit * (1.0 - r.discount / 100.0)
            taxes = r.tax_id.compute_all(price_reduce, r.repair_id.pricelist_id.currency_id, r.product_uom_qty, r.product_id, r.repair_id.partner_id)
            r.price_subtotal = taxes['total_excluded']
