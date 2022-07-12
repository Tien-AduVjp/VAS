from odoo import fields, models, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _get_default_journal_id(self):
        return self.env['account.journal'].sudo().search([('code', '=', 'SAL'), ('company_id', '=', self.env.company.id)], limit=1)

    account_expense_id = fields.Many2one('account.account', string='Expense Account',
                                         domain="[('deprecated', '=', False),('company_id', '=', company_id)]", tracking=True,
                                         help="Default Expense Account that will be used for encoding employee expenses into"
                                         " general accounting system (e.g. employee payroll expenses). If not specified, the one"
                                         " specified for the corresponding department will be used.")
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', tracking=True,
                                          groups='analytic.group_analytic_accounting',
                                          help="Default analytic account to be used for encoding analytic items related to payslips"
                                          " of this contract when no analytic account defined on the salary rules that concern.")
    journal_id = fields.Many2one('account.journal', string='Salary Journal', default=_get_default_journal_id, tracking=True, groups='account.group_account_user')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', groups='analytic.group_analytic_tags')

    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        # Override to avoid access rights error when duplicating contract if the user has no accounting access rights
        default = default or {}
        if 'account_expense_id' not in default:
            default['account_expense_id'] = self.sudo().account_expense_id.id
        if 'analytic_account_id' not in default:
            default['analytic_account_id'] = self.sudo().analytic_account_id.id
        if 'journal_id' not in default:
            default['journal_id'] = self.sudo().journal_id.id
        if 'analytic_tag_ids' not in default:
            default['analytic_tag_ids'] = [(6, 0, self.sudo().analytic_tag_ids.ids)]
        return super(HrContract, self).copy(default=default)

    def _get_accounts(self):
        self.ensure_one()
        # use sudo to avoid access error when analytic accounting is not enabled
        self_sudo = self.sudo()
        return {
            'expense_account': self_sudo.account_expense_id or self_sudo.department_id.account_expense_id,
            'analytic_account': self_sudo.analytic_account_id or self_sudo.department_id.analytic_account_id,
            'analytic_tags': self_sudo.analytic_tag_ids or self_sudo.department_id.analytic_tag_ids,
            }
