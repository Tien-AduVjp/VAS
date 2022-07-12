from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged

from .test_hr_meal_common import TestHrMealCommon


@tagged('post_install', '-at_install')
class TestHrMealOrder(TestHrMealCommon):

    def setUp(self):
        super(TestHrMealOrder, self).setUp()

    def test_create_meal_order(self):
        meal_order = self.create_meal_order(self.meal_type_lunch, 'external', [self.employee_1, self.employee_2])
        self.assertEqual(meal_order.order_lines_count, 2)
        self.assertEqual(meal_order.total_qty, 2)
        self.assertEqual(meal_order.total_price, 20)

    def test_delete_meal_order(self):
        meal_order = self.create_meal_order(self.meal_type_lunch, 'external', [self.employee_1, self.employee_2])
        meal_order.with_user(self.user_meal_manager).action_confirm()
        with self.assertRaises(UserError):
            meal_order.with_user(self.user_meal_manager).unlink()

    def test_overlap_meal_order_lines(self):
        meal_order_1 = self.create_meal_order(self.meal_type_lunch, 'external', [self.employee_1, self.employee_2])
        meal_order_2 = self.create_meal_order(self.meal_type_lunch, 'external', [self.employee_1])
        meal_order_3 = self.create_meal_order(self.meal_type_dinner, 'external', [self.employee_1, self.employee_1])
        with self.assertRaises(ValidationError):
            meal_order_1.with_user(self.user_meal_manager).action_confirm()
            meal_order_1.flush()
            meal_order_2.with_user(self.user_meal_manager).action_confirm()
            meal_order_2.flush()

        with self.assertRaises(ValidationError):
            meal_order_3.with_user(self.user_meal_manager).action_confirm()
            meal_order_3.flush()

    def test_empty_meal_order(self):
        meal_order = self.create_meal_order(self.meal_type_lunch, 'external', [])
        with self.assertRaises(UserError):
            meal_order.with_user(self.user_meal_manager).action_confirm()
