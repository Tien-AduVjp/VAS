from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VehicleLogServicesDistributionLine(models.TransientModel):
    _name = 'vehicle.log.services.distribution.line'
    _description = 'Vehicle Service Distribution Line'

    vehicle_log_services_distribution_wizard_id = fields.Many2one('vehicle.log.services.distribution', required=True, ondelete='cascade')
    invoice_line_id = fields.Many2one('account.move.line', string='Invoice Line', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', domain="[('product_id', '=', invoice_line_id.product_id.id)]")
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', required=True, ondelete='cascade')
    currency_id = fields.Many2one('res.currency', related='invoice_line_id.currency_id', readonly=True, ondelete='cascade')
    cost_subtype_id = fields.Many2one('fleet.service.type', string='Type', ondelete='cascade', compute='_compute_cost_subtype_id',
                                      readonly=False, store=True)
    quantity = fields.Float(string='Quantity')
    amount = fields.Monetary(string='Amount')

    @api.depends('invoice_line_id')
    def _compute_cost_subtype_id(self):
        FleetServiceType = self.env['fleet.service.type']
        for r in self:
            if r.invoice_line_id and r.invoice_line_id.product_id:
                domain = [('product_id', '=', self.invoice_line_id.product_id.id)]
                r.cost_subtype_id = FleetServiceType.search(domain, limit=1)
            else:
                r.cost_subtype_id = False

    @api.model
    def _prepare_vehicle_log_services_data(self):
        res = {
            'vehicle_id': self.vehicle_id.id,
            'quantity': self.quantity,
            'amount': self.amount,
            'currency_id':self.currency_id.id,
            'date': self.invoice_line_id.move_id.invoice_date,
            'company_id': self.invoice_line_id.company_id.id,
            'product_id': self.invoice_line_id.product_id.id,
            'invoice_line_id': self.invoice_line_id.id,
            'vendor_id': self.invoice_line_id.partner_id.id,
            'created_from_invoice_line_id': self.invoice_line_id.id,
            'service_type_id': self.cost_subtype_id
            }

        return res


class VehicleLogServicesDistribution(models.TransientModel):
    _name = 'vehicle.log.services.distribution'
    _description = 'Vehicle Service Distribution Wizard'

    @api.model
    def _get_default_vehicles(self):
        active_ids = self._context.get('active_ids', False)
        active_model = self._context.get('active_model', False)

        invoice_line_ids = self.env[active_model].browse(active_ids)
        vehicle_ids = invoice_line_ids.mapped('fleet_vehicle_service_ids').mapped('vehicle_id')

        return vehicle_ids and vehicle_ids.ids or False

    vehicle_log_services_distribution_line_ids = fields.One2many('vehicle.log.services.distribution.line', 'vehicle_log_services_distribution_wizard_id',
                                                       string='Service Distribution Lines')

    invoice_line_ids = fields.Many2many('account.move.line', string='Invoice Lines', required=True,
                                        domain=[('exclude_from_invoice_tab', '=', False),('has_vehicle_service', '=', False)])

    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicle', default=_get_default_vehicles,
                                   help="Select vehicles to allocate the service",)

    @api.onchange('invoice_line_ids', 'vehicle_ids')
    def _onchange_invoice_line_ids_vehicle_ids(self):
        vehicle_log_services_distribution_line_ids = self.env['vehicle.log.services.distribution.line']
        for line in self.invoice_line_ids:
            vehicle_count = len(self.vehicle_ids)
            for vehicle_id in self.vehicle_ids:
                new_line = line._prepare_vehicle_service_allocation_line_data_model(vehicle_id, vehicle_count)
                vehicle_log_services_distribution_line_ids += new_line

        self.vehicle_log_services_distribution_line_ids = vehicle_log_services_distribution_line_ids

    def create_vehicle_service(self):
        for r in self:
            services_distribution_line_no_type = r.vehicle_log_services_distribution_line_ids.filtered(lambda l: not l.cost_subtype_id)
            if services_distribution_line_no_type:
                raise ValidationError(_("Type on distribution line cannot be blank! Line has invoice line: "
                                        "%s") % services_distribution_line_no_type[0].invoice_line_id.display_name)
            for invoice_line in r.invoice_line_ids:
                if invoice_line.move_id.state in ('paid', 'cancel'):
                    raise ValidationError(_("You can allocate invoice line's amount to vehicles (as vehicle services)"
                                            " ONLY when the invoice state is neither 'Paid' nor 'Cancelled'."
                                            " You may need to set the invoice back to draft state then do allocation again."))
                fleet_vehicle_log_services_ids = self.env['fleet.vehicle.log.services']
                for line in r.vehicle_log_services_distribution_line_ids.filtered(lambda x: x.invoice_line_id.id == invoice_line.id):
                    if line.cost_subtype_id:
                        new_service = fleet_vehicle_log_services_ids.new(line._prepare_vehicle_log_services_data())
                        fleet_vehicle_log_services_ids += new_service
                invoice_line.fleet_vehicle_service_ids = fleet_vehicle_log_services_ids
        invoices = self.mapped('invoice_line_ids.move_id')
        posted_invoices = invoices.filtered(lambda inv: inv.state == 'posted')
        analytic_lines = posted_invoices.mapped('invoice_line_ids.fleet_vehicle_service_ids')._generate_anlytic_lines()
        return analytic_lines

