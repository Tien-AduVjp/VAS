from odoo import models, fields, api


class Picking(models.Model):
    _inherit = 'stock.picking'

    product_set_line_ids = fields.One2many('product.set', 'picking_id', string='Product Set', groups='stock.group_stock_user',
                                           compute='_compute_product_set_line_ids', store=True, readonly=False)

    @api.depends('move_lines.product_uom_qty')
    def _compute_product_set_line_ids(self):
        for r in self:
            if r.purchase_id:
                r.product_set_line_ids.unlink()
                r.purchase_id._create_product_set(r.purchase_id.order_line)
