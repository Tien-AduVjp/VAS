from odoo import models

class FleetTripsAnalysis(models.Model):
    _inherit = 'fleet.trips.analysis'

    def _select_sum_costs(self):
        return """
            WITH currency_rate as (%s)
            SELECT
                SUM(fvs.amount / COALESCE(cr.rate, 1.0)) as amount
            FROM fleet_vehicle_log_services AS fvs
            JOIN fleet_vehicle_trip AS fvt ON fvt.id = fvs.trip_id
            LEFT JOIN currency_rate cr on (cr.currency_id = fvs.currency_id and
                    cr.company_id = fvs.company_id and
                    cr.date_start <= coalesce(fvs.date, now()) and
                    (cr.date_end is null or cr.date_end > coalesce(fvs.date, now())))
            WHERE fvt.id = t.id
        """ % (self.env['res.currency']._select_companies_rates(),)
