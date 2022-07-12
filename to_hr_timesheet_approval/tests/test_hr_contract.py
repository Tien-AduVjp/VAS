from odoo.tests.common import tagged

from .common import CommonTimesheetApproval


@tagged('-at_install', 'post_install')
class TestHrContract(CommonTimesheetApproval):

    def test_01_check_compute_contract(self):
    # Contract has department or job marked 'timesheet approval'
        self.contract_employee_1.write({'department_id': self.department_a.id})
        self.assertTrue(self.contract_employee_1.timesheet_approval)

    def test_02_check_compute_contract(self):
    # Contract has department or job marked 'timesheet approval'
        self.job_position_1.write({'timesheet_approval': True})
        self.contract_employee_1.write({'job_id': self.job_position_1.id})
        self.assertTrue(self.contract_employee_1.timesheet_approval)

    def test_03_check_compute_contract(self):
    # Contract has department and job marked no 'timesheet approval'
        self.department_a.write({'timesheet_approval': False})
        self.contract_employee_1.write({
            'department_id': self.department_a.id,
            'job_id': self.job_position_1.id
        })
        self.assertFalse(self.contract_employee_1.timesheet_approval)
