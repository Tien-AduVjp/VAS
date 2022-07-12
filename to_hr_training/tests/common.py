from odoo.tests.common import SavepointCase


class Common(SavepointCase):
    def setUp(self):
        super(Common, self).setUp()

        #department
        self.department_1 = self.env['hr.department'].create({'name' : 'Department 1'})

        #role
        self.role_demo = self.env['hr.role'].with_context(tracking_disable=True).create({
            'name': 'Role demo',
            'department_id' : self.department_1.id
            })

        #grade

        self.grade_2 = self.env['hr.employee.grade'].with_context(tracking_disable=True).create({
            'name': 'Level 2'
            })
        self.grade_1 = self.env['hr.employee.grade'].with_context(tracking_disable=True).create({
            'name': 'Level 1',
            'parent_id': self.grade_2.id
            })
        #rank

        self.rank_2 = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id' : self.role_demo.id,
            'grade_id' : self.grade_2.id
            })
        self.rank_1 = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id' : self.role_demo.id,
            'grade_id' : self.grade_1.id,
            })

        #skill type
        self.skill_type_1 = self.env['hr.skill.type'].with_context(tracking_disable=True).create({
            'name' : 'skill_type_1'
            })

        #skill
        self.skill_1 = self.env['hr.skill'].with_context(tracking_disable=True).create({
            'name' : 'skill_1',
            'skill_type_id' : self.skill_type_1.id
            })

        #skill level
        self.level_1 = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Level 1',
            'level_progress' : 25,
            'skill_type_id' : self.skill_type_1.id
            })
        self.level_2 = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Level 2',
            'level_progress' : 50,
            'skill_type_id' : self.skill_type_1.id
            })

        #rank skill description
        self.rank_skill_description_1 = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).create({
            'rank_id' : self.rank_1.id,
            'skill_type_id' : self.skill_type_1.id,
            'skill_id': self.skill_1.id,
            'skill_level_id': self.level_1.id,
            'expectation' : 'required'
            })
        self.rank_skill_description_2 = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).create({
            'rank_id' : self.rank_2.id,
            'skill_type_id' : self.skill_type_1.id,
            'skill_id': self.skill_1.id,
            'skill_level_id': self.level_2.id,
            'expectation' : 'required'
            })
        #course
        self.course_1 = self.env['slide.channel'].with_context(tracking_disable=True).create({
            'name': 'Course 1'
            })

        self.course_2 = self.env['slide.channel'].with_context(tracking_disable=True).create({
            'name': 'Course 2'
            })
        # hr.skill.description
        self.rank_1.consolidated_rank_skill_description_ids.skill_description_id.slide_channel_ids = [(6, 0, self.course_1.ids)]
        self.rank_2.consolidated_rank_skill_description_ids.skill_description_id.slide_channel_ids = [(6, 0, self.course_2.ids)]
        #user
        self.employee = self.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Employee',
                'login': 'employee',
                'email': 'employee@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        self.officer_elearning = self.env['res.users'].with_context({
            'no_reset_password': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'officer elearning',
                'login': 'officer1',
                'email': 'officer1@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('website_slides.group_website_slides_officer').id])],
        })

        #Employee
        self.employee.action_create_employee()
        self.employee.employee_id.write({
            'role_id': self.role_demo.id,
            'grade_id': self.grade_1.id,
            'rank_id': self.rank_1.id,
            'next_rank_id': self.rank_2.id,
            })
