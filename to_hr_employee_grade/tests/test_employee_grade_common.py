from odoo.tests.common import TransactionCase


class TestGradeCommon(TransactionCase):

    def setUp(self):
        super(TestGradeCommon, self).setUp()
        Grade = self.env['hr.employee.grade'].with_context(tracking_disable=True)
        self.expert = Grade.create({
            'name': 'Expert Test',
            'sequence': 100,
            })
        self.senior = Grade.create({
            'name': 'Senior Test',
            'sequence': 90,
            'parent_id': self.expert.id
            })
        self.junior = Grade.create({
            'name': 'Junior Test',
            'sequence': 80,
            'parent_id': self.senior.id
            })
        self.intern = Grade.create({
            'name': 'Intern Test',
            'sequence': 70,
            'parent_id': self.junior.id
            })
        self.admin_dept = self.env.ref('hr.dep_administration').with_context(tracking_disable=True)
        self.sales_dept = self.env.ref('hr.dep_sales').with_context(tracking_disable=True)
        self.companya = self.env.ref('base.main_company').with_context(tracking_disable=True)
        self.companyb = self.env['res.company'].with_context(tracking_disable=True).create({'name': 'company b'})
        self.employeea = self.env['hr.employee'].with_context(tracking_disable=True).create({'name':'employeea'})

    def reset_grade(self):
        (self.intern | self.junior | self.senior | self.expert).with_context(tracking_disable=True).write({
            'company_id': False,
            'department_id': False,
            'parent_id': False,
            })
