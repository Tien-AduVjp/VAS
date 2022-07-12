from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    stock_picking_id = fields.Many2one('stock.picking', string='Stock Picking',
                                       related='stock_move_id.picking_id', store=True)
    ####