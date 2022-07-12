from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    
    
    asset_status = fields.Selection([
        ('draft', 'Draft'), ('open', 'Running'), ('stock_in', 'Stock-In'), ('sold', 'Sold'), ('disposed', 'Disposed'), ('close', 'Close')],
        string='Asset Status', default='draft', readonly=True, tracking=True)
    
    def _prepare_production_lot_vals_when_removing_asset(self, status=False):
        self.ensure_one()
        if status:
            return {}
        return {
            'asset_status': status,
            }
