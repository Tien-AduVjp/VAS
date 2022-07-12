from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from ..lib import lunardate


class HolidayYear(models.Model):
    _name = 'holiday.year'
    _description = "Holiday Years"
    _inherits = {'resource.calendar.leaves': 'resource_leaves_id'}

    resource_leaves_id = fields.Many2one('resource.calendar.leaves', ondelete='cascade', required=True)
    lunar_date = fields.Date(default=fields.Date.today, string='Holiday Date', required=True)
    holiday_date = fields.Date(string="Convert to Calendar day", compute='_compute_holiday_date', store=True)
    holiday_type = fields.Selection([('national_holiday', 'National Holiday'), ('other_holiday', 'Other Holiday')], default='national_holiday')
    date_type = fields.Selection([('solar_date', 'Solar Calendar'), ('lunar_date', 'Lunar Day')], default='solar_date')
    company_id = fields.Many2one('res.company', string="Company", ondelete="set null", default=lambda self: self.resource_leaves_id.company_id or self.env.company)
    year = fields.Integer(string="Year")

    _sql_constraints = [
        ('unique_date', 'unique(holiday_date)', 'The holiday has been declared.')
    ]

    @api.depends('lunar_date', 'date_type')
    def _compute_holiday_date(self):
        for r in self:
            r.holiday_date = self._getSolar(r.lunar_date, r.date_type)

    @api.onchange('lunar_date', 'date_type')
    def _onchange_lunar_date_and_date_type(self):
        for r in self:
            if r.lunar_date and r.date_type:
                solar_date = self._getSolar(r.lunar_date, r.date_type)
                r.date_from = str(solar_date) + ' 00:00:00'
                r.date_to = str(solar_date) + ' 23:59:59'

    def unlink(self):
        self.mapped('resource_leaves_id').unlink()
        super(HolidayYear, self).unlink()

    def write(self, vals):
        if 'date_to' in vals:
            if fields.Datetime.to_datetime(vals['date_to']) < self.resource_leaves_id.date_from:
                super(HolidayYear, self).write({'date_from': vals.pop('date_from')})
            super(HolidayYear, self).write({'date_to': vals.pop('date_to')})
        return super(HolidayYear, self).write(vals)

    def _getSolar(self, lunar_date, date_type):
        if  date_type == 'solar_date':
            return lunar_date
        temp_year = int(str(lunar_date).split('-')[0])
        temp_month = int(str(lunar_date).split('-')[1]) + 1
        if temp_month > 12:
            temp_month = 1
            temp_year += 1
        try:
            lunar = lunardate.LunarDate.fromSolarDate(temp_year, temp_month, int(str(lunar_date).split('-')[2]))
            leapMonth = 1 if lunar.isLeapMonth else 0
            solar = lunardate.LunarDate(int(str(lunar_date).split('-')[0]), int(str(lunar_date).split('-')[1]), int(str(lunar_date).split('-')[2]), leapMonth).toSolarDate()
            return solar
        except Exception as e:
            raise ValidationError(_("Incorrect lunar date: day is out of range for month. Month: %s; Day: %s") % (lunar_date.month, lunar_date.day))
