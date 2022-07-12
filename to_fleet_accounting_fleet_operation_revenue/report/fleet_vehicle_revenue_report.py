from odoo import models, fields


class FleetVehicleRevenueReport(models.Model):
    _inherit = "fleet.vehicle.revenue.report"

    route_section_id = fields.Many2one('route.section', string='Route Section', readonly=True)
    address_id = fields.Many2one('res.partner', string='Waypoint', readonly=True)
    route_id = fields.Many2one('route.route', string='Route', readonly=True)
    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', readonly=True)
    trip_operator_id = fields.Many2one('res.users', string='Trip Operator', readonly=True,
                                       help="The user who takes the responsibility for the related trip as the operator")

    def _select(self):
        select_str = super(FleetVehicleRevenueReport, self)._select()
        select_str += """,
                rs.id AS route_section_id,
                wp.id AS address_id,
                rt.id AS route_id,
                t.id AS trip_id,
                t.operator_id AS trip_operator_id
        """
        return select_str

    def _join(self):
        join_str = super(FleetVehicleRevenueReport, self)._join()
        join_str += """
            LEFT JOIN route_section AS rs ON rs.id = r.route_section_id
            LEFT JOIN res_partner AS wp ON wp.id = r.address_id
            LEFT JOIN route_route AS rt ON rt.id = r.route_id
            LEFT JOIN fleet_vehicle_trip AS t ON t.id = r.trip_id
        """
        return join_str

    def _group_by(self):
        group_by_str = super(FleetVehicleRevenueReport, self)._group_by()
        group_by_str += """,
            rs.id,
            wp.id,
            rt.id,
            t.id
        """
        return group_by_str

