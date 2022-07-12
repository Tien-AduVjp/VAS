from odoo import models, fields


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    salary_rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule', copy=False, groups="to_hr_payroll.group_hr_payroll_user",
                                     help="The salary rule that generated this journal item.")

