from datetime import datetime
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestEvent(TransactionCase):

    def setUp(self):
        super(TestEvent, self).setUp()

        project1 = self.env['project.project'].create({
            'name': 'project 1'
            })

        project2 = self.env['project.project'].create({
            'name': 'project 2'
            })

        self.timesheet1 = self.env['account.analytic.line'].create({
                'project_id': project1.id,
                'date': datetime.today(),
                'date_start': datetime.today(),
                'employee_id': self.env.ref('hr.employee_al').id,
                'unit_amount': 2
                })

        self.timesheet2 = self.env['account.analytic.line'].create({
                'project_id': project1.id,
                'date': datetime.today(),
                'date_start': datetime.today(),
                'employee_id': self.env.ref('hr.employee_al').id,
                'unit_amount': 0
                })

        self.timesheet3 = self.env['account.analytic.line'].create({
                'project_id': project2.id,
                'date': datetime.today(),
                'date_start': datetime.today(),
                'employee_id': self.env.ref('hr.employee_al').id,
                'unit_amount': 0
                })
        event_val = {
            'name': 'Test Event',
            'date_begin': datetime.today(),
            'date_end': datetime.today(),
            'project_ids': [(6, 0, [project1.id,project2.id])],
        }
        self.event = self.env['event.event'].create(event_val)

    def test_compute_total_hour_case_1(self):
        self.assertEqual(self.event.total_timesheet_hours, 2)

    def test_compute_total_hour_case_2(self):
        self.timesheet2.unit_amount = 2
        self.event.invalidate_cache(None,None)
        self.assertEqual(self.event.total_timesheet_hours, 4)

    def test_compute_total_hour_case_3(self):
        self.timesheet2.unit_amount = 2
        self.timesheet3.unit_amount = 4
        self.event.invalidate_cache(None,None)
        self.assertEqual(self.event.total_timesheet_hours, 8)

