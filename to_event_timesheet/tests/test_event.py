from datetime import datetime
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestEvent(TransactionCase):

    def setUp(self):
        super(TestEvent, self).setUp()
        self.timesheet_val = {
            'name': 'Timesheet Test',
            'unit_amount': 10
        }

        project_val = {
            'name': 'Project Template',
            'timesheet_ids': [(0, 0, self.timesheet_val)]
        }

        event_val = {
            'name': 'Test Event',
            'date_begin': datetime.today(),
            'date_end': datetime.today(),
            'project_ids': [(0, 0, project_val)],
            'total_hour': 15
        }
        self.event = self.env['event.event'].create(event_val)

    def test_compute_total_hour_case_1(self):
        vals_change = {
            'unit_amount': 20
        }

        self.assertEqual(first=self.event.total_hour, second=self.timesheet_val['unit_amount'], msg='Not compute total_hour')
        self.event.project_ids.timesheet_ids.unit_amount = vals_change['unit_amount']
        self.assertEqual(first=self.event.total_hour, second=vals_change['unit_amount'], msg='Not compute total_hour')

    def test_compute_total_hour_case_2(self):
        self.event.project_ids.timesheet_ids = [(5, 0, 0)]
        self.assertEqual(first=self.event.total_hour, second=0, msg='Not compute total_hour')
