from odoo import models, fields


class HrOvertimeReason(models.Model):
    _inherit = 'hr.overtime.reason'

    recognition_mode = fields.Selection(selection_add=[('timesheet', 'Timesheet')], ondelete={'timesheet': lambda self: self.company_id.overtime_recognition_mode})
    project_required = fields.Boolean(string='Project Required', help="If enabled, all the overtime plans of this reason require a project specified.")
