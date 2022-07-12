from odoo.tests.common import SavepointCase


class TestRelativeCommon(SavepointCase):

    def setUp(self):
        super(TestRelativeCommon, self).setUp()
        self.father = self.env.ref('base.res_partner_address_1')
        self.mother = self.env.ref('base.res_partner_address_31')
        self.wife_a = self.env.ref('base.res_partner_address_32')

        self.employee_a = self.env.ref('hr.employee_admin')
        self.employee_b = self.env.ref('hr.employee_niv')

        self.relative_father_a = self.env['hr.employee.relative'].create({
            'employee_id': self.employee_a.id,
            'contact_id': self.father.id,
            'type': 'father'
            })
        self.relative_mother_a = self.env['hr.employee.relative'].create({
            'employee_id': self.employee_a.id,
            'contact_id': self.mother.id,
            'type': 'mother'
            })
        self.relative_wife_a = self.env['hr.employee.relative'].create({
            'employee_id': self.employee_a.id,
            'contact_id': self.wife_a.id,
            'type': 'wife'
            })
        self.relative_father_b = self.env['hr.employee.relative'].create({
            'employee_id': self.employee_b.id,
            'contact_id': self.father.id,
            'type': 'father'
            })
        self.relative_mother_b = self.env['hr.employee.relative'].create({
            'employee_id': self.employee_b.id,
            'contact_id': self.mother.id,
            'type': 'mother'
            })




