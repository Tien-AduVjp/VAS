from odoo import fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    equipment_ids = fields.Many2many('maintenance.equipment', string='Equipments', readonly=True,
                                     help="Equipments that refer this move")

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super(StockMove, self)._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        res.update({
            'can_create_equipment': self.picking_type_id.can_create_equipment and self.product_id.can_be_equipment
            })
        return res
    
    def _generate_serial_move_line_commands(self, lot_names, origin_move_line=None):
        res = super(StockMove, self)._generate_serial_move_line_commands(lot_names,origin_move_line)   
        if self.picking_type_id.can_create_equipment and self.product_id.can_be_equipment:
            for r in res:
                r[2]['can_create_equipment'] = True
        return res