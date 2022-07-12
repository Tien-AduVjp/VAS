from odoo.tests.common import SavepointCase


class Common(SavepointCase):
    def setUp(self):
        super(Common, self).setUp()
        #company
        self.company_demo = self.env['res.company'].create({'name': 'Company demo'})

        #department
        self.department_1 = self.env['hr.department'].create({'name' : 'Department 1'})

        # #role
        self.role_demo = self.env['hr.role'].with_context(tracking_disable=True).create({
            'name': 'Role demo',
            'department_id' : self.department_1.id
            })
        self.role_demo_2 = self.env['hr.role'].with_context(tracking_disable=True).create({
            'name': 'Role demo 2',
            })

        #grade
        self.grade_demo = self.env['hr.employee.grade'].with_context(tracking_disable=True).create({
            'name': 'Level demo'
            })
        self.grade_demo_2 = self.env['hr.employee.grade'].with_context(tracking_disable=True).create({
            'name': 'Level demo 2'
            })

        #rank
        self.rank_common = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id' : self.role_demo_2.id,
            'grade_id' : self.grade_demo_2.id
            })

        #job rank line
        self.job_1 = self.env['hr.job'].with_context(tracking_disable=True).create({
            'name' : 'Job 1'
            })
        self.job_2 = self.env['hr.job'].with_context(tracking_disable=True).create({
            'name' : 'Job 2'
            })

        #skill type
        self.skill_type_1 = self.env['hr.skill.type'].with_context(tracking_disable=True).create({
            'name' : 'skill_type_1'
            })
        self.skill_type_2 = self.env['hr.skill.type'].with_context(tracking_disable=True).create({
            'name' : 'skill_type_2'
            })

        #skill
        self.skill_1 = self.env['hr.skill'].with_context(tracking_disable=True).create({
            'name' : 'skill_1',
            'skill_type_id' : self.skill_type_1.id
            })
        self.skill_2 = self.env['hr.skill'].with_context(tracking_disable=True).create({
            'name' : 'skill_2'
            })

        #skill level
        self.level_beginner = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Beginner',
            'level_progress' : 25,
            })
        self.level_intermediate = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Intermediate',
            'level_progress' : 50,
            'skill_type_id' : self.skill_type_1.id
            })
        self.level_expert = self.env['hr.skill.level'].with_context(tracking_disable=True).create({
            'name' : 'Expert',
            'level_progress' : 100
            })

        #skill description
        self.skill_description = self.env['hr.skill.description'].with_context(tracking_disable=True).create({
            'skill_type_id' : self.skill_type_1.id,
            'skill_id': self.skill_2.id,
            'skill_level_id': self.level_intermediate.id
            })

        #rank skill description
        self.rank_skill_description = self.env['hr.rank.skill.description'].with_context(tracking_disable=True).create({
            'rank_id' : self.rank_common.id,
            'skill_type_id' : self.skill_type_1.id,
            'skill_id': self.skill_2.id,
            'skill_level_id': self.level_intermediate.id,
            'expectation' : 'required'
            })

        #user
        self.employee_hr_skill = self.env['res.users'].with_context({
            'no_reset_password': True,                                                 
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Employee Hr Skill',
                'login': 'employee_hr_skill',
                'email': 'employee_hr_skill@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })

        self.hr_officer = self.env['res.users'].with_context({
            'no_reset_password': True,                                                 
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'HR Officer',
                'login': 'hr_officer',
                'email': 'hr_officer@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('hr.group_hr_user').id])],
        })

        self.skill_officer = self.env['res.users'].with_context({
            'no_reset_password': True,                                                 
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Skill Officer',
                'login': 'skill_officer',
                'email': 'skill_officer@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('viin_hr_skill_framework.group_skill_officer').id])],
        })

        self.skill_officer_admin = self.env['res.users'].with_context({
            'no_reset_password': True,                                                 
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True}).create({
                'name': 'Skill Officer Admin',
                'login': 'skill_officer_admin',
                'email': 'skill_officer_admin@example.viindoo.com',
                'groups_id': [(6, 0, [self.env.ref('viin_hr_skill_framework.group_skill_admin').id])],
        })
            
        #Employee
        self.employee_hr_skill.action_create_employee()
        self.employee_hr_skill.employee_id.role_id = self.role_demo_2
        self.employee_hr_skill.employee_id.grade_id = self.grade_demo_2
        self.employee_hr_skill.employee_id.department_id = self.department_1
        
        #Manager department
        self.skill_officer.action_create_employee()
        self.skill_officer.employee_id.department_id = self.department_1
        self.skill_officer.employee_id.department_id.manager_id = self.skill_officer.employee_id
