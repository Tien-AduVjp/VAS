from . import test_common

from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestOdooModule(test_common.TestCommon):

    def test_get_latest_version(self):
        latest_version = self.test_om.get_latest_version().odoo_version_id.name
        self.assertEqual(first=latest_version,
                         second='13.0',
                         msg="Latest version of module should be '13.0'")
        self.assertEqual(first=self.test_om.odoo_module_version_id.id,
                         second=self.test_omv_test_sale_template_13.id,
                         msg="Module latest version should be id of its latest version")
