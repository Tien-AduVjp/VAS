from odoo import models, fields


class HrOvertimeReason(models.Model):
    _inherit = 'hr.overtime.reason'

    recognition_mode = fields.Selection(selection_add=[('attendance', 'Attendance')], ondelete={'attendance':lambda self: self.company_id.overtime_recognition_mode})
