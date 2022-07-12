from odoo import models, fields


class HrOvertimeRequestMassLine(models.TransientModel):
    _name = 'hr.overtime.request.mass.line'
    _description = 'HR Overtime Request Mass Line'
    
    overtime_request_mass_id = fields.Many2one('hr.overtime.request.mass', string='Mass Overtime Request Wizard', required=True, ondelete='cascade')
    
    date = fields.Date(string='Date', required=True, default=fields.Date.today, help="The date on which the overtime work happens.")
    time_start = fields.Float(string='Start Time', default=0.0, required=True,
                              help="The time on the date specified in the Date at which the overtime work starts.")
    time_end = fields.Float(string='End Time', default=0.01, required=True,
                            help="The time on the date specified in the Date at which the overtime work ends.")
    
    _sql_constraints = [
        ('times_check', "CHECK (time_start < time_end)", "The Start Time must be anterior to the End Time."),
        ('time_start_check', "CHECK (time_start >= 0 and time_start < 24)", "The Start Time must be greater than or equal to 0 and less than 24."),
        ('time_start_check', "CHECK (time_end > 0 and time_end <= 24)", "The End Time must be greater than 0 and less than or equal to 24."),
    ]

    def _prepare_overtime_plan_vals(self):
        self.ensure_one()
        return {
            'date': self.date,
            'time_start': self.time_start,
            'time_end': self.time_end,
            'reason_id': self.overtime_request_mass_id.reason_id.id
            }

    def _prepare_overtime_plan_vals_list(self):
        vals_list = []
        for r in self:
            vals_list.append(r._prepare_overtime_plan_vals())
        return vals_list
