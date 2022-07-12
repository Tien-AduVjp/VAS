from odoo import  fields, models


class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order')

