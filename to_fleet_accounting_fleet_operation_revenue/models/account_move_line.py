from odoo import models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.depends('fleet_vehicle_cost_ids', 'fleet_vehicle_cost_ids.trip_id', 'fleet_vehicle_revenue_ids', 'fleet_vehicle_revenue_ids.trip_id')
    def _compute_has_vehicle_cost(self):
        for r in self:
            if r.has_vehicle_revenue:
                r.trip_id = r.fleet_vehicle_revenue_ids[0].trip_id
            else:
                super(AccountMoveLine, r)._compute_has_vehicle_cost()

    @api.model
    def _prepare_vehicle_revenue_allocation_line_data(self, vehicle_id, vehicle_count):
        data = super(AccountMoveLine, self)._prepare_vehicle_revenue_allocation_line_data(vehicle_id, vehicle_count)
        trip_id = self.env['fleet.vehicle.trip'].search([('vehicle_id', '=', vehicle_id.id), ('state', 'not in', ('draft', 'cancelled'))], limit=1)
        if trip_id:
            data['trip_id'] = trip_id.id

        return data
