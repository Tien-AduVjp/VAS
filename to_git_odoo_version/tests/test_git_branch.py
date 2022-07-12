from odoo.exceptions import ValidationError
from odoo.tests.common import tagged
from .test_common import TestCommon


@tagged('-at_install', 'post_install')
class TestToGitOdooVersion(TestCommon):
    
    def test_create_git_branch(self):
        # case 1: create git.branch with the same name as odoo.version
        git_branch = self.env['git.branch'].with_context(skip_check_branch_name=True).create({
            'repository_id': self.git_repo1.id,
            'name': '13.1.1'
        })
        self.assertEqual(git_branch.odoo_version_id.id, self.odoo_version13.id)
    
    def test_edit_name_git_branch(self):
        # case 1: edit git.branch with the same name as odoo.version
        self.git_branch1.name = '13.1.1'
        self.assertEqual(self.git_branch1.odoo_version_id.id, self.odoo_version13.id)
    
    def test_check_is_odoo_source_code_vs_is_odoo_enterprise_source_code(self):
        # case 3:
        with self.assertRaises(ValidationError):
            self.git_branch14.is_odoo_source_code = True
            self.git_branch14.is_odoo_enterprise_source_code = True
    
    def test_check_depending_git_branches(self):
        # case 6:
        self.git_branch15.odoo_version_id = self.odoo_version15
        self.git_branch1.odoo_version_id = self.odoo_version13
        
        with self.assertRaises(ValidationError):
            self.git_branch15.depending_git_branch_ids = self.git_branch1
    
    def test_check_depended_git_branches(self):
        # case 7:
        self.git_branch15.odoo_version_id = self.odoo_version15
        self.git_branch1.odoo_version_id = self.odoo_version13
        
        with self.assertRaises(ValidationError):
            self.git_branch15.depended_git_branch_ids = self.git_branch1
