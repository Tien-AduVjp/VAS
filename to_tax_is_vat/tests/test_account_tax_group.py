from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestAccountTaxGroup(TransactionCase):
    
    def setUp(self):
        super(TestAccountTaxGroup, self).setUp()
        self.tax_group1 = self.env['account.tax.group'].create({
            'name': 't1',
            'is_vat': True
            })
        
        self.tax_group2 = self.env['account.tax.group'].create({
            'name': 't2',
            'is_vat': False
            })
       
    def test_is_vat(self):
        self.assertEqual(self.tax_group1.is_vat, True, "'Is VAT' is not checked on this tax group")
        self.assertEqual(self.tax_group2.is_vat, False, "'Is VAT' is checked on this tax group")
