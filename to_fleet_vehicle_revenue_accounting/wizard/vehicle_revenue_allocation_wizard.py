from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class VehicleRevenueAllocationWizard(models.TransientModel):
    _name = 'vehicle.revenue.allocation.wizard'
    _description = 'Vehicle Revenue Allocation Wizard'

    @api.model
    def _get_default_vehicles(self):
        active_ids = self._context.get('active_ids', False)
        active_model = self._context.get('active_model', False)

        invoice_line_ids = self.env[active_model].browse(active_ids)
        vehicle_ids = invoice_line_ids.mapped('fleet_vehicle_revenue_ids.vehicle_id')

        return vehicle_ids and vehicle_ids.ids or False

    vehicle_revenue_allocation_line_ids = fields.One2many('vehicle.revenue.allocation.line', 'vehicle_revenue_allocation_wizard_id',
                                                       string='Revenue Allocation Lines')

    invoice_line_ids = fields.Many2many('account.move.line', string='Invoice Lines', required=True)

    vehicle_ids = fields.Many2many('fleet.vehicle', string='Vehicle', default=_get_default_vehicles,
                                   help="Select vehicles to allocate the revenue")

    @api.onchange('vehicle_revenue_allocation_line_ids')
    def _onchange_vehicle_revenue_allocation_line_ids(self):
        for vehicle_id in self.vehicle_ids:
            if vehicle_id not in self.vehicle_revenue_allocation_line_ids.mapped('vehicle_id'):
                self.vehicle_ids -= vehicle_id

    @api.onchange('invoice_line_ids', 'vehicle_ids')
    def _onchange_invoice_line_ids_vehicle_ids(self):
        vehicle_revenue_allocation_line_ids = self.env['vehicle.revenue.allocation.line']
        vehicle_count = len(self.vehicle_ids)

        for line in self.invoice_line_ids:
            for vehicle_id in self.vehicle_ids:
                vehicle_revenue_allocation_line_data = line._prepare_vehicle_revenue_allocation_line_data(vehicle_id, vehicle_count)
                new_line = vehicle_revenue_allocation_line_ids.new(vehicle_revenue_allocation_line_data)
                vehicle_revenue_allocation_line_ids += new_line

        self.vehicle_revenue_allocation_line_ids = vehicle_revenue_allocation_line_ids

    def create_vehicle_revenue(self):
        AccountMoveLine = self.env['account.move.line']
        for r in self:
            invoices_to_reset = self.env['account.move']
            for invoice_line in r.invoice_line_ids:
                if invoice_line.move_id.state in ('paid', 'cancel'):
                    raise ValidationError(_("You can allocate invoice line's amount to vehicles (as vehicle revenue)"
                                            " ONLY when the invoice state is neither 'Paid' nor 'Cancelled'."
                                            " You may need to set the invoice back to draft state then do allocation again."))
                # remove existing revenues
                if invoice_line.fleet_vehicle_revenue_ids:
                    move_lines = AccountMoveLine.search([('vehicle_revenue_id', 'in', invoice_line.fleet_vehicle_revenue_ids.ids)])
                    if move_lines:
                        move_lines.write({'vehicle_revenue_id': False})
                    invoice_line.fleet_vehicle_revenue_ids.unlink()

                fleet_vehicle_revenue_ids = []
                for line in r.vehicle_revenue_allocation_line_ids:
                    fleet_vehicle_revenue_ids.append((0, 0, line._prepare_vehicle_revenue_data()))
                invoice_line.write({'fleet_vehicle_revenue_ids': fleet_vehicle_revenue_ids})

                if invoice_line.move_id.state == 'open':
                    invoices_to_reset |= invoice_line.move_id

            if invoices_to_reset:
                invoices_to_reset.with_context(keep_vehicle_revenue=True)._action_reopen()
                return {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
