from odoo.tests.common import SavepointCase


class TestTrainingCommon(SavepointCase):

    def setUp(self):
        super(TestTrainingCommon, self).setUp()
        self.garden_basic = self.env.ref('website_slides.slide_channel_demo_0_gard_0')
        self.garden_advance = self.env.ref('website_slides.slide_channel_demo_1_gard1')
        self.tree_basic = self.env.ref('website_slides.slide_channel_demo_2_gard2')
        
        HrRequireTraining = self.env['hr.require.training'].with_context(tracking_disable=True)
        self.garden_course1 = HrRequireTraining.create({
            'slide_channel_id': self.garden_basic.id,
            'require_hour': 5
            })
        self.garden_course2 = HrRequireTraining.create({
            'slide_channel_id': self.garden_basic.id,
            'require_hour':3
            })
        self.garden_course3 = HrRequireTraining.create({
            'slide_channel_id': self.garden_basic.id,
            'require_hour':1
            })

        self.tree_course1 = HrRequireTraining.create({
            'slide_channel_id': self.tree_basic.id,
            'require_hour': 5
            })
        self.tree_course2 = HrRequireTraining.create({
            'slide_channel_id': self.tree_basic.id,
            'require_hour': 3
            })
        self.tree_course3 = HrRequireTraining.create({
            'slide_channel_id': self.tree_basic.id,
            'require_hour': 1
            })
        Grade = self.env['hr.employee.grade'].with_context(tracking_disable=True)
        self.junior = Grade.create({
            'name': 'Junior Test',
            'sequence': 80,
            })
        self.intern = Grade.create({
            'name': 'Intern Test',
            'sequence': 70,
            'parent_id': self.junior.id
            })
        
        self.admin_dept = self.env.ref('hr.dep_administration')
        self.sales_dept = self.env.ref('hr.dep_sales')
        self.job_position = self.env.ref('hr.job_ceo')
        self.employeea = self.env.ref('hr.employee_admin')
