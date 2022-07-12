from odoo import fields, models


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    update_employee_timesheet_cost = fields.Boolean(string='Update Employee Timesheet Cost', default=True,
                                                    help="If enabled, upon confirming a payslip, the"
                                                    " following will updated to reflect the new computed"
                                                    " timesheet cost based on payslip computation:\n"
                                                    "- Employee Timesheet Cost: which is found in employee form view\n"
                                                    "- Total Amount of all timesheet records within the payslip's period.")
