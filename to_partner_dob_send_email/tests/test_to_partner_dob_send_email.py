from odoo import fields

from odoo.tests import tagged
from odoo.tests.common import Form, TransactionCase

from . import ultil


@tagged('post_install', '-at_install')
class TestToPartnerDobSendEmail(TransactionCase):

    def setUp(self):
        super(TestToPartnerDobSendEmail, self).setUp()
        self.res_partner_form = Form(self.env['res.partner'])
        self.company_email_template_partner_happy_birthday = self.env.ref('to_partner_dob_send_email.email_template_partner_happy_birthday')
        self.env.company.hdb_email_template_id = self.company_email_template_partner_happy_birthday
        self.cron_send_hdb_email = self.env.ref('to_partner_dob_send_email.ir_cron_scheduler_sync_attendance')
        self.viindoo_partner_1 = self.env['res.partner'].create({
            'name':'Viindoo Partner 01',
            'company_type':'person',
            'dob':ultil.generate_random_birthday(),
            'property_send_hbd_email':True,
            'property_hbd_email_template_id':self.env.company.hdb_email_template_id.id
        })
        self.viindoo_partner_2 = self.env['res.partner'].create({
            'name':'Viindoo Partner 02',
            'company_type':'person',
            'email':'viin.partner02@example.viindoo.com',
            'property_send_hbd_email':True,
            'dob':ultil.generate_random_birthday(),
            'property_hbd_email_template_id':self.env.company.hdb_email_template_id.id
        })
        self.viindoo_partner_3 = self.env['res.partner'].create({
            'name':'Viindoo Partner 03',
            'company_type':'person',
            'email':'viin.partner03@example.viindoo.com',
            'dob':ultil.generate_random_birthday(),
            'property_send_hbd_email':True,
            'property_hbd_email_template_id':self.env.company.hdb_email_template_id.id

        })

    def test_res_partner_onchange_dob(self):
        """
            Testcase 1 - Onchange: The field "Send Happy Birthday Email" should be auto enabled when was set
        """
        self.res_partner_form.dob = fields.Date.to_date('1989-01-10')
        self.assertTrue(self.res_partner_form.property_send_hbd_email, "Send Happy Bithday have to auto enable when birday of partner was set")

    def test_res_partner_onchange_send_hbd_email(self):
        """
            Testcase 2 - Onchange: The field "Happy Birthday Email Template" of partner should be company email template.
        """
        self.res_partner_form.dob = fields.Date.to_date('1989-01-10')
        self.assertEqual(self.res_partner_form.property_hbd_email_template_id, self.env.company.hdb_email_template_id, "Template email send happly bithday to partner should be set same with company")

    def test_send_hpbd_to_partner(self):
        """
            User without email: cannot send happy birthday email.
            User with email: Should send happy birthday email to all partners have same birthday.
        """
        self.cron_send_hdb_email.method_direct_trigger()
        self.assertFalse(self.viindoo_partner_1.property_last_hbd_email_sent, "Partner without email: cannot send hpbd email")
        self.assertEqual(self.viindoo_partner_2.property_last_hbd_email_sent, fields.Date.today(), "Partner should send hpbd email by today")
        self.assertEqual(self.viindoo_partner_3.property_last_hbd_email_sent, fields.Date.today(), "Partner should send hpbd email by today")

    def test_duplicate_partner(self):
        """
            when duplicate a partner record, value of fields 'Send Happy Birthday Email' and 'Happy Birthday Email Template' should be copied.
        """
        viindoo_partner_4 = self.viindoo_partner_3.copy()
        self.assertEqual(viindoo_partner_4.property_send_hbd_email, self.viindoo_partner_3.property_send_hbd_email)
        self.assertEqual(viindoo_partner_4.property_hbd_email_template_id, self.viindoo_partner_3.property_hbd_email_template_id)
