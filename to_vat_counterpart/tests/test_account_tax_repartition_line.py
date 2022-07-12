from odoo.tests import tagged
from .common import Common


@tagged('post_install', '-at_install')
class TestAccountTaxRepartion(Common):

    def test_check_vat_ctp_account_id(self):
        vat_ctp_account = self.account_tax1.invoice_repartition_line_ids[:1].vat_ctp_account_id
        self.assertEqual(vat_ctp_account, self.env.company.property_vat_ctp_account_id)
