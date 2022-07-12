from odoo.tests.common import tagged

from .common import CommonTimesheetApproval


@tagged('post_install', '-at_install')
class TestHrJob(CommonTimesheetApproval):

    def setUp(self):
        super(TestHrJob, self).setUp()
        self.job_position_1 = self.env['hr.job'].create({
            'name': 'Job 1',
        })

    def test_01_check_compute_job(self):
    # Job position have department marked 'timesheet approval'
        self.job_position_1.write({'department_id': self.department_a.id})
        self.assertTrue(self.job_position_1.timesheet_approval)

    def test_02_check_compute_job(self):
    # Job position have department marked no 'timesheet approval'
        self.department_a.write({'timesheet_approval': False})
        self.job_position_1.write({'department_id': self.department_a.id})
        self.assertFalse(self.job_position_1.timesheet_approval)
