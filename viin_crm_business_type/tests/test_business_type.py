from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBusinessType(TransactionCase):

    def setUp(self):
        #Setup demo data
        super(TestBusinessType, self).setUp()
        #Create business type
        self.business_jsc = self.env['res.partner.business.type'].create({
            'name':'JSC Company'
            })
        self.business_fc = self.env['res.partner.business.type'].create({
            'name':'FC Company'
            })
        # create a lead
        self.lead_demo = self.env['crm.lead'].with_context(tracking_disable=True).create({
            'name': 'Lead demo'
            })
        # create partner
        self.company_demo = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Demo partner ',
            'is_company': True
            })
        self.person_demo_have_company = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Demo partner 2',
            'is_company': False,
            'parent_id': self.company_demo.id
            })
        self.person_demo_no_company = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Demo partner 3',
            'is_company': False,
            })

    def test_compute_customer_is_company(self):
        """
        Case: change opportunity with customer is company .
        Expect: business type's oportunity is business_jsc .
        """
        self.lead_demo.write({
            'partner_id': self.company_demo.id
            })
        self.company_demo.write({
            'business_type_id': self.business_jsc.id
            })
        self.assertEqual(self.lead_demo.business_type_id,
                         self.business_jsc,
                         'Business type on lead is not correct')

    def test_compute_customer_is_person_no_company(self):
        """
        Case: Change opportunity with customer is person, this person don't have any company .
        Expect: business type's oportunity is False.
        """
        self.lead_demo.write({
            'partner_id': self.person_demo_no_company.id
            })
        self.assertEqual(self.lead_demo.business_type_id.id,
                        False,
                         'Business type on lead is not correct')

    def test_compute_customer_is_person_have_company(self):
        """
        Case: Change opportunity with customer is person, this person have company .
        Expect: business type's oportunity is business_fc" .
        """
        self.company_demo.write({
            'business_type_id': self.business_fc.id
            })
        self.lead_demo.write({
            'partner_id': self.person_demo_have_company.id
            })
        self.assertEqual(self.lead_demo.business_type_id,
                         self.business_fc,
                         'Business type on lead is not correct')

    def test_convert_lead2opportunity_create_partner(self):
        """
        Case: With company name in lead,convert to opportunity then create new partner .
        Expect: Business type in Partner is business_jsc .
        """
        self.lead_demo.write({
            'business_type_id': self.business_jsc.id,
            'partner_name': "CompanyName"
            })
        LeadConvertWizard = self.env['crm.lead2opportunity.partner'].with_context(
            active_model=self.lead_demo._name,
            active_id=self.lead_demo.id,
            active_ids=self.lead_demo.ids
            )
        lead_convert = LeadConvertWizard.create({
            'name': 'convert',
            'action': 'create',
            })
        result = lead_convert.action_apply()
        result_lead = self.env['crm.lead'].browse(result['res_id'])
        new_partner = result_lead.partner_id
        self.assertEqual(new_partner.business_type_id,
                         self.business_jsc,
                         'Business type on lead is not the same as partner')

    def test_convert_lead2opportunity_create_partner_person_have_company(self):
        """
        Case: With company name and contact name in lead,convert to opportunity then create new partner .
        Expect: Business type in Partner is business_jsc .
        """
        self.lead_demo.write({
            'business_type_id': self.business_jsc.id,
            'partner_name': "CompanyName",
            'contact_name': "PersonName"
            })
        LeadConvertWizard = self.env['crm.lead2opportunity.partner'].with_context(
            active_model=self.lead_demo._name,
            active_id=self.lead_demo.id,
            active_ids=self.lead_demo.ids
            )
        lead_convert = LeadConvertWizard.create({
            'name': 'convert',
            'action': 'create',
            })
        result = lead_convert.action_apply()
        result_lead = self.env['crm.lead'].browse(result['res_id'])
        new_partner = result_lead.partner_id
        company_of_person = new_partner.parent_id
        self.assertEqual(company_of_person.business_type_id,
                         self.business_jsc,
                         'Business type on lead is not the same as partner')

    def test_convert_lead2opportunity_create_partner_person(self):
        """
        Case: With contact name in lead,convert to opportunity then create new partner .
        Expect: Business type in Partner is False .
        """
        self.lead_demo.write({
            'business_type_id': self.business_jsc.id,
            'contact_name': "PersonName"
            })
        LeadConvertWizard = self.env['crm.lead2opportunity.partner'].with_context(
            active_model=self.lead_demo._name,
            active_id=self.lead_demo.id,
            active_ids=self.lead_demo.ids
            )
        lead_convert = LeadConvertWizard.create({
            'name': 'convert',
            'action': 'create',
            })
        result = lead_convert.action_apply()
        result_lead = self.env['crm.lead'].browse(result['res_id'])
        new_partner = result_lead.partner_id
        self.assertEqual(new_partner.business_type_id.id,
                         False,
                         'Business type on lead is not the same as partner')

    def test_change_business_type_in_partner_person_have_company(self):
        """
        Case: A Lead have partner is person and this person have a company, change business type in company .
        Expect: Business type in lead not change same company's partner person .
        """
        self.company_demo.write({
            'business_type_id': self.business_fc.id
            })
        self.lead_demo.write({
            'partner_id': self.person_demo_have_company.id
            })
        self.lead_demo.flush()
        self.company_demo.write({
            'business_type_id': self.business_jsc.id
            })
        self.assertEqual(self.lead_demo.business_type_id,
                         self.business_fc,
                         'Business type in lead must be not change')

    def test_change_business_type_in_partner_company(self):
        """
        Case: A Lead have partner is company, change business type in this company .
        Expect: Business type in lead not change same partner .
        """
        self.company_demo.write({
            'business_type_id': self.business_fc.id
            })
        self.lead_demo.write({
            'partner_id': self.company_demo.id
            })
        self.lead_demo.flush()
        self.company_demo.write({
            'business_type_id': self.business_jsc.id
            })
        self.assertEqual(self.lead_demo.business_type_id,
                         self.business_fc,
                         'Business type in lead must be not change')
