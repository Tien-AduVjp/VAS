import datetime
from lxml import etree

from odoo.tests import TransactionCase, Form, tagged


@tagged('post_install', '-at_install')
class TestCrmLead(TransactionCase):
    def setUp(self):
        super(TestCrmLead, self).setUp()
        self.lead_1 = self.env.ref('crm.crm_case_1')

    def test_compute_yy_mm_of_birth(self):
        # Set birthday on lead
        self.lead_1.write({
            'customer_dob': '1990-08-21'
        })

        # Check if compute values is correct
        self.assertEqual(self.lead_1.customer_dyob, 21, "Day of birth does not match!")
        self.assertEqual(self.lead_1.customer_mob, 8, "Month of birth does not match!")
        self.assertEqual(self.lead_1.customer_yob, 1990, "Year of birth does not match!")

    def test_default_compute_yy_mm_of_birth(self):
        # Check if default values is correct
        self.assertEqual(self.lead_1.customer_dyob, 0, "Day of birth does not match!")
        self.assertEqual(self.lead_1.customer_mob, 0, "Month of birth does not match!")
        self.assertEqual(self.lead_1.customer_yob, 0, "Year of birth does not match!")

    def test_compute_customer_dob(self):
        partner_1 = self.env.ref('base.res_partner_1')
        partner_1.write({ 'dob': '1991-06-01' })

        # Birth date on lead should be changed when assigning partner having birth date
        self.lead_1.partner_id = partner_1
        self.assertEqual(self.lead_1.customer_dob, datetime.date(1991, 6, 1))

        # Birth date on lead should be unchaged when chaging birth date on partner
        partner_1.write({ 'dob': '1991-07-13' })
        self.assertEqual(self.lead_1.customer_dob, datetime.date(1991, 6, 1))

        # Birth date on lead should be unchaged when unassign partner
        self.lead_1.partner_id = False
        self.assertEqual(self.lead_1.customer_dob, datetime.date(1991, 6, 1))

        # Birth date on lead should be unchaged if assigning partner without birth date
        partner_1.write({ 'dob': False })
        self.assertEqual(self.lead_1.customer_dob, datetime.date(1991, 6, 1))

    def test_create_partner_default_dob_context(self):
        # Set birthday and partner on lead
        self.lead_1.write({ 'customer_dob': '1990-08-21' })

        # Check if default context having default_dob
        with Form(self.lead_1) as f:
            values = f._get_context('partner_id')
            self.assertEqual(values.get('default_dob', False), '1990-08-21', "Default date of birth context does not match!")

    def test_lead2opportunity_create_partner(self):
        # Set birthday on lead
        self.lead_1.write({
            'customer_dob': '1990-08-21'
        })

        # Convert lead to opportunity (Create new partner)
        LeadConvertWizard = self.env['crm.lead2opportunity.partner'].with_context(
            active_model=self.lead_1._name,
            active_id=self.lead_1.id,
            active_ids=self.lead_1.ids
        )
        lead_convert = LeadConvertWizard.create({
            'name': 'convert',
            'action': 'create',
        })
        result = lead_convert.action_apply()
        result_lead = self.env['crm.lead'].browse(result['res_id'])
        new_partner = result_lead.partner_id

        # Check if birth date on partner is same as opportunity's
        self.assertEqual(new_partner.dob, self.lead_1.customer_dob, "Birth Date on partner doesn't match with oppotunity")

    def test_crm_lead_form(self):
        """
            Create a new form associate with model crm.lead
            Expected: 
            - If form contains only field `partner_id` then context of this field not contains `default_dob` 
            - If form contains both `partner_id` and `customer_dob` then context of this field contains `default_dob`
        """
        Crm_Lead = self.env['crm.lead']
        Partner = self.env['res.partner']
        partner_demo_1 = Partner.with_context(tracking_disable=True).create({
            'name': 'Johnny Depp',
            'dob' : '2022-06-18'
            })
        crm_lead_form = Form(Crm_Lead)
        crm_lead_form.name = 'Test lead demo 1'
        crm_lead_form.partner_id = partner_demo_1
        self.assertEqual(crm_lead_form._get_context('partner_id').get('default_dob', ''), partner_demo_1.dob,
                         "Errors: Context 'default_dob': customer_dob not pass through partner_id ")
        #remove field `customer_dob` from view crm.lead.form
        crm_lead_form_view_id = self.env.ref('viin_crm_dob.crm_lead_view_form')
        fields_view_get = self.env['crm.lead'].fields_view_get(crm_lead_form_view_id.id)
        arch = etree.XML(fields_view_get['arch'])
        for field_customer_dob in arch.xpath('//field[@name="customer_dob"]'):
            field_customer_dob.getparent().remove(field_customer_dob)
        
        #update date of birth Partner
        partner_demo_1.write({
            'dob' : '2022-05-18'
            })
        self.assertNotEqual(crm_lead_form._get_context('partner_id').get('default_dob', ''), partner_demo_1.dob,
                            "Errors: Context 'default_dob': customer_dob should not pass through partner_id because field `customer_dob` not in crm.lead form view")
