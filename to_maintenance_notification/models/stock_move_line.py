from odoo import fields, models, api, _
from odoo.exceptions import UserError


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def create_equipment(self):
        equipment_ids = super(StockMoveLine, self).create_equipment()
        equipment_ids._compute_next_maintenance()
        return equipment_ids