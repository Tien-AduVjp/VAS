from datetime import datetime
from odoo import models, fields


class AdjustmentLeave(models.TransientModel):
    _name = 'adjustment.leave'
    _description = "Time Off Adjustment"

    leave_id = fields.Many2one('hr.leave', string='Time Off', required=True)
    date_from = fields.Date(string="Date From", required=True)
    date_to = fields.Date(string="Date To", required=True)

    def action_confirm(self):
        leave = self.leave_id
        date_from = datetime.combine(self.date_from, leave.date_from.time())
        date_to = datetime.combine(self.date_to, leave.date_to.time())
        leave._adjust_dates(date_from, date_to)
