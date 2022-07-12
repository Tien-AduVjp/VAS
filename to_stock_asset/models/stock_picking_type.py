from odoo import fields, models


class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    code = fields.Selection(selection_add=[('asset_allocation', 'Asset Allocation')],
                            ondelete={'asset_allocation': 'cascade'})
