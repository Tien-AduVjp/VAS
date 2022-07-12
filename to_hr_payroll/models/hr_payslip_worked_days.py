from odoo import fields, models

from .browsable_object import WorkedDays


class HrPayslipWorkedDays(models.Model):
    # TODO: remove this model in master/15
    _name = 'hr.payslip.worked_days'
    _description = 'Payslip Worked Days'
    _order = 'payslip_id, sequence'

    name = fields.Char(string='Description', required=True)
    payslip_id = fields.Many2one('hr.payslip', string='Pay Slip', required=True, ondelete='cascade', index=True)
    sequence = fields.Integer(required=True, index=True, default=10)
    code = fields.Char(required=True, help="The code that can be used in the salary rules")
    number_of_days = fields.Float(string='Number of Days')
    number_of_hours = fields.Float(string='Number of Hours')
    contract_id = fields.Many2one('hr.contract', string='Contract', help="The contract for which applied this input")

    def get_workedday_obj(self):
        """
        Get a WorkedDays object for usage in salary rule python code
        @return: WorkedDays object
        @rtype: WorkedDays
        """
        worked_days_dict = {}
        for r in self:
            worked_days_dict[r.code] = r
        return WorkedDays(self.payslip_id.employee_id.id, worked_days_dict, self.env)
