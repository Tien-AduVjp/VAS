from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tests import TransactionCase
from odoo.tools import mute_logger


@tagged('post_install','-at_install')
class TestHrOvertimeReason(TransactionCase):

    def setUp(self):
        super(TestHrOvertimeReason, self).setUp()
    
    #-----------------------------------------------------------Test Functional-----------------------------------------------------------#
     
    @mute_logger('odoo.sql_db')
    def test_01_unique_overtime_reason(self):
        """
            Case: Test unique overtime reason in case create new record with existed title.
            Expect: Cannot create, show user error.
        """
        with self.assertRaises(IntegrityError):
            self.env['hr.overtime.reason'].create({
                'name':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name
            })
    
    @mute_logger('odoo.sql_db')
    def test_02_unique_overtime_reason(self):
        """
            Case: Test unique overtime reason in case duplicated existed record.
            Expect: Cannot create, show user error. 
        """    
        with self.assertRaises(IntegrityError):
            self.env.ref('viin_hr_overtime.hr_overtime_reason_general').copy()

    @mute_logger('odoo.sql_db')
    def test_unique_overtime_code(self):
        """
            Test unique overtime reason in case create new record with existed name.
        """   
        ot0006 = self.env.ref('viin_hr_overtime.rule_code_ot0006')
        with self.assertRaises(IntegrityError):
            self.env['hr.overtime.rule.code'].create({
                'name':ot0006.name
            })
