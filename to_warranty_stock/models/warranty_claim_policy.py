from odoo import models, fields


class WarrantyClaimPolicy(models.Model):
    _inherit = 'warranty.claim.policy'

    stock_production_lot_id = fields.Many2one('stock.production.lot', string='Stock Production Lot')
