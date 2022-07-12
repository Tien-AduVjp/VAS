from odoo.tests import tagged
from odoo.exceptions import AccessError

from odoo.addons.account.tests.account_test_classes import AccountingTestCase


@tagged('post_install', '-at_install')
class TestInvoiceTaxDetailsSettings(AccountingTestCase):
    
    def test_10_switch_tax_details(self):
        config = self.env['res.config.settings'].create({})
        config.show_line_subtotals_tax_selection = 'tax_details'
        self.assertEqual(config.show_line_subtotals_tax_selection, 'tax_details')
        
        config._onchange_sale_tax()
        config.flush()
        config.execute()
        
        self.assertEqual(self.env.user.has_group('account.group_show_line_subtotals_tax_excluded'), False)
        self.assertEqual(self.env.user.has_group('account.group_show_line_subtotals_tax_included'), False)
        self.assertEqual(self.env.user.has_group('to_invoice_tax_details.group_show_line_tax_details'), True)
    
    def test_20_access_right(self):
        user_admin = self.env.ref('base.user_admin')
        public_user = self.env.ref('base.public_user')
        config = self.env['res.config.settings'].with_user(user_admin).create({})
        config.with_user(user_admin).write({'show_line_subtotals_tax_selection': 'tax_details'})
        config.with_user(user_admin).execute()
        self.assertEqual(config.show_line_subtotals_tax_selection, 'tax_details')
        
        config.with_user(public_user).write({'show_line_subtotals_tax_selection': 'tax_included'})
        with self.assertRaises(AccessError):
            config.with_user(public_user).execute()
