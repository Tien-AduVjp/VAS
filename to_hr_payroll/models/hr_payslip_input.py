from odoo import fields, models

from .browsable_object import InputLine


class HrPayslipInput(models.Model):
    _name = 'hr.payslip.input'
    _description = 'Payslip Input'
    _order = 'payslip_id, sequence'

    name = fields.Char(string='Description', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(required=True, index=True, default=10)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    amount = fields.Float(help="It is used in computation. For e.g. A rule for sales having "
                               "1% commission of basic salary for per product can defined in expression "
                               "like result = inputs.SALEURO.amount * contract.wage*0.01.")
    contract_id = fields.Many2one('hr.contract', string='Contract', required=True,
        help="The contract for which applied this input")
    salary_rule_id = fields.Many2one('hr.salary.rule', string='Salary Rule',
                                     help="The salary rule that generated this payslip input.")

    def get_inputline_obj(self):
        """
        Get an InputLine object for usage in salary rule python code
        @return: InputLine object
        @rtype: InputLine
        """
        inputs_dict = {}
        for r in self:
            inputs_dict[r.code] = r
        return InputLine(self.payslip_id.employee_id.id, inputs_dict, self.env)
