from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    
    account_asset_asset_id = fields.Many2one('account.asset.asset', string='Asset')
