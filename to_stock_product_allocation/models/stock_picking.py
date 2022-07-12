from odoo import models, fields, api


class Picking(models.Model):
    _inherit = "stock.picking"

    stock_allocation_request_ids = fields.Many2many('stock.allocation.request', 'stock_allocation_request_stock_picking_rel', 'picking_id', 'request_id',
                                                 string='Stock Allocation Requests')

    def action_done(self):
        super(Picking, self).action_done()
        self.mapped('stock_allocation_request_ids')._check_done()
