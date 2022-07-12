from psycopg2 import IntegrityError

from odoo.tools import mute_logger
from odoo.tests.common import tagged, Form

from .common import Common

@tagged('post_install', '-at_install')
class TestEquityRange(Common):

    #Case 1
    def test_create_equity_range(self):
        """
        INPUT: Create new contact A and assign equity range 'From 5 to 10M USD' to contact A
        OUTPUT: Equity range 'From 5 to 10M USD' is assigned to contact A
        """
        self.assertEqual(self.contact_a.equity_range_id, self.equity_range_5_10M_USD)

    #Case 2
    def test_01_change_company_type(self):
        """
        INPUT: Change type company of contact A from 'company' to 'individual'
        OUTPUT: Equity range of contact A is invisible
        """
        contact_a_form = Form(self.contact_a)
        contact_a_form.company_type = 'person'
        self.assertFalse(contact_a_form.equity_range_id)
        self.assertTrue(contact_a_form._get_modifier('equity_range_id', 'invisible'))

    #Case 3
    def test_02_change_company_type(self):
        """
        INPUT: Change type company of contact B from 'individual' to 'company'
        OUTPUT: Equity range of contact B is empty
        """
        contact_b_form = Form(self.contact_b)
        contact_b_form.company_type = 'company'
        self.assertFalse(contact_b_form.equity_range_id)
        self.assertFalse(contact_b_form._get_modifier('equity_range_id', 'invisible'))

    #Case 4
    @mute_logger('odoo.sql_db')
    def test_remove_equity_range(self):
        """
        INPUT: Remove equity_range 'From 5 to 10M USD' which is assigned to Contact A
        OUTPUT: Remove unsuccessful
        """
        with self.assertRaises(IntegrityError):
            self.equity_range_5_10M_USD.unlink()

    #Case 5
    def test_unique_name_equity_range(self):
        """
        INPUT: Create new record of Partner Equity Range with exist name
        OUTPUT: Raise a false of constraints unique
        """
        Range  = self.env['res.partner.equity.range']
        Range.create({'name' : 'range_1'})
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            Range.create({'name' : 'range_1'})

    #Case 6
    def test_duplicate_record_equity_range(self):
        """
        INPUT: Duplicate record
        OUTPUT: New record has a unique name with suffix (Copy)
        """
        duplicate_record = self.equity_range_5_10M_USD.copy()
        self.assertNotEqual(duplicate_record.name, self.equity_range_5_10M_USD.name, "New record's name already exist")
