from odoo import fields, models

TAX_POLICY = [
    ('escalation', 'Progressive Tax Table'),
    ('flat_rate', 'Flat Rate')
    ]


class HrContract(models.Model):
    _inherit = 'hr.contract'

    salary_attendance_computation_mode = fields.Selection(selection_add=[
        ('attendance', 'Attendance Entries'),
        ],
        ondelete={'attendance': 'set default'},
        help="How the employee worked hours would be computed in salary rules, based on either Time-Off registration or"
        " attendance data (depending on the availability of the module `to_hr_payroll_attendance`):\n"
        "* Time-Off Registration: worked hours (and days) and the paid rate will be computed correspondingly based on the"
        " formulas `Duty Working Hours (or Days) - Leave Hours (or Days)` and `(Duty Working Hours (or Days) - Unpaid"
        " Leave Hours (or Days)) / Calendar Working Hours (or Days) in Full Month`;\n"
        "* Attendance Entries: worked hours will be the total valid attendance hours and the paid rate will be computed as:"
        " Valid Attendance Hours / Calendar Working Hours in Full Month.")
