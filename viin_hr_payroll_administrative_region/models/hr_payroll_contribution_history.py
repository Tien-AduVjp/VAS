from odoo import models, fields


class HRPayrollContributionHistory(models.Model):
    _inherit = 'hr.payroll.contribution.history'

    max_contribution_employee = fields.Monetary(string="Monthly Max. Contribution by Employee", default=0.0, readonly=True,
                                                    help="The maximum amount per month that the employee has to contribute. Leave this zero to disable this limit.")
    max_contribution_company = fields.Monetary(string="Monthly Max. Contribution by Company", default=0.0, readonly=True,
                                                   help="The maximum amount per month that the company has to contribute. Leave this zero to disable this limit.")
