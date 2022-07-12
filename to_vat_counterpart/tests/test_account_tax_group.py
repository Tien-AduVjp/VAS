from odoo.tests import tagged

from odoo.exceptions import ValidationError

from .common import Common


@tagged('post_install', '-at_install')
class TestAccountTaxGroup(Common):
    
    # 'Is Vat' is False
    def test_constrains_is_vat_vat_ctp_account_id(self):
        with self.assertRaises(ValidationError):
            self.account_tax_group1.write({'is_vat': False})
