from odoo import fields, models


class AssetAssetReport(models.Model):
    _inherit = "asset.asset.report"


    lot_id = fields.Many2one('stock.production.lot', string='Lot/Seria Number', readonly=True)

    def _select(self):
        select_str = super(AssetAssetReport, self)._select()
        select_str += """, a.production_lot_id as lot_id """
        return select_str

    def _from(self):
        from_str = super(AssetAssetReport, self)._from()
        from_str += """ left join stock_production_lot lot on (a.production_lot_id=lot.id) """
        return from_str

    def _group_by(self):
        group_by_str = super(AssetAssetReport, self)._group_by()
        group_by_str += """, a.production_lot_id """
        return group_by_str
    
