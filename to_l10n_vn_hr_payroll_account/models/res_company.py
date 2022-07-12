from odoo import models, api, _

SALARY_RULES_ACCOUNTS_MAP = {
    'GROSS': {
        'generate_account_move_line': True,
        'account_credit': '334',
        'anylytic_option': 'debit_account',
        },
    # social ensurance by employee
    'ESINS': {
        'generate_account_move_line': True,
        'account_debit': '3383',
        'account_credit': '334',
        },
    # social ensurance by company
    'CSINS': {
        'generate_account_move_line': True,
        'account_credit': '3383',
        'anylytic_option': 'debit_account',
        },

    # health ensurance by employee
    'EHINS': {
        'generate_account_move_line': True,
        'account_debit': '3384',
        'account_credit': '334',
        },
    # health ensurance by company
    'CHINS': {
        'generate_account_move_line': True,
        'account_credit': '3384',
        'anylytic_option': 'debit_account',
        },

    # Unemployment ensurance by employee
    'EUEINS': {
        'generate_account_move_line': True,
        'account_debit': '3386',
        'account_credit': '334',
        },
    # Unemployment ensurance by company
    'CUEINS': {
        'generate_account_move_line': True,
        'account_credit': '3386',
        'anylytic_option': 'debit_account',
        },

    # Unemployment ensurance by employee
    'ELUF': {
        'generate_account_move_line': True,
        'account_debit': '3382',
        'account_credit': '334',
        },
    # Unemployment ensurance by company
    'CLUF': {
        'generate_account_move_line': True,
        'account_credit': '3382',
        'anylytic_option': 'debit_account',
        },

    # Personal income tax
    'PTAX': {
        'generate_account_move_line': True,
        'account_debit': '3335',
        'account_credit': '334',
        },

    # tax exemption allowances
    'HARMFUL': {
        'generate_account_move_line': True,
        'account_credit': '334',
        'anylytic_option': 'debit_account',
        },
    }


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _filter_vietnam_coa(self):
        """
        Filter the companies having Vietnam CoA in self
        """
        vn_coa = self.env.ref('l10n_vn.vn_template')
        return self.filtered(lambda c: c.chart_template_id and c.chart_template_id == vn_coa)

    def _get_vietnam_salary_rule_map(self):
        self.ensure_one()
        account_obj = self.env['account.account'].sudo()
        res = {}
        for code, acc_dict in SALARY_RULES_ACCOUNTS_MAP.items():
            res[code] = {}
            for field, val in acc_dict.items():
                if field in ('generate_account_move_line', 'anylytic_option'):
                    res[code][field] = val
                else:
                    account = account_obj.search([('company_id', '=', self.id), ('code', '=ilike', val + '%'), ('deprecated', '=', False)], limit=1)
                    res[code][field] = account and account.id or False
        return res

    def _parepare_salary_rules_vals_list(self, struct):
        self.ensure_one()
        vals_list = super(ResCompany, self)._parepare_salary_rules_vals_list(struct)
        vn_coa = self.env.ref('l10n_vn.vn_template')
        if self.chart_template_id and self.chart_template_id == vn_coa:
            for vals in vals_list:
                for code, acc_dict in self._get_vietnam_salary_rule_map().items():
                    if vals['code'] == code:
                        vals.update(acc_dict)
        return vals_list

    def _prepare_salary_journal_data(self):
        data = super(ResCompany, self)._prepare_salary_journal_data()
        vn_coa = self.env.ref('l10n_vn.vn_template')
        if self.chart_template_id and self.chart_template_id == vn_coa:
            default_account = self.env['account.account'].search([
                ('code', '=ilike', '334' + '%'),
                ('company_id', '=', self.id),
                ('deprecated', '=', False)], limit=1)
            data.update({
                'default_credit_account_id': default_account.id,
                'default_debit_account_id': default_account.id
                })
        return data

    def _update_vietnam_salary_account_journal_default_accounts(self):
        """
        To be called by post_init_hook
        """
        for r in self._filter_vietnam_coa():
            default_account = self.env['account.account'].sudo().search([
                ('code', '=ilike', '334' + '%'),
                ('company_id', '=', r.id),
                ('deprecated', '=', False)], limit=1)
            journals = self.env['account.journal'].sudo().search([('code', '=', 'SAL'), ('company_id', '=', r.id)])
            journals.write({
                'default_credit_account_id': default_account.id,
                'default_debit_account_id': default_account.id
                })

    def _update_vietnam_salary_rules_accounts(self):
        for r in self._filter_vietnam_coa():
            salary_rules = self.env['hr.salary.rule'].sudo().with_context(active_test=False).search([('company_id', '=', r.id)])
            for rule in salary_rules:
                for code, acc_dict in r._get_vietnam_salary_rule_map().items():
                    if rule.code == code:
                        rule.write(acc_dict)
                        
    def _update_departments_expense_account(self):
        for r in self._filter_vietnam_coa():
            departments = self.env['hr.department'].sudo().with_context(active_test=False).search([
                ('company_id', '=', r.id), ('account_expense_id', '=', False)])
            account = self.env['account.account'].search([
                ('company_id', '=', r.id),
                ('code', '=ilike', '642' + '%'), ('deprecated', '=', False)], limit=1)
            if account and departments:
                departments.write({'account_expense_id': account.id})

