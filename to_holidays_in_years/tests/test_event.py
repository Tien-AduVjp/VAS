import datetime

from odoo.exceptions import ValidationError
from odoo.tests.common import Form, SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestEvent(SavepointCase):

    def setUp(self):
        super(TestEvent, self).setUp()
        self.event_lunar = self.env['holiday.year'].create({
            'lunar_date': '2021-01-15',
            'date_type': 'lunar_date',
            'date_from': '2021-02-26 00:00:00',
            'date_to': '2021-02-26 23:59:59'
        })
        self.event_solar = self.env['holiday.year'].create({
            'lunar_date': '2021-01-01',
            'date_type': 'solar_date',
            'date_from': '2021-01-01 00:00:00',
            'date_to': '2021-01-01 23:59:59'
        })

    def test_compute_holiday_date(self):
        self.assertEqual(self.event_lunar.holiday_date, datetime.date(2021, 2, 26), 'Wrong compute lunar_date from lunar_date')
        self.assertEqual(self.event_solar.holiday_date, datetime.date(2021, 1, 1), 'Wrong compute solar_date to lunar_date')

    def test_onchange_lunar_date(self):
        self.holidays_in_years_lunar_form = Form(self.event_lunar)
        self.holidays_in_years_lunar_form.date_type = 'solar_date'
        self.assertEqual(self.holidays_in_years_lunar_form.date_from, datetime.datetime(2021, 1, 15, 0, 0, 0), "Wrong date_from")
        self.assertEqual(self.holidays_in_years_lunar_form.date_to, datetime.datetime(2021, 1, 15, 23, 59, 59), "Wrong date_to")
        self.holidays_in_years_lunar_form.save()

        self.holidays_in_years_solar_form = Form(self.event_solar)
        self.holidays_in_years_solar_form.date_type = 'lunar_date'
        self.assertEqual(self.holidays_in_years_solar_form.date_from, datetime.datetime(2021, 2, 12, 0, 0, 0), "Wrong date_from")
        self.assertEqual(self.holidays_in_years_solar_form.date_to, datetime.datetime(2021, 2, 12, 23, 59, 59), "Wrong date_to")
        self.holidays_in_years_lunar_form.save()

        self.holidays_in_years_solar_form_2 = Form(self.event_lunar)
        with self.assertRaises(ValidationError):
            self.holidays_in_years_solar_form_2.lunar_date = '2021-04-30'
            self.holidays_in_years_solar_form_2.date_type = 'lunar_date'
            self.holidays_in_years_solar_form_2.save()
    
    def test_getSolar(self):
        solar_date = self.env['holiday.year']._getSolar(datetime.date(2022, 1, 1), 'lunar_date')
        self.assertEqual(solar_date, datetime.date(2022, 2, 1))
        
        solar_date = self.env['holiday.year']._getSolar(datetime.date(2022, 1, 1), 'solar_date')
        self.assertEqual(solar_date, datetime.date(2022, 1, 1))
