from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    usage = fields.Selection(selection_add=[('asset_allocation', 'Asset Allocation')],
                             ondelete={'asset_allocation': 'cascade'})
