from odoo import models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    def button_validate(self):
        self.ensure_one()
        if not self.picking_type_id.allow_process_exceeded_demand_qty:
            for move in self.move_lines:
                rounding = move.product_uom.rounding
                sum_qty_done = move.quantity_done
                sum_qty_done += sum(self.move_line_ids.filtered(
                    lambda line: not line.move_id and line.product_id.id == move.product_id.id
                    ).mapped("qty_done"))
                if float_compare(sum_qty_done, move.product_uom_qty, precision_rounding=rounding) == 1:
                    raise UserError(_("The quantity done must not be greater than the initial demand \nProduct: %s, Initial Demand: %s, Done: %s") % (
                                    move.product_id.name, move.product_uom_qty, sum_qty_done))
        return super(StockPicking, self).button_validate()
