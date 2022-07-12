from odoo import models, fields

class FleetVehicleCostReport(models.Model):
    _inherit = "fleet.vehicle.cost.report"

    route_section_id = fields.Many2one('route.section', string='Route Section', readonly=True)
    address_id = fields.Many2one('res.partner', string='Route Location', readonly=True)
    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', readonly=True)
    route_id = fields.Many2one('route.route', string='Route', readonly=True)

    def _select(self):
        sql = super(FleetVehicleCostReport, self)._select()
        sql += """,
            rs.id AS route_section_id,
            ra.id AS address_id,
            c.trip_id AS trip_id,
            c.route_id AS route_id
        """
        return sql

    def _from(self):
        from_str = """
            FROM
                fleet_vehicle_cost AS c
        """
        return from_str

    def _join(self):
        sql = super(FleetVehicleCostReport, self)._join()
        sql += """
            LEFT JOIN route_section AS rs ON rs.id = c.route_section_id
            LEFT JOIN res_partner AS ra ON ra.id = c.address_id
        """
        return sql

    def _group_by(self):
        sql = super(FleetVehicleCostReport, self)._group_by()
        sql += """,
                rs.id,
                ra.id,
                c.trip_id,
                c.route_id
        """
        return sql
