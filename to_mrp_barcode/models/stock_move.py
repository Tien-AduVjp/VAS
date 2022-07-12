from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    lot_barcode = fields.Char(related="lot_id.name", string='Barcode Number')
