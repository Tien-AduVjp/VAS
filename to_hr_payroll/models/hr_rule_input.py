from odoo import fields, models


class HrRuleInput(models.Model):
    _name = 'hr.rule.input'
    _description = 'Salary Rule Input'

    name = fields.Char(string='Description', required=True, translate=True)
    code = fields.Char(required=True, help="The code that can be used in the salary rules. For example: inputs.CODE.amount")
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule Input', required=True)

    def _prepare_hr_payslip_input_vals(self, contract):
        self.ensure_one()
        return {
            'name': self.name,
            'code': self.code,
            'contract_id': contract.id,
            'salary_rule_id': self.salary_rule_id.id
            }
