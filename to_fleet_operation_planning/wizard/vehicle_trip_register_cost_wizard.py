from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class VehicleTripRegisterCostWizard(models.TransientModel):
    _name = 'vehicle.trip.register.cost.wizard'
    _description = "Vehicle Trip Register Cost Wizard"
    _inherit = 'abstract.vehicle.trip.wizard'

    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    cost_subtype_id = fields.Many2one('fleet.service.type', string='Type', ondelete='cascade')
    trip_section_id = fields.Many2one('fleet.vehicle.trip.section', string='Trip Section', ondelete='cascade',
                                      help="The section of the trip for which the cost is registered")
    trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Trip Waypoint', ondelete='cascade',
                                       help="The waypoint of the trip for where the cost is registered")

    amount = fields.Float(string='Amount', required=True)

    _sql_constraints = [
        ('zero_amount_check',
         'CHECK(amount != 0)',
         "Creating cost of zero amount does not make sense!"),
    ]

    @api.constrains('amount')
    def _negative_cost_check(self):
        for r in self:
            if float_compare(r.amount, 0.0, precision_digits=3) == -1 and not self.env.user.has_group('fleet.fleet_group_manager'):
                raise UserError(_("Only Fleet Managers can create negative costs (amount < 0)."
                                  " If you really want to create a nagative cost (to correct your"
                                  " previous mistake), please ask the managers for help"))

    @api.constrains('trip_id', 'trip_waypoint_id')
    def _check_contrains_trip_id_trip_waypoint_id(self):
        for r in self:
            if r.trip_id and r.trip_waypoint_id:
                if r.trip_id.id != r.trip_waypoint_id.trip_id.id:
                    raise UserError(_("The Trip Waypoint '%s' you've selected does not belong to this trip '%s'")
                                    % (r.trip_waypoint_id.display_name, r.trip_id.name))

    @api.constrains('trip_id', 'trip_section_id')
    def _check_contrains_trip_id_trip_section_id(self):
        for r in self:
            if r.trip_id and r.trip_section_id:
                if r.trip_id.id != r.trip_section_id.trip_id.id:
                    raise UserError(_("The Trip Section '%s' you've selected does not belong to this trip '%s'")
                                    % (r.trip_section_id.display_name, r.trip_id.name))

    @api.constrains('trip_section_id', 'trip_waypoint_id')
    def _check_contrains_trip_waypoint_id_trip_section_id(self):
        for r in self:
            if r.trip_id:
                if not r.trip_section_id and not r.trip_waypoint_id:
                    raise UserError(_("You must assign the cost either for a trip section or trip waypoint."
                                  " You cannot leave both empty!"))
            else:
                raise UserError(_("You must select a trip to register a cost for it."))

    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        res = {}
        if self.trip_id:
            res['domain'] = {}
            if self.trip_id.trip_section_ids:
                res['domain']['trip_section_id'] = [('id', 'in', self.trip_id.trip_section_ids.ids)]

            if self.trip_id.trip_waypoint_ids:
                res['domain']['trip_waypoint_id'] = [('id', 'in', self.trip_id.trip_waypoint_ids.ids)]
        return res

    @api.model
    def _prepare_cost_data(self):
        return {
            'date': self.date,
            'cost_subtype_id': self.cost_subtype_id and self.cost_subtype_id.id or False,
            'trip_section_id': self.trip_section_id and self.trip_section_id.id or False,
            'trip_waypoint_id': self.trip_waypoint_id and self.trip_waypoint_id.id or False,
            'amount': self.amount,
            'vehicle_id': self.trip_id.vehicle_id.id
            }

    def action_register_cost(self):
        self.ensure_one()
        Cost = self.env['fleet.vehicle.cost']
        data = self._prepare_cost_data()
        return Cost.create(data)
