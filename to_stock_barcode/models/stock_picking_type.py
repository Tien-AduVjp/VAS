from odoo import api, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def get_action_ready_picking_tree(self):
        return self.env.ref('to_stock_barcode.stock_picking_kanban_action').read()[0]
