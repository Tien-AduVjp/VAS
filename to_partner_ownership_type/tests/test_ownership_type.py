from psycopg2 import IntegrityError

from odoo.tools import mute_logger
from odoo.tests import tagged
from odoo.tests.common import Form

from .common import Common


@tagged('post_install', '-at_install')
class TestOwnershipType(Common):

    #Case 1
    def test_create_ownership_type(self):
        """
        INPUT: Create new contact A and assign ownership type 'Join Stock Company' to contact A
        OUTPUT: Ownership type 'Join Stock Company' is assigned to contact A
        """
        self.assertEqual(self.contact_a.ownership_type_id, self.ownership_type_joint_stock_company)

    #Case 2
    def test_01_change_company_type(self):
        """
        INPUT: Change type company of contact A from 'company' to 'individual'
        OUTPUT: Ownership type of contact A is empty
        """
        contact_a_form = Form(self.contact_a)
        contact_a_form.company_type = 'person'
        self.assertFalse(contact_a_form.ownership_type_id)
        self.assertTrue(contact_a_form._get_modifier('ownership_type_id', 'invisible'))

    #Case 3
    def test_02_change_company_type(self):
        """
        INPUT: Change type company of contact B from 'individual' to 'company'
        OUTPUT: Ownership type of contact B is empty
        """
        contact_b_form = Form(self.contact_b)
        contact_b_form.company_type = 'company'
        self.assertFalse(contact_b_form.ownership_type_id)
        self.assertFalse(contact_b_form._get_modifier('ownership_type_id', 'invisible'))

    #Case 4
    @mute_logger('odoo.sql_db')
    def test_01_remove_ownership_type(self):
        """
        INPUT: Remove ownership type 'Join Stock Company' which is assigned to Contact A
        OUTPUT: Remove unsuccessful
        """
        with self.assertRaises(IntegrityError):
            self.ownership_type_joint_stock_company.unlink()

    #Case 5
    @mute_logger('odoo.sql_db')
    def test_unique_name_ownership_type(self):
        """
        INPUT: Create new record of Partner Equity Range with exist name
        OUTPUT: Raise a false of constraints unique
        """
        Type = self.env['res.partner.ownership.type']
        Type.create({'name' : 'range 1'})
        with self.assertRaises(IntegrityError):
            Type.create({'name' : 'range 1'})

    #Case 6
    def test_duplicate_record_ownership_type(self):
        """
        INPUT: Duplicate record
        OUTPUT: New record has a unique name with suffix (Copy)
        """
        duplicate_record = self.ownership_type_joint_stock_company.copy()
        self.assertNotEqual(duplicate_record.name,
                            self.ownership_type_joint_stock_company.name,
                            "New record's name already exist")
