# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    overtime_recognition_mode = fields.Selection(related='company_id.overtime_recognition_mode', readonly=False)
    module_viin_hr_overtime_attendance = fields.Boolean(string='Overtime with Attendance')
    module_viin_hr_overtime_timesheet = fields.Boolean(string='Overtime Timesheet')
    module_viin_hr_overtime_approval = fields.Boolean(string='Overtime Plan Approval')
    module_viin_hr_overtime_payroll = fields.Boolean(string='Overtime Payroll')
