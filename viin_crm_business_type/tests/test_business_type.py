from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestBusinessType(TransactionCase):

    def setUp(self):
        super(TestBusinessType, self).setUp()
        self.business_tnhh = self.env['res.partner.business.type'].create({
            'name':'TNHH Company'
        })
        self.lead_demo = self.env['crm.lead'].create({
            'name': 'Lead demo'
            })

    def test_choose_business_type(self):
        """
        Test: Choose the business type for the lead
        """
        # Test
        self.lead_demo.write({
            'business_type_id': self.business_tnhh.id,
        })
        self.assertEqual(self.lead_demo.business_type_id, self.business_tnhh, 'Business type is incorrect')
