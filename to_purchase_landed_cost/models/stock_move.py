from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    landed_cost_adjustment_line_ids = fields.One2many('stock.valuation.adjustment.lines', 'move_id', string='Landed Cost Adjustment Lines')
