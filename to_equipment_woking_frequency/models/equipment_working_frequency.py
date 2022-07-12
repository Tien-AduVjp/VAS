from odoo import models, fields, api, _
from datetime import datetime, timedelta
from pytz import timezone


class EquipmentWorkingFrequency(models.Model):
    _name = 'equipment.working.frequency'
    _description = 'Equipment Working Frequency'

    @api.model
    def _get_working_uom_id_domain(self):
        return [('category_id.id', '!=', self.env.ref('uom.uom_categ_wtime').id)]

    equipment_id = fields.Many2one('maintenance.equipment', string='Equipment')
    start_amount = fields.Float(string='Starting Amount', default=0.0, required=True,
                                help="The amount of work that the equipment has done before. "
                                "If the equipment is not in use, this field is set to 0.")
    working_amount = fields.Float(string='Working Amount', required=True)
    working_uom_id = fields.Many2one('uom.uom', string='Working Amount UoM', required=True, domain=_get_working_uom_id_domain)
    period_time = fields.Float(string='Period Time (Hours)', required=True)
    total_working_amount = fields.Float(string='Total Working', compute='_compute_total_working_amount')

    _sql_constraints = [
        ('working_frequency_unique',
         'unique(equipment_id,working_uom_id)',
         _("Working frequency must be unique!")),

         ('working_amount_check',
         'CHECK(working_amount >= 0)',
         "Working Amount must be greater than or equal to zero!"),

         ('period_time_check',
         'CHECK(period_time >= 0)',
         "Period Time must be greater than or equal to zero!"),

         ('start_amount_check',
         'CHECK(start_amount >= 0)',
         "Starting Amount must be greater than or equal to zero!")
    ]

    @api.depends('start_amount', 'working_amount', 'period_time', 'equipment_id.effective_date')
    def _compute_total_working_amount(self):
        for r in self:
            total_working_amount = 0.0
            resource_calendar = (r.equipment_id.resource_calendar_id
                                 or r.equipment_id.company_id.resource_calendar_id
                                 or self.env.company.resource_calendar_id)
            tz = timezone(resource_calendar.tz)
            datetime_now = fields.Datetime.context_timestamp(r, fields.Datetime.now()).astimezone(tz)
            effective_date = r.equipment_id.effective_date
            if not effective_date:
                r.total_working_amount = total_working_amount
                continue
            dayofweek = str(effective_date.weekday())
            dayofweek_list = resource_calendar.attendance_ids.mapped('dayofweek')
            if not dayofweek_list:
                r.total_working_amount = total_working_amount
            else:
                # handling to avoid errors when the effective date is a holiday
                while dayofweek not in dayofweek_list:
                    effective_date = effective_date + timedelta(days=1)
                    dayofweek = str(effective_date.weekday())

                hour_from = min(resource_calendar.attendance_ids.filtered(lambda a: a.dayofweek == dayofweek).mapped('hour_from'))
                start_time = self.env['to.base'].float_hours_to_time(hour_from)
                date_start = tz.localize(datetime.combine(effective_date, start_time))
                if r.equipment_id.effective_date and r.working_amount and r.period_time :
                    workload_per_hour = r.working_amount / r.period_time
                    total_working_time = resource_calendar.get_work_duration_data(date_start, datetime_now, compute_leaves=True)
                    if total_working_time:
                        if total_working_time['hours'] <= 0:
                            total_working_amount = r.start_amount
                        else:
                            total_working_amount = r.start_amount + workload_per_hour * total_working_time['hours']
                r.total_working_amount = total_working_amount

    def name_get(self):
        return [(p.id, "%s %s(s) per %s hours" % (p.working_amount, p.working_uom_id.name, p.period_time)) for p in self]
