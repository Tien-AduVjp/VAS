from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare


class VehicleTripRegisterRevenueWizard(models.TransientModel):
    _name = 'vehicle.trip.register.revenue.wizard'
    _description = "Vehicle Trip Register Revenue Wizard"
    _inherit = 'abstract.vehicle.trip.wizard'

    @api.model
    def _get_default_company(self):
        return self.env.company

    @api.model
    def _get_default_currency(self):
        return self.env.company.currency_id

    customer_id = fields.Many2one('res.partner', string='Customer', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Invoiceable Product', ondelete='cascade',
                                 help="The product that will be used when invoicing this revenue")
    company_id = fields.Many2one('res.company', string='Company', default=_get_default_company, required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', string='Currency', default=_get_default_currency, required=True, ondelete='cascade')

    amount = fields.Monetary(string='Amount', required=True)

    date = fields.Date(string='Date', default=fields.Date.context_today, required=True)
    revenue_subtype_id = fields.Many2one('fleet.service.type', string='Type', ondelete='cascade')
    trip_section_id = fields.Many2one('fleet.vehicle.trip.section', string='Trip Section', ondelete='cascade',
                                      help="The section of the trip for which the revenue is registered")
    trip_waypoint_id = fields.Many2one('fleet.vehicle.trip.waypoint', string='Trip Waypoint', ondelete='cascade',
                                       help="The waypoint of the trip for where the revenue is registered")

    _sql_constraints = [
        ('zero_amount_check',
         'CHECK(amount != 0)',
         "Creating revenue of zero amount does not make sense!"),
    ]

    @api.constrains('revenue_subtype_id', 'product_id')
    def _check_constrains_revenue_subtype_id_product_id(self):
        for r in self:
            if r.revenue_subtype_id and r.product_id:
                if r.revenue_subtype_id.product_id:
                    if r.revenue_subtype_id.product_id.id != r.product_id.id:
                        raise ValidationError(_("There is a discrepancy between the product (%s) you selected and"
                                                " the product (%s) predefined for the service type %s")
                                              % (r.product_id.name, r.revenue_subtype_id.product_id.name, r.revenue_subtype_id.name))

    @api.constrains('amount')
    def _negative_revenue_check(self):
        for r in self:
            if float_compare(r.amount, 0.0, precision_digits=3) == -1 and not self.env.user.has_group('fleet.fleet_group_manager'):
                raise UserError(_("Only Fleet Managers can create negative revenues (amount < 0)."
                                  " If you really want to create a nagative revenue (to correct your"
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
                    raise UserError(_("You must assign the revenue either for a trip section or trip waypoint."
                                  " You cannot leave both empty!"))
            else:
                raise UserError(_("You must select a trip to register a revenue for it."))

    @api.onchange('trip_id')
    def _onchange_trip_id(self):
        res = {}
        if self.trip_id:
            vehicle_id = self.trip_id.vehicle_id
            if vehicle_id:
                if vehicle_id.company_id:
                    self.company_id = vehicle_id.company_id

            res['domain'] = {}
            if self.trip_id.trip_section_ids:
                res['domain']['trip_section_id'] = [('id', 'in', self.trip_id.trip_section_ids.ids)]
            else:
                res['domain']['trip_section_id'] = []

            if self.trip_id.trip_waypoint_ids:
                res['domain']['trip_waypoint_id'] = [('id', 'in', self.trip_id.trip_waypoint_ids.ids)]
            else:
                res['domain']['trip_waypoint_ids'] = []
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            self.currency_id = self.company_id.currency_id

    @api.onchange('revenue_subtype_id')
    def _onchange_revenue_subtype_id(self):
        res = {}
        if self.revenue_subtype_id:
            if self.revenue_subtype_id.product_id:
                self.product_id = self.revenue_subtype_id.product_id
                res['domain'] = {'product_id':[('id', '=', self.revenue_subtype_id.product_id.id)]}
            else:
                res['domain'] = {'product_id':[('id', '>', 0)]}
        return res

    @api.model
    def _prepare_revenue_data(self):
        product_id = self.product_id and self.product_id or False
        if not product_id:
            product_id = self.revenue_subtype_id and self.revenue_subtype_id.product_id

        return {
            'customer_id': self.customer_id.id,
            'product_id': product_id and product_id.id or False,
            'company_id': self.company_id.id,
            'currency_id': self.currency_id.id,
            'date': self.date,
            'revenue_subtype_id': self.revenue_subtype_id and self.revenue_subtype_id.id or False,
            'trip_section_id': self.trip_section_id and self.trip_section_id.id or False,
            'trip_waypoint_id': self.trip_waypoint_id and self.trip_waypoint_id.id or False,
            'amount': self.amount,
            'vehicle_id': self.trip_id.vehicle_id.id
            }

    def action_register_revenue(self):
        self.ensure_one()
        Revenue = self.env['fleet.vehicle.revenue']
        data = self._prepare_revenue_data()
        return Revenue.create(data)
