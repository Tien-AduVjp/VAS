from odoo import models


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _prepare_equipment_data(self):
        res = super(StockMoveLine, self)._prepare_equipment_data()
        res['maintenance_schedule_ids'] = [(6, 0, self.product_id.maintenance_schedule_ids.ids)]
        return res

    def create_equipment(self):
        equipment_ids = super(StockMoveLine, self).create_equipment()
        for e in equipment_ids.filtered(lambda e: e.maintenance_schedule_ids and e.lot_id):
            e.lot_id.maintenance_schedule_ids = e.maintenance_schedule_ids
        return equipment_ids
