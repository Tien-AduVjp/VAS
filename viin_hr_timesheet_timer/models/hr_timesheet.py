from datetime import datetime, time
from pytz import timezone

from odoo import api, fields, models
from odoo.tools import relativedelta


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    time_start = fields.Float(string='Start Time', help="Employee's local time at which the work was started.")
    date_start = fields.Datetime(string='Start Date', compute='_compute_date_start', inverse='_set_date_start', store=True)
    date_end = fields.Datetime(string='End Date', compute='_compute_date_end', store=True)

    @api.depends('date', 'time_start', 'project_id')
    def _compute_date_start(self):
        float_hours_to_time = self.env['to.base'].float_hours_to_time
        for r in self:
            r.date_start = False
            if r.project_id and r.date:
                if r.time_start > 24:
                    r.time_start = 24
                if r.time_start == 24:
                    date_start = datetime.combine(r.date + relativedelta(days=1), time.min)
                else:
                    date_start = datetime.combine(r.date, float_hours_to_time(r.time_start))
                utc = self.env['to.base'].convert_time_to_utc(
                    date_start,
                    tz_name=r.employee_id.tz or self.env.user.tz or 'UTC',
                    naive=True
                    )
                r.date_start = utc

    @api.depends('date_start', 'unit_amount', 'employee_id', 'project_id')
    def _compute_date_end(self):
        for r in self:
            if r.project_id and r.employee_id and r.date_start and r.unit_amount > 0.0:
                r.date_end = r.date_start + relativedelta(hours=r.unit_amount)
            else:
                r.date_end = False

    def _set_date_start(self):
        time_to_float_hour = self.env['to.base'].time_to_float_hour
        for r in self:
            tz = r.employee_id.tz or self.env.user.tz or self._context.get('tz') or 'UTC'
            if r.date_start:
                local_datetime = r.date_start.astimezone(tz=timezone(tz)).replace(tzinfo=None)
                r.date = local_datetime.date()
                r.time_start = time_to_float_hour(local_datetime)

    def _get_elapsed_time(self):
        self.ensure_one()
        if self.date_start:
            return (fields.Datetime.now() - self.date_start).total_seconds() / 3600
        return 0.0
