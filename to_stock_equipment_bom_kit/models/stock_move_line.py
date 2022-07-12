# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools import float_compare

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _find_parent_equipment(self):
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        product_set_line_ids = False
        picking_id = self.move_id.picking_id
        while picking_id:
            if picking_id.product_set_line_ids:
                product_set_line_ids = picking_id.product_set_line_ids
                break
            else:
                picking_id = picking_id.backorder_id
        if product_set_line_ids:
            product_set_ids = product_set_line_ids.filtered(lambda x: x.purchase_line_id == self.move_id.purchase_line_id and \
                                                            self.move_id.product_id.id in x.line_ids.mapped('product_id').ids and \
                                                            x.can_create_equipment)
            for set in product_set_ids:
                for line in set.line_ids:
                    if line.product_id == self.move_id.product_id and float_compare(line.remaining_qty, 0.0, precision_digits=precision) == 1:
                        return set, line
        return False, False

    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        for r in self.exists():
            if r.equipment_id:
                product_set_id, line_id = r._find_parent_equipment()
                if product_set_id:
                    equipment_id = product_set_id.equipment_id
                    if not equipment_id:
                        equipment_id = self.env['maintenance.equipment'].create({'name': product_set_id.name})
                        product_set_id.write({'equipment_id': equipment_id.id})
                    r.equipment_id.write({'parent_id': equipment_id.id})
                    line_id.write({'remaining_qty': line_id.remaining_qty - 1})
                
