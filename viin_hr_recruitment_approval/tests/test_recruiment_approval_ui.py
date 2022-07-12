try:
    # try to use CheckViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    CheckViolation = errors.CheckViolation
except Exception:
    import psycopg2
    CheckViolation = psycopg2.IntegrityError

from odoo.tests import tagged, Form
from odoo.tools.misc import mute_logger
from odoo.exceptions import ValidationError

from .common import Common


@tagged('post_install', '-at_install')
class TestRecruitmentRequest(Common):

    def test_onchange_and_default_value_form_request(self):
        with Form(self.env['approval.request'].with_user(self.base_user)) as f:
            f.title = 'test onchange'
            f.approval_type_id = self.approval_recruitment_type
            f.job_id = self.hr_job
            self.assertEqual(f.department_id, self.base_user.employee_id.department_id)
            self.assertEqual(f.description_job, self.hr_job.description)
            self.assertEqual(f.requirements, self.hr_job.requirements)

    def test_percent_widgetbar(self):
        recruitment_req = self.create_validated_recruitment_request(job=self.hr_job, exp_count=3, user_create=self.base_user)
        applicant = self.create_applicant_apply_job(recruitment_req.job_id)
        self.action_recruit_applicant(applicant)

        self.assertEqual(recruitment_req.recruited_employees, 100/3)

    def test_constraint_expect_employees_positive(self):
        with self.assertRaises(CheckViolation), mute_logger('odoo.sql_db'):
            self.create_recruitment_request(job=self.hr_job, exp_count=0, user_create=self.base_user)

    def test_compute_applicant_and_recruited_field_on_recruitment_request(self):
        recruitment_req = self.create_validated_recruitment_request(job=self.hr_job, user_create=self.base_user)

        # Create 2 applicant apply to job
        applicant1 = self.create_applicant_apply_job(recruitment_req.job_id)
        applicant2 = self.create_applicant_apply_job(recruitment_req.job_id)

        self.assertEqual(recruitment_req.applicant_ids, applicant1 | applicant2)
        self.assertFalse(recruitment_req.employee_ids)

        # Recruit 2 applicant
        self.action_recruit_applicant(applicant1)
        self.action_recruit_applicant(applicant2)

        self.assertEqual(recruitment_req.employee_ids, applicant1.emp_id | applicant2.emp_id)

    def test_constraint_duplicate_recruitment_request(self):
        self.create_recruitment_request(job=self.hr_job, user_create=self.base_user)
        with self.assertRaises(ValidationError):
            self.create_recruitment_request(job=self.hr_job, user_create=self.base_user)
