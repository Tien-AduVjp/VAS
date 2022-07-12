from odoo import models, api


class HrContributionRegister(models.Model):
    _inherit = 'hr.contribution.register'

    @api.constrains('partner_id', 'salary_rule_ids')
    def _check_salary_rule_ids_partner_id(self):
        self.filtered(lambda r: r.partner_id).salary_rule_ids._check_register_employee_journal_item()
