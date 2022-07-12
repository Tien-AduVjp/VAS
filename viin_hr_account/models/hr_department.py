from odoo import fields, models, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    account_expense_id = fields.Many2one('account.account', string='Expense Account', domain=[('deprecated', '=', False)],
                                         tracking=True,
                                         help="Default Expense Account that will be used for encoding the department expenses into"
                                         " general accounting system (e.g. employee payroll expenses).")
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', tracking=True,
                                          help="Default analytic account to be used for encoding analytic items related to payslips"
                                          " of this contract when no analytic account defined on the salary rules that concern.")
    analytic_tag_ids = fields.Many2many('account.analytic.tag',
                                        'hr_department_account_analytic_tag_rel', 'department_id', 'account_analytic_tag_id',
                                        string='Analytic Tags')

    @api.model_create_multi
    def create(self, vals_list):
        departments = super(HrDepartment, self).create(vals_list)
        departments._generate_analytic_account()
        return departments

    def write(self, vals):
        res = super(HrDepartment, self).write(vals)
        if 'name' in vals:
            for r in self:
                r.analytic_account_id.with_context(force_write=True).write({
                    'name': r.name
                    })
        return res

    def _prepare_analytic_account_vals(self):
        self.ensure_one()
        return {
            'name': self.name,
            'company_id': self.company_id.id
            }

    def _prepare_existing_analytic_account_domain(self):
        self.ensure_one()
        return [
            ('name', '=', self.name),
            '|', ('company_id', '=', False), ('company_id', '=', self.company_id.id)
        ]

    def _generate_analytic_account(self):
        analytic_account_sudo = self.env['account.analytic.account'].sudo()
        for r in self.filtered(lambda d: not d.analytic_account_id):
            account = analytic_account_sudo.search(r._prepare_existing_analytic_account_domain(), limit=1)
            if not account:
                account = analytic_account_sudo.create(r._prepare_analytic_account_vals())
                analytic_account_sudo |= account
            r.write({
                'analytic_account_id': account.id
                })
        return analytic_account_sudo

    def _prepare_analytic_distribution_line_vals(self, percentage=100.0):
        self.ensure_one()
        return self.analytic_account_id._prepare_analytic_distribution_line_vals(percentage) or {}
