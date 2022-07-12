from odoo import models


class Company(models.Model):
    _inherit = 'res.company'

    def _update_vietnam_meal_salary_rule_accounts(self):
        for r in self._filter_vietnam_coa():
            meal_salary_rules = self.env['hr.salary.rule'].sudo().search([('code', '=', 'MODED'),('company_id', '=', r.id)])
            account334 = self.env['account.account'].search([('code', '=ilike', '334' + '%'), ('company_id', '=', r.id)], limit=1)
            account1388 = self.env['account.account'].search([('code', '=ilike', '1388' + '%'), ('company_id', '=', r.id)], limit=1)
            for rule in meal_salary_rules:
                rule.write({'account_debit': account1388.id, 'account_credit': account334.id})
