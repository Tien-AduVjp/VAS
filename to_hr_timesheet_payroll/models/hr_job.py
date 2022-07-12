from odoo import fields, models

class Job(models.Model):
    _inherit = 'hr.job'

    payroll_timesheet_enabled = fields.Boolean(string='Payroll Timesheet Enabled', default=False, tracking=True, help="Default value for contracts of this job position")
