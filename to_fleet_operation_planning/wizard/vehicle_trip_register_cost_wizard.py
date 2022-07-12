from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class VehicleTripRegisterCostWizard(models.TransientModel):
    _name = 'vehicle.trip.register.cost.wizard'
    _description = "Vehicle Trip Register Cost Wizard"
    _inherit = 'abstract.vehicle.trip.wizard'

    @api.model
    def _get_default_company(self):
        return self.env.company

    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    service_type_id = fields.Many2one('fleet.service.type', string='Type', required=True, ondelete='cascade')
    trip_section_id = fields.Many2one('fleet.vehicle.trip.section', string='Trip Section', ondelete='cascade',
                                      domain="[('trip_id','=',trip_id)]",
                                      help="The section of the trip for which the cost is registered")
    trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Trip Waypoint', ondelete='cascade',
                                       domain="[('trip_id','=',trip_id)]",
                                       help="The waypoint of the trip for where the cost is registered")
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True)
    quantity = fields.Float('Quantity', default=1.0)
    price_unit = fields.Monetary('Unit Price')
    company_id = fields.Many2one('res.company', string='Company', default=_get_default_company, required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', related='company_id.currency_id')
    amount = fields.Monetary(string='Amount', compute='_compute_amount', inverse='_inverse_amount', store=True)

    _sql_constraints = [
        ('zero_amount_check',
         'CHECK(amount != 0)',
         "Creating cost of zero amount does not make sense!"),
        ('check_quantity',
         'CHECK (quantity > 0)',
         "Quantity of a service must be positive!"),
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

    @api.depends('price_unit', 'quantity')
    def _compute_amount(self):
        for r in self:
            r.amount = r.quantity * r.price_unit

    def _inverse_amount(self):
        for r in self:
            r.price_unit = r.amount / r.quantity

    @api.model
    def _prepare_cost_data(self):
        return {
            'date': self.date,
            'service_type_id': self.service_type_id and self.service_type_id.id or False,
            'trip_section_id': self.trip_section_id and self.trip_section_id.id or False,
            'trip_waypoint_id': self.trip_waypoint_id and self.trip_waypoint_id.id or False,
            'quantity': self.quantity,
            'price_unit': self.price_unit,
            'amount': self.amount,
            'vehicle_id': self.trip_id.vehicle_id.id,
            'vendor_id': self.vendor_id.id,
            'company_id': self.company_id.id,
            'currency_id':self.currency_id.id
            }

    def action_register_cost(self):
        self.ensure_one()
        Cost = self.env['fleet.vehicle.log.services']
        data = self._prepare_cost_data()
        return Cost.create(data)
