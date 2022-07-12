from odoo import fields, models

class RouteSection(models.Model):
    _inherit = 'route.section'

    trip_section_ids = fields.One2many('fleet.vehicle.trip.section', 'route_section_id', string='Trip Sections')

    log_services_ids = fields.One2many('fleet.vehicle.log.services', 'route_section_id', string='Services Logs',
                                       help="Services for vehicle")
