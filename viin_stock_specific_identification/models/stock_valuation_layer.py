from odoo import fields, models


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    lot_id = fields.Many2one('stock.production.lot', string='Lot/Serial Number', readonly=True)
