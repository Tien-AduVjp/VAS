from odoo import models, fields


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    customer_id = fields.Many2one('res.partner', string="Customer")
    supplier_id = fields.Many2one('res.partner', string="Supplier")
    country_state_id = fields.Many2one('res.country.state', string="Service State",
                                       help="A country state where the product of this lot serves")
