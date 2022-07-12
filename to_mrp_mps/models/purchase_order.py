from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    date_planned_mps = fields.Datetime(string='Scheduled Date', compute='_compute_date_planned_mps',
                                       store=True, index=True)

    @api.depends('order_line.date_planned', 'date_order')
    def _compute_date_planned_mps(self):
        for r in self:
            min_planned_date = r.order_line._get_min_planned_date()
            r.date_planned_mps = min_planned_date or r.date_order
