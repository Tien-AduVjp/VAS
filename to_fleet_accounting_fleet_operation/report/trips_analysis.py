from odoo import models

class FleetTripsAnalysis(models.Model):
    _inherit = 'fleet.trips.analysis'

    def _select_sum_costs(self):
        return """
            WITH currency_rate as (%s)
            SELECT
                SUM(fvc.amount / COALESCE(cr.rate, 1.0)) as amount
            FROM fleet_vehicle_cost AS fvc
            JOIN fleet_vehicle_trip AS fvt ON fvt.id = fvc.trip_id
            LEFT JOIN currency_rate cr on (cr.currency_id = fvc.currency_id and
                    cr.company_id = fvc.company_id and
                    cr.date_start <= coalesce(fvc.date, now()) and
                    (cr.date_end is null or cr.date_end > coalesce(fvc.date, now())))
            WHERE fvt.id = t.id
        """ % (self.env['res.currency']._select_companies_rates(),)
