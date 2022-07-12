from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    can_assign_equipment = fields.Boolean(compute='_compute_can_assign_equipment', store=True,
                                         help="A technical field to show/hide assignment info.")

    @api.depends('picking_type_id', 'move_line_ids.lot_id')
    def _compute_can_assign_equipment(self):
        for r in self:
            if r.location_dest_id.usage == 'asset_allocation' and r.move_line_ids.lot_id.sudo().equipment_id:
                r.can_assign_equipment = True
            else:
                r.can_assign_equipment = False
