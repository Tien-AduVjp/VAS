from odoo import fields, models

class RouteSection(models.Model):
    _inherit = 'route.section'

    trip_section_ids = fields.One2many('fleet.vehicle.trip.section', 'route_section_id', string='Trip Sections')

    fleet_vehicle_cost_ids = fields.One2many('fleet.vehicle.cost', 'route_section_id', string='Vehicle Costs',
                                             help="Vehicle Cost Statistics")
