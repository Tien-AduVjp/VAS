from odoo import models, fields


class StockMove(models.Model):
    _inherit = 'stock.move'
    
    account_move_line_ids = fields.One2many('account.move.line', 'stock_move_id', string='Account Move Lines')
