from odoo import models
from odoo.tools import float_round


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _prepare_product_set(self, line, i, bom):
        picking_ids = line.order_id.picking_ids
        picking_id = False
        if picking_ids:
            picking_id = picking_ids[len(picking_ids) - 1]
            return {
                    'name': line.product_id.name + ' (%s)' % i,
                    'sequence': i,
                    'product_id': line.product_id.id,
                    'product_qty': 1,
                    'product_uom': line.product_id.uom_id.id,
                    'picking_id': picking_id and picking_id.id or False,
                    'bom_id': bom.id,
                    'can_create_equipment': picking_id.picking_type_id.can_create_equipment and line.product_id.can_be_equipment,
                    'purchase_line_id': line.id
                }
        return False

    def _prepare_product_set_line(self, bom_line, product_set_id):
        qty = bom_line.product_uom_id._compute_quantity(bom_line.product_qty, bom_line.product_id.uom_id) / \
                bom_line.bom_id.product_uom_id._compute_quantity(bom_line.bom_id.product_qty, bom_line.bom_id.product_tmpl_id.uom_id)
        return {
                    'product_set_id': product_set_id.id,
                    'product_qty': qty,
                    'remaining_qty': qty,
                    'product_uom': bom_line.product_id.uom_id.id,
                    'product_id': bom_line.product_id.id,
                }

    def _create_product_set(self, order_line):
        BOM = self.env['mrp.bom'].sudo()
        ProductSet = self.env['product.set'].sudo()
        ProductSetLine = self.env['product.set.line'].sudo()
        for line in order_line:
            boms = BOM._bom_find(product_tmpl=line.product_id.product_tmpl_id, bom_type='phantom')
            if boms:
                prec = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                qty_round = float_round(line.product_uom._compute_quantity(line.product_qty, line.product_id.uom_id), precision_digits=prec)
                for i in range(int(qty_round)):
                    vals = self._prepare_product_set(line, i + 1, boms[0])
                    if vals:
                        product_set_id = ProductSet.create(vals)
                        for bom_line in product_set_id.bom_id.bom_line_ids:
                            line_vals = self._prepare_product_set_line(bom_line, product_set_id)
                            ProductSetLine.create(line_vals)

    def button_confirm(self):
        res = super(PurchaseOrder, self).button_confirm()
        for r in self:
            r._create_product_set(r.order_line)
        return res
