from odoo import models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.depends('vehicle_cost_id.trip_id', 'vehicle_revenue_id.trip_id')
    def _compute_trip_id(self):
        for r in self:
            if r.vehicle_revenue_id.trip_id:
                r.trip_id = r.vehicle_revenue_id.trip_id
            else:
                super(AccountAnalyticLine, r)._compute_trip_id()

