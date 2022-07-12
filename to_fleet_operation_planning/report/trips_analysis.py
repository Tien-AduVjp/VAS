from odoo import models, fields, api
from odoo import tools


class FleetTripsAnalysis(models.Model):
    _name = 'fleet.trips.analysis'
    _description = "Fleet Trips Analysis"
    _order = 'start_date desc'
    _auto = False

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', readonly=True)
    start_date = fields.Datetime('Start Date', readonly=True)
    end_date = fields.Datetime('End Date', readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', readonly=True)
    driver_id = fields.Many2one('res.partner', string='Driver', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', readonly=True)
    route_id = fields.Many2one('route.route', string='Route', readonly=True)
    est_distance = fields.Float('Est. Distance', readonly=True)
    est_trip_time = fields.Float('Est. Duration', readonly=True)
    operation_duration = fields.Float('Actual Duration', readonly=True)
    time_deviation = fields.Float('Time Deviation', readonly=True)
    actual_distance = fields.Float('Actual Distance', readonly=True)
    distance_deviation = fields.Float('Distance Deviation', readonly=True)
    odometer_value = fields.Float('Odometer Value', readonly=True)
    odometer_unit = fields.Selection([('kilometers', 'Kilometers'), ('miles', 'Miles')], 'Odometer Unit', readonly=True)
    sum_cost = fields.Float(string='Cost', readonly=True)
    state = fields.Selection([
        ('progress', 'In Operation'),
        ('done', 'Done'),
    ], string="Status", readonly=True)
    fuel_consumption = fields.Float('Fuel Consumption', readonly=True)

    def _select_sum_costs(self):
        return """
            SELECT
                SUM(fvc.amount)
            FROM fleet_vehicle_log_services AS fvc
            JOIN fleet_vehicle_trip AS fvt ON fvt.id = fvc.trip_id
            WHERE fvt.id = t.id
        """

    def _select(self):
        select_str = """
            SELECT
                t.id AS id,
                t.id AS trip_id,
                t.vehicle_id,
                t.driver_id,
                t.employee_id,
                t.route_id,
                CASE WHEN t.odometer_unit = 'kilometers'
                    THEN t.est_distance
                    ELSE t.est_distance * 1.60934
                END AS est_distance,
                t.est_trip_time,
                t.operation_duration,
                t.time_deviation,
                t.actual_distance,
                t.distance_deviation,
                t.fuel_consumption,
                t.start_date,
                t.end_date,
                CASE WHEN t.odometer_unit = 'kilometers'
                    THEN (SELECT value FROM fleet_vehicle_odometer WHERE vehicle_id = v.id AND date <= t.end_date LIMIT 1)
                    ELSE (SELECT value * 1.60934 FROM fleet_vehicle_odometer WHERE vehicle_id = v.id AND date <= t.end_date LIMIT 1)
                END AS odometer_value,
                t.odometer_unit,
                t.state,
                (%s) AS sum_cost
        """ % (self._select_sum_costs(),)
        return select_str

    def _from(self):
        from_str = """
            FROM
                fleet_vehicle_trip AS t
        """
        return from_str

    def _join(self):
        join_str = """
                JOIN fleet_vehicle AS v ON v.id = t.vehicle_id
        """
        return join_str

    def _where(self):
        where_str = """
            WHERE t.state IN ('progress','done')
        """
        return where_str

    def _group_by(self):
        group_by_str = """
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s AS (
            %s
            %s
            %s
            %s
            %s
            )
        """ % (self._table, self._select(), self._from(), self._join(), self._where(), self._group_by()))

