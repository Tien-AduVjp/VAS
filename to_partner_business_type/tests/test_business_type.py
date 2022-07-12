from psycopg2 import IntegrityError

from odoo.tests import TransactionCase
from odoo.tests.common import Form, tagged
from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestBusinessType(TransactionCase):

    def setUp(self):
        super(TestBusinessType, self).setUp()
        self.business_tnhh = self.env['res.partner.business.type'].create({
            'name':'TNHH Company'
        })
        self.business_join_stock = self.env['res.partner.business.type'].create({
            'name':'Joint Stock Company'
        })
        self.contact_a = self.env['res.partner'].create({
            'name':'Contact A',
            'company_type': 'company',
            'business_type_id':self.business_tnhh.id
        })
        self.contact_b = self.env['res.partner'].create({
            'name':'Contact B',
            'company_type': 'person',
        })

    def test_choose_business_type(self):
        """
        Test1: Choose the type of business for the contact, which is company type
        Test2: In the form view, change company type to individual and don't save, later change individual type to company and check business type
        """
        # Test1
        self.assertEqual(self.contact_a.business_type_id, self.business_tnhh, "Business type is incorrect")

        # Test2
        contact_a_form = Form(self.contact_a)
        contact_a_form.company_type = 'person'
        contact_a_form.company_type = 'company'
        self.assertEqual(contact_a_form.business_type_id, self.business_tnhh, "After change company type, business type is incorrect")

    def test_change_company_type(self):
        """
        Test1: Change company type to individual, check business type
        Test2: Change company type to individual and save, later change individual type to company and check business type
        """
        # Test1
        contact_a_form = Form(self.contact_a)
        contact_a_form.company_type = 'person'
        self.assertNotEqual(contact_a_form.business_type_id, self.business_tnhh, "Business type information is still exists")

        # Test2
        contact_b_form = Form(self.contact_b)
        contact_b_form.company_type = 'company'
        self.assertNotEqual(contact_b_form.business_type_id, self.business_tnhh, "Business type information is still exists")

    @mute_logger('odoo.sql_db')
    def test_01_remove_business_type(self):
        # Remove business type when assigned to a partner
        with self.assertRaises(IntegrityError):
            self.business_tnhh.unlink()

    def test_02_remove_business_type(self):
        # Remove business type when not assigned to a partner
        self.business_join_stock.unlink()
