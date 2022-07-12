from odoo import models, fields


class Picking(models.Model):
    _inherit = "stock.picking"

    approvals_id = fields.Many2many('approval.request', 'stock_allocation_request_stock_picking_rel', 'picking_id', 'approval_id',
                                                 string='Stock Allocation Requests')

    def _action_done(self):
        res = super(Picking, self)._action_done()
        if self.approvals_id.type == 'stock_allocation':
            self.approvals_id._check_done()
        return res
