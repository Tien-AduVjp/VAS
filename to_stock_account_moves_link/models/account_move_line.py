from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    stock_move_id = fields.Many2one('stock.move', string='Stock Move', readonly=True,
                                    related='move_id.stock_move_id', store=True)
    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking',
                                       related='stock_move_id.picking_id', readonly=True, store=True)