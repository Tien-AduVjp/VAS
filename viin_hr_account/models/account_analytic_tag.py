from odoo import fields, models, api


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    department_ids = fields.Many2many('hr.department',
                                        'hr_department_account_analytic_tag_rel', 'account_analytic_tag_id', 'department_id',
                                        string='HR Departments')

    @api.onchange('department_ids', 'active_analytic_distribution')
    def _onchange_hr_department_active_analytic_distribution(self):
        departments = self.department_ids.filtered(lambda d: d.analytic_account_id)
        if self.active_analytic_distribution and departments:
            distribution_lines = self.env['account.analytic.distribution']
            for department in departments:
                new_line = distribution_lines.new(department._prepare_analytic_distribution_line_vals(100.0 / len(departments)))
                distribution_lines += new_line
            self.analytic_distribution_ids = distribution_lines
