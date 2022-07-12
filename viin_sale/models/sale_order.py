from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    days_to_confirm = fields.Float('Days To Confirm', compute='_compute_days_to_confirm', store=True,
                                   help="Number of days counting from Creation Date to Ordered Date of an order.")

    @api.depends('date_order', 'create_date')
    def _compute_days_to_confirm(self):
        for r in self:
            delta = r.date_order - r.create_date
            r.days_to_confirm = delta.days + delta.seconds / 3600 / 24
