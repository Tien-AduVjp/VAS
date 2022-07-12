from datetime import datetime
from odoo.tests import SingleTransactionCase, tagged


@tagged('post_install', '-at_install')
class TestEvent(SingleTransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestEvent, cls).setUpClass()

        event_val = {
            'name': 'Test Event',
            'date_begin': datetime(2021, 10, 10, 8, 0, 0),
            'date_end': datetime(2021, 10, 10, 11, 0, 0)
        }
        cls.event = cls.env['event.event'].create(event_val)

        cls.project_vals = [{
            'name': 'Project Template'
        }]

    def test_compute_project_count_case_1(self):
        projects = [(0, 0, project_val) for project_val in self.project_vals]

        self.event.project_ids = projects

        self.assertEqual(first=self.event.project_count, second=len(self.project_vals), msg='Not compute project_count')

    def test_compute_project_count_case_2(self):
        project_val = {
            'name': 'Project 2 Template'
        }
        project = self.env['project.project'].create(project_val)

        project.event_id = self.event.id

        self.assertEqual(first=self.event.project_count, second=len(self.project_vals) + 1, msg='Not compute project_count')
