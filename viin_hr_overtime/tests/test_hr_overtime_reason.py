from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.tests import SavepointCase
from odoo.tools import mute_logger


@tagged('post_install','-at_install')
class TestHrOvertimeReason(SavepointCase):

    def setUp(self):
        super(TestHrOvertimeReason, self).setUp()
        self.company_01 = self.env.ref('base.main_company')
        self.company_02 = self.env['res.company'].create({
            'name': 'My Company'
        })

    #-----------------------------------------------------------Test Functional-----------------------------------------------------------#
    @mute_logger('odoo.sql_db')
    def test_01_unique_overtime_reason(self):
        """
            Case: Test unique overtime reason in case create new record with existed title and don't have a company.
            Expect: Can't create, show user error.
        """
        self.env['hr.overtime.reason'].create({
                'name': self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name,
            })
        with self.assertRaises(IntegrityError):
            self.env['hr.overtime.reason'].create({
                'name': self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name,
            })
    
    def test_02_unique_overtime_reason(self):
        """
            Case: Test unique overtime reason in case create new record with dont't existed title and don't have a company.
            Expect: Can create, don't show user error.
        """
        try:
            self.env['hr.overtime.reason'].create({
                'name': self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name,
            })
        except IntegrityError:
            self.fail("Unexpected error.")

    @mute_logger('odoo.sql_db')
    def test_03_unique_overtime_reason(self):
        """
            Case: Test unique overtime reason in case create new record with existed title and company.
            Expect: Cannot create, show user error.
        """
        self.env['hr.overtime.reason'].create({
            'name':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name,
            'company_id': self.company_01.id
        })
        with self.assertRaises(IntegrityError):
            self.env['hr.overtime.reason'].create({
                'name':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name,
                'company_id': self.company_01.id
            })

    def test_04_unique_overtime_reason(self):
        """
            Case: Test unique overtime reason in case create new record with existed title but different company.
            Expect: Can create, don't show user error.
        """
        self.env['hr.overtime.reason'].create({
            'name': self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name,
            'company_id': self.company_01.id
        })
        try:
            self.env['hr.overtime.reason'].create({
                'name': self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name,
                'company_id': self.company_02.id,
            })
        except IntegrityError:
            self.fail("Unexpected error.")

    @mute_logger('odoo.sql_db')
    def test_05_unique_overtime_reason(self):
        """
            Case: Test unique overtime reason in case duplicated existed record.
            Expect: Cannot create, show user error.
        """
        overtime_reason_01 = self.env['hr.overtime.reason'].create({
            'name':self.env.ref('viin_hr_overtime.hr_overtime_reason_general').name,
            'company_id': self.company_01.id
        })
        with self.assertRaises(IntegrityError):
            overtime_reason_01.copy()

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
