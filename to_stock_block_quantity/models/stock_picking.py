from odoo import models, fields, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for r in self:
            if not r.picking_type_id.allow_process_exceeded_demand_qty:
                for move in r.move_lines:
                    rounding = move.product_uom.rounding
                    sum_qty_done = move.quantity_done
                    sum_qty_done += sum(r.move_line_ids.filtered(
                        lambda line: not line.move_id and line.product_id.id == move.product_id.id
                        ).mapped("qty_done"))
                    if fields.Float.compare(sum_qty_done, move.product_uom_qty, precision_rounding=rounding) > 0:
                        raise UserError(_("The quantity done must not be greater than the initial demand \nProduct: %s, Initial Demand: %s, Done: %s") % (
                                        move.product_id.name, move.product_uom_qty, sum_qty_done))
        return super(StockPicking, self).button_validate()
