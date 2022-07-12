from odoo import models, fields, api

class VehicleCostDistributionLine(models.TransientModel):
    _inherit = 'vehicle.cost.distribution.line'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', help="The trip on which this amount is registered", ondelete='cascade')
    trip_section_id = fields.Many2one('fleet.vehicle.trip.section', string='Trip Section', ondelete='cascade')
    trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Trip Waypoint', ondelete='cascade')

    @api.model
    def _prepare_vehicle_cost_data(self):
        data = super(VehicleCostDistributionLine, self)._prepare_vehicle_cost_data()
        data['trip_id'] = self.trip_id.id
        data['trip_section_id'] = self.trip_section_id.id
        data['trip_waypoint_id'] = self.trip_waypoint_id.id
        return data

    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        res = {}
        if self.trip_id:
            res['domain'] = {
                'trip_section_id': [('id', 'in', self.trip_id.trip_section_ids.ids)],
                'trip_waypoint_id': [('id', 'in', self.trip_id.trip_waypoint_ids.ids)]
                }
        return res
