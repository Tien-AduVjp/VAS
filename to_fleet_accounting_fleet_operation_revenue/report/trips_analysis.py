from odoo import models, fields


class FleetTripsAnalysis(models.Model):
    _inherit = 'fleet.trips.analysis'

    sum_revenue = fields.Float(string='Revenue', readonly=True)
    profit_loss = fields.Float(string='P&L', readonly=True)

    def _select_sum_revenues(self):
        return """
            WITH currency_rate as (%s)
            SELECT
                SUM(fvr.amount / COALESCE(cr.rate, 1.0)) as amount
            FROM fleet_vehicle_revenue AS fvr
            JOIN fleet_vehicle_trip AS fvt ON fvt.id = fvr.trip_id
            LEFT JOIN currency_rate cr on (cr.currency_id = fvr.currency_id and
                    cr.company_id = fvr.company_id and
                    cr.date_start <= coalesce(fvr.date, now()) and
                    (cr.date_end is null or cr.date_end > coalesce(fvr.date, now())))
            WHERE fvt.id = t.id
        """ % (self.env['res.currency']._select_companies_rates(),)

    def _select(self):
        select_str = super(FleetTripsAnalysis, self)._select()
        revenues = self._select_sum_revenues()
        costs = self._select_sum_costs()

        select_str += """,
                (%s) AS sum_revenue,
                ((%s) - (%s)) AS profit_loss
        """ % (revenues, revenues, costs)
        return select_str

