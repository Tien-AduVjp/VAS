from odoo import models, api, _

SALARY_RULES_ACCOUNTS_MAP = {
    'UNTAXED_OT': {
        'generate_account_move_line': True,
        'account_credit': '334',
        'anylytic_option': 'debit_account',
        },
    }


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _get_ot_salary_rule_map(self):
        self.ensure_one()
        res = {}
        account_obj = self.env['account.account'].sudo()
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
                for code, acc_dict in self._get_ot_salary_rule_map().items():
                    if vals['code'] == code:
                        vals.update(acc_dict)
        return vals_list

    def _update_ot_salary_rules_accounts(self):
        for r in self._filter_vietnam_coa():
            salary_rules = self.env['hr.salary.rule'].sudo().with_context(active_test=False).search([('company_id', '=', r.id)])
            for rule in salary_rules:
                for code, acc_dict in r._get_ot_salary_rule_map().items():
                    if rule.code == code:
                        rule.write(acc_dict)

