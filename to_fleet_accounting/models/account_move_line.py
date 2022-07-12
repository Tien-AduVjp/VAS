from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    fleet_vehicle_service_ids = fields.One2many('fleet.vehicle.log.services', 'invoice_line_id', string='Vehicle Services', groups='account.group_account_invoice')
    fleet_vehicle_services_count = fields.Integer(string='Vehicle Services Count', compute='_compute_fleet_vehicle_services_count', store=True)

    has_vehicle_service = fields.Boolean(string='Has Vehicle Service', compute='_compute_has_vehicle_service', store=True)

    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicles', compute='_compute_vehicles',
                                 store=True, index=True, ondelete='restrict',
                                 help="The vehicle to which this move line refers")

    @api.depends('fleet_vehicle_service_ids')
    def _compute_vehicles(self):
        for r in self:
            r.vehicle_ids = r.fleet_vehicle_service_ids.mapped('vehicle_id')

    @api.depends('fleet_vehicle_service_ids')
    def _compute_has_vehicle_service(self):
        for r in self:
            r.has_vehicle_service = r.fleet_vehicle_service_ids and True or False

    @api.constrains('currency_id', 'price_subtotal', 'fleet_vehicle_service_ids')
    def _check_invl_vehicle_service_constrains(self):
        for r in self:
            if not r.fleet_vehicle_service_ids:
                continue

            total = 0.0
            for service in r.fleet_vehicle_service_ids:
                if service.currency_id.id != r.move_id.currency_id.id:
                    raise ValidationError(_("Vehicle service %s's currency (%s) must be the same as the invoice's one (%s)")
                                          % (service.display_name, service.currency_id.name, r.currency_id.name))
                total += service.amount

            if float_compare(r.price_subtotal, total, precision_digits=r.move_id.currency_id.decimal_places) != 0:
                raise ValidationError(_('The sum of the vehicle service of the invoice line (%d)'
                                        ' is not equal to the Amount of the invoice line (%d).'
                                        ' Please adjust the unit price to make the Amount equal.')
                                      % (total, r.price_subtotal))

    @api.depends('fleet_vehicle_service_ids')
    def _compute_fleet_vehicle_services_count(self):
        for r in self:
            r.fleet_vehicle_services_count = len(r.fleet_vehicle_service_ids)

    def _prepare_vehicle_service_allocation_line_data(self, vehicle_id, vehicle_count):
        self.ensure_one()
        FleetServiceType = self.env['fleet.service.type']
        cost_subtype_id = self.product_id and FleetServiceType.search([('product_id', '=', self.product_id.id)], limit=1) or False
        return {
            'invoice_line_id': self._origin and self._origin.id or self.id,
            'vehicle_id': vehicle_id._origin and vehicle_id._origin.id or vehicle_id.id,
            'cost_subtype_id': cost_subtype_id and cost_subtype_id.id or False,
            'quantity': (self.product_uom_id and self.product_uom_id._compute_quantity(self.quantity, self.product_id.uom_id) or self.quantity) / vehicle_count,
            'amount': self.price_subtotal / vehicle_count,
            }

    def _prepare_vehicle_service_allocation_line_data_model(self, vehicle_id, vehicle_count):
        return self.env['vehicle.log.services.distribution.line'].new(self._prepare_vehicle_service_allocation_line_data(vehicle_id, vehicle_count))

    def unlink(self):
        for r in self:
            r.fleet_vehicle_service_ids.filtered(lambda c: c.created_from_invoice_line_id.id == r.id).unlink()
        return super(AccountMoveLine, self).unlink()

    def action_vehicle_log_services_allocation_wizard(self):
        if not self:
            raise UserError(_("Please hit Save button first!"))
        
        self.ensure_one()

        if not self.has_vehicle_service:
            action = self.env['ir.actions.act_window']._for_xml_id('to_fleet_accounting.action_vehicle_log_services_allocation_wizard')
            return action
        else:
            return self.action_view_vehicle_service()

    def action_view_vehicle_service(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('fleet.fleet_vehicle_log_services_action')
        services = self.fleet_vehicle_service_ids
        if len(services) == 1:
            service = services[0]
            action['res_id'] = service.id
            action['view_mode'] = 'form'
            form_view = [(self.env.ref('fleet.fleet_vehicle_log_services_view_form').id, 'form')]
            action['views'] = form_view
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', services.ids)]
        return action
