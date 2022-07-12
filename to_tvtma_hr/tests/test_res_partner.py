from odoo.tests import tagged

from .test_tvtma_hr_savepoint import HrTestEmployeeCommon


@tagged('post_install', '-at_install')
class TestPartner(HrTestEmployeeCommon):
    
    def test_method_compute_hr_applicants_count(self):
        # Check compute applicants count link with partner
        stage_job2 = self.env.ref('hr_recruitment.stage_job2')
        self.applicant_b.write({'stage_id': stage_job2.id})
        partner = self.applicant_b.partner_id
        self.assertEqual(partner.hr_applicants_count, 1, "The method compute hr applicants account not success")
        
        self.applicant_c = self.env['hr.applicant'].create({
            'name': 'Applicant Woman 2',
            'partner_name': 'Applicant Woman 2',
            'email_from': 'applicant.woman@example.viindoo.com'
            })
        self.applicant_c.write({'stage_id': stage_job2.id})
        
        self.assertEqual(partner.hr_applicants_count, 2, "The method compute hr applicants account not success")
