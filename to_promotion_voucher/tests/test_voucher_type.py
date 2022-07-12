from psycopg2 import IntegrityError

from odoo.tests import tagged
from odoo.exceptions import UserError
from odoo.tools.misc import mute_logger

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestVoucherType(TestCommon):

    def test_01_check_constrains_voucher_type(self):
        # Create new voucher type, voucher value > 0, valid duration > 0
        voucher_type = self.VoucherType.create({'name':'New', 'value': 100000, 'valid_duration': 30})
        self.assertIn(voucher_type.id, self.VoucherType.search([]).ids, "Create failed")

    @mute_logger('odoo.sql_db')
    def test_02_check_constrains_voucher_type(self):
        # Create new voucher type, voucher value = 0 or valid duration = 0
        with self.assertRaises(IntegrityError):
            voucher_type = self.VoucherType.create({'name':'New', 'value': 0, 'valid_duration': 30})
            voucher_type.flush()

    def test_03_check_constrains_voucher_type(self):
        # Voucher type not have voucher issued allow value correction
        self.voucher_type.write({'value': 10})
        self.assertEqual(self.voucher_type.value, 10)

    def test_04_check_constrains_voucher_type(self):
        # Voucher type have voucher issued does not allow value correction
        self.voucher_type.write({'voucher_ids': [(6, 0, [self.voucher.id])]})
        with self.assertRaises(UserError):
            self.voucher_type.write({'value': 10})

    def test_05_check_constrains_voucher_type(self):
        # Duplicate voucher type
        voucher_type = self.voucher_type.copy()
        self.assertIn(voucher_type.id, self.VoucherType.search([]).ids, "Duplicate failed")
