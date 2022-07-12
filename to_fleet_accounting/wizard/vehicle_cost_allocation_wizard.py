from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VehicleCostDistributionLine(models.TransientModel):
    _name = 'vehicle.cost.distribution.line'
    _description = 'Vehicle Cost Distribution Line'

    vehicle_cost_allocation_wizard_id = fields.Many2one('vehicle.cost.distribution', required=True, ondelete='cascade')
    invoice_line_id = fields.Many2one('account.move.line', string='Invoice Line', required=True, ondelete='cascade')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='invoice_line_id.currency_id', readonly=True, ondelete='cascade')
    cost_subtype_id = fields.Many2one('fleet.service.type', string='Type', ondelete='cascade')
    amount = fields.Monetary(string='Amount')

    @api.onchange('invoice_line_id')
    def _onchange_invoice_line_id(self):
        res = {}
        FleetServiceType = self.env['fleet.service.type']
        if self.invoice_line_id:
            if self.invoice_line_id.product_id:
                domain = [('product_id', '=', self.invoice_line_id.product_id.id)]
                self.cost_subtype_id = FleetServiceType.search(domain, limit=1)
                res['domain'] = {'cost_subtype_id':domain + [('product_id', '=', False)]}
        return res

    @api.model
    def _prepare_vehicle_cost_data(self):
        res = {
            'vehicle_id': self.vehicle_id.id,
            'amount': self.amount,
            'currency_id':self.currency_id.id,
            'date': self.invoice_line_id.move_id.invoice_date,
            'company_id': self.invoice_line_id.company_id.id,
            'product_id': self.invoice_line_id.product_id.id,
            'invoice_line_id': self.invoice_line_id.id,
            'vendor_id': self.invoice_line_id.partner_id.id,
            'created_from_invoice_line_id': self.invoice_line_id.id,
            }

        cost_type = ''
        if self.cost_subtype_id:
            cost_subtype_id = self.cost_subtype_id.id
            fuel_type_id = self.env.ref('fleet.type_service_refueling', raise_if_not_found=False)
            if fuel_type_id and fuel_type_id.id == self.cost_subtype_id.id:
                cost_type = 'fuel'
            elif self.cost_subtype_id.category == 'service':
                cost_type = 'services'
            elif self.cost_subtype_id.category == 'contract':
                cost_type = 'contract'
        else:
            cost_subtype_id = False

        if cost_type:
            res['cost_type'] = cost_type
        if cost_subtype_id:
            res['cost_subtype_id'] = cost_subtype_id

        return res


class VehicleCostDistribution(models.TransientModel):
    _name = 'vehicle.cost.distribution'
    _description = 'Vehicle Cost Distribution Wizard'

    @api.model
    def _get_default_vehicles(self):
        active_ids = self._context.get('active_ids', False)
        active_model = self._context.get('active_model', False)

        invoice_line_ids = self.env[active_model].browse(active_ids)
        vehicle_ids = invoice_line_ids.mapped('fleet_vehicle_cost_ids').mapped('vehicle_id')

        return vehicle_ids and vehicle_ids.ids or False

    vehicle_cost_allocation_line_ids = fields.One2many('vehicle.cost.distribution.line', 'vehicle_cost_allocation_wizard_id',
                                                       string='Cost Allocation Lines')

    invoice_line_ids = fields.Many2many('account.move.line', string='Invoice Lines', required=True,
                                        domain=[('exclude_from_invoice_tab', '=', False),('has_vehicle_cost', '=', False)])

    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicle', default=_get_default_vehicles,
                                   help="Select vehicles to allocate the cost",)

    @api.onchange('invoice_line_ids', 'vehicle_ids')
    def _onchange_invoice_line_ids_vehicle_ids(self):
        vehicle_cost_allocation_line_ids = self.env['vehicle.cost.distribution.line']
        for line in self.invoice_line_ids:
            vehicle_count = len(self.vehicle_ids)
            for vehicle_id in self.vehicle_ids:
                new_line = line._prepare_vehicle_cost_allocation_line_data_model(vehicle_id, vehicle_count)
                vehicle_cost_allocation_line_ids += new_line

        self.vehicle_cost_allocation_line_ids = vehicle_cost_allocation_line_ids

    def create_vehicle_cost(self):
        for r in self:
            for invoice_line in r.invoice_line_ids:
                if invoice_line.move_id.state in ('paid', 'cancel'):
                    raise ValidationError(_("You can allocate invoice line's amount to vehicles (as vehicle costs)"
                                            " ONLY when the invoice state is neither 'Paid' nor 'Cancelled'."
                                            " You may need to set the invoice back to draft state then do allocation again."))
                fleet_vehicle_cost_ids = self.env['fleet.vehicle.cost']
                for line in r.vehicle_cost_allocation_line_ids.filtered(lambda x: x.invoice_line_id.id == invoice_line.id):
                    new_cost = fleet_vehicle_cost_ids.new(line._prepare_vehicle_cost_data())
                    fleet_vehicle_cost_ids += new_cost
                invoice_line.fleet_vehicle_cost_ids = fleet_vehicle_cost_ids
        invoices = self.mapped('invoice_line_ids.move_id')
        posted_invoices = invoices.filtered(lambda inv: inv.state == 'posted')
        analytic_lines = posted_invoices.mapped('invoice_line_ids.fleet_vehicle_cost_ids')._generate_anlytic_lines()
        return analytic_lines

