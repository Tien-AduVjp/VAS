from odoo import  fields, models


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    sale_order_id = fields.Many2one('sale.order', string='Sale Order')

