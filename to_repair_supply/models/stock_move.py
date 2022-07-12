from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'

    repair_line_id = fields.Many2one('repair.line', string='Repair Line')
    repair_id = fields.Many2one('repair.order', string='Repair')
