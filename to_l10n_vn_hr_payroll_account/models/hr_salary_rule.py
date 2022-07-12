from odoo import models, api


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    @api.model
    def _get_fields_to_reset(self):
        data_dict = super(HrSalaryRule, self)._get_fields_to_reset()
        data_dict.update({
            'generate_account_move_line': False,
            'account_debit': False,
            'account_credit': False,
            'anylytic_option': 'none',
            })
        return data_dict

    def _get_partner(self, credit_account, employee=None):
        """
        Get partner of the salary rule to use in account move line
        """
        employee = employee or self.env['hr.employee']
        vn_coa = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
        if self.company_id.chart_template_id in vn_coa and self.register_id.partner_id:
            all_account = ['338', '333', '138', '128']
            if credit_account and self.account_credit.code and any(self.account_credit.code[:3] == code for code in all_account):
                return self.register_id.partner_id
            elif not credit_account and self.account_debit.code and any(self.account_debit.code[:3] == code for code in all_account):
                return self.register_id.partner_id
            else:
                return employee.address_home_id
        else:
            return super(HrSalaryRule, self)._get_partner(credit_account, employee)
