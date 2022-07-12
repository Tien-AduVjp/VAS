from odoo import api, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    def get_action_ready_picking_tree(self):
        return self.env['ir.actions.act_window']._for_xml_id('to_stock_barcode.stock_picking_kanban_action')
