from odoo import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    vehicle_trip_ids = fields.One2many('fleet.vehicle.trip', 'hr_payslip_id', string='Vehicle Trips',
                                       compute='_compute_vehicle_trip_ids', store=True)
    total_job_wage = fields.Float(string='Total Job Wage', compute='_compute_total_job_wage')
    total_allowance = fields.Float(string='Total Allowance', compute='_compute_total_allowance')

    @api.depends('employee_id', 'date_from', 'date_to')
    def _compute_vehicle_trip_ids(self):
        trips = self.env['fleet.vehicle.trip'].search([
                ('employee_id', 'in', self.employee_id.ids),
                ('end_date', '>=', min(self.mapped('date_from'))),
                ('end_date', '<=', max(self.mapped('date_to'))),
                ('hr_payslip_id', '=', False),
                ('state', '=', 'done')
            ])
        for r in self:
            vehicle_trip_ids = trips.filtered(lambda t: t.employee_id == r.employee_id and r.date_from <= t.end_date.date() <= r.date_to)
            if vehicle_trip_ids:
                r.vehicle_trip_ids = [(6, 0, vehicle_trip_ids.ids)]
            else:
                r.vehicle_trip_ids = False

    @api.depends('vehicle_trip_ids')
    def _compute_total_job_wage(self):
        for r in self:
            r.total_job_wage = sum(r.vehicle_trip_ids.mapped('fuel_based_job_wage'))

    @api.depends('vehicle_trip_ids')
    def _compute_total_allowance(self):
        for r in self:
            r.total_allowance = sum(r.vehicle_trip_ids.mapped('job_allowance'))
