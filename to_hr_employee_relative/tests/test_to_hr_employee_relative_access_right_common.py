from odoo.tests.common import SavepointCase


class TestAccessRightCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRightCommon, cls).setUpClass()
        ResUsers = cls.env['res.users'].with_context({'no_reset_password': True})
        cls.internal_user = ResUsers.create({
            'name': 'Internal User',
            'login': 'internal_user',
            'email': 'internal_user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('base.group_user').id])]
        })
        cls.hr_user = ResUsers.create({
            'name': 'Hr User ',
            'login': 'hr_user',
            'email': 'hr_user@example.viindoo.com',
            'groups_id': [(6, 0, [cls.env.ref('hr.group_hr_user').id])]
        })

        cls.father = cls.env.ref('base.res_partner_address_1')
        cls.mother = cls.env.ref('base.res_partner_address_31')

        cls.employee_a = cls.env.ref('hr.employee_admin')
        cls.employee_b = cls.env.ref('hr.employee_niv')

        cls.relative_father_a = cls.env['hr.employee.relative'].create({
            'employee_id': cls.employee_a.id,
            'contact_id': cls.father.id,
            'type': 'father'
            })
        cls.relative_mother_a = cls.env['hr.employee.relative'].create({
            'employee_id': cls.employee_a.id,
            'contact_id': cls.mother.id,
            'type': 'mother'
            })

        cls.vals = {
            'employee_id': cls.employee_a.id,
            'contact_id': cls.mother.id,
            'type': 'mother'}
