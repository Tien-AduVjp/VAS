from psycopg2 import IntegrityError
from odoo.tests.common import SavepointCase, tagged, Form
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestToHrHolidaysPeriodLimit(SavepointCase):
    
    @classmethod
    def setUpClass(cls):
        super(TestToHrHolidaysPeriodLimit, cls).setUpClass()
        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))
        
        cls.user_admin = cls.env.ref('base.user_admin')
        cls.hr_leave_type_1 = cls.env['hr.leave.type'].create({
            'name': 'HR Leave Type 1',
            'request_unit': 'hour',
            'responsible_id': cls.user_admin.id,
            'allocation_type': 'fixed',
            'max_leave_days': 1,
            'leave_period_unit': 'month',
            'color_name': 'red'
        })
        allocation = cls.env['hr.leave.allocation'].create({
            'name': 'Allocation of HR Leave Type 1 to Mitchell Admin',
            'holiday_status_id': cls.hr_leave_type_1.id,
            'holiday_type': 'employee',
            'employee_id': cls.user_admin.employee_id.id,
            'number_of_days': 20
        })
        allocation.action_validate()
    
    def test_01_check_holiday_period_limit_monthly(self):
        # case 1. Th1
        with self.assertRaises(ValidationError):
            self.env['hr.leave'].create({
                'holiday_status_id': self.hr_leave_type_1.id,
                'date_from': '2021-11-01',
                'date_to': '2021-11-02',
                'number_of_days': 2,
                'employee_id': self.user_admin.employee_id.id
            })
    
    def test_02_check_holiday_period_limit_monthly(self):
        # case 1. Th2
        leave1 = self.env['hr.leave'].create({
            'holiday_status_id': self.hr_leave_type_1.id,
            'date_from': '2021-11-01',
            'date_to': '2021-11-01',
            'number_of_days': 1,
            'employee_id': self.user_admin.employee_id.id
        })
        
        # case 1. Th3
        leave1.action_approve()
        with self.assertRaises(ValidationError):
            self.env['hr.leave'].create({
                'holiday_status_id': self.hr_leave_type_1.id,
                'date_from': '2021-11-01',
                'date_to': '2021-11-01',
                'number_of_days': 1,
                'employee_id': self.user_admin.employee_id.id
            })
        
        # case 1. Th4
        leave2 =  self.env['hr.leave'].create({
            'holiday_status_id': self.hr_leave_type_1.id,
            'date_from': '2021-12-01',
            'date_to': '2021-12-01',
            'number_of_days': 1,
            'employee_id': self.user_admin.employee_id.id
        })
        leave2.action_approve()
    
    def test_01_check_holiday_period_limit_quarterly(self):
        # case 2. Th1
        self.hr_leave_type_1.leave_period_unit = 'quarter'
        with self.assertRaises(ValidationError):
            self.env['hr.leave'].create({
                'holiday_status_id': self.hr_leave_type_1.id,
                'date_from': '2021-09-01',
                'date_to': '2021-09-02',
                'number_of_days': 2,
                'employee_id': self.user_admin.employee_id.id
            })
    
    def test_02_check_holiday_period_limit_quarterly(self):
        # case 2. Th2
        self.hr_leave_type_1.leave_period_unit = 'quarter'
        leave1 = self.env['hr.leave'].create({
            'holiday_status_id': self.hr_leave_type_1.id,
            'date_from': '2021-09-01',
            'date_to': '2021-09-01',
            'number_of_days': 1,
            'employee_id': self.user_admin.employee_id.id
        })
        
        # case 2. Th3
        leave1.action_approve()
        with self.assertRaises(ValidationError):
            self.env['hr.leave'].create({
                'holiday_status_id': self.hr_leave_type_1.id,
                'date_from': '2021-09-02',
                'date_to': '2021-09-02',
                'number_of_days': 1,
                'employee_id': self.user_admin.employee_id.id
            })
        
        # case 3. Th4
        leave2 = self.env['hr.leave'].create({
            'holiday_status_id': self.hr_leave_type_1.id,
            'date_from': '2021-10-01',
            'date_to': '2021-10-01',
            'number_of_days': 1,
            'employee_id': self.user_admin.employee_id.id
        })
        leave2.action_approve()
    
    def test_01_check_holiday_period_limit_yearly(self):
        # case 3. Th1
        self.hr_leave_type_1.leave_period_unit = 'year'
        with self.assertRaises(ValidationError):
            self.env['hr.leave'].create({
                'holiday_status_id': self.hr_leave_type_1.id,
                'date_from': '2021-09-01',
                'date_to': '2021-09-02',
                'number_of_days': 2,
                'employee_id': self.user_admin.employee_id.id
            })
    
    def test_02_check_holiday_period_limit_yearly(self):
        # case 2. Th2
        self.hr_leave_type_1.leave_period_unit = 'year'
        leave1 = self.env['hr.leave'].create({
            'holiday_status_id': self.hr_leave_type_1.id,
            'date_from': '2021-09-01',
            'date_to': '2021-09-01',
            'number_of_days': 1,
            'employee_id': self.user_admin.employee_id.id
        })
        
        # case 2. Th3
        leave1.action_approve()
        with self.assertRaises(ValidationError):
            self.env['hr.leave'].create({
                'holiday_status_id': self.hr_leave_type_1.id,
                'date_from': '2021-12-01',
                'date_to': '2021-12-01',
                'number_of_days': 1,
                'employee_id': self.user_admin.employee_id.id
            })
        
        # case 3. Th4
        leave2 = self.env['hr.leave'].create({
            'holiday_status_id': self.hr_leave_type_1.id,
            'date_from': '2022-01-10',
            'date_to': '2022-01-10',
            'number_of_days': 1,
            'employee_id': self.user_admin.employee_id.id
        })
        leave2.action_approve()
        
    def test_constraint_max_leave_days_check(self):
        # case 4.
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.hr_leave_type_1.max_leave_days = -1
            self.hr_leave_type_1.flush()
    
    def test_no_holiday_time_limit(self):
        # case 5.
        self.hr_leave_type_1.max_leave_days = 0
        leave2 = self.env['hr.leave'].create({
            'holiday_status_id': self.hr_leave_type_1.id,
            'date_from': '2021-09-06',
            'date_to': '2021-09-10',
            'number_of_days': 5,
            'employee_id': self.user_admin.employee_id.id
        })
        leave2.action_approve()
    
    def test_01_request_leave_in_form(self):
        # case 6.
        leave_form = Form(self.env['hr.leave'].with_user(self.user_admin))
        leave_form.holiday_status_id = self.hr_leave_type_1
        leave_form.date_from = '2021-10-18 08:00:00'
        leave_form.date_to = '2021-10-19 15:00:00'
        
        with self.assertRaises(ValidationError):
            leave_form.save()
    
    def test_02_request_leave_in_form(self):
        # case 7.
        leave_form = Form(self.env['hr.leave'].with_user(self.user_admin))
        leave_form.holiday_status_id = self.hr_leave_type_1
        leave_form.date_from = '2021-10-18 08:00:00'
        leave_form.date_to = '2021-10-19 08:00:00'
        leave_form.save()
    
    def test_constraint_check_holiday_period_limit_yearly(self):
        leave1 = self.env['hr.leave'].create({
            'holiday_status_id': self.hr_leave_type_1.id,
            'date_from': '2021-11-01',
            'date_to': '2021-11-01',
            'number_of_days': 1,
            'employee_id': self.user_admin.employee_id.id
        })
        with self.assertRaises(ValidationError):
            leave1.write({
                'date_from': '2021-11-02',
                'date_to': '2021-11-03',
                'number_of_days': 2
            })
    
    def test_request_leave_for_two_quarters(self):
        # case 8.
        self.hr_leave_type_1.leave_period_unit = 'quarter'
        leave_form = Form(self.env['hr.leave'].with_user(self.user_admin))
        leave_form.holiday_status_id = self.hr_leave_type_1
        leave_form.request_date_from = '2021-03-31'
        leave_form.request_date_to = '2021-04-01'
        leave = leave_form.save()
        
        self.assertEqual(leave.number_of_days, 2)
        
        with self.assertRaises(ValidationError):
            self.env['hr.leave'].create({
                'holiday_status_id': self.hr_leave_type_1.id,
                'date_from': '2021-04-02',
                'date_to': '2021-04-02',
                'number_of_days': 1,
                'employee_id': self.user_admin.employee_id.id
            })
