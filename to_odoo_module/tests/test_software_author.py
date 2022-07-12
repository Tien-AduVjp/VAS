from . import test_common

from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestSoftwareAuthor(test_common.TestCommon):

    def test_software_author_unlink(self):
        software_author = self.env['software.author'].create({
            'name': 'Software Author',
            'odoo_module_version_ids': [(6, 0, self.test_omv_test.ids)]
        })

        with self.assertRaises(UserError):
            software_author.unlink()
