from odoo import models, fields


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    rate = fields.Float(string='Rate (%)', digits='Payroll Rate', default=100.0,
                        help="The rate in percentage that could be used in other applications. For example,"
                        " calculate salary with different rate based on different attendances.")
