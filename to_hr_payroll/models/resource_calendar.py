from odoo import models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _prepare_payslip_working_month_calendar_line_data(self, date_from, date_to):
        self.ensure_one()
        return {
            'date_from': date_from,
            'date_to': date_to,
            'resource_calendar_id': self.id,
            }
