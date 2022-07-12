from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from .test_hr_meal_common import TestHrMealCommon


@tagged('post_install', '-at_install')
class TestAccessRights(TestHrMealCommon):

    def setUp(self):
        super(TestAccessRights, self).setUp()
        self.meal_order_lunch = self.create_meal_order(self.meal_type_lunch, 'internal', [self.employee_1, self.employee_2])
        self.meal_order_dinner = self.create_meal_order(self.meal_type_dinner, 'external', [self.employee_1, self.employee_2])

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_meal_user_access_rights(self):
        # Meal users are able to cofirm a meal order
        self.meal_order_lunch.with_user(self.user_meal_user).action_confirm()
        self.assertEqual(self.meal_order_lunch.state, 'confirmed')

        # Meal users are not able to approve a meal order if not responsible or vendor
        with self.assertRaises(UserError):
            self.meal_order_lunch.with_user(self.user_meal_user).action_approve()

        # or refuse
        with self.assertRaises(UserError):
            self.meal_order_lunch.with_user(self.user_meal_user).action_refuse()

        # but can cancel and set to draft
        self.meal_order_lunch.with_user(self.user_meal_user).action_cancel()
        self.assertEqual(self.meal_order_lunch.state, 'cancelled', 'Meal user should be able to cancel a meal order.')
        self.meal_order_lunch.with_user(self.user_meal_user).action_draft()
        self.assertEqual(self.meal_order_lunch.state, 'draft', 'Meal user should be able to set a meal order to draft.')

        # Kitchen responsible or vendor can confirm and approve a meal order at the same time
        self.meal_order_dinner.with_user(self.user_meal_user_responsible).action_confirm()
        self.assertEqual(self.meal_order_dinner.state, 'approved')

        # Meal users should not be able to modify kitchens, meal types and meal type alerts
        with self.assertRaises(AccessError):
            self.env['hr.kitchen'].with_user(self.user_meal_user).create({'name': 'Test Kitchen'})

        with self.assertRaises(AccessError):
            self.env['hr.meal.type.alert'].with_user(self.user_meal_user).create({
                'name': 'Test Meal Alert',
                'scheduled_hour': 7.0
            })

        with self.assertRaises(AccessError):
            self.env['hr.meal.type'].with_user(self.user_meal_user).create({
                'name': 'Test Meal',
                'alert_id': self.meal_type_alert_lunch.id,
                'price': 10.0,
                'description': 'This is a test meal'
            })

    @mute_logger('odoo.addons.base.models.ir_model', 'odoo.addons.base.models.ir_rule')
    def test_employee_access_rights(self):
        self.meal_order_lunch.with_user(self.user_meal_manager).action_confirm()
        self.meal_order_lunch.with_user(self.user_meal_manager).action_approve()

        meal_order_line_employee_1 = self.meal_order_lunch.order_line_ids.filtered(lambda r: r.employee_id.id == self.employee_1.id)

        # Employees should be able to see their own meal orders
        meal_order_line_employee_1.with_user(self.user_1).read(['employee_id'])

        # Employees should not be able to see other's meal orders
        with self.assertRaises(AccessError):
            meal_order_line_employee_1.with_user(self.user_2).read(['employee_id'])

        # Employees should not be able to change meal orders
        with self.assertRaises(AccessError):
            meal_order_line_employee_1.with_user(self.user_1).write({'price': 0.0})
