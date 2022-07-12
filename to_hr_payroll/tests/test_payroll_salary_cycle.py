from psycopg2 import IntegrityError
from odoo.tools import mute_logger
from odoo.tests import tagged
from .common import TestPayrollCommon


@tagged('post_install', '-at_install')
class TestPayrollSalaryCycle(TestPayrollCommon):

    # 6. Chu kỳ lương
    @mute_logger('odoo.sql_db')
    def test_salary_period(self):
        """
        Case 1: Tạo ban ghi với dữ liệu "Độ lệch ngày bắt đầu" trong khoảng từ -28 đến 27
            TH 1: Độ lệch ngày bắt đầu trong khoảng -28 đến 27
            TH 2: Độ lệch ngày bắt đầu ngoài khoảng -28 đến 27
        """
        SalaryCycle = self.env['hr.salary.cycle']

        # TH 2: Độ lệch ngày bắt đầu ngoài khoảng -28 đến 27
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                SalaryCycle.create(self._prepare_data_salary_cycle('Test 1', -29, 0))
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                SalaryCycle.create(self._prepare_data_salary_cycle('Test 1', 28, 0))

        # TH 1: Độ lệch ngày bắt đầu trong khoảng -28 đến 27
        result = self.env['hr.salary.cycle'].create(self._prepare_data_salary_cycle('Test 1', 0, 0))
        self.assertTrue(result, 'Test create Salary Period not oke')

    def _prepare_data_salary_cycle(self, name, day, month):
            return {
            'name': name,
            'start_day_offset': day,
            'start_month_offset': month
        }
