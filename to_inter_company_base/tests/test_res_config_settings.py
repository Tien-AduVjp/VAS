from odoo.tests import TransactionCase
from odoo.exceptions import UserError
from odoo.tests.common import Form, tagged

from odoo.tools import mute_logger


@tagged('post_install', '-at_install')
class TestResConfigSetting(TransactionCase):
    def setUp(self):
        super(TestResConfigSetting, self).setUp()
        self.res_config_setting_obj = self.env['res.config.settings']
        self.res_config_setting_form = Form(self.res_config_setting_obj)

    def test_check_require_module_to_inter_company_invoice(self):
        """
            Inter-Company for Invoices must be enabled while Inter-Company for Sale/Purchase is enabled.
        """
        with self.assertRaises(UserError):
            self.res_config_setting_obj.create({
                'module_to_inter_company_sale_purchase':True,
                'module_to_inter_company_invoice':False
            })

    def test_onchange_module_to_inter_company_sale_purchase(self):
        """
            Inter-Company for Invoices must be enabled when enable Inter-company for Sale/Purchase
        """
        self.res_config_setting_form.module_to_inter_company_sale_purchase = True
        self.assertTrue(self.res_config_setting_form.module_to_inter_company_invoice,"Inter-Company for Invoices must be enabled when enable Inter-company for Sale/Purchase")

    def test_onchange_module_to_inter_company_invoice(self):
        """
            Inter-Company for Sale/Purchase must be disabled when disable Inter-Company for Invoice
        """
        with mute_logger('odoo.tests.common.onchange'):
            self.res_config_setting_form.module_to_inter_company_invoice = False
            self.assertFalse(self.res_config_setting_form.module_to_inter_company_sale_purchase,"Inter-Company for Invoices must be enabled when enable Inter-company for Sale/Purchase")
