from odoo import models, fields, api


class FleetVehicleCost(models.Model):
    _inherit = 'fleet.vehicle.cost'

    vendor_is_employee = fields.Boolean(string='Vendor Is Employee', compute='_compute_vendor_is_employee', store=True)

    @api.depends('vendor_id.is_driver')
    def _compute_vendor_is_employee(self):
        employees = self.env['hr.employee'].sudo().search([('address_home_id', 'in', self.vendor_id.ids)])
        for r in self:
            if r.vendor_id.employee or (r.vendor_id.is_driver and employees.filtered(lambda e: e.address_home_id == r.vendor_id)):
                r.vendor_is_employee = True
            else:
                r.vendor_is_employee = False

    @api.model
    def _is_invoiceable(self):
        return super(FleetVehicleCost, self)._is_invoiceable()

    @api.depends('invoice_id', 'invoice_line_id', 'vendor_id', 'created_from_invoice_line_id')
    def _compute_invoiceable(self):
        super(FleetVehicleCost, self)._compute_invoiceable()
