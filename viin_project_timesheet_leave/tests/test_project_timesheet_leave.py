
from odoo.exceptions import AccessError
from odoo.tests.common import SavepointCase, Form, tagged


@tagged('post_install', '-at_install')
class TestProjectTimeSheetLeave(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProjectTimeSheetLeave, cls).setUpClass()
        cls.hr_leave_type = cls.env.ref('hr_holidays.holiday_status_cl')
        cls.user_demo = cls.env.ref('base.user_demo')

    def test_01_compute_project_required(self):
        """ If timesheet_generate = True, project_required can be True or False
            When change timesheet_generate from True to False, function onchange_timesheet_generate will change project_required = False"""
        self.hr_leave_type.timesheet_generate = True
        form = Form(self.hr_leave_type)
        form.project_required = False
        form.project_required = True
        form.timesheet_generate = False
        form.save()
        self.assertFalse(self.hr_leave_type.project_required, "viin_project_timesheet_leave: wrong onchange_timesheet_generate")

    def test_project_required_false(self):
        """When project_required = False, timesheet_project_id can be False"""
        self.hr_leave_type.timesheet_generate = True
        self.hr_leave_type.project_required = False
        form = Form(self.env['hr.leave'])
        form.name = 'Hol21'
        form.employee_id = self.user_demo.employee_id
        form.holiday_status_id = self.hr_leave_type
        form.date_from = '2022-08-01 08:00:00'
        form.date_to = '2022-08-01 17:00:00'
        form.number_of_days = 1
        form.save()

    def test_project_required_true(self):
        """When project_required = True, timesheet_project_id is require"""
        self.hr_leave_type.timesheet_generate = True
        self.hr_leave_type.project_required = True
        form = Form(self.env['hr.leave'])
        form.name = 'Hol21'
        form.employee_id = self.user_demo.employee_id
        form.holiday_status_id = self.hr_leave_type
        form.date_from = '2022-08-01 08:00:00'
        form.date_to = '2022-08-01 17:00:00'
        form.number_of_days = 1
        with self.assertRaises(AssertionError):
            form.save()
