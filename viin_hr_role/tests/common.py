from odoo.tests.common import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()
        #department
        self.department_1 = self.env['hr.department'].with_context(tracking_disable=True).create({
            'name': 'Department demo'
            })
        #company
        self.company_demo = self.env['res.company'].create({
            'name': 'Company demo'
            })
        #role
        self.role_1 = self.env['hr.role'].with_context(tracking_disable=True).create({
            'name': 'Role 1'
            })
        #employee
        self.employee_1 = self.env['hr.employee'].with_context(tracking_disable=True).create({
            'name': 'Employee demo'
            })
        #user
        self.user_employee = self.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Employee user',
                'login': 'user_employee',
                'email': 'user@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        self.user_hr_officer = self.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'HR Officer user',
                'login': 'user_hr_officer',
                'email': 'userhr@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('hr.group_hr_user').id])],
        })

        self.user_multicomp = self.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'multi company user',
                'login': 'user_multi',
                'email': 'usermulti@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('hr.group_hr_user').id])],
                'company_id' : self.company_demo.id,
                'company_ids' : [(6, 0, self.env.user.company_ids.ids)],
            })
