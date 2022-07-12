from odoo.tests import tagged, Form

from .common import HrTestEmployeeCommon


@tagged('post_install', '-at_install')
class TestPartner(HrTestEmployeeCommon):

    def test_method_compute_hr_applicants_count(self):
        # Check compute applicants count link with partner
        # Compute no store and no depend, we need user Form test to get data from cache
        applicant_b_form = Form(self.env['hr.applicant'])
        applicant_b_form.name = 'Applicant Woman'
        applicant_b_form.partner_name = 'Applicant Woman'
        applicant_b_form.email_from = 'applicant.woman@example.viindoo.com'
        applicant_b_form.stage_id = self.env.ref('hr_recruitment.stage_job2')
        applicant_b = applicant_b_form.save()
        partner = applicant_b.partner_id
        self.assertEqual(partner.hr_applicants_count, 1,
                         "The method compute hr applicants account not success")

        pplicant_c_form = Form(self.env['hr.applicant'])
        pplicant_c_form.name = 'Applicant Woman'
        pplicant_c_form.partner_name = 'Applicant Woman'
        pplicant_c_form.email_from = 'applicant.woman@example.viindoo.com'
        pplicant_c_form.stage_id = self.env.ref('hr_recruitment.stage_job2')
        pplicant_c_form.save()

        self.assertEqual(partner.hr_applicants_count, 2,
                         "The method compute hr applicants account not success")
