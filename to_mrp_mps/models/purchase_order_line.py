from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _get_min_planned_date(self):
        date_list = [r.date_planned for r in self if r.date_planned]
        min_planned_date = min(date_list) if date_list else False
        return min_planned_date
