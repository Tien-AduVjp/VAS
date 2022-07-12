from datetime  import timedelta, datetime
from pytz import timezone
from unittest.mock import patch

from odoo import fields
from odoo.tests import TransactionCase, Form, tagged

from . import ultils

@tagged('post_install', '-at_install')
class TestEquipmentWorkingFrequency(TransactionCase):

    def setUp(self):
        super(TestEquipmentWorkingFrequency, self).setUp()
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.working_hour = self.env.ref('resource.resource_calendar_std')
        form_maintenance_equipment = Form(self.env['maintenance.equipment'])
        with form_maintenance_equipment as f:
            f.name = 'Equipment test 01'
            f.resource_calendar_id = self.working_hour
            f.effective_date = fields.Date.to_date('2022-02-09')
            with f.equipment_working_frequency_ids.new() as line:
                line.start_amount = ultils.START_AMOUNT
                line.working_amount = ultils.WORKING_AMOUNT
                line.working_uom_id = self.uom_unit
                line.period_time = ultils.PERIOD_TIME
        self.equipment = form_maintenance_equipment.save()

    @patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2022-02-12 09:00:00'))
    def test_compute_total_working_amount(self):
        """
            *Test compute Total Working Amount
            total_working_amount = start_amount + (working_amount / period_time) *
            (the total time from the time the machine is operating to the current date according to the working schedule)
        """
        dayofweek_list = self.equipment.resource_calendar_id.attendance_ids.mapped('dayofweek')
        if not dayofweek_list:
            self.assertEqual(self.equipment.equipment_working_frequency_ids[:1].total_working_amount, 0)
        else:
            tz = timezone(self.equipment.resource_calendar_id.tz)
            effective_date = self.equipment.effective_date
            dayofweek = str(effective_date.weekday())
            while dayofweek not in dayofweek_list:
                effective_date = effective_date + timedelta(days=1)
                dayofweek = str(effective_date.weekday())
            hour_from = min(self.equipment.resource_calendar_id.attendance_ids.filtered(lambda a: a.dayofweek == dayofweek).mapped('hour_from'))
            start_time = self.env['to.base'].float_hours_to_time(hour_from)
            date_from = tz.localize(datetime.combine(effective_date, start_time))
            date_to = fields.Datetime.context_timestamp(self.equipment, fields.Datetime.now()).astimezone(tz)
            total_working_time = self.equipment.resource_calendar_id.get_work_duration_data(date_from, date_to, compute_leaves=True)
            total_working = ultils.START_AMOUNT +  total_working_time['hours'] * (ultils.WORKING_AMOUNT / ultils.PERIOD_TIME)
            self.assertEqual(self.equipment.equipment_working_frequency_ids[:1].total_working_amount, total_working)
