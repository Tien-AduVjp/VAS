from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', store=True,
                              help="The trip that relates to this journal item")
    
    @api.model
    def _prepare_vehicle_cost_allocation_line_data(self, vehicle_id, vehicle_count):
        data = super(AccountMoveLine, self)._prepare_vehicle_cost_allocation_line_data(vehicle_id, vehicle_count)
        trip_id = self.env['fleet.vehicle.trip'].search([('vehicle_id', '=', vehicle_id.id), ('state', 'not in', ('draft', 'cancelled'))], limit=1)
        if trip_id:
            data['trip_id'] = trip_id.id
        return data

    @api.model
    def _prepare_vehicle_cost_allocation_line_data_model(self, vehicle_id, vehicle_count):
        line = super(AccountMoveLine, self)._prepare_vehicle_cost_allocation_line_data_model(vehicle_id, vehicle_count)
        line._onchange_trip_id()
        return line
    
    @api.depends('fleet_vehicle_cost_ids')
    def _compute_has_vehicle_cost(self):
        super(AccountMoveLine, self)._compute_has_vehicle_cost()
        for r in self:
            if r.has_vehicle_cost:
                r.trip_id = r.fleet_vehicle_cost_ids[0].trip_id
