from odoo import models, fields


class PayslipLeaveInterval(models.Model):
    _name = 'payslip.leave.interval'
    _rec_name = 'leave_id'
    _description = 'Payslip Leave Interval'

    working_month_calendar_line_id = fields.Many2one('hr.working.month.calendar.line', string='Working Month Calendar Line',
                                                     required=True, ondelete='cascade', index=True)
    leave_id = fields.Many2one('resource.calendar.leaves', string='Time Off', ondelete='restrict', index=True)
    holiday_id = fields.Many2one(related='leave_id.holiday_id', store=True, index=True)
    holiday_status_id = fields.Many2one(related='leave_id.holiday_id.holiday_status_id', store=True, index=True)
    unpaid = fields.Boolean(string='Unpaid')
    date = fields.Date(string='Date')
    hours = fields.Float(string='Hours')
    days = fields.Float(string='Days')
