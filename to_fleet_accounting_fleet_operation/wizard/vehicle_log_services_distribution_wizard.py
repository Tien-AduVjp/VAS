from odoo import models, fields, api

class VehicleLogServicesDistributionLine(models.TransientModel):
    _inherit = 'vehicle.log.services.distribution.line'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', help="The trip on which this amount is registered", ondelete='cascade')
    trip_section_id = fields.Many2one('fleet.vehicle.trip.section', string='Trip Section', ondelete='cascade',
                                      domain="[('trip_id','=',trip_id)]")
    trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Trip Waypoint', ondelete='cascade',
                                       domain="[('trip_id','=',trip_id)]")

    @api.model
    def _prepare_vehicle_log_services_data(self):
        data = super(VehicleLogServicesDistributionLine, self)._prepare_vehicle_log_services_data()
        data['trip_id'] = self.trip_id.id
        data['trip_section_id'] = self.trip_section_id.id
        data['trip_waypoint_id'] = self.trip_waypoint_id.id
        return data
