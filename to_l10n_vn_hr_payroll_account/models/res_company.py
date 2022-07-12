from odoo import models

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

    def _get_vietnam_salary_rule_map(self):
        self.ensure_one()
        res = {}
        coa_200 = self.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        coa_133 = self.env.ref('l10n_vn_c133.vn_template_c133', raise_if_not_found=False)
        if coa_133 and self.chart_template_id == coa_133:
            SALARY_RULES_ACCOUNTS_MAP.update({
                # Unemployment ensurance by employee
                'EUEINS': {
                    'generate_account_move_line': True,
                    'account_debit': '3385',
                    'account_credit': '334',
                },
                # Unemployment ensurance by company
                'CUEINS': {
                    'generate_account_move_line': True,
                    'account_credit': '3385',
                    'anylytic_option': 'debit_account',
                },
            })
        elif coa_200 and self.chart_template_id == coa_200:
            SALARY_RULES_ACCOUNTS_MAP.update({
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
            })

        for code, acc_dict in SALARY_RULES_ACCOUNTS_MAP.items():
            res[code] = {}
            for field, val in acc_dict.items():
                if field in ('generate_account_move_line', 'anylytic_option'):
                    res[code][field] = val
                else:
                    account = self.env['account.account'].sudo().search([
                        ('company_id', '=', self.id),
                        ('code', '=ilike', val + '%'),
                        ('deprecated', '=', False)
                        ], limit=1)
                    res[code][field] = account and account.id or False
        return res

    def _parepare_salary_rules_vals_list(self, struct):
        self.ensure_one()
        vals_list = super(ResCompany, self)._parepare_salary_rules_vals_list(struct)
        vn_coa = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if self.chart_template_id and self.chart_template_id in vn_coa:
            for vals in vals_list:
                for code, acc_dict in self._get_vietnam_salary_rule_map().items():
                    if vals['code'] == code:
                        vals.update(acc_dict)
        return vals_list

    def _update_vietnam_salary_rules_accounts(self):
        for r in self._filter_vietnam_coa():
            salary_rules = self.env['hr.salary.rule'].sudo().with_context(active_test=False).search([('company_id', '=', r.id)])
            for rule in salary_rules:
                for code, acc_dict in r._get_vietnam_salary_rule_map().items():
                    if rule.code == code:
                        rule.write(acc_dict)
