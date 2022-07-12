from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    allocation_type = fields.Selection(related='holiday_status_id.allocation_type', readonly=True)

    max_leave_days = fields.Float(related='holiday_status_id.max_leave_days', readonly=True)
    leave_period_unit = fields.Selection([
        ('month', 'Month'),
        ('quarter', 'Quarter'),
        ('year', 'Year'),
        ], related='holiday_status_id.leave_period_unit', readonly=True)

    @api.constrains('state', 'employee_id', 'holiday_status_id', 'number_of_days')
    def _check_holiday_period_limit(self):
        for r in self:
            if r.holiday_type == 'employee' and r.employee_id and not r.holiday_status_id.allocation_type == 'no':
                holiday_status = r.holiday_status_id
                taken_leaves = holiday_status.get_leaves_taken_in_period(
                    r.employee_id,
                    fields.Datetime.context_timestamp(r.employee_id, r.date_from)
                    )
                nb_of_leave_days = 0.0
                for leave in taken_leaves:
                    nb_of_leave_days += leave.number_of_days_display
                if holiday_status.max_leave_days > 0 and nb_of_leave_days > holiday_status.max_leave_days:
                    if holiday_status.leave_period_unit == 'month':
                        unit_str = _('Month')
                    elif holiday_status.leave_period_unit == 'quarter':
                        unit_str = _('Quarter')
                    elif holiday_status.leave_period_unit == 'year':
                        unit_str = _('Year')
                    else:
                        unit_str = ''
                    raise ValidationError(_('You have reached maximum number of leaves of type "%s" in this %s.'
                                            ' Hence, you cannot take another leave on this leave type.\n'
                                            'The maximum days of type "%s" allowed is %s while you have already'
                                            ' taken, or registered to take, %s days.')
                                          % (holiday_status.name, unit_str, holiday_status.name, holiday_status.max_leave_days, nb_of_leave_days))

