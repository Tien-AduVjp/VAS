from odoo import models, fields, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', store=True,
                              help="The trip that relates to this journal item")

    @api.model
    def _prepare_vehicle_service_allocation_line_data(self, vehicle_id, vehicle_count):
        data = super(AccountMoveLine, self)._prepare_vehicle_service_allocation_line_data(vehicle_id, vehicle_count)
        trip_id = self.env['fleet.vehicle.trip'].search([('vehicle_id', '=', vehicle_id.id), ('state', 'not in', ('draft', 'cancelled'))], limit=1)
        if trip_id:
            data['trip_id'] = trip_id.id
        return data

    @api.depends('fleet_vehicle_service_ids')
    def _compute_has_vehicle_service(self):
        super(AccountMoveLine, self)._compute_has_vehicle_service()
        for r in self:
            if r.has_vehicle_service:
                r.trip_id = r.fleet_vehicle_service_ids[0].trip_id
