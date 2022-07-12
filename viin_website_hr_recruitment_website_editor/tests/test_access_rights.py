from odoo.tests import tagged, SavepointCase
from odoo.exceptions import AccessError


@tagged('post_install', '-at_install', 'access_rights')
class TestAccessRights(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccessRights, cls).setUpClass()
        cls.user_demo = cls.env.ref('base.user_demo')
        cls.user_demo.groups_id = [(6, 0, [cls.env.ref('website.group_website_designer').id])]
        cls.job = cls.env.ref('hr.job_developer')
        cls.website_1 = cls.env['website'].browse(1)

    def test_designer_edit_job_website_description_01(self):
        """
            Input: - job A in website 1, has no company, website 1 using
                    "Allow Website Editors to edit HR Job Recruitment Page Base on Specific Website"
            Output: allow to write website_description on job A
        """
        self.website_1.allow_edit_website_jobs_website_setting = True
        self.job.website_id = self.website_1.id
        self.job.with_user(self.user_demo).website_description = '<p>Test</p>'

    def test_designer_edit_job_website_description_02(self):
        """
            Input: - job A in company 1, has no website, company using
                    "Allow Website Editors to edit HR Job Recruitment Page Base On Company Setting"
            Output: allow to write website_description on job A
        """
        self.env.company.allow_edit_website_jobs_company_setting = True
        self.job.with_user(self.user_demo).write({
            'website_description': '<p>Test</p>'
        })

    def test_designer_edit_job_website_description_03(self):
        """
            Input: - job A has no website and company
                   - Using both "Allow Website Editors to edit HR Job Recruitment Page Base On Company Setting" &
                    "Allow Website Editors to edit HR Job Recruitment Page Base on Specific Website"

            Output: not allowed to write website_description on job A
        """
        self.env['res.company'].search([]).write({
            'allow_edit_website_jobs_company_setting': True
        })
        self.env['website'].search([]).write({
            'allow_edit_website_jobs_website_setting': True
        })
        self.job.write({
            'website_id': False,
            'company_id': False
        })
        with self.assertRaises(AccessError):
            self.job.with_user(self.user_demo).write({
                'website_description': '<p>Test</p>'
            })
