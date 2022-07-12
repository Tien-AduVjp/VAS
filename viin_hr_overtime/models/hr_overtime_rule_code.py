from odoo import models, fields


class HrOvertimeRuleCode(models.Model):
    _name = 'hr.overtime.rule.code'
    _description = 'Overtime Rule Code'

    name = fields.Char(string='Code', size=40, help="The unique code to be used in conjunction with Overtime Rule for overtime payroll computation", required=True)
    pay_rate = fields.Float(string='Pay Rate', help="The extra pay in percentage (of basic wage, for example) which can be used in payroll computation.", required=True, default=100.0)
    holiday = fields.Boolean(string='Holiday', default=False, help="If enabled, this indicates the rule code is for overtime in holidays")

    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', "The code must be unique"),
    ]
