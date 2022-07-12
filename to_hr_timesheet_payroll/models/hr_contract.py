# -*- coding: utf-8 -*-

from odoo import fields, models, api

class Contract(models.Model):
    _inherit = 'hr.contract'

    payroll_timesheet_enabled = fields.Boolean(string='Payroll Timesheet Enabled', default=False, tracking=True, store=True, compute='_compute_payroll_timesheet_enabled', readonly=False,
                                               states={'open':[('readonly',True)],
                                                       'close':[('readonly',True)],
                                                       'cancel':[('readonly',True)]}, help="If enabled, the payslips of this contract will respect timesheet log of the corresponding "
                                               "employee. Payroll Manager may need to create salary rule(s) to process employees timesheet data for payslip computation")

    @api.depends('job_id')
    def _compute_payroll_timesheet_enabled(self):
        for r in self:
            r.payroll_timesheet_enabled = r.job_id.payroll_timesheet_enabled