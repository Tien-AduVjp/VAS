from odoo.exceptions import AccessError
from odoo.tests import tagged

from .common import Common


@tagged('post_install','-at_install', 'access_rights')
class TestAccessRight(Common):

    def test_access_rights_1(self):
        """
        Case 1: User is HR Officer, having full CRUD rights with ranks and job rank lines
        """
        #CRUD ranks
        self.rank_demo = self.env['hr.rank'].with_user(self.user_hr_officer_rank).with_context(tracking_disable=True).create({
            'role_id' : self.role_demo_1.id,
            'grade_id': self.grade_demo_2.id
            })
        self.rank_demo.with_user(self.user_hr_officer_rank).read()
        self.rank_demo.with_user(self.user_hr_officer_rank).write({
            'role_id': self.role_demo_2.id,
            })
        self.rank_demo.with_user(self.user_hr_officer_rank).unlink()
        #CRUD job_rank_lines
        self.job_rank_line_demo = self.env['hr.job.rank.line'].with_user(self.user_hr_officer_rank).with_context(tracking_disable=True).create({
            'job_id' : self.job_2.id,
            'role_id' : self.role_demo_1.id,
            'grade_id' : self.grade_demo_1.id,
            })
        self.job_rank_line_demo.with_user(self.user_hr_officer_rank).read()
        self.job_rank_line_demo.with_user(self.user_hr_officer_rank).write({
            'role_id' : self.role_demo_2.id,
            })
        self.job_rank_line_demo.with_user(self.user_hr_officer_rank).unlink()
    def test_access_rights_2(self):
        """
        Case 2: User is internal user, only able to read rank and job rank lines
        """
        #ranks
        self.rank_demo_1.with_user(self.user_employee_rank).read()
        with self.assertRaises(AccessError):
            self.rank_demo_1.with_user(self.user_employee_rank).write({
                'role_id': self.role_demo_2.id,
                })
        with self.assertRaises(AccessError):
            self.rank_test = self.env['hr.role'].with_user(self.user_employee_rank).with_context(tracking_disable=True).create({
                'role_id': self.role_demo_2.id,
                'grade_id': self.grade_demo_1.id
                })
        with self.assertRaises(AccessError):
            self.rank_demo_1.with_user(self.user_employee_rank).unlink()

        #job_rank_lines
        self.job_rank_line_1.with_user(self.user_employee_rank).read()
        with self.assertRaises(AccessError):
            self.job_rank_line_1.with_user(self.user_employee_rank).write({
                'role_id': self.role_demo_2.id,
                })
        with self.assertRaises(AccessError):
            self.job_rank_line_test = self.env['hr.job.rank.line'].with_user(self.user_employee_rank).with_context(tracking_disable=True).create({
                'job_id' : self.job_1.id,
                'role_id' : self.role_demo_1.id,
                'grade_id' : self.grade_demo_2.id,
                })
        with self.assertRaises(AccessError):
            self.job_rank_line_1.with_user(self.user_employee_rank).unlink()
    def test_access_rights_3(self):
        """
        Case 3: User belongs to group 'hr.group_hr_user' but different company
        Expect: User able to read ranks and job_rank_line in company that user participant
        """
        #ranks and job_rank_lines
        self.rank_demo_2 = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id': self.role_demo_2.id,
            'grade_id': self.grade_demo_1.id,
            'company_id': self.company_demo_rank.id,
            })
        self.job_rank_line_2 = self.env['hr.job.rank.line'].with_context(tracking_disable=True).create({
            'job_id' : self.job_2.id,
            'role_id' : self.role_demo_2.id,
            'grade_id' : self.grade_demo_1.id,
            })
        #test record rule
        self.rank_demo_2.with_user(self.user_multicomp_rank).read()
        self.job_rank_line_2.with_user(self.user_multicomp_rank).read()
        with self.assertRaises(AccessError):
            self.rank_demo_1.with_user(self.user_multicomp_rank).read()
            self.job_rank_line_1.with_user(self.user_multicomp_rank).read()
        with self.assertRaises(AccessError):
            self.rank_demo_2.with_user(self.user_hr_officer_rank).read()
            self.job_rank_line_2.with_user(self.user_hr_officer_rank).read()
