from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import Common


@tagged('post_install','-at_install', 'access_rights')
class TestAccessRight(Common):

    def test_access_rights_1(self):
        """
        Case 1: User is Skill Officer, having full CRUD rights with model
         - hr.rank
         - hr.role
         - hr.job.rank.line
         - hr.skill
         - hr.skill.type
         - hr.skill.level
         - hr.rank.skill.description
         - hr.skill.description
        """
        #role
        self.role_demo_1 = self.env['hr.role'].with_user(self.skill_officer).with_context(tracking_disable=True).create({
            'name': 'Role demo 1'
            })
        self.role_demo_1.with_user(self.skill_officer).read()
        self.role_demo_1.with_user(self.skill_officer).write({
            'name': 'Role demo 1 edited',
            })
        self.role_demo_1.with_user(self.skill_officer).unlink()
        #rank
        self.rank_demo_1 = self.env['hr.rank'].with_user(self.skill_officer).with_context(tracking_disable=True).create({
            'role_id' : self.role_demo.id,
            'grade_id': self.grade_demo_2.id
            })
        self.rank_demo_1.with_user(self.skill_officer).read()
        self.rank_demo_1.with_user(self.skill_officer).write({
            'grade_id': self.grade_demo.id,
            })
        self.rank_demo_1.with_user(self.skill_officer).unlink()
        #job rank line
        self.rank_demo = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id' : self.role_demo.id,
            'grade_id': self.grade_demo.id,
            })
        self.job_rank_line_demo = self.env['hr.job.rank.line'].with_user(self.skill_officer).with_context(tracking_disable=True).create({
            'job_id' : self.job_1.id,
            'role_id' : self.role_demo.id,
            'grade_id' : self.grade_demo.id
            })         
        self.job_rank_line_demo.with_user(self.skill_officer).read()
        self.job_rank_line_demo.with_user(self.skill_officer).write({
            'job_id' : self.job_2.id,
            })
        self.job_rank_line_demo.with_user(self.skill_officer).unlink()
        #skill
        self.skill_2 = self.env['hr.skill'].with_user(self.skill_officer).with_context(tracking_disable=True).create({
            'name' : 'skill 2'
            })
        self.skill_2.with_user(self.skill_officer).read()
        self.skill_2.with_user(self.skill_officer).write({
            'name' : 'skill 2 edited'
            })
        self.skill_2.with_user(self.skill_officer).unlink()
        #skill level
        self.level_A = self.env['hr.skill.level'].with_user(self.skill_officer).with_context(tracking_disable=True).create({
            'name' : 'Level A',
            'level_progress' : 10
            })
        self.level_A.with_user(self.skill_officer).read()
        self.level_A.with_user(self.skill_officer).write({
            'name' : 'Level A edited'
            })
        self.level_A.with_user(self.skill_officer).unlink()
        #skill type
        self.type_a = self.env['hr.skill.type'].with_user(self.skill_officer).with_context(tracking_disable=True).create({
            'name' : 'Type A',
            })
        self.type_a.with_user(self.skill_officer).read()
        self.type_a.with_user(self.skill_officer).write({
            'name' : 'Type A edited'
            })
        self.type_a.with_user(self.skill_officer).unlink()
        #skill description
        self.skill_description_demo = self.env['hr.skill.description'].with_user(self.skill_officer).with_context(tracking_disable=True).create({
            'skill_type_id' : self.skill_type_1.id,
            'skill_id': self.skill_1.id,
            'skill_level_id': self.level_beginner.id
            })
        self.skill_description_demo.with_user(self.skill_officer).read()
        self.skill_description_demo.with_user(self.skill_officer).write({
            'skill_type_id' : self.skill_type_2.id,
            })
        self.skill_description_demo.with_user(self.skill_officer).unlink()
        #rank skill description
        self.rank_skill_description_demo = self.env['hr.rank.skill.description'].with_user(self.skill_officer).with_context(tracking_disable=True).create({
            'rank_id' : self.rank_demo.id,
            'skill_type_id' : self.skill_type_1.id,
            'skill_id': self.skill_1.id,
            'skill_level_id': self.level_beginner.id
            })
        self.rank_skill_description_demo.with_user(self.skill_officer).read()
        self.rank_skill_description_demo.with_user(self.skill_officer).write({
            'skill_type_id' : self.skill_type_2.id,
            })
        self.rank_skill_description_demo.with_user(self.skill_officer).unlink()
        
    def test_access_right_2(self):
        """
        Case 2: User is Employee only read rights to model
         - hr.rank.skill.description
         - hr.skill.description
         - hr.skill.report
        """

        #skill description
        self.skill_description.with_user(self.employee_hr_skill).read()
        with self.assertRaises(AccessError):
            self.skill_description.with_user(self.employee_hr_skill).write({
                'skill_type_id' : self.skill_type_2.id,
                })
        with self.assertRaises(AccessError):
            self.skill_description.with_user(self.employee_hr_skill).unlink()
        with self.assertRaises(AccessError):
            self.skill_description_1 = self.env['hr.skill.description'].with_user(self.employee_hr_skill).with_context(tracking_disable=True).create({
            'skill_type_id' : self.skill_type_2.id,
            'skill_id': self.skill_2.id,
            'skill_level_id': self.level_intermediate.id
            })

        #skill description
        self.rank_skill_description.with_user(self.employee_hr_skill).read()
        with self.assertRaises(AccessError):
            self.rank_skill_description.with_user(self.employee_hr_skill).write({
                'skill_type_id' : self.skill_type_2.id,
                })
        with self.assertRaises(AccessError):
            self.rank_skill_description.with_user(self.employee_hr_skill).unlink()
        with self.assertRaises(AccessError):
            self.rank_skill_description_1 = self.env['hr.rank.skill.description'].with_user(self.employee_hr_skill).with_context(tracking_disable=True).create({
                'rank_id' : self.rank_common.id,
                'skill_type_id' : self.skill_type_2.id,
                'skill_id': self.skill_2.id,
                'skill_level_id': self.level_intermediate.id
                })

        #report
        """
        User only see their own personal report 
        """
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.employee_hr_skill).search([])
        if self.report_demo:
            with self.assertRaises(AccessError):
                self.report_demo.with_user(self.employee_hr_skill).unlink()
            with self.assertRaises(AccessError):
                self.report_demo.with_user(self.employee_hr_skill).write({
                    'reach_progress' : 50
                    })
        
    def test_access_right_3(self):
        """
        Case 3: User is Hr Officer, having full CRUD rights with model
         - hr.rank.skill.description
         - hr.skill.description
        """
        #skill description
        self.skill_description_demo = self.env['hr.skill.description'].with_user(self.hr_officer).with_context(tracking_disable=True).create({
            'skill_type_id' : self.skill_type_1.id,
            'skill_id': self.skill_1.id,
            'skill_level_id': self.level_beginner.id
            })
        self.skill_description_demo.with_user(self.hr_officer).read()
        self.skill_description_demo.with_user(self.hr_officer).write({
            'skill_type_id' : self.skill_type_2.id,
            })
        self.skill_description_demo.with_user(self.hr_officer).unlink()
        #rank skill description
        self.rank_demo = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id' : self.role_demo.id,
            'grade_id': self.grade_demo.id,
            })
        self.rank_skill_description_demo = self.env['hr.rank.skill.description'].with_user(self.hr_officer).with_context(tracking_disable=True).create({
            'rank_id' : self.rank_demo.id,
            'skill_type_id' : self.skill_type_1.id,
            'skill_id': self.skill_1.id,
            'skill_level_id': self.level_beginner.id
            })
        self.rank_skill_description_demo.with_user(self.hr_officer).read()
        self.rank_skill_description_demo.with_user(self.hr_officer).write({
            'skill_type_id' : self.skill_type_2.id,
            })
        self.rank_skill_description_demo.with_user(self.hr_officer).unlink()
    
    def test_access_right_4(self):
        """
        User Skill Officer able to see report from subordinates
        """
        self.report_demo = self.env['hr.employee.skill.report'].with_user(self.skill_officer).search([])
        if self.report_demo:
            with self.assertRaises(AccessError):
                self.report_demo.with_user(self.skill_officer).unlink()
            with self.assertRaises(AccessError):
                self.report_demo.with_user(self.skill_officer).write({
                    'reach_progress' : 50
                    })
