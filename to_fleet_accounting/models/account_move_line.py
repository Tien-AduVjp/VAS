from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fleet_vehicle_cost_ids = fields.One2many('fleet.vehicle.cost', 'invoice_line_id', string='Vehicle Costs', groups='account.group_account_invoice')
    fleet_vehicle_costs_count = fields.Integer(string='Vehicle Cost Count', compute='_compute_fleet_vehicle_costs_count', store=True)

    has_vehicle_cost = fields.Boolean(string='Has Vehicle Cost', compute='_compute_has_vehicle_cost', store=True)

    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicle', compute='_compute_vehicles',
                                 store=True, index=True, ondelete='restrict',
                                 help="The vehicle to which this move line refers")

    @api.depends('fleet_vehicle_cost_ids')
    def _compute_vehicles(self):
        for r in self:
            r.vehicle_ids = r.fleet_vehicle_cost_ids.mapped('vehicle_id')

    @api.depends('fleet_vehicle_cost_ids')
    def _compute_has_vehicle_cost(self):
        for r in self:
            r.has_vehicle_cost = r.fleet_vehicle_cost_ids and True or False

    @api.constrains('currency_id', 'price_subtotal', 'fleet_vehicle_cost_ids')
    def _check_invl_vehicle_cost_constrains(self):
        for r in self:
            if not r.fleet_vehicle_cost_ids:
                continue

            total = 0.0
            for cost in r.fleet_vehicle_cost_ids:
                if cost.currency_id.id != r.move_id.currency_id.id:
                    raise ValidationError(_("Vehicle cost %s's currency (%s) must be the same as the invoice's one (%s)")
                                          % (cost.display_name, cost.currency_id.name, r.currency_id.name))
                total += cost.amount

            if float_compare(r.price_subtotal, total, precision_digits=r.move_id.currency_id.decimal_places) != 0:
                raise ValidationError(_('The sum of the vehicle cost of the invoice line (%d)'
                                        ' is not equal to the Amount of the invoice line (%d).'
                                        ' Please adjust the unit price to make the Amount equal.')
                                      % (total, r.price_subtotal))

    @api.depends('fleet_vehicle_cost_ids')
    def _compute_fleet_vehicle_costs_count(self):
        for r in self:
            r.fleet_vehicle_costs_count = len(r.fleet_vehicle_cost_ids)

    def _prepare_vehicle_cost_allocation_line_data(self, vehicle_id, vehicle_count):
        self.ensure_one()
        FleetServiceType = self.env['fleet.service.type']
        cost_subtype_id = self.product_id and FleetServiceType.search([('product_id', '=', self.product_id.id)], limit=1) or False
        return {
            'invoice_line_id': self._origin and self._origin.id or self.id,
            'vehicle_id': vehicle_id._origin and vehicle_id._origin.id or vehicle_id.id,
            'cost_subtype_id': cost_subtype_id and cost_subtype_id.id or False,
            'amount': self.price_subtotal / vehicle_count,
            }

    def _prepare_vehicle_cost_allocation_line_data_model(self, vehicle_id, vehicle_count):
        return self.env['vehicle.cost.distribution.line'].new(self._prepare_vehicle_cost_allocation_line_data(vehicle_id, vehicle_count))

    def unlink(self):
        for r in self:
            r.fleet_vehicle_cost_ids.filtered(lambda c: c.created_from_invoice_line_id.id == r.id).unlink()
        return super(AccountMoveLine, self).unlink()

    def action_vehicle_cost_allocation_wizard(self):
        if not self:
            raise UserError(_("Please hit Save button first!"))
        
        self.ensure_one()

        if not self.has_vehicle_cost:
            action = self.env.ref('to_fleet_accounting.action_vehicle_cost_allocation_wizard')
            result = action.read()[0]
    
            return result
        else:
            return self.action_view_vehicle_cost()

    def action_view_vehicle_cost(self):
        self.ensure_one()
        action = self.env.ref('fleet.fleet_vehicle_costs_action').read()[0]
        costs = self.fleet_vehicle_cost_ids
        if len(costs) == 1:
            cost = costs[0]
            action['res_id'] = cost.id
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('fleet.fleet_vehicle_costs_view_form').id, 'form')]
            action['views'] = form_view
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', costs.ids)]
        return action
