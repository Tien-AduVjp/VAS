from psycopg2 import IntegrityError

from odoo.exceptions import UserError
from odoo.tests import Form, tagged
from odoo.tools.misc import mute_logger
from .test_hr_meal_common import TestHrMealCommon


@tagged('post_install', '-at_install')
class TestToHrMeal(TestHrMealCommon):

    def setUp(self):
        super(TestToHrMeal, self).setUp()
        self.hr_meal_order_1 = self.create_meal_order(self.meal_type_lunch, 'internal', [self.employee_1, self.employee_2])
        self.department_1 = self.env['hr.department'].create({
            'name': 'department 1',
            'member_ids': [(6, 0, [self.employee_1.id, self.employee_2.id])]
        })

    def test_constraints_name_unique_hr_meal_type_alert(self):
        # case 1:
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.meal.type.alert'].create({
                'name': 'Lunch',
                'scheduled_hour': 0,
                'message': 'test'
            })

    def test_constraints_name_unique_hr_meal_type(self):
        # case 2:
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.meal.type'].create({
                'name': 'Lunch for Everyone',
                'alert_id': self.meal_type_alert_dinner.id,
            })

    def test_constraints_scheduled_hour_check_positive(self):
        # case 3:
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.meal.order'].create({
                'meal_type_id': self.meal_type_lunch.id,
                'scheduled_hour': -1
            })

    def test_constraints_scheduled_hour_check_less_than_24(self):
        # case 4:
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.meal.order'].create({
                'meal_type_id': self.meal_type_lunch.id,
                'scheduled_hour': 24
            })

    def test_01_compute_partners_count(self):
        # case 5:
        self.hr_meal_order_1.order_line_ids[0].partner_ids = self.env.ref('base.res_partner_1')
        self.hr_meal_order_1.order_line_ids[1].partner_ids = \
            self.env.ref('base.res_partner_2') + self.env.ref('base.res_partner_3')
        self.assertEqual(self.hr_meal_order_1.partners_count, 3)

    def test_02_compute_partners_count(self):
        # case 5.1
        self.hr_meal_order_1.order_line_ids[0].partner_ids = self.env.ref('base.res_partner_1')
        self.hr_meal_order_1.order_line_ids[1].partner_ids = \
            self.env.ref('base.res_partner_1') + self.env.ref('base.res_partner_2')
        self.assertEqual(self.hr_meal_order_1.partners_count, 2)

    def test_01_onchange_meal_type_id(self):
        # case 9:
        with Form(self.env['hr.meal.order']) as meal_order_form:
            meal_order_form.meal_type_id = self.meal_type_lunch
        with meal_order_form.order_line_ids.new() as line:
            line.employee_id = self.employee_1
        self.assertEqual(line.meal_type_id.id, self.meal_type_lunch.id)

    def test_02_onchange_meal_type_id(self):
        # case 10:
        with Form(self.env['hr.meal.order']) as meal_order_form:
            meal_order_form.meal_type_id = self.meal_type_lunch
        self.assertEqual(meal_order_form.scheduled_hour, self.meal_type_lunch.scheduled_hour)

    def test_count_order_lines(self):
        # case 11:
        self.assertEqual(self.hr_meal_order_1.order_lines_count, 2)

    def test_01_compute_total(self):
        # case 12:
        self.hr_meal_order_1.order_line_ids[0].partner_ids = self.env.ref('base.res_partner_1') + self.env.ref('base.res_partner_2')
        self.assertEqual(self.hr_meal_order_1.total_qty, 4)

    def test_02_compute_total(self):
        # case 13:
        self.hr_meal_order_1.order_line_ids[0].price = 50
        self.hr_meal_order_1.order_line_ids[1].price = 100
        self.assertEqual(self.hr_meal_order_1.total_price, 150)

    def test_onchange_department_id(self):
        # case 16:
        meal_order = Form(self.env['hr.meal.order'])
        meal_order.meal_type_id = self.meal_type_dinner
        meal_order.department_id = self.department_1
        meal_order = meal_order.save()

        self.assertTrue(meal_order.order_line_ids.employee_id == self.department_1.member_ids)

    def test_02_onchange_all(self):
        # case 18:
        meal_order = Form(self.env['hr.meal.order'])
        meal_order.meal_type_id = self.meal_type_dinner
        with meal_order.order_line_ids.new() as line:
            line.employee_id = self.employee_1
        meal_order.load_employee = 'clear_all'

        meal_order = meal_order.save()
        self.assertEqual(len(meal_order.order_line_ids), 0)

    def test_01_action_confirm(self):
        # case 19
        self.hr_meal_order_1.order_line_ids = False
        with self.assertRaises(UserError):
            self.hr_meal_order_1.action_confirm()

    def test_02_action_confirm(self):
        # case 20
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_confirm()
        self.assertEqual(self.hr_meal_order_1.ordered_by, self.user_meal_manager)

    def test_01_action_approve(self):
        # case 21
        partner1 = self.env.ref('base.res_partner_1')

        self.hr_meal_order_1.order_source = 'external'
        self.hr_meal_order_1.vendor_id = partner1
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_confirm()
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_approve()

        self.assertEqual(self.hr_meal_order_1.state, 'approved')
        self.assertEqual(self.hr_meal_order_1.approved_by, self.user_meal_manager)
        self.assertTrue(partner1.id in self.hr_meal_order_1.message_follower_ids.partner_id.ids)

    def test_02_action_approve(self):
        # case 22
        self.hr_meal_order_1.order_source = 'internal'
        self.hr_meal_order_1.kitchen_id = self.kitchen
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_confirm()
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_approve()

        self.assertEqual(self.hr_meal_order_1.state, 'approved')
        self.assertEqual(self.hr_meal_order_1.approved_by, self.user_meal_manager)
        self.assertTrue(self.user_meal_user_responsible.partner_id.id in self.hr_meal_order_1.message_follower_ids.partner_id.ids)

    def test_03_action_approve(self):
        # case 23:
        self.hr_meal_order_1.with_user(self.user_meal_user).action_confirm()
        with self.assertRaises(UserError):
            self.hr_meal_order_1.with_user(self.user_meal_user).action_approve()

    def test_03_action_confirm(self):
        # case 24:
        self.hr_meal_order_1.order_source = 'internal'
        self.hr_meal_order_1.kitchen_id = self.kitchen
        self.hr_meal_order_1.with_user(self.user_meal_user_responsible).action_confirm()

        self.assertEqual(self.hr_meal_order_1.state, 'approved')

    def test_04_action_confirm(self):
        # case 25:
        self.hr_meal_order_1.order_source = 'external'
        self.hr_meal_order_1.vendor_id = self.user_meal_user.partner_id
        self.hr_meal_order_1.with_user(self.user_meal_user).action_confirm()

        self.assertEqual(self.hr_meal_order_1.state, 'approved')

    def test_01_action_refuse(self):
        # case 26:
        self.hr_meal_order_1.action_confirm()
        with self.assertRaises(UserError):
            self.hr_meal_order_1.with_user(self.user_meal_user).action_refuse()

    def test_02_action_refuse(self):
        # case 27:
        self.hr_meal_order_1.action_confirm()
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_refuse()

        self.assertEqual(self.hr_meal_order_1.state, 'refused')

    def test_01_action_cancel(self):
        # case 28:
        self.hr_meal_order_1.with_user(self.user_meal_user).action_confirm()
        self.hr_meal_order_1.with_user(self.user_meal_user).action_cancel()
        self.assertEqual(self.hr_meal_order_1.state, 'cancelled')

    def test_02_action_cancel(self):
        # case 29:
        self.hr_meal_order_1.state = 'approved'
        with self.assertRaises(UserError):
            self.hr_meal_order_1.with_user(self.user_meal_user).action_cancel()

    def test_03_action_cancl(self):
        # case 30:
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_confirm()
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_approve()
        self.hr_meal_order_1.with_user(self.user_meal_manager).action_cancel()
        self.assertEqual(self.hr_meal_order_1.state, 'cancelled')

    def test_unlink(self):
        # case 31:
        self.hr_meal_order_1.action_confirm()
        with self.assertRaises(UserError):
            self.hr_meal_order_1.unlink()

    def test_unlink_2(self):
        # case 32:
        self.hr_meal_order_1.unlink()
        self.assertFalse(bool(self.hr_meal_order_1.exists()))

    def test_compute_total_price(self):
        # case 33:
        self.hr_meal_order_1.order_line_ids[0].write({
            'price': 20000,
            'quantity': 3
        })
        self.assertEqual(self.hr_meal_order_1.order_line_ids[0].total_price, 60000)

    def test_compute_price(self):
        # case 34:
        self.meal_type_lunch.price = 20000
        self.hr_meal_order_1.meal_type_id = self.meal_type_lunch
        self.assertEqual(self.hr_meal_order_1.order_line_ids[0].price, 20000)

    def test_compute_meal_type(self):
        # case 38:
        self.assertEqual(self.hr_meal_order_1.meal_type_id, self.hr_meal_order_1.order_line_ids[0].meal_type_id)

    def test_compute_department(self):
        # case 39:
        self.assertEqual(self.hr_meal_order_1.department_id, self.hr_meal_order_1.order_line_ids[0].department_id)

    def test_compute_partner(self):
        # case 40:
        self.hr_meal_order_1.order_line_ids[0].partner_ids = self.env.ref('base.res_partner_1') + self.env.ref('base.res_partner_2')
        self.assertEqual(self.hr_meal_order_1.order_line_ids[0].quantity, 3)
