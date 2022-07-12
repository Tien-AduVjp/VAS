from odoo import fields, models


class AccountBudgetPost(models.Model):
    _inherit = 'account.budget.post'

    include_timesheets = fields.Boolean(string='Timesheets Included', default=True,
                                      help="If checked, timesheet lines will be included for timesheet costing in crossover budgets of this Budgetary Position.")

    def _prepare_analytic_lines_domain(self):
        domain = super(AccountBudgetPost, self)._prepare_analytic_lines_domain()
        if self.include_timesheets:
            # include timesheet analytic lines which have both project task and employee but have no journal item
            domain = ['|', '&', ('task_id', '!=', False), ('employee_id', '!=', False)] + domain
        return domain
