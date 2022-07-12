from odoo.tests.common import tagged
from .test_common import TestCommon


@tagged('-at_install', 'post_install')
class TestOdooVersion(TestCommon):
    
    def test_create_odoo_version(self):
        # case 2:
        odoo_version1 = self.env['odoo.version'].create({
            'release_date': '2021-09-25',
            'name': '14.1.1'
        })
        self.assertEqual(odoo_version1.git_branch_ids[0].id, self.git_branch14.id)
    
    def test_edit_name_odoo_version(self):
        # case 2:
        self.odoo_version13.git_branch_ids = self.git_branch1 + self.git_branch14
        self.odoo_version13.name = '14.1.1'
        
        self.assertEqual(len(self.odoo_version13.git_branch_ids), 1)
        self.assertEqual(self.odoo_version13.git_branch_ids[0].id, self.git_branch14.id)
    
    def test_compute_git_branches_count(self):
        # case 5:
        self.odoo_version13.git_branch_ids = self.git_branch1 + self.git_branch14
        self.assertEqual(self.odoo_version13.git_branches_count, 2)
