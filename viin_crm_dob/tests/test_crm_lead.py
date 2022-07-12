import datetime
from lxml import etree

from odoo.tests import TransactionCase, Form, tagged


@tagged('post_install', '-at_install')
class TestCrmLead(TransactionCase):
    def setUp(self):
        super(TestCrmLead, self).setUp()
        self.lead_1 = self.env.ref('crm.crm_case_1')
        self.partner_1 = self.env.ref('base.res_partner_1')

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

    def test_onchange_partner_dob(self):
        # Set birth date on partner
        self.partner_1.write({ 'dob': '1991-06-01' })

        # Change partner on lead
        with Form(self.lead_1) as f:
            f.partner_id = self.partner_1

        # Check if date of birth on lead is changed
        self.assertEqual(self.lead_1.customer_dob, datetime.date(1991, 6, 1))

        # Change date of birth on lead
        with Form(self.lead_1) as f:
            f.customer_dob = '1990-08-21'

        # Ensure date of birth on partner is not changed
        self.assertEqual(self.partner_1.dob, datetime.date(1991, 6, 1))

        # Remove partner on lead
        with Form(self.lead_1) as f:
            f.partner_id = self.env['res.partner']

        # Ensure date of birth on lead is not changed
        self.assertEqual(self.lead_1.customer_dob, datetime.date(1990, 8, 21))

    def test_create_partner_default_dob_context(self):
        # Set birthday and partner on lead
        self.lead_1.write({ 'customer_dob': '1990-08-21' })

        # Check if default context having default_dob
        with Form(self.lead_1) as f:
            values = f._get_context('partner_id')
            self.assertEqual(values.get('default_dob', False), '1990-08-21', "Default date of birth context does not match!")

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
