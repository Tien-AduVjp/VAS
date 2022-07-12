from odoo.tests import tagged
from odoo.exceptions import ValidationError

from .common import Common


@tagged('post_install', '-at_install')
class TestAccountTaxRepartion(Common):
    
    def test_check_is_vat_vat_ctp_account_id(self):
        self.account_tax1.invoice_repartition_line_ids[:1].vat_ctp_account_id = self.account
        self.account_tax1.refund_repartition_line_ids[:1].vat_ctp_account_id = self.account
        # Invoice is not VAT or False
        with self.assertRaises(ValidationError):
            self.account_tax1.invoice_repartition_line_ids[:1].invoice_tax_id = self.account_tax2
        # Refund tax is not VAT or False
        with self.assertRaises(ValidationError):
            self.account_tax1.invoice_repartition_line_ids[:1].refund_tax_id = self.account_tax2
