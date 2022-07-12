from odoo.tests import Form
from odoo.tests.common import SavepointCase, tagged


@tagged('post_install', '-at_install')
class TestHrMealCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestHrMealCommon, cls).setUpClass()

        user_group_employee = cls.env.ref('base.group_user')
        user_group_hr_meal_user = cls.env.ref('to_hr_meal.hr_meal_group_user')
        user_group_hr_meal_manager = cls.env.ref('to_hr_meal.hr_meal_group_manager')

        # Test users
        Users = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.user_meal_user = Users.create({
            'name': 'Sarah MealUser',
            'login': 'sarah_mealuser',
            'email': 'sarah.mealuser@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_hr_meal_user.id])]
        })

        cls.user_meal_user_responsible = Users.create({
            'name': 'Peter MealUser',
            'login': 'Peter_mealuser',
            'email': 'peter.mealuser@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_hr_meal_user.id])]
        })

        cls.user_meal_manager = Users.create({
            'name': 'Gordon MealManager',
            'login': 'gordon_mealmanager',
            'email': 'gordon.mealmanager@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id, user_group_hr_meal_manager.id])]
        })

        cls.user_1 = Users.create({
            'name': 'May Employee',
            'login': 'may_employee',
            'email': 'may.employee@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id])],
        })

        cls.user_2 = Users.create({
            'name': 'Milia Employeee',
            'login': 'milia_employee',
            'email': 'milia.employee@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id])],
        })

        cls.user_3 = Users.create({
            'name': 'Maria Employeee',
            'login': 'maria_employee',
            'email': 'maria.employee@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id])],
        })

        cls.user_4 = Users.create({
            'name': 'David Employeee',
            'login': 'david_employee',
            'email': 'david.employee@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id])],
        })

        cls.user_5 = Users.create({
            'name': 'Larry Employeee',
            'login': 'larry_employee',
            'email': 'larry.employee@example.viindoo.com',
            'groups_id': [(6, 0, [user_group_employee.id])],
        })

        # Test employees
        Employee = cls.env['hr.employee'].with_context(tracking_disable=True)
        cls.employee_1 = Employee.create({
            'name': 'John Employee',
            'work_email': 'John.employee@example.viindoo.com',
            'user_id': cls.user_1.id
        })

        cls.employee_2 = Employee.create({
            'name': 'Milia Employee',
            'work_email': 'milia.employee@example.viindoo.com',
            'user_id': cls.user_2.id
        })

        cls.employee_3 = Employee.create({
            'name': 'Maria Employee',
            'work_email': 'maria.employee@example.viindoo.com',
            'user_id': cls.user_3.id
        })

        cls.employee_4 = Employee.create({
            'name': 'David Employee',
            'work_email': 'david.employee@example.viindoo.com',
            'user_id': cls.user_4.id
        })

        cls.employee_5 = Employee.create({
            'name': 'Larry Employee',
            'work_email': 'larry.employee@example.viindoo.com',
            'user_id': cls.user_5.id
        })

        # Test kitchens
        cls.kitchen = cls.env['hr.kitchen'].with_user(cls.user_meal_manager).create({
            'name': 'Awesome Kitchen',
            'responsible_id': cls.user_meal_user_responsible.partner_id.id
        })

        # Test meal type alerts
        cls.meal_type_alert_lunch = cls.env['hr.meal.type.alert'].with_user(cls.user_meal_manager).create({
            'name': 'Lunch Meal Alert',
            'scheduled_hour': 12.0,
            'message': 'Meal will be delivered at 12:00 PM'
        })

        cls.meal_type_alert_dinner = cls.env['hr.meal.type.alert'].with_user(cls.user_meal_manager).create({
            'name': 'Dinner Meal Alert',
            'scheduled_hour': 19.0,
            'message': 'Meal will be delivered at 7:00 PM'
        })

        # Test meal type
        cls.meal_type_lunch = cls.env['hr.meal.type'].with_user(cls.user_meal_manager).create({
            'name': 'Lunch Meal',
            'alert_id': cls.meal_type_alert_lunch.id,
            'price': 10.0,
            'description': 'This is a lunch meal'
        })

        cls.meal_type_dinner = cls.env['hr.meal.type'].with_user(cls.user_meal_manager).create({
            'name': 'Dinner Meal',
            'alert_id': cls.meal_type_alert_dinner.id,
            'price': 10.0,
            'description': 'This is a dinner meal'
        })

    def create_meal_order(self, meal_type, order_source, employees):
        MealOrder = self.env['hr.meal.order'].with_user(self.user_meal_manager).with_context({'mail_create_nolog': True})
        meal_order_form = Form(MealOrder)

        if order_source == 'external':
            meal_order_form.vendor_id = self.user_meal_user_responsible.partner_id
        elif order_source == 'internal':
            meal_order_form.kitchen_id = self.kitchen

        for employee in employees:
            with meal_order_form.order_line_ids.new() as line:
                line.employee_id = employee

        meal_order_form.meal_type_id = meal_type # The mechanism of 'Form' on odoo 14 is slightly changed, causing an error if set value of type first
        meal_order = meal_order_form.save()
        return meal_order
