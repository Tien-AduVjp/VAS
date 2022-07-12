from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    repair_id = fields.Many2one('repair.order', string='Repair', readonly=True)

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[('repair_supply', 'Repair Supply Operation')], ondelete={'repair_supply': 'cascade'})
