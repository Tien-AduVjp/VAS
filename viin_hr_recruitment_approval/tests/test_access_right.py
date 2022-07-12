from datetime import datetime

from odoo.exceptions import AccessError
from odoo.tests import tagged, SavepointCase

from .common import Common

@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRight(Common):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRight, cls).setUpClass()

    def test_base_user_access_hr_job(self):
        # HrJob(1,0,0,0)
        hr_job = self.hr_job.with_user(self.base_user)
        self.base_user.employee_id.department_id = False
        hr_job.read()
        self.assertRaises(AccessError, hr_job.write, {'name': 'new name'})
        self.assertRaises(AccessError, hr_job.create, {'name': 'job2'})
        self.assertRaises(AccessError, hr_job.unlink)

    def test_user_approval_access_hr_job(self):
        # HrJob(1,1.1.1)
        hr_job = self.hr_job.with_user(self.approval_officer_user)
        hr_job.read()
        hr_job.write({'name': 'new name'})
        hr_job.create({'name': 'job2'})
        hr_job.unlink()

    def test_base_user_access_hr_applicant(self):
        # HrApplicant not relate user(0,0,0,0)
        applicant = self.create_applicant_apply_job(self.hr_job).with_user(self.base_user)
        self.assertRaises(AccessError, applicant.read)
        self.assertRaises(AccessError, applicant.write, {'name': 'Tom'})
        self.assertRaises(AccessError, applicant.create, {'name': 'Jerry', 'job_id': self.hr_job.id})
        self.assertRaises(AccessError, applicant.unlink)

        # HrApplicant relate user(1,0,0,0)
        self.create_validated_recruitment_request(self.hr_job, user_create=self.base_user)
        applicant = self.create_applicant_apply_job(self.hr_job).with_user(self.base_user)
        applicant.read()
        self.assertRaises(AccessError, applicant.write, {'name': 'Tom'})
        self.assertRaises(AccessError, applicant.create, {'name': 'Jerry', 'job_id': self.hr_job.id})
        self.assertRaises(AccessError, applicant.unlink)

    def test_user_approval_access_hr_applicant(self):
        # Applicant
        # Case 3: Applicant apply to job which user not relate(1,1,1,1)
        applicant = self.env['hr.applicant'].with_context(tracking_disable=True).create({
            'name': 'H',
            'job_id': self.hr_job.id
            }).with_user(self.approval_officer_user)
        applicant.read()
        applicant.write({'name': 'Tom'})
        applicant.create({'name': 'Jerry', 'job_id': self.hr_job.id})
        applicant.unlink()
