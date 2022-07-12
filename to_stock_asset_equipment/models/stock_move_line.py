from odoo import fields, models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def write(self, vals):
        res = super(StockMoveLine, self).write(vals)
        for r in self.filtered(lambda r: r.account_asset_asset_id and r.lot_id.equipment_id):
            r.lot_id.equipment_id.write({'assign_date': fields.Date.context_today(self, r.date)})
        return res
