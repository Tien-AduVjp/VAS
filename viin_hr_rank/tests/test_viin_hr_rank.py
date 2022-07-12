from psycopg2 import IntegrityError

from odoo.tests import Form, tagged
from odoo.tools.misc import mute_logger
from odoo.exceptions import UserError

from .common import Common

@tagged('post_install', '-at_install')
class TestViinHrRank(Common):

    def test_hr_rank_constrains_unique_create(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.env['hr.rank'].create({
                'role_id' : self.role_demo_1.id,
                'grade_id': self.grade_demo_1.id
                })

    def test_hr_rank_constrains_unique_write(self):
        self.rank_demo_unique = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id' : self.role_demo_1.id,
            'grade_id': self.grade_demo_2.id
        })
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.rank_demo_unique.write({
                'grade_id': self.grade_demo_1.id
                })

    def test_job_rank_line_constrains_unique(self):
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.job_rank_line_unique = self.env['hr.job.rank.line'].create({
                'job_id' : self.job_1.id,
                'role_id' : self.role_demo_1.id,
                'grade_id' : self.grade_demo_1.id,
                })
    def test_hr_rank_compute_name(self):
        rank_demo_1_name = "Role 1 | Level 1"
        self.assertEqual(self.rank_demo_1.name, rank_demo_1_name, "Error when compute name")

    def test_hr_rank_compute_parent_id(self):
        self.grade_demo_1.parent_id = self.grade_demo_2
        self.rank_demo_2 = self.env['hr.rank'].create({
            'role_id' : self.role_demo_1.id,
            'grade_id': self.grade_demo_2.id
            })
        rank_demo_1_parent_name = "Role 1 | Level 2"
        self.assertEqual(self.rank_demo_1.parent_id.name, rank_demo_1_parent_name,
                         "Error when compute parent id")

    def test_hr_rank_compute_employees_count(self):
        self.user_employee_rank.action_create_employee()
        self.user_employee_rank.employee_id.rank_id = self.rank_demo_1
        self.assertEqual(self.rank_demo_1.employees_count, 1)

    def test_hr_rank_constrains_check_department(self):
        # Role's department different than rank's department
        with self.assertRaises(UserError):
            self.rank_demo_1.write({
                'department_id' : self.department_2.id
                })
        # Grade's department different than rank's department
        self.grade_demo_1.write({
            'department_id' : self.department_1.id
            })
        with self.assertRaises(UserError):
            self.rank_demo_1.write({
                'department_id' : self.department_2.id
                })
        # Department's company different than rank's company
        self.company_demo_rank_1 = self.env['res.company'].create({'name': 'Company demo rank 1'})
        self.department_1.write({
            'company_id': self.company_demo_rank.id
            })
        with self.assertRaises(UserError):
            self.rank_demo_1.write({
                'company_id' : self.company_demo_rank_1.id
                })

    def test_hr_job_rank_line_compute_rank_id(self):
        """
        Adding Rank in Job Position but Rank not created
        Expect: When choose role_id and grade_id in rank_line_ids, Rank isn't generated; only when saving, Rank is generated 
        """
        role_demo = self.env['hr.role'].create({'name':'role_demo'})
        grade_demo = self.env['hr.employee.grade'].create({'name':'grade_demo'})
        rank_name = ("{role} | {grade}").format(role=role_demo.name, grade=grade_demo.name)
        with Form(self.env['hr.job']) as hr_job_form:
            hr_job_form.name = "Job demo"
            with hr_job_form.rank_line_ids.new() as line:
                line.role_id = role_demo
                line.grade_id = grade_demo
                self.assertEqual(line.rank_id.name,False)
            hr_job_demo = hr_job_form.save()
            self.assertEqual(hr_job_demo.rank_line_ids[0].rank_id.name, rank_name)

    def test_hr_job_constrains_rank_ids(self):
        self.rank_demo = self.env['hr.rank'].with_context(tracking_disable=True).create({
            'role_id' : self.role_demo_1.id,
            'grade_id': self.grade_demo_2.id
            })
        rank_ids_demo = self.rank_demo | self.rank_demo_1
        with self.assertRaises(UserError):
            self.job_1.write({
                'rank_ids' : [(6, 0, rank_ids_demo.ids)]
                })
