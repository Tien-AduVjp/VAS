from odoo import models, fields, api


class VehicleRevenueAllocationLine(models.TransientModel):
    _inherit = 'vehicle.revenue.allocation.line'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', help="The trip on which this amount is registered", ondelete='cascade')
    trip_section_id = fields.Many2one('fleet.vehicle.trip.section', string='Trip Section', ondelete='cascade',
                                      domain="[('trip_id','=',trip_id)]")
    trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Trip Waypoint', ondelete='cascade',
                                       domain="[('trip_id','=',trip_id)]")

    @api.model
    def _prepare_vehicle_revenue_data(self):
        data = super(VehicleRevenueAllocationLine, self)._prepare_vehicle_revenue_data()
        if self.trip_id:
            data['trip_id'] = self.trip_id.id

        if self.trip_section_id:
            data['trip_section_id'] = self.trip_section_id.id

        if self.trip_waypoint_id:
            data['trip_waypoint_id'] = self.trip_waypoint_id.id
        return data


class VehicleRevenueAllocationWizard(models.TransientModel):
    _inherit = 'vehicle.revenue.allocation.wizard'

    @api.onchange('invoice_line_ids', 'vehicle_ids')
    def _onchange_invoice_line_ids_vehicle_ids(self):
        super(VehicleRevenueAllocationWizard, self)._onchange_invoice_line_ids_vehicle_ids()
        for line in self.vehicle_revenue_allocation_line_ids:
            line._onchange_trip_id()
