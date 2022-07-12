from unittest import mock

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestCrmLead(TransactionCase):

    def setUp(self):
        super(TestCrmLead, self).setUp()
        self.lead = self.env['crm.lead'].with_context(tracking_disable=False).create({
            'name': 'Test Lead'
        })
        self.partner = self.env['res.partner'].with_context(tracking_disable=False).create({
            'name': 'Test Partner',
            'email': 'test-partner@example.viindoo.com',
            'phone': '0123456789',
            'mobile': '0987654321'
        })

    def test_recognize_partner_with_email(self):
        """
        Check recognize partner with email
        Expect:
            - Partner on lead is Test Partner
        """

        self.lead.write({
            'email_from': 'test-partner@example.viindoo.com',
            'phone': '0111222333',
            'mobile': '0333222111',
        })
        self.lead.action_recognize_partner()
        self.assertEquals(self.lead.partner_id.id, self.partner.id)

    def test_recognize_partner_with_phone(self):
        """
        Check recognize partner with phone
        Expect:
            - Partner on lead is Test Partner
        """

        self.lead.write({
            'email_from': 'test-partner-1@example.viindoo.com',
            'phone': '0123456789',
            'mobile': '0333222111',
        })
        self.lead.action_recognize_partner()
        self.assertEquals(self.lead.partner_id.id, self.partner.id)

    def test_recognize_partner_with_mobile(self):
        """
        Check recognize partner with mobile
        Expect:
            - Partner on lead is Test Partner
        """

        self.lead.write({
            'email_from': 'test-partner-1@example.viindoo.com',
            'phone': '0111222333',
            'mobile': '0987654321',
        })
        self.lead.action_recognize_partner()
        self.assertEquals(self.lead.partner_id.id, self.partner.id)

    def test_no_recognize_partner(self):
        """
        Check if partner is not recognized
        Expect:
            - Partner on lead is empty
        """
        self.lead.write({
            'email_from': 'test-partner-1@example.viindoo.com',
            'phone': '0111222333',
            'mobile': '0333222111',
        })
        self.lead.action_recognize_partner()
        self.assertFalse(self.lead.partner_id)

    def test_recognize_partner_after_create(self):
        """
        Check if partner if recognize after creating lead
        Expect:
            - Recognize partner function is called
        """

        with mock.patch.object(type(self.env['crm.lead']), '_recognize_partner') as mock_recognize_partner:
            mock_recognize_partner.return_value = True
            self.env['crm.lead'].with_context(tracking_disable=False).create({
                'name': 'Test Lead',
                'email_from': 'test-partner@example.viindoo.com',
                'phone': '0777888999',
                'mobile': '0999888777',
            })

            # Check if detect partner function is called
            mock_recognize_partner.assert_called_once()

    def test_lead_data_after_partner_recognize(self):
        """
        Check lead data after partner is recognized
        Expect:
            - Only partner is changed, partner information is not
        """
        self.lead.write({
            'email_from': 'test-partner@example.viindoo.com',
            'phone': '0111222333',
            'mobile': '0333222111',
        })
        self.lead.action_recognize_partner()

        # Customer data on lead is same as before
        self.assertEqual(self.lead.phone, '0111222333')
        self.assertEqual(self.lead.mobile, '0333222111')
