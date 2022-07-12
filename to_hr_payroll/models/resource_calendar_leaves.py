from odoo import models, fields


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    payslip_leave_interval_ids = fields.One2many('payslip.leave.interval', 'leave_id', string='Payslip Leave Intervals')
