from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    pow_timesheet_required = fields.Boolean(string='PoW Timesheet Required', default=True, tracking=True,
                                            groups="hr.group_hr_user",
                                            help="If checked, the employee will be required to log timesheet for PoW"
                                            " (proof of work) during time off of the time off types that require"
                                            " timesheet recording for PoW (e.g. Work from home, etc).")
