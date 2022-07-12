from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import CommonTimesheetApproval


@tagged('-at_install', 'post_install')
class TestTimesheetApprovalRequest(CommonTimesheetApproval):
    
    @classmethod
    def setUpClass(cls):
        super(TestTimesheetApprovalRequest, cls).setUpClass()
        # type that only supports test cases
        cls.approve_type_generic = cls._create_type(
            name='Generic',
            type='generic'
        )
        
    def test_01_check_timesheet_approval(self):
    # Check create timesheet approval request
        self.timesheet_approve_request_employee = self.env['approval.request'].create({
            'title': 'Timesheet Approval Request Employee 1',
            'employee_id': self.employee_1.id,
            'approval_type_id': self.approve_type_no_valid.id,
        })
        self.assertEqual(self.timesheet_approve_request_employee.approval_type_id.type, 'timesheets')
        self.assertEqual(len(self.timesheet_approve_request_employee.timesheet_line_ids), 2)
        self.assertEqual(self.timesheet_approve_request_employee.timesheet_line_ids.employee_id, self.employee_1)
    
    def test_02_check_timesheet_approval(self):
    # Change the approval type, not the 'timesheets' type, in the request has timesheets
        self.timesheet_approve_request_employee = self.env['approval.request'].create({
            'title': 'Approval Request Employee 1',
            'employee_id': self.employee_1.id,
            'approval_type_id': self.approve_type_generic.id,
        })
        with self.assertRaises(UserError):
            self.timesheet_approve_request_employee.write({
                'timesheet_line_ids': [(6, 0, [self.timesheet_1.id])]
            })

    def test_03_check_timesheet_approval(self):
    # The request contains timekeeping of multiple employees
        with self.assertRaises(UserError):
            self.timesheet_approve_request_employee = self.env['approval.request'].create({
                'title': 'Timesheet Approval Request Employee 1',
                'employee_id': self.employee_1.id,
                'approval_type_id': self.approve_type_no_valid.id,
                'timesheet_line_ids': [(6, 0, [self.timesheet_1.id, self.timesheet_2.id, self.timesheet_3.id])]
            })
    
    def test_04_check_timesheet_approval(self):
    # Delete timesheet when assigned with a request
        self.timesheet_approve_request_employee = self.env['approval.request'].create({
            'title': 'Timesheet Approval Request Employee 1',
            'employee_id': self.employee_1.id,
            'approval_type_id': self.approve_type_no_valid.id,
        })
        self.timesheet_1.unlink()

    """
        Check execution at timekeeping request on model timesheet
    """
    def test_05_check_timesheet_approval(self):
    # Create timesheet approve from model timesheets with timesheet not in draft status
        self.timesheet_1.write({'timesheet_state': 'validate'})
        with self.assertRaises(UserError):
            timesheet_approval_wizard = self.env['timesheet.approval.request.create'].create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_1.id])],
                'employee_id': self.employee_1.id,
            })

    def test_06_check_timesheet_approval(self):
    # Create timesheet approve from model timesheets with same employee timesheet
        timesheet_approval_wizard = self.env['timesheet.approval.request.create'].with_user(self.user_employee_1).create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_1.id])],
                'employee_id': self.employee_1.id,
            })

    def test_07_check_timesheet_approval(self):
    # Create timesheet approve from model timesheets with multiple employee timesheet
        with self.assertRaises(UserError):
            timesheet_approval_wizard = self.env['timesheet.approval.request.create'].with_user(self.user_employee_1).create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_1.id, self.timesheet_3.id])],
                'employee_id': self.employee_1.id,
            })
    
    def test_08_check_timesheet_approval(self):
    # Create a request for timesheet approval for subordinates
        timesheet_approval_wizard = self.env['timesheet.approval.request.create'].with_user(self.user_employee_1).create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_2.id])],
                'employee_id': self.employee_2.id,
            })

    def test_09_check_timesheet_approval(self):
    # Create a request for timesheet approval for non-subordinates
        with self.assertRaises(UserError):
            timesheet_approval_wizard = self.env['timesheet.approval.request.create'].with_user(self.user_employee_1).create({
                'title': 'Timesheet Approval Demo',
                'timesheet_line_ids': [(6, 0, [self.timesheet_4.id])],
                'employee_id': self.employee_approve_officer.id,
            })
