from odoo import fields, models, api


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    trip_id = fields.Many2one('fleet.vehicle.trip', string='Trip', compute='_compute_trip_id', store=True,
                              help="The trip that relates to this analytic line")

    @api.depends('vehicle_cost_id.trip_id')
    def _compute_trip_id(self):
        for r in self:
            r.trip_id = r.vehicle_cost_id.trip_id
