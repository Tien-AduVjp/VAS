from odoo import models, fields


class Picking(models.Model):
    _inherit = "stock.picking"

    replenishment_request_ids = fields.Many2many('replenishment.request', 'replenishment_request_stock_picking_rel', 'picking_id', 'request_id',
                                                 string='Replenishment Requests')
